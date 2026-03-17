# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TaxProSettings(Document):
	def validate(self):
		"""Validate that only one feature is enabled at a time."""
		if self.enable_profit_margin_tax and self.enable_auto_add_profit_margin_item:
			frappe.throw(
				msg="Only one feature can be enabled at a time. Please disable one feature before enabling the other.",
				title="Multiple Features Enabled"
			)


def is_profit_margin_tax_enabled():
	"""
	Check if profit margin tax feature (Feature 1) is enabled in settings.
	
	Returns:
		bool: True if enabled, False otherwise
	"""
	try:
		settings = frappe.get_single("Tax Pro Settings")
		return settings.enable_profit_margin_tax
	except Exception as e:
		frappe.log_error(
			message=f"Error checking Tax Pro Settings: {str(e)}",
			title="Tax Pro Settings Error"
		)
		# Default to enabled if settings don't exist
		return True


def is_auto_add_profit_margin_item_enabled():
	"""
	Check if auto-add profit margin item feature (Feature 2) is enabled in settings.
	
	Returns:
		bool: True if enabled, False otherwise
	"""
	try:
		settings = frappe.get_single("Tax Pro Settings")
		return settings.enable_auto_add_profit_margin_item
	except Exception as e:
		frappe.log_error(
			message=f"Error checking Tax Pro Settings for auto-add profit margin item: {str(e)}",
			title="Tax Pro Settings Error"
		)
		# Default to enabled if settings don't exist
		return True
