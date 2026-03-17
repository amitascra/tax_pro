# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Patch to add enable_auto_add_profit_margin_item field to existing Tax Pro Settings.
	"""
	try:
		if frappe.db.exists("Tax Pro Settings", "Tax Pro Settings"):
			settings = frappe.get_doc("Tax Pro Settings", "Tax Pro Settings")
			
			# Add the new field if it doesn't exist
			if not hasattr(settings, 'enable_auto_add_profit_margin_item'):
				settings.enable_auto_add_profit_margin_item = 1  # Enabled by default
				settings.save(ignore_permissions=True)
				frappe.db.commit()
				
				print("Added enable_auto_add_profit_margin_item field to Tax Pro Settings")
			else:
				print("enable_auto_add_profit_margin_item field already exists")
		else:
			print("Tax Pro Settings does not exist - will be created on next install")
	except Exception as e:
		frappe.log_error(
			message=f"Error adding Feature 2 field to Tax Pro Settings: {str(e)}\nTraceback: {frappe.get_traceback()}",
			title="Tax Pro Settings Patch Error"
		)
		print(f"Error: {str(e)}")
