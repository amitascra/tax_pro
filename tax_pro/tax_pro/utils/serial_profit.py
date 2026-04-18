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
		frappe.log_error(
			message="Item code is empty or None",
			title="Serial Profit Debug - No Item Code"
		)
		return []
	
	try:
		frappe.log_error(
			message=f"Fetching serial numbers for item_code: {item_code}",
			title="Serial Profit Debug - Fetching Serials"
		)
		
		# Fetch all serial numbers for this item
		serial_data = frappe.db.get_all(
			'Serial No',
			filters={'item_code': item_code},
			fields=['name', 'custom_purchase_price', 'custom_selling_price']
		)
		
		frappe.log_error(
			message=f"Found {len(serial_data)} serial numbers for item_code: {item_code}\nData: {serial_data}",
			title="Serial Profit Debug - Serial Data"
		)
		
		return serial_data
		
	except Exception as e:
		frappe.log_error(
			message=f"Error fetching serial numbers for item: {str(e)}\nItem Code: {item_code}",
			title="Serial Number Fetch Error"
		)
		return []


def get_serial_by_serial_no(serial_no):
	"""
	Fetch a single serial number record by its name/serial_no.
	
	Args:
		serial_no (str): Serial number name to fetch
		
	Returns:
		dict: Serial number record with custom fields, or empty dict if not found
	"""
	if not serial_no:
		frappe.log_error(
			message="Serial No is empty or None",
			title="Serial Profit Debug - No Serial No"
		)
		return {}
	
	try:
		frappe.log_error(
			message=f"Fetching serial number: {serial_no}",
			title="Serial Profit Debug - Fetching Serial"
		)
		
		# Fetch the specific serial number
		serial_data = frappe.db.get_all(
			'Serial No',
			filters={'name': serial_no},
			fields=['name', 'item_code', 'custom_purchase_price', 'custom_selling_price']
		)
		
		if serial_data:
			frappe.log_error(
				message=f"Found serial number: {serial_no}\nData: {serial_data[0]}",
				title="Serial Profit Debug - Serial Found"
			)
			return serial_data[0]
		else:
			frappe.log_error(
				message=f"Serial number not found: {serial_no}",
				title="Serial Profit Debug - Serial Not Found"
			)
			return {}
		
	except Exception as e:
		frappe.log_error(
			message=f"Error fetching serial number: {str(e)}\nSerial No: {serial_no}",
			title="Serial Number Fetch Error"
		)
		return {}


