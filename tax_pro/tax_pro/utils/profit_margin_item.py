# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


@frappe.whitelist()
def calculate_combined_profit_margin(items):
	"""
	Calculate combined profit margin for all vehicle items in a transaction.
	
	Args:
		items (list): List of item dictionaries from Sales Invoice/Order items table
		
	Returns:
		dict: {
			'total_profit': float,
			'vehicle_count': int,
			'vehicle_items': list
		}
	"""
	try:
		from tax_pro.tax_pro.utils.serial_profit import calculate_item_profit_margin
		
		# Parse items if it's a JSON string
		if isinstance(items, str):
			import json
			items = json.loads(items)
		
		total_profit = 0.0
		vehicle_count = 0
		vehicle_items = []
		
		frappe.log_error(
			message=f"Calculating combined profit margin for {len(items)} items",
			title="Tax Pro - Combined Profit Margin Calculation"
		)
		
		for item in items:
			# Check if item has a serial number (indicates it's a vehicle/serialized item)
			# Try multiple field names for serial number
			serial_no = (
				item.get('custom_vehicle_serial_no') or 
				item.get('custom_serial_no') or 
				item.get('serial_no')
			)
			
			item_type = item.get('custom_item_type', '')
			item_code = item.get('item_code', '')
			
			frappe.log_error(
				message=f"Item: {item_code}\nType: {item_type}\nSerial No: {serial_no}",
				title="Tax Pro - Item Check"
			)
			
			# If item has a serial number, treat it as a vehicle item
			if serial_no:
				# Calculate profit for this vehicle item
				item_profit = calculate_item_profit_margin(item)
				
				# Only count if profit is non-zero (has valid purchase/selling prices)
				if item_profit != 0:
					total_profit += item_profit
					vehicle_count += 1
					
					vehicle_items.append({
						'item_code': item_code,
						'serial_no': serial_no,
						'profit': item_profit
					})
					
					frappe.log_error(
						message=f"Vehicle Item Found: {item_code}\nSerial: {serial_no}\nProfit: {item_profit}",
						title="Tax Pro - Vehicle Profit"
					)
				else:
					frappe.log_error(
						message=f"Item has serial but zero profit: {item_code}\nSerial: {serial_no}",
						title="Tax Pro - Zero Profit Item"
					)
		
		result = {
			'total_profit': flt(total_profit),
			'vehicle_count': vehicle_count,
			'vehicle_items': vehicle_items
		}
		
		frappe.log_error(
			message=f"Combined Profit Calculation Result:\n{result}",
			title="Tax Pro - Combined Profit Result"
		)
		
		return result
		
	except Exception as e:
		frappe.log_error(
			message=f"Error calculating combined profit margin: {str(e)}\nTraceback: {frappe.get_traceback()}",
			title="Combined Profit Margin Calculation Error"
		)
		return {
			'total_profit': 0.0,
			'vehicle_count': 0,
			'vehicle_items': []
		}


@frappe.whitelist()
def check_feature_enabled():
	"""
	Check if auto-add profit margin item feature is enabled.
	
	Returns:
		dict: {'enabled': bool}
	"""
	from tax_pro.tax_pro.doctype.tax_pro_settings.tax_pro_settings import is_auto_add_profit_margin_item_enabled
	
	return {
		'enabled': is_auto_add_profit_margin_item_enabled()
	}
