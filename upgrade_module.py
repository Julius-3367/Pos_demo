#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upgrade the pos_demo module to add the service_to_purchase field
"""
import xmlrpc.client

# Connection parameters
url = 'http://localhost:8069'
db = 'pharmacy_kenya'
username = 'admin'
password = 'admin'

print("Upgrading pos_demo module...")

# Authenticate
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✓ Authenticated as user ID: {uid}")
    
    # Get models access
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    
    try:
        # Find the pos_demo module
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', 'pos_demo']]]
        )
        
        if module_ids:
            print(f"Found module ID: {module_ids[0]}")
            
            # Upgrade the module
            models.execute_kw(
                db, uid, password,
                'ir.module.module', 'button_immediate_upgrade',
                [module_ids]
            )
            
            print("✅ Module upgrade initiated successfully!")
            print("⏳ Please wait for the upgrade to complete (this may take a minute)...")
            
        else:
            print("❌ pos_demo module not found")
            exit(1)
            
    except Exception as e:
        print(f"❌ Error upgrading module: {e}")
        exit(1)
else:
    print("❌ Authentication failed")
    exit(1)
