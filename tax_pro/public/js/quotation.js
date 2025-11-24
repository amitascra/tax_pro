// Copyright (c) 2025, Amit Kumar and contributors
// For license information, please see license.txt

// Extend Quotation to support custom tax calculations
frappe.ui.form.on('Quotation', {
	onload: function(frm) {
		// Ensure taxes_and_totals override is loaded
		// The override is included via hooks
	}
});

// Trigger calculation when charge_type changes to "On Profit Margin"
frappe.ui.form.on('Sales Taxes and Charges', {
	charge_type: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.charge_type === 'On Profit Margin') {
			console.log('On Profit Margin selected - triggering calculation');
			frm.script_manager.trigger("rate", cdt, cdn);
			frm.cscript.calculate_taxes_and_totals();
		}
	},
	rate: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.charge_type === 'On Profit Margin') {
			console.log('Tax rate changed for On Profit Margin - triggering calculation');
			frm.cscript.calculate_taxes_and_totals();
		}
	}
});

