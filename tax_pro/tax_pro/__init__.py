# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

# Monkey patch the calculate_taxes_and_totals class to support "On Profit Margin" charge type
def patch_taxes_and_totals():
	"""
	Monkey patch ERPNext's calculate_taxes_and_totals.get_current_tax_amount method
	to add support for "On Profit Margin" charge type.
	"""
	import frappe
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
		
		frappe.log_error(
			message=f"Charge Type: {tax.charge_type}\nItem: {item.item_code if hasattr(item, 'item_code') else 'NO ITEM CODE'}\nSerial No Field: {item.get('custom_vehicle_serial_no', 'NOT FOUND')}\nTax Rate: {tax_rate}",
			title="Tax Pro Debug - Backend Tax Calculation"
		)
		
		# Handle "On Profit Margin" charge type
		if tax.charge_type == "On Profit Margin":
			try:
				frappe.log_error(
					message=f"Processing 'On Profit Margin' for item: {item.item_code if hasattr(item, 'item_code') else item}\nSerial No: {item.get('custom_vehicle_serial_no', 'NONE')}",
					title="Tax Pro Debug - On Profit Margin Detected"
				)
				
				from tax_pro.tax_pro.utils.serial_profit import calculate_item_profit_margin
				
				# Calculate profit margin for this item
				item_profit = calculate_item_profit_margin(item)
				
				frappe.log_error(
					message=f"Item Profit: {item_profit}, Tax Rate: {tax_rate}",
					title="Tax Pro Debug - Profit Calculated"
				)
				
				# Calculate tax on profit: tax_amount = profit * (tax_rate / 100)
				# This becomes the actual tax that gets added to tax.tax_amount
				current_tax_amount = (tax_rate / 100.0) * item_profit
				current_tax_amount = flt(current_tax_amount)
				
				frappe.log_error(
					message=f"Tax on profit ({tax_rate}% of {item_profit}): {current_tax_amount}",
					title="Tax Pro Debug - Tax Amount"
				)
				
			except Exception as e:
				frappe.log_error(
					message=f"Error calculating profit margin tax: {str(e)}\nItem: {item.name if hasattr(item, 'name') else item}\nTraceback: {frappe.get_traceback()}",
					title="Profit Margin Tax Calculation Error"
				)
				current_tax_amount = 0.0
		else:
			# Use the original method for all standard charge types
			return original_get_current_tax_amount(self, item, tax, item_tax_map)
		
		# Store item-wise tax details
		if not (self.doc.get("is_consolidated") or tax.get("dont_recompute_tax")):
			self.set_item_wise_tax(item, tax, tax_rate, current_tax_amount)
		
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

