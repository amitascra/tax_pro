# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe


def after_install():
	"""
	Called after app installation.
	Ensures the tax calculations patch is loaded and creates default settings.
	"""
	from tax_pro.tax_pro import patch_taxes_and_totals
	
	try:
		# Apply the monkey patch
		patch_taxes_and_totals()
		
		# Create default Tax Pro Settings
		create_default_settings()
		
		frappe.msgprint("Tax Pro installed successfully. 'On Profit Margin' charge type is now available.")
	except Exception as e:
		frappe.log_error(
			message=f"Error during Tax Pro installation: {str(e)}",
			title="Tax Pro Installation Error"
		)


def create_default_settings():
	"""
	Create default Tax Pro Settings if they don't exist.
	"""
	try:
		# Check if settings already exist
		if not frappe.db.exists("Tax Pro Settings", "Tax Pro Settings"):
			# Create new settings document
			# Only Feature 2 enabled by default (mutual exclusivity)
			settings = frappe.get_doc({
				"doctype": "Tax Pro Settings",
				"enable_profit_margin_tax": 0,  # Feature 1: Disabled by default
				"enable_auto_add_profit_margin_item": 1  # Feature 2: Enabled by default
			})
			settings.insert(ignore_permissions=True)
			frappe.db.commit()
			
			frappe.log_error(
				message="Tax Pro Settings created successfully with feature enabled by default",
				title="Tax Pro Settings Created"
			)
		else:
			frappe.log_error(
				message="Tax Pro Settings already exist",
				title="Tax Pro Settings Exists"
			)
	except Exception as e:
		frappe.log_error(
			message=f"Error creating Tax Pro Settings: {str(e)}\nTraceback: {frappe.get_traceback()}",
			title="Tax Pro Settings Creation Error"
		)

