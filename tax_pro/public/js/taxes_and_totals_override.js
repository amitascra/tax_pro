// Copyright (c) 2025, Amit Kumar and contributors
// For license information, please see license.txt

// Override the get_current_tax_amount method to support "On Profit Margin" charge type
(function() {
	// Store the original method
	const original_get_current_tax_amount = erpnext.taxes_and_totals.prototype.get_current_tax_amount;
	
	// Override with extended functionality
	erpnext.taxes_and_totals.prototype.get_current_tax_amount = function(item, tax, item_tax_map) {
		var tax_rate = this._get_tax_rate(tax, item_tax_map);
		var current_tax_amount = 0.0;
		
		// Handle "On Profit Margin" charge type
		if (tax.charge_type == "On Profit Margin") {
			current_tax_amount = this.get_profit_margin_tax_amount(item, tax_rate);
		}
		// Handle all standard charge types
		else {
			// Call the original method for standard charge types
			return original_get_current_tax_amount.call(this, item, tax, item_tax_map);
		}
		
		if (!tax.dont_recompute_tax) {
			this.set_item_wise_tax(item, tax, tax_rate, current_tax_amount);
		}
		
		return current_tax_amount;
	};
	
	// Add new method to calculate profit margin tax
	erpnext.taxes_and_totals.prototype.get_profit_margin_tax_amount = function(item, tax_rate) {
		// Check if item has item_code
		if (!item.item_code) {
			return 0.0;
		}
		
		// Calculate profit margin by fetching serial numbers for this item code
		var total_profit = 0.0;
		
		// Fetch serial number profit data synchronously by item code
		frappe.call({
			method: 'tax_pro.tax_pro.utils.serial_profit.get_serial_profit_data_by_item',
			args: {
				item_code: item.item_code
			},
			async: false,
			callback: function(r) {
				if (r.message && r.message.total_profit) {
					total_profit = flt(r.message.total_profit);
				}
			}
		});
		
		// Apply tax rate to profit margin
		var tax_amount = (tax_rate / 100.0) * total_profit;
		
		return flt(tax_amount);
	};
	
})();

console.log("Tax Pro: Taxes and Totals override loaded - On Profit Margin charge type enabled");

