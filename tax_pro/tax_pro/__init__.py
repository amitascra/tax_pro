# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe

# Monkey patch the calculate_taxes_and_totals class to support "On Profit Margin" charge type
def patch_taxes_and_totals():
	"""
	Monkey patch ERPNext's calculate_taxes_and_totals.get_current_tax_amount method
	to add support for "On Profit Margin" charge type.
	"""
	from frappe.utils import cint, flt
	from erpnext.controllers import taxes_and_totals
	
	# Store the original method
	original_get_current_tax_amount = taxes_and_totals.calculate_taxes_and_totals.get_current_tax_amount
	
	def custom_get_current_tax_amount(self, item, tax, item_tax_map):
		"""
		Extended version of get_current_tax_amount that supports "On Profit Margin" charge type.
		"""
		tax_rate = self._get_tax_rate(tax, item_tax_map)
		current_tax_amount = 0.0
		current_net_amount = 0.0
		
		frappe.log_error(
			message=f"Tax Pro Backend: get_current_tax_amount called\nCharge Type: {tax.charge_type}\nItem: {item.item_code if hasattr(item, 'item_code') else 'NO ITEM CODE'}",
			title="Tax Pro Debug - Backend Tax Calculation"
		)
		
		# Handle "On Profit Margin" charge type
		if tax.charge_type == "On Profit Margin":
			try:
				frappe.log_error(
					message="Tax Pro Backend: On Profit Margin detected",
					title="Tax Pro Debug - Profit Margin Detected"
				)
				
				from tax_pro.tax_pro.utils.serial_profit import calculate_item_profit_margin
				
				# Calculate profit margin for this item
				item_profit = calculate_item_profit_margin(item)
				
				frappe.log_error(
					message=f"Tax Pro Backend: Item Profit: {item_profit}, Tax Rate: {tax_rate}",
					title="Tax Pro Debug - Profit Calculated"
				)
				
				# Apply tax rate to profit margin
				current_tax_amount = (tax_rate / 100.0) * item_profit
				current_tax_amount = flt(current_tax_amount)
				current_net_amount = flt(item_profit)
				
				# CRITICAL: Set item.taxable_value to profit margin
				# This ensures India Compliance validation passes when it recalculates:
				# tax_amount = tax_rate * item.taxable_value / 100
				if item_profit > 0:
					item.taxable_value = item_profit
					frappe.log_error(
						message=f"Set item.taxable_value = {item_profit} (profit margin) for item {item.item_code}",
						title="Tax Pro Debug - Taxable Value Set"
					)
				
				frappe.log_error(
					message=f"Tax Pro Backend: Net Amount: {current_net_amount}, Tax Amount: {current_tax_amount}",
					title="Tax Pro Debug - Tax Amount"
				)
				
			except Exception as e:
				frappe.log_error(
					message=f"Error calculating profit margin tax: {str(e)}\nItem: {item.name if hasattr(item, 'name') else item}\nTraceback: {frappe.get_traceback()}",
					title="Profit Margin Tax Calculation Error"
				)
				current_tax_amount = 0.0
				current_net_amount = 0.0
		else:
			# Use the original method for all standard charge types
			return original_get_current_tax_amount(self, item, tax, item_tax_map)
		
		# Store item-wise tax details
		if not (self.doc.get("is_consolidated") or tax.get("dont_recompute_tax")):
			self.set_item_wise_tax(item, tax, tax_rate, current_tax_amount)
		
		# Return only current_tax_amount (Python backend doesn't use destructuring like JS)
		return current_tax_amount
	
	# Replace the method
	taxes_and_totals.calculate_taxes_and_totals.get_current_tax_amount = custom_get_current_tax_amount


# Apply the patch when the module is imported
try:
	patch_taxes_and_totals()
except Exception as e:
	import frappe
	frappe.log_error(
		message=f"Error patching taxes_and_totals: {str(e)}",
		title="Tax Pro Module Init Error"
	)

