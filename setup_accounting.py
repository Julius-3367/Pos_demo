#!/usr/bin/env python3
"""
Automated Accounting Setup for Kenya Pharmacy
This script configures the accounting module with Kenya settings.
"""

import xmlrpc.client
import sys

# Configuration
URL = "http://localhost:8069"
DB = "pharmacy_kenya"
USERNAME = "admin"
PASSWORD = "admin"

def setup_accounting():
    """Setup accounting with Kenya configuration"""
    print("🚀 Setting up Accounting for Kenya...")
    
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    
    # Authenticate
    try:
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        if not uid:
            print("❌ Authentication failed! Check username/password")
            return False
        print(f"✅ Authenticated as user ID: {uid}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Make sure Odoo server is running at http://localhost:8069")
        return False
    
    # Get models proxy
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    try:
        # Check if accounting module is installed
        account_installed = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'search_count',
            [[['name', '=', 'account'], ['state', '=', 'installed']]]
        )
        
        if not account_installed:
            print("📦 Installing Accounting module...")
            module_id = models.execute_kw(DB, uid, PASSWORD,
                'ir.module.module', 'search',
                [[['name', '=', 'account']]]
            )
            if module_id:
                models.execute_kw(DB, uid, PASSWORD,
                    'ir.module.module', 'button_immediate_install',
                    [module_id]
                )
                print("✅ Accounting module installed")
        else:
            print("✅ Accounting module already installed")
        
        # Get Kenya country
        kenya_id = models.execute_kw(DB, uid, PASSWORD,
            'res.country', 'search',
            [[['code', '=', 'KE']]]
        )
        
        if kenya_id:
            kenya_id = kenya_id[0]
            print(f"✅ Found Kenya country (ID: {kenya_id})")
            
            # Update company
            company_id = models.execute_kw(DB, uid, PASSWORD,
                'res.company', 'search',
                [[['id', '=', 1]]]
            )
            
            if company_id:
                models.execute_kw(DB, uid, PASSWORD,
                    'res.company', 'write',
                    [company_id, {'name': 'Options Pharmacy'}]
                )
                print("✅ Company name set to 'Options Pharmacy'")
                
                # Update company partner with Kenya
                partner_id = models.execute_kw(DB, uid, PASSWORD,
                    'res.company', 'read',
                    [company_id, ['partner_id']]
                )[0]['partner_id'][0]
                
                models.execute_kw(DB, uid, PASSWORD,
                    'res.partner', 'write',
                    [[partner_id], {'country_id': kenya_id, 'name': 'Options Pharmacy'}]
                )
                print(f"✅ Company country set to Kenya")
        
        # Get KES currency
        kes_id = models.execute_kw(DB, uid, PASSWORD,
            'res.currency', 'search',
            [[['name', '=', 'KES']]]
        )
        
        if kes_id:
            kes_id = kes_id[0]
            # Make KES active
            models.execute_kw(DB, uid, PASSWORD,
                'res.currency', 'write',
                [[kes_id], {'active': True}]
            )
            
            # Set as company currency
            models.execute_kw(DB, uid, PASSWORD,
                'res.company', 'write',
                [[1], {'currency_id': kes_id}]
            )
            print("✅ Currency set to KES (Kenyan Shilling)")
        
        print("\n🎉 Accounting setup complete!")
        print("\n📋 Next steps:")
        print("   1. Open browser: http://localhost:8069")
        print("   2. Login: admin / admin")
        print("   3. Go to Apps → Search 'accounting' → Click 'Activate'")
        print("   4. Follow the setup wizard if it appears")
        print("   5. You should now see Inventory, Purchase, and POS menus!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_accounting()
    sys.exit(0 if success else 1)
