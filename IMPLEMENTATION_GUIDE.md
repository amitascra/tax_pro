# On Profit Margin Tax - Implementation Guide

## Overview

This custom app adds a new **"On Profit Margin"** charge type to the Sales Taxes and Charges table in ERPNext. This allows you to calculate taxes based on the profit margin of serialized items.

## How It Works

### Profit Margin Calculation

When you select **"On Profit Margin"** as the charge type:

1. For each item in the sales transaction (Sales Invoice Item, Sales Order Item, or Quotation Item), the system takes the `item_code`
2. Fetches ALL Serial No records from the database where `item_code` matches
3. For each serial number found, it retrieves:
   - `custom_purchase_price` - The purchase/cost price
   - `custom_selling_price` - The selling price
4. Calculates profit: `profit = selling_price - purchase_price`
5. Sums up the total profit from all serial numbers for that item
6. Applies the tax rate: `tax_amount = (rate / 100) × total_profit`

### Example

**Sales Invoice has 1 item**: Laptop (Item Code: LAPTOP-001)

In the Serial No master, there are 2 records with item_code = "LAPTOP-001":
- Serial No: SN001 - Purchase Price = ₹40,000, Selling Price = ₹50,000 → Profit = ₹10,000
- Serial No: SN002 - Purchase Price = ₹42,000, Selling Price = ₹52,000 → Profit = ₹10,000

**Total Profit** = ₹20,000

If tax rate = 10%, then **Tax Amount** = ₹2,000

**Important**: The system looks up ALL serial numbers with matching item_code, not just the ones in the transaction's serial_no field.

## Prerequisites

### 1. Custom Fields in Serial No

You must add two custom fields to the **Serial No** doctype:

1. **Field 1:**
   - Label: Purchase Price
   - Fieldname: `custom_purchase_price`
   - Fieldtype: Currency

2. **Field 2:**
   - Label: Selling Price
   - Fieldname: `custom_selling_price`
   - Fieldtype: Currency

### Steps to Add Custom Fields:

```bash
# Via bench console
bench --site [site-name] console

# In the console:
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

custom_fields = {
    "Serial No": [
        {
            "fieldname": "custom_purchase_price",
            "label": "Purchase Price",
            "fieldtype": "Currency",
            "insert_after": "purchase_rate"
        },
        {
            "fieldname": "custom_selling_price",
            "label": "Selling Price",
            "fieldtype": "Currency",
            "insert_after": "custom_purchase_price"
        }
    ]
}

create_custom_fields(custom_fields)
```

Or add them via the UI:
1. Go to: **Customize Form**
2. Select DocType: **Serial No**
3. Add the two currency fields as specified above
4. Save

## Usage

### In Sales Invoice, Sales Order, or Quotation:

1. Add items with serial numbers
2. In the **Sales Taxes and Charges** table, add a new row
3. Select **Type**: "On Profit Margin"
4. Select an **Account Head**
5. Enter **Tax Rate** (e.g., 10 for 10%)
6. The system will automatically calculate the tax amount based on profit margin

### Important Notes:

- **Item Code Based**: The system fetches serial numbers based on the item's `item_code`, not from the transaction's serial_no field
- **All Serial Numbers**: ALL serial numbers in the Serial No master with matching item_code are included in the calculation
- **Custom Fields Must Exist**: The `custom_purchase_price` and `custom_selling_price` fields must be filled for each serial number
- **Real-time Calculation**: The tax amount updates in real-time as you add/remove items or change item codes
- **Zero Values**: If serial numbers don't have the custom fields populated, their profit is considered as 0

## Supported Documents

- Sales Invoice
- Sales Order
- Quotation

## Technical Details

### Files Modified/Created:

1. **Doctype JSON**: `/tax_pro/tax_pro/doctype/sales_taxes_and_charges/sales_taxes_and_charges.json`
   - Added "On Profit Margin" to charge_type options

2. **Helper Utils**: `/tax_pro/tax_pro/utils/serial_profit.py`
   - Functions to parse serial numbers and calculate profit margins

3. **Backend Override**: `/tax_pro/tax_pro/__init__.py`
   - Monkey patches ERPNext's `calculate_taxes_and_totals` class

4. **Frontend Override**: `/tax_pro/public/js/taxes_and_totals_override.js`
   - Extends JavaScript tax calculation for real-time updates

5. **Hooks**: `/tax_pro/hooks.py`
   - Registers JS includes and app configuration

## Troubleshooting

### Tax amount shows as 0:
- Check if serial numbers are properly assigned to items
- Verify that `custom_purchase_price` and `custom_selling_price` are populated for each serial number
- Check browser console for JavaScript errors

### Changes not reflecting:
```bash
bench clear-cache
bench build --app tax_pro
# Refresh your browser (Ctrl+F5)
```

### To view error logs:
```bash
bench --site [site-name] console

# In console:
frappe.db.sql("SELECT * FROM `tabError Log` ORDER BY creation DESC LIMIT 10")
```

## Development

To modify the calculation logic, edit:
- Backend: `/tax_pro/tax_pro/__init__.py` (monkey patch function)
- Frontend: `/tax_pro/public/js/taxes_and_totals_override.js`

After changes:
```bash
bench build --app tax_pro
bench clear-cache
bench restart
```

## Support

For issues or feature requests, please contact the development team or create an issue in the repository.

