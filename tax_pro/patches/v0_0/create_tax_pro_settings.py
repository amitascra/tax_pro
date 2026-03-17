# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Patch to create Tax Pro Settings for existing installations.
	This ensures that sites upgrading from older versions get the settings document.
	"""
	try:
		# Check if settings already exist
		if not frappe.db.exists("Tax Pro Settings", "Tax Pro Settings"):
			# Create new settings document
			settings = frappe.get_doc({
				"doctype": "Tax Pro Settings",
				"enable_profit_margin_tax": 1  # Enabled by default
			})
			settings.insert(ignore_permissions=True)
			frappe.db.commit()
			
			print("Tax Pro Settings created successfully")
		else:
			print("Tax Pro Settings already exist")
	except Exception as e:
		frappe.log_error(
			message=f"Error creating Tax Pro Settings in patch: {str(e)}\nTraceback: {frappe.get_traceback()}",
			title="Tax Pro Settings Patch Error"
		)
		print(f"Error creating Tax Pro Settings: {str(e)}")
