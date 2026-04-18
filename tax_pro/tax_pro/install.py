# Copyright (c) 2025, Amit Kumar and contributors
# For license information, please see license.txt

import frappe


def after_install():
	"""
	Called after app installation.
	Ensures the tax calculations patch is loaded.
	"""
	from tax_pro.tax_pro import patch_taxes_and_totals
	
	try:
		patch_taxes_and_totals()
		frappe.msgprint("Tax Pro installed successfully. 'On Profit Margin' charge type is now available.")
	except Exception as e:
		frappe.log_error(
			message=f"Error during Tax Pro installation: {str(e)}",
			title="Tax Pro Installation Error"
		)