def calculate_item_profit_margin(item):
	"""
	Calculate profit margin for an item based on its custom_vehicle_serial_no.
	Fetches the specific serial number and calculates profit from custom fields.
	
	Args:
		item: Item document with custom_vehicle_serial_no field
		
	Returns:
		float: Profit margin for the specific serial number
	"""
	frappe.log_error(
		message=f"calculate_item_profit_margin called\nItem Object: {item}\nItem Dict: {item.as_dict() if hasattr(item, 'as_dict') else item}",
		title="Serial Profit Debug - Function Entry"
	)
	
	# Check for serial number field (try all possible field names)
	# Sales Invoice Item: custom_vehicle_serial_no
	# Sales Order Item: custom_serial_no
	# Quotation Item: custom_serial_no
	serial_no = None
	if hasattr(item, 'get'):
		serial_no = item.get('custom_vehicle_serial_no') or item.get('custom_serial_no') or item.get('serial_no')
	
	frappe.log_error(
		message=f"Checked field names:\ncustom_vehicle_serial_no: {item.get('custom_vehicle_serial_no') if hasattr(item, 'get') else 'N/A'}\ncustom_serial_no: {item.get('custom_serial_no') if hasattr(item, 'get') else 'N/A'}\nserial_no: {item.get('serial_no') if hasattr(item, 'get') else 'N/A'}\nFinal serial_no: {serial_no}",
		title="Serial Profit Debug - Serial No Check"
	)
	
	if serial_no:
		frappe.log_error(
			message=f"Using serial_no: {serial_no}",
			title="Serial Profit Debug - Calculate Profit by Serial No"
		)
		
		# Fetch the specific serial number
		serial_data = get_serial_by_serial_no(serial_no)
		
		if not serial_data:
			frappe.log_error(
				message=f"No serial data found for serial_no: {serial_no}",
				title="Serial Profit Debug - No Serial Data"
			)
			return 0.0
		
		# Calculate profit from the single serial number
		purchase_price = flt(serial_data.get('custom_purchase_price', 0))
		selling_price = flt(serial_data.get('custom_selling_price', 0))
		profit = selling_price - purchase_price
		
		profit_details = {
			'serial_no': serial_data.get('name'),
			'purchase': purchase_price,
			'selling': selling_price,
			'profit': profit
		}
		
		frappe.log_error(
			message=f"Serial No: {serial_no}\nProfit: {profit}\nDetails: {profit_details}",
			title="Serial Profit Debug - Profit Calculated"
		)
		
		return flt(profit)
	
	# Fallback to item_code method if serial number is not present (backward compatibility)
	item_code = item.get('item_code') if hasattr(item, 'get') else None
	
	if item_code:
		frappe.log_error(
			message=f"No serial_no found, falling back to item_code: {item_code}",
			title="Serial Profit Debug - Fallback to Item Code"
		)
		
		# Fetch all serial numbers for this item code
		serial_data = get_serial_nos_by_item_code(item_code)
		
		if not serial_data:
			frappe.log_error(
				message=f"No serial data found for item_code: {item_code}",
				title="Serial Profit Debug - No Serial Data"
			)
			return 0.0
		
		# Calculate total profit from all serial numbers (backward compatibility)
		total_profit = 0.0
		profit_details = []
		
		for serial in serial_data:
			purchase_price = flt(serial.get('custom_purchase_price', 0))
			selling_price = flt(serial.get('custom_selling_price', 0))
			profit = selling_price - purchase_price
			total_profit += profit
			
			profit_details.append({
				'serial_no': serial.get('name'),
				'purchase': purchase_price,
				'selling': selling_price,
				'profit': profit
			})
		
		frappe.log_error(
			message=f"Item: {item_code}\nTotal Profit: {total_profit}\nDetails: {profit_details}",
			title="Serial Profit Debug - Profit Calculated (Fallback)"
		)
		
		return flt(total_profit)
	
	else:
		frappe.log_error(
			message=f"Item has no custom_vehicle_serial_no or item_code\nItem: {item}",
			title="Serial Profit Debug - No Serial or Item Code"
		)
		return 0.0


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
	Whitelisted method to fetch serial number profit data for frontend use (DEPRECATED).
	Kept for backward compatibility. Use get_serial_profit_data_by_serial_no instead.
	
	Args:
		item_code (str): Item code to fetch serial numbers for
		
	Returns:
		dict: Dictionary with profit data
	"""
	try:
		frappe.log_error(
			message=f"Frontend API called with item_code: {item_code} (DEPRECATED)",
			title="Serial Profit Debug - Frontend API Call"
		)
		
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
		
		response = {
			'serial_data': result,
			'total_profit': flt(total_profit)
		}
		
		frappe.log_error(
			message=f"Frontend API Response: {response}",
			title="Serial Profit Debug - Frontend Response"
		)
		
		return response
		
	except Exception as e:
		frappe.log_error(
			message=f"Error in get_serial_profit_data_by_item: {str(e)}\nTraceback: {frappe.get_traceback()}",
			title="Serial Profit Data Error"
		)
		return {'serial_data': {}, 'total_profit': 0.0}


@frappe.whitelist()
def get_serial_profit_data_by_serial_no(serial_no):
	"""
	Whitelisted method to fetch profit data for a specific serial number.
	This is the new method that replaces get_serial_profit_data_by_item.
	
	Args:
		serial_no (str): Serial number name to fetch profit data for
		
	Returns:
		dict: Dictionary with profit data for the specific serial number
	"""
	try:
		frappe.log_error(
			message=f"Frontend API called with serial_no: {serial_no}",
			title="Serial Profit Debug - Frontend API Call (Serial No)"
		)
		
		if not serial_no:
			return {
				'serial_no': None,
				'purchase_price': 0.0,
				'selling_price': 0.0,
				'profit': 0.0
			}
		
		serial_data = get_serial_by_serial_no(serial_no)
		
		if not serial_data:
			frappe.log_error(
				message=f"Serial number not found: {serial_no}",
				title="Serial Profit Debug - Serial Not Found (API)"
			)
			return {
				'serial_no': serial_no,
				'purchase_price': 0.0,
				'selling_price': 0.0,
				'profit': 0.0
			}
		
		purchase_price = flt(serial_data.get('custom_purchase_price', 0))
		selling_price = flt(serial_data.get('custom_selling_price', 0))
		profit = selling_price - purchase_price
		
		response = {
			'serial_no': serial_data.get('name'),
			'item_code': serial_data.get('item_code'),
			'purchase_price': purchase_price,
			'selling_price': selling_price,
			'profit': flt(profit)
		}
		
		frappe.log_error(
			message=f"Frontend API Response: {response}",
			title="Serial Profit Debug - Frontend Response (Serial No)"
		)
		
		return response
		
	except Exception as e:
		frappe.log_error(
			message=f"Error in get_serial_profit_data_by_serial_no: {str(e)}\nTraceback: {frappe.get_traceback()}",
			title="Serial Profit Data Error"
		)
		return {
			'serial_no': serial_no,
			'purchase_price': 0.0,
			'selling_price': 0.0,
			'profit': 0.0
		}

