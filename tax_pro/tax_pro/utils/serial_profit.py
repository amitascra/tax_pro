# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def get_serial_nos_by_item_code(item_code):
	"""
	Fetch all serial numbers for a given item code.
	
	Args:
		item_code (str): Item code to fetch serial numbers for
		
	Returns:
		list: List of serial number records with custom fields
	"""
	if not item_code:
		return []
	
	try:
		# Fetch all serial numbers for this item
		serial_data = frappe.db.get_all(
			'Serial No',
			filters={'item_code': item_code},
			fields=['name', 'custom_purchase_price', 'custom_selling_price']
		)
		
		return serial_data
		
	except Exception as e:
		frappe.log_error(
			message=f"Error fetching serial numbers for item: {str(e)}\nItem Code: {item_code}",
			title="Serial Number Fetch Error"
		)
		return []


def calculate_item_profit_margin(item):
	"""
	Calculate total profit margin for an item based on all its serial numbers.
	Fetches serial numbers by item_code and calculates profit from custom fields.
	
	Args:
		item: Item document with item_code field
		
	Returns:
		float: Total profit margin for all serial numbers of this item
	"""
	if not item.get('item_code'):
		return 0.0
	
	# Fetch all serial numbers for this item code
	serial_data = get_serial_nos_by_item_code(item.get('item_code'))
	
	if not serial_data:
		return 0.0
	
	# Calculate total profit from all serial numbers
	total_profit = 0.0
	for serial in serial_data:
		purchase_price = flt(serial.get('custom_purchase_price', 0))
		selling_price = flt(serial.get('custom_selling_price', 0))
		profit = selling_price - purchase_price
		total_profit += profit
	
	return flt(total_profit)


def calculate_total_profit_for_items(items):
	"""
	Calculate total profit margin across multiple items.
	
	Args:
		items (list): List of item documents
		
	Returns:
		float: Total profit margin
	"""
	total_profit = 0.0
	
	for item in items:
		item_profit = calculate_item_profit_margin(item)
		total_profit += item_profit
	
	return flt(total_profit)


@frappe.whitelist()
def get_serial_profit_data_by_item(item_code):
	"""
	Whitelisted method to fetch serial number profit data for frontend use.
	
	Args:
		item_code (str): Item code to fetch serial numbers for
		
	Returns:
		dict: Dictionary with profit data
	"""
	try:
		serial_data = get_serial_nos_by_item_code(item_code)
		
		result = {}
		total_profit = 0.0
		
		for serial in serial_data:
			purchase_price = flt(serial.get('custom_purchase_price', 0))
			selling_price = flt(serial.get('custom_selling_price', 0))
			profit = selling_price - purchase_price
			
			result[serial['name']] = {
				'purchase_price': purchase_price,
				'selling_price': selling_price,
				'profit': profit
			}
			total_profit += profit
		
		return {
			'serial_data': result,
			'total_profit': flt(total_profit)
		}
		
	except Exception as e:
		frappe.log_error(
			message=f"Error in get_serial_profit_data_by_item: {str(e)}",
			title="Serial Profit Data Error"
		)
		return {'serial_data': {}, 'total_profit': 0.0}

