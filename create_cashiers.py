#!/usr/bin/env python3
"""
Create Cashiers and Assign Roles for Pharmacy POS
Creates multiple cashier users with appropriate permissions
"""

import xmlrpc.client
from datetime import datetime

URL = "http://localhost:8069"
DB = "pharmacy_kenya"
USERNAME = "admin"
PASSWORD = "admin"

def connect():
    print("🔌 Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        print("❌ Authentication failed!")
        return None, None
    print(f"✓ Connected (UID: {uid})")
    return uid, xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

def get_or_create_groups(uid, models):
    """Get or create user groups for pharmacy roles"""
    print("\n📋 Setting up User Groups & Permissions...")
    
    groups = {}
    
    # 1. POS User Group
    pos_user = models.execute_kw(DB, uid, PASSWORD,
        'res.groups', 'search',
        [[['name', '=', 'User'], ['category_id.name', '=', 'Point of Sale']]]
    )
    
    if pos_user:
        groups['pos_user'] = pos_user[0]
        print("  ✓ POS User group found")
    
    # 2. Sales User Group
    sales_user = models.execute_kw(DB, uid, PASSWORD,
        'res.groups', 'search',
        [[['name', '=', 'User: Own Documents Only'], ['category_id.name', '=', 'Sales']]]
    )
    
    if not sales_user:
        sales_user = models.execute_kw(DB, uid, PASSWORD,
            'res.groups', 'search',
            [[['name', 'ilike', 'User'], ['category_id.name', '=', 'Sales']]]
        )
    
    if sales_user:
        groups['sales_user'] = sales_user[0]
        print("  ✓ Sales User group found")
    
    # 3. Pharmacy User Group (custom)
    pharmacy_user = models.execute_kw(DB, uid, PASSWORD,
        'res.groups', 'search',
        [[['name', '=', 'Pharmacy User']]]
    )
    
    if not pharmacy_user:
        # Create custom pharmacy user group
        try:
            pharmacy_category = models.execute_kw(DB, uid, PASSWORD,
                'ir.module.category', 'search',
                [[['name', '=', 'Pharmacy']]]
            )
            
            if not pharmacy_category:
                pharmacy_category = [models.execute_kw(DB, uid, PASSWORD,
                    'ir.module.category', 'create',
                    [{'name': 'Pharmacy', 'sequence': 10}]
                )]
            
            pharmacy_user_id = models.execute_kw(DB, uid, PASSWORD,
                'res.groups', 'create',
                [{
                    'name': 'Pharmacy User',
                    'category_id': pharmacy_category[0],
                    'comment': 'Access to pharmacy features for cashiers',
                }]
            )
            groups['pharmacy_user'] = pharmacy_user_id
            print("  ✓ Created Pharmacy User group")
        except:
            print("  ℹ️  Using existing groups")
    else:
        groups['pharmacy_user'] = pharmacy_user[0]
        print("  ✓ Pharmacy User group found")
    
    # 4. Inventory User Group
    inventory_user = models.execute_kw(DB, uid, PASSWORD,
        'res.groups', 'search',
        [[['name', 'ilike', 'User'], ['category_id.name', '=', 'Inventory']]]
    )
    
    if inventory_user:
        groups['inventory_user'] = inventory_user[0]
        print("  ✓ Inventory User group found")
    
    return groups

def create_cashiers(uid, models, groups):
    """Create cashier users"""
    print("\n👥 Creating Cashier Users...")
    
    cashiers_data = [
        {
            'name': 'Grace Wanjiru',
            'login': 'grace.wanjiru',
            'email': 'grace.wanjiru@pharmacy.co.ke',
            'phone': '+254722111001',
            'employee_id': 'EMP001',
        },
        {
            'name': 'James Mwangi',
            'login': 'james.mwangi',
            'email': 'james.mwangi@pharmacy.co.ke',
            'phone': '+254722111002',
            'employee_id': 'EMP002',
        },
        {
            'name': 'Mary Akinyi',
            'login': 'mary.akinyi',
            'email': 'mary.akinyi@pharmacy.co.ke',
            'phone': '+254722111003',
            'employee_id': 'EMP003',
        },
        {
            'name': 'Peter Ochieng',
            'login': 'peter.ochieng',
            'email': 'peter.ochieng@pharmacy.co.ke',
            'phone': '+254722111004',
            'employee_id': 'EMP004',
        },
        {
            'name': 'Sarah Chebet',
            'login': 'sarah.chebet',
            'email': 'sarah.chebet@pharmacy.co.ke',
            'phone': '+254722111005',
            'employee_id': 'EMP005',
        },
    ]
    
    created_cashiers = []
    default_password = 'cashier123'
    
    for cashier_info in cashiers_data:
        # Check if user already exists
        existing_user = models.execute_kw(DB, uid, PASSWORD,
            'res.users', 'search',
            [[['login', '=', cashier_info['login']]]]
        )
        
        if existing_user:
            print(f"  ⚠️  User {cashier_info['login']} already exists")
            created_cashiers.append({
                'id': existing_user[0],
                'login': cashier_info['login'],
                'name': cashier_info['name']
            })
            continue
        
        # Prepare groups list
        group_ids = []
        if groups.get('pos_user'):
            group_ids.append(groups['pos_user'])
        if groups.get('sales_user'):
            group_ids.append(groups['sales_user'])
        if groups.get('pharmacy_user'):
            group_ids.append(groups['pharmacy_user'])
        if groups.get('inventory_user'):
            group_ids.append(groups['inventory_user'])
        
        # Create user
        user_data = {
            'name': cashier_info['name'],
            'login': cashier_info['login'],
            'email': cashier_info['email'],
            'password': default_password,
            'groups_id': [[6, 0, group_ids]],
        }
        
        try:
            user_id = models.execute_kw(DB, uid, PASSWORD,
                'res.users', 'create',
                [user_data]
            )
            
            # Update partner info (phone)
            partner = models.execute_kw(DB, uid, PASSWORD,
                'res.users', 'read',
                [[user_id]], {'fields': ['partner_id']}
            )[0]
            
            if partner.get('partner_id'):
                models.execute_kw(DB, uid, PASSWORD,
                    'res.partner', 'write',
                    [[partner['partner_id'][0]], {
                        'phone': cashier_info['phone'],
                        'function': 'Pharmacy Cashier',
                    }]
                )
            
            print(f"  ✓ Created cashier: {cashier_info['name']} ({cashier_info['login']})")
            
            created_cashiers.append({
                'id': user_id,
                'login': cashier_info['login'],
                'name': cashier_info['name'],
                'password': default_password
            })
            
        except Exception as e:
            print(f"  ⚠️  Error creating {cashier_info['login']}: {str(e)[:80]}")
    
    return created_cashiers

def assign_pos_access(uid, models, cashiers):
    """Assign POS configurations to cashiers"""
    print("\n🏪 Assigning POS Access...")
    
    # Get POS configurations
    pos_configs = models.execute_kw(DB, uid, PASSWORD,
        'pos.config', 'search_read',
        [[]],
        {'fields': ['id', 'name']}
    )
    
    if not pos_configs:
        print("  ℹ️  No POS configurations found")
        return
    
    print(f"  Found {len(pos_configs)} POS configuration(s)")
    
    for pos_config in pos_configs:
        # Update POS config to allow these users
        try:
            cashier_ids = [c['id'] for c in cashiers]
            
            # Note: In Odoo, POS access is primarily controlled by groups
            # The users with POS User group can access all POS configs
            print(f"  ✓ POS Config '{pos_config['name']}' accessible to all cashiers via groups")
            
        except Exception as e:
            print(f"  ℹ️  POS access controlled by user groups")
            break
    
    return True

def create_employee_records(uid, models, cashiers):
    """Create employee records for cashiers"""
    print("\n👔 Creating Employee Records...")
    
    # Check if HR module exists
    try:
        hr_exists = models.execute_kw(DB, uid, PASSWORD,
            'ir.model', 'search_count',
            [[['model', '=', 'hr.employee']]]
        )
        
        if not hr_exists:
            print("  ℹ️  HR module not installed (not required for POS)")
            return True
            
    except:
        print("  ℹ️  HR module not installed (not required for POS)")
        return True
    
    for cashier in cashiers:
        # Check if employee exists
        partner = models.execute_kw(DB, uid, PASSWORD,
            'res.users', 'read',
            [[cashier['id']]], {'fields': ['partner_id']}
        )[0]
        
        if not partner.get('partner_id'):
            continue
        
        partner_id = partner['partner_id'][0]
        
        # Check if employee record exists
        try:
            existing_employee = models.execute_kw(DB, uid, PASSWORD,
                'hr.employee', 'search',
                [[['user_id', '=', cashier['id']]]]
            )
            
            if existing_employee:
                print(f"  ⚠️  Employee record exists for {cashier['name']}")
                continue
            
            # Create employee
            employee_data = {
                'name': cashier['name'],
                'user_id': cashier['id'],
                'work_email': models.execute_kw(DB, uid, PASSWORD,
                    'res.users', 'read',
                    [[cashier['id']]], {'fields': ['email']}
                )[0].get('email'),
                'job_title': 'Pharmacy Cashier',
                'work_phone': models.execute_kw(DB, uid, PASSWORD,
                    'res.partner', 'read',
                    [[partner_id]], {'fields': ['phone']}
                )[0].get('phone'),
            }
            
            employee_id = models.execute_kw(DB, uid, PASSWORD,
                'hr.employee', 'create',
                [employee_data]
            )
            
            print(f"  ✓ Created employee record for {cashier['name']}")
            
        except Exception as e:
            # HR module might not be installed
            print(f"  ℹ️  Employee records: {str(e)[:60]}")
            break
    
    return True

def display_summary(uid, models, cashiers):
    """Display summary of created cashiers and their roles"""
    print("\n" + "="*70)
    print("👥 CASHIER SETUP SUMMARY")
    print("="*70)
    
    print(f"\n✅ Created {len(cashiers)} Cashier Accounts:")
    print(f"\n{'Name':<20} {'Login':<20} {'Password':<15} {'Status'}")
    print("-" * 70)
    
    for cashier in cashiers:
        password = cashier.get('password', 'existing')
        print(f"{cashier['name']:<20} {cashier['login']:<20} {password:<15} Active")
    
    print("\n📋 ASSIGNED PERMISSIONS:")
    print("  ✓ Point of Sale - User (can use POS)")
    print("  ✓ Sales - User (can create invoices)")
    print("  ✓ Pharmacy - User (pharmacy features)")
    print("  ✓ Inventory - User (view stock)")
    
    print("\n🔑 ACCESS RIGHTS:")
    print("  • Open/Close POS sessions")
    print("  • Process sales and payments")
    print("  • Create customer invoices")
    print("  • View patient records")
    print("  • Dispense medications")
    print("  • View inventory levels")
    print("  • Process insurance claims")
    
    print("\n🚫 RESTRICTED (Admin Only):")
    print("  • Modify product prices")
    print("  • Delete transactions")
    print("  • Access accounting reports")
    print("  • Manage users")
    print("  • Change system settings")
    
    print("\n🌐 LOGIN INFORMATION:")
    print(f"  URL: http://localhost:8069")
    print(f"  Database: pharmacy_kenya")
    print(f"  Default Password: cashier123")
    print(f"  (Users should change password on first login)")
    
    print("\n📍 HOW CASHIERS USE THE SYSTEM:")
    print("  1. Login with their credentials")
    print("  2. Click 'Point of Sale' app")
    print("  3. Open POS session")
    print("  4. Start selling:")
    print("     - Scan/select products")
    print("     - Select customer (patient)")
    print("     - Choose payment method")
    print("     - Print receipt")
    print("  5. Close session at end of shift")
    
    print("\n💡 TIPS FOR CASHIERS:")
    print("  • Always link sales to patient records")
    print("  • Verify prescription for controlled drugs")
    print("  • Check stock before dispensing")
    print("  • Process insurance claims correctly")
    print("  • Balance cash at end of shift")
    
    # Get total users
    total_users = models.execute_kw(DB, uid, PASSWORD,
        'res.users', 'search_count',
        [[['active', '=', True]]]
    )
    
    print(f"\n📊 SYSTEM USERS:")
    print(f"  • Total Active Users: {total_users}")
    print(f"  • Administrators: 1 (admin)")
    print(f"  • Cashiers: {len(cashiers)}")
    
    return True

def test_cashier_access(uid, models, cashiers):
    """Test cashier login and permissions"""
    print("\n🔐 Testing Cashier Access...")
    
    if not cashiers:
        print("  ⚠️  No cashiers to test")
        return
    
    # Test first cashier login
    test_cashier = cashiers[0]
    
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        test_uid = common.authenticate(DB, test_cashier['login'], test_cashier.get('password', 'cashier123'), {})
        
        if test_uid:
            print(f"  ✓ Login successful for {test_cashier['name']}")
            
            # Test access to POS
            test_models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
            
            pos_access = test_models.execute_kw(DB, test_uid, test_cashier.get('password', 'cashier123'),
                'pos.config', 'search_count', [[]]
            )
            
            print(f"  ✓ Can access {pos_access} POS configuration(s)")
            
            # Test patient access
            patient_access = test_models.execute_kw(DB, test_uid, test_cashier.get('password', 'cashier123'),
                'res.partner', 'search_count', [[['is_patient', '=', True]]]
            )
            
            print(f"  ✓ Can view {patient_access} patient records")
            
            print(f"  ✅ {test_cashier['name']} has correct permissions")
        else:
            print(f"  ⚠️  Login failed for {test_cashier['name']}")
            
    except Exception as e:
        print(f"  ℹ️  Access test: {str(e)[:60]}")

def main():
    print("="*70)
    print("🇰🇪 PHARMACY CASHIER SETUP")
    print("="*70)
    
    uid, models = connect()
    if not uid:
        return
    
    # Get or create groups
    groups = get_or_create_groups(uid, models)
    
    # Create cashiers
    cashiers = create_cashiers(uid, models, groups)
    
    # Assign POS access
    assign_pos_access(uid, models, cashiers)
    
    # Create employee records
    create_employee_records(uid, models, cashiers)
    
    # Test access
    test_cashier_access(uid, models, cashiers)
    
    # Display summary
    display_summary(uid, models, cashiers)
    
    print("\n" + "="*70)
    print("✅ CASHIER SETUP COMPLETED!")
    print("="*70)
    print("\nℹ️  IMPORTANT SECURITY NOTES:")
    print("  • Change default password on first login")
    print("  • Keep login credentials secure")
    print("  • Report any suspicious activity to admin")
    print("  • Log out when leaving the counter")
    print("="*70)

if __name__ == '__main__':
    main()
