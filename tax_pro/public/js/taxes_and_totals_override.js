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
		console.log('=== TAX PRO DEBUG: get_profit_margin_tax_amount called ===');
		console.log('Item object:', item);
		console.log('Item type:', typeof item);
		console.log('Item keys:', Object.keys(item));
		
		// Try to access the field in different ways
		console.log('Direct access - item.custom_serial_no:', item.custom_serial_no);
		console.log('Direct access - item.custom_vehicle_serial_no:', item.custom_vehicle_serial_no);
		console.log('Direct access - item.serial_no:', item.serial_no);
		
		// Try bracket notation
		console.log('Bracket notation - item["custom_serial_no"]:', item['custom_serial_no']);
		console.log('Bracket notation - item["custom_vehicle_serial_no"]:', item['custom_vehicle_serial_no']);
		console.log('Bracket notation - item["serial_no"]:', item['serial_no']);
		
		console.log('Tax Rate:', tax_rate);
		
		// Check for serial number field (try all possible field names)
		var serial_no = item.custom_vehicle_serial_no || item.custom_serial_no || item.serial_no || 
						item['custom_vehicle_serial_no'] || item['custom_serial_no'] || item['serial_no'];
		
		console.log('Final serial_no value:', serial_no);
		
		// Check if item has any serial number field (new requirement)
		if (serial_no) {
			console.log('✓ Found serial_no:', serial_no);
			console.log('Calling get_serial_profit_data_by_serial_no');
			
			// Calculate profit margin by fetching the specific serial number
			var profit = 0.0;
			
			// Fetch serial number profit data synchronously by serial no
			frappe.call({
				method: 'tax_pro.tax_pro.utils.serial_profit.get_serial_profit_data_by_serial_no',
				args: {
					serial_no: serial_no
				},
				async: false,
				callback: function(r) {
					console.log('API Response:', r);
					if (r.message) {
						console.log('Response message:', r.message);
						if (r.message.profit !== undefined) {
							profit = flt(r.message.profit);
							console.log('✓ Profit from API:', profit);
						} else {
							console.log('No profit in response');
						}
					} else {
						console.log('No message in response');
					}
				},
				error: function(r) {
					console.error('API Error:', r);
				}
			});
			
			// Calculate tax on profit: tax_amount = profit * (tax_rate / 100)
			var tax_amount = (tax_rate / 100.0) * profit;
			
			console.log('✓ Calculated tax on profit: ' + tax_rate + '% of ' + profit + ' = ' + tax_amount);
			console.log('=== TAX PRO DEBUG END ===');
			
			return flt(tax_amount);
		}
		// Fallback to item_code method (backward compatibility)
		else if (item.item_code) {
			console.log('✗ WARNING: No serial_no field found! Falling back to item_code method:', item.item_code);
			console.log('This will fetch ALL serials with matching item_code');
			console.log('Calling get_serial_profit_data_by_item (DEPRECATED)');
			
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
					console.log('API Response:', r);
					if (r.message) {
						console.log('Response message:', r.message);
						if (r.message.total_profit) {
							total_profit = flt(r.message.total_profit);
							console.log('Total profit from API:', total_profit);
						} else {
							console.log('No total_profit in response');
						}
					} else {
						console.log('No message in response');
					}
				},
				error: function(r) {
					console.error('API Error:', r);
				}
			});
			
			// Calculate tax on profit: tax_amount = profit * (tax_rate / 100)
			var tax_amount = (tax_rate / 100.0) * total_profit;
			
			console.log('Calculated tax on profit (fallback): ' + tax_rate + '% of ' + total_profit + ' = ' + tax_amount);
			console.log('=== TAX PRO DEBUG END ===');
			
			return flt(tax_amount);
		}
		else {
			console.log('✗ ERROR: No serial_no or item_code found in item');
			console.log('=== TAX PRO DEBUG END ===');
			return 0.0;
		}
	};
	
})();

console.log("Tax Pro: Taxes and Totals override loaded - On Profit Margin charge type enabled");

