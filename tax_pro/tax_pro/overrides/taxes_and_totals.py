# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint, flt
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals

from tax_pro.tax_pro.utils.serial_profit import calculate_total_profit_for_items


class CustomCalculateTaxesAndTotals(calculate_taxes_and_totals):
	"""
	Custom tax calculation class that extends ERPNext's calculate_taxes_and_totals
	to support "On Profit Margin" charge type.
	"""
	
	def get_current_tax_amount(self, item, tax, item_tax_map):
		"""
		Override the get_current_tax_amount method to add support for "On Profit Margin" charge type.
		
		This method calculates the tax amount for a single item based on the charge type.
		For "On Profit Margin", it calculates tax based on the difference between
		custom_selling_price and custom_purchase_price from Serial No doctype.
		"""
		tax_rate = self._get_tax_rate(tax, item_tax_map)
		current_tax_amount = 0.0
		
		# Handle "On Profit Margin" charge type
		if tax.charge_type == "On Profit Margin":
			current_tax_amount = self.get_profit_margin_tax_amount(item, tax_rate)
		
		# Handle all standard ERPNext charge types
		elif tax.charge_type == "Actual":
			# distribute the tax amount proportionally to each item row
			actual = flt(tax.tax_amount, tax.precision("tax_amount"))
			
			if tax.get("is_tax_withholding_account") and item.meta.get_field("apply_tds"):
				if not item.get("apply_tds") or not self.doc.tax_withholding_net_total:
					current_tax_amount = 0.0
				else:
					current_tax_amount = item.net_amount * actual / self.doc.tax_withholding_net_total
			else:
				current_tax_amount = (
					item.net_amount * actual / self.doc.net_total if self.doc.net_total else 0.0
				)
		
		elif tax.charge_type == "On Net Total":
			current_tax_amount = (tax_rate / 100.0) * item.net_amount
		
		elif tax.charge_type == "On Previous Row Amount":
			current_tax_amount = (tax_rate / 100.0) * self.doc.get("taxes")[
				cint(tax.row_id) - 1
			].tax_amount_for_current_item
		
		elif tax.charge_type == "On Previous Row Total":
			current_tax_amount = (tax_rate / 100.0) * self.doc.get("taxes")[
				cint(tax.row_id) - 1
			].grand_total_for_current_item
		
		elif tax.charge_type == "On Item Quantity":
			current_tax_amount = tax_rate * item.qty
		
		# Store item-wise tax details
		if not (self.doc.get("is_consolidated") or tax.get("dont_recompute_tax")):
			self.set_item_wise_tax(item, tax, tax_rate, current_tax_amount)
		
		return current_tax_amount
	
	def get_profit_margin_tax_amount(self, item, tax_rate):
		"""
		Calculate tax amount based on profit margin from serial numbers.
		
		Args:
			item: Item document with serial_no field
			tax_rate: Tax rate to apply
			
		Returns:
			float: Tax amount based on profit margin
		"""
		try:
			from tax_pro.tax_pro.utils.serial_profit import calculate_item_profit_margin
			
			# Calculate profit margin for this item
			item_profit = calculate_item_profit_margin(item)
			
			# Apply tax rate to profit margin
			tax_amount = (tax_rate / 100.0) * item_profit
			
			return flt(tax_amount)
			
		except Exception as e:
			frappe.log_error(
				message=f"Error calculating profit margin tax: {str(e)}\nItem: {item.name}",
				title="Profit Margin Tax Calculation Error"
			)
			return 0.0

