# Product Creation Error Fix - service_to_purchase Field

## Issue Summary
When trying to create a new product in the Inventory module, users encountered an error:
```
Error: "product.template"."service_to_purchase" field is undefined.
```

## Root Cause
The `sale_purchase` module (which is installed in the system) adds a view that references the `service_to_purchase` field on the `product.template` model. However, this field wasn't defined in our custom module, causing the form view to fail when trying to render.

**Error Location:**
```
File: /opt/odoo/odoo/addons/sale_purchase/views/product_views.xml
Field: service_to_purchase (referenced in product template form view)
```

## Solution Implemented
Added the missing `service_to_purchase` field to the `product.template` model in the custom module to ensure compatibility with the `sale_purchase` module views.

**File Modified:** [`models/product_template.py`](models/product_template.py)

**Changes Made:**
```python
# Fix for sale_purchase module compatibility
# Add this field to prevent errors when sale_purchase module views reference it
service_to_purchase = fields.Boolean(
    string='Subcontract Service',
    default=False,
    company_dependent=True,
    copy=False,
    help='If ticked, each time you sell this product through a SO, a RfQ is automatically created to buy the product.'
)
```

## Upgrade Process
1. Added the field definition to the model
2. Restarted Odoo server
3. Upgraded the `pos_demo` module to create the field in the database
4. Verified product creation works correctly

## Testing Results
✅ `service_to_purchase` field successfully added to database  
✅ Product template form view loads without errors  
✅ New products can be created successfully  
✅ Field value defaults to `False` (not a subcontract service)

## Impact
- **Users affected:** All users creating or editing products in Inventory module
- **System impact:** Low - adds a standard field that's expected by installed modules
- **Functionality:** Product creation and editing now work correctly
- **Compatibility:** Ensures compatibility with `sale_purchase` and related modules

## Module Dependencies
This fix ensures compatibility with:
- `sale_purchase` - Automatic PO creation from SO for services
- `purchase` - Purchase management
- Any other modules that extend product views

---

**Fixed on:** January 8, 2026  
**Status:** ✅ Resolved and tested
