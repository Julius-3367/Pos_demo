#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test creating a new product to verify the service_to_purchase field is working
"""
import xmlrpc.client

# Connection parameters
url = 'http://localhost:8069'
db = 'pharmacy_kenya'
username = 'admin'
password = 'admin'

print("Testing product creation...")

# Authenticate
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✓ Authenticated as user ID: {uid}")
    
    # Get models access
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    
    try:
        # Try to read product template fields to verify service_to_purchase exists
        print("\nChecking if service_to_purchase field exists...")
        fields_info = models.execute_kw(
            db, uid, password,
            'product.template', 'fields_get',
            [],
            {'attributes': ['string', 'help', 'type']}
        )
        
        if 'service_to_purchase' in fields_info:
            print(f"✓ service_to_purchase field exists: {fields_info['service_to_purchase']['string']}")
        else:
            print("⚠ service_to_purchase field not found")
        
        # Try to create a test product
        print("\nAttempting to create a test product...")
        product_id = models.execute_kw(
            db, uid, password,
            'product.template', 'create',
            [{
                'name': 'Test Product - Field Verification',
                'type': 'consu',
                'list_price': 100.0,
                'is_pharmaceutical': False,
            }]
        )
        
        print(f"✓ Successfully created test product with ID: {product_id}")
        
        # Read the product back
        product = models.execute_kw(
            db, uid, password,
            'product.template', 'read',
            [product_id],
            {'fields': ['name', 'service_to_purchase']}
        )
        
        print(f"✓ Product details: {product[0]}")
        
        # Clean up - delete test product
        models.execute_kw(
            db, uid, password,
            'product.template', 'unlink',
            [[product_id]]
        )
        print(f"✓ Cleaned up test product")
        
        print("\n✅ Product creation is working correctly!")
        print("You can now create new products in the Inventory module.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
else:
    print("❌ Authentication failed")
    exit(1)
