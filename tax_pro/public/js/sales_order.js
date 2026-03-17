// Copyright (c) 2025, Amit Kumar and contributors
// For license information, please see license.txt

// Extend Sales Order to support custom tax calculations
frappe.ui.form.on('Sales Order', {
	onload: function(frm) {
		// Ensure taxes_and_totals override is loaded
		// The override is included via hooks
	},
	
	refresh: function(frm) {
		// Check and update profit margin item on refresh
		update_profit_margin_item_so(frm);
	}
});

// Store the calculated profit globally to use after item details are fetched
window.tax_pro_calculated_profit_so = 0;

// Feature 2: Auto-add Profit Margin Item
frappe.ui.form.on('Sales Order Item', {
	custom_serial_no: function(frm, cdt, cdn) {
		console.log('=== TAX PRO: Serial number changed (SO) ===');
		update_profit_margin_item_so(frm);
	},
	
	custom_item_type: function(frm, cdt, cdn) {
		console.log('=== TAX PRO: Item type changed (SO) ===');
		update_profit_margin_item_so(frm);
	},
	
	item_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// If this is the Profit Margin item and we have a calculated profit, set it after item details load
		if (row.item_code === 'Profit Margin' && window.tax_pro_calculated_profit_so > 0) {
			console.log('=== TAX PRO: Profit Margin item_code set (SO), will update rate after details load ===');
			// Use setTimeout to ensure this runs after get_item_details completes
			setTimeout(function() {
				console.log('Setting Profit Margin rate to (SO):', window.tax_pro_calculated_profit_so);
				frappe.model.set_value(cdt, cdn, 'rate', window.tax_pro_calculated_profit_so);
				frappe.model.set_value(cdt, cdn, 'qty', 1);
				frm.refresh_field('items');
				frm.cscript.calculate_taxes_and_totals();
			}, 500);
		}
	},
	
	items_remove: function(frm, cdt, cdn) {
		console.log('=== TAX PRO: Item removed (SO) ===');
		// Delay to ensure item is removed from the table
		setTimeout(function() {
			update_profit_margin_item_so(frm);
		}, 100);
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

// Feature 2: Update Profit Margin Item for Sales Order
function update_profit_margin_item_so(frm) {
	console.log('=== TAX PRO: update_profit_margin_item_so called ===');
	
	// Check if feature is enabled
	frappe.call({
		method: 'tax_pro.tax_pro.utils.profit_margin_item.check_feature_enabled',
		async: false,
		callback: function(r) {
			if (!r.message || !r.message.enabled) {
				console.log('Feature 2 is disabled - skipping');
				return;
			}
			
			console.log('Feature 2 is enabled - processing...');
			
			// Get all items from the form
			let items = frm.doc.items || [];
			
			// Calculate combined profit margin
			frappe.call({
				method: 'tax_pro.tax_pro.utils.profit_margin_item.calculate_combined_profit_margin',
				args: {
					items: items
				},
				async: false,
				callback: function(profit_result) {
					console.log('Profit calculation result:', profit_result);
					
					if (profit_result.message) {
						let total_profit = profit_result.message.total_profit;
						let vehicle_count = profit_result.message.vehicle_count;
						
						console.log('Total Profit:', total_profit);
						console.log('Vehicle Count:', vehicle_count);
						
						// Store profit in global variable for use in item_code event
						window.tax_pro_calculated_profit_so = total_profit;
						
						// Find existing "Profit Margin" item
						let profit_margin_row = null;
						let profit_margin_idx = -1;
						
						for (let i = 0; i < items.length; i++) {
							if (items[i].item_code === 'Profit Margin') {
								profit_margin_row = items[i];
								profit_margin_idx = i;
								break;
							}
						}
						
						if (vehicle_count > 0 && total_profit > 0) {
							// Add or update Profit Margin item
							if (profit_margin_row) {
								// Update existing row - set rate directly
								console.log('Updating existing Profit Margin item');
								frappe.model.set_value(profit_margin_row.doctype, profit_margin_row.name, 'rate', total_profit);
								frappe.model.set_value(profit_margin_row.doctype, profit_margin_row.name, 'qty', 1);
								frm.refresh_field('items');
								frm.cscript.calculate_taxes_and_totals();
							} else {
								// Add new row - item_code event will handle setting the rate
								console.log('Adding new Profit Margin item');
								let new_row = frm.add_child('items');
								frappe.model.set_value(new_row.doctype, new_row.name, 'item_code', 'Profit Margin');
								// Don't set rate here - let the item_code event handle it after get_item_details
							}
						} else {
							// Remove Profit Margin item if no vehicles
							window.tax_pro_calculated_profit_so = 0;
							if (profit_margin_row) {
								console.log('Removing Profit Margin item - no vehicles');
								frm.get_field('items').grid.grid_rows[profit_margin_idx].remove();
								frm.refresh_field('items');
								frm.cscript.calculate_taxes_and_totals();
							}
						}
					}
				}
			});
		}
	});
}

