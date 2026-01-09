#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify POS config can be accessed without AttributeError
"""
import xmlrpc.client

# Connection parameters
url = 'http://localhost:8069'
db = 'pharmacy_kenya'
username = 'admin'
password = 'admin'

# Authenticate
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✓ Authenticated as user ID: {uid}")
    
    # Get models access
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    
    try:
        # Try to search and read POS configs
        print("\nTesting POS Config access...")
        configs = models.execute_kw(
            db, uid, password,
            'pos.config', 'search_read',
            [],
            {'fields': ['name', 'last_session_closing_date'], 'limit': 5}
        )
        
        print(f"✓ Successfully retrieved {len(configs)} POS config(s)")
        for config in configs:
            print(f"  - {config['name']}: last_session_closing_date = {config.get('last_session_closing_date', 'N/A')}")
        
        print("\n✅ POS integration is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error accessing POS config: {e}")
        exit(1)
else:
    print("❌ Authentication failed")
    exit(1)
