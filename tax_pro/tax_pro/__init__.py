# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe

# Hook to fix item GST amounts before India Compliance validation
def before_submit_fix_item_gst(doc, method=None):
	"""
	Fix item GST amounts for On Profit Margin charge type before India Compliance validation.
	This hook runs in before_submit to ensure item GST fields are set correctly.
	"""
	if not doc.taxes:
		return
	
	# Check if any tax uses On Profit Margin charge type
	has_profit_margin_tax = any(t.charge_type == "On Profit Margin" for t in doc.taxes)
	if not has_profit_margin_tax:
		return
	
	frappe.log_error(
		message="Tax Pro: before_submit_fix_item_gst called - fixing item GST amounts for On Profit Margin",
		title="Tax Pro Debug - Before Submit Fix"
	)
	
	# Fix each item's GST amounts based on the taxes calculated on profit margin
	for item in doc.items:
		# Reset GST amounts
		item.cgst_amount = 0
		item.sgst_amount = 0
		item.igst_amount = 0
		item.cess_amount = 0
		item.cess_non_advol_amount = 0
		
		# Find the profit margin for this item
		from tax_pro.tax_pro.utils.serial_profit import calculate_item_profit_margin
		try:
			item_profit = calculate_item_profit_margin(item)
			if item_profit > 0:
				item.taxable_value = item_profit
		except:
			continue
	
	# Recalculate item GST amounts based on the taxes
	for tax in doc.taxes:
		if tax.charge_type != "On Profit Margin":
			continue
		
		gst_tax_type = tax.get("gst_tax_type")
		tax_rate = tax.rate
		
		if not gst_tax_type:
			continue
		
		# Distribute tax amount to items
		if tax.item_wise_tax_detail:
			try:
				import json
				item_wise_detail = json.loads(tax.item_wise_tax_detail)
				for item_key, (rate, amount) in item_wise_detail.items():
					# Find the item
					for item in doc.items:
						if item.item_code == item_key or item.item_name == item_key:
							amount_field = f"{gst_tax_type}_amount"
							setattr(item, amount_field, amount)
							frappe.log_error(
								message=f"Set item.{amount_field} = {amount} for item {item_key}",
								title="Tax Pro Debug - Item GST Fix"
							)
							break
			except Exception as e:
				frappe.log_error(
					message=f"Error fixing item GST: {str(e)}",
					title="Tax Pro Error - Item GST Fix"
				)

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

