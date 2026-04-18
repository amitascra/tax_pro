// Copyright (c) 2025, Amit Kumar and contributors
// For license information, please see license.txt

// Extend Sales Order to support custom tax calculations
frappe.ui.form.on('Sales Order', {
	onload: function(frm) {
		// Ensure taxes_and_totals override is loaded
		// The override is included via hooks
	}
});

