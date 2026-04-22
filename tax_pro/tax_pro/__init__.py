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

# Monkey patch India Compliance's GST validation to skip validation for "On Profit Margin" charge type
def patch_india_compliance_validation():
	"""
	Monkey patch India Compliance's validate_item_gst_details method
	to skip validation when "On Profit Margin" charge type is present.
	"""
	try:
		from india_compliance.gst_india.overrides.transaction import ItemGSTDetails
		
		# Store the original method
		original_validate_item_gst_details = ItemGSTDetails.validate_item_gst_details
		
		def custom_validate_item_gst_details(self):
			"""
			Extended version that skips validation if "On Profit Margin" charge type is present.
			"""
			# Check if any tax row uses "On Profit Margin" charge type
			has_profit_margin_tax = any(
				tax.charge_type == "On Profit Margin"
				for tax in self.doc.taxes
			)
			
			if has_profit_margin_tax:
				frappe.log_error(
					message=f"Skipping GST validation for {self.doc.doctype} {self.doc.name} due to On Profit Margin charge type",
					title="Tax Pro - GST Validation Skipped"
				)
				return  # Skip validation
			
			# Call the original method for standard cases
			return original_validate_item_gst_details(self)
		
		# Replace the method
		ItemGSTDetails.validate_item_gst_details = custom_validate_item_gst_details
		
	except ImportError:
		# India Compliance not installed, skip this patch
		pass
	except Exception as e:
		frappe.log_error(
			message=f"Error patching India Compliance validation: {str(e)}",
			title="Tax Pro India Compliance Patch Error"
		)

# Apply the India Compliance patch when the module is imported
try:
	patch_india_compliance_validation()
except Exception as e:
	frappe.log_error(
		message=f"Error applying India Compliance patch: {str(e)}",
		title="Tax Pro Module Init Error"
	)

