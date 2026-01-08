#!/usr/bin/env python3
"""
Install and Configure HR Module for Pharmacy
"""

import xmlrpc.client
import time

URL = "http://localhost:8069"
DB = "pharmacy_kenya"
USERNAME = "admin"
PASSWORD = "admin"

def connect():
    print("🔌 Connecting to Odoo...")
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        if not uid:
            print("❌ Authentication failed!")
            return None, None
        print(f"✓ Connected (UID: {uid})\n")
        return uid, xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return None, None

def install_hr_module(uid, models):
    """Install HR module"""
    print("📦 Installing HR Module...")
    
    try:
        # Check if already installed
        hr_module = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'search_read',
            [[['name', '=', 'hr']]],
            {'fields': ['state'], 'limit': 1}
        )
        
        if hr_module and hr_module[0]['state'] == 'installed':
            print("  ✓ HR module already installed")
            return True
        
        if not hr_module:
            print("  ❌ HR module not found in system")
            return False
        
        # Install the module
        print("  Installing HR module (this may take a minute)...")
        module_id = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'search',
            [[['name', '=', 'hr']]]
        )
        
        if module_id:
            models.execute_kw(DB, uid, PASSWORD,
                'ir.module.module', 'button_immediate_install',
                [module_id]
            )
            print("  ✓ HR module installed successfully")
            time.sleep(2)  # Wait for installation
            return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:80]}")
        return False

def create_employee_records(uid, models):
    """Create employee records for existing users"""
    print("\n👔 Creating Employee Records...")
    
    try:
        # Get all POS users
        pos_users = models.execute_kw(DB, uid, PASSWORD,
            'res.users', 'search_read',
            [[['active', '=', True]]],
            {'fields': ['id', 'name', 'login', 'partner_id']}
        )
        
        created = 0
        existing = 0
        
        for user in pos_users:
            if user['login'] == '__system__':
                continue
            
            # Check if employee exists
            employee_exists = models.execute_kw(DB, uid, PASSWORD,
                'hr.employee', 'search_count',
                [[['user_id', '=', user['id']]]]
            )
            
            if employee_exists:
                existing += 1
                continue
            
            # Create employee record
            try:
                employee_data = {
                    'name': user['name'],
                    'user_id': user['id'],
                }
                
                # Add work email if available
                user_details = models.execute_kw(DB, uid, PASSWORD,
                    'res.users', 'read',
                    [[user['id']]], {'fields': ['email']}
                )[0]
                
                if user_details.get('email'):
                    employee_data['work_email'] = user_details['email']
                
                # Add phone if available
                if user.get('partner_id'):
                    partner = models.execute_kw(DB, uid, PASSWORD,
                        'res.partner', 'read',
                        [[user['partner_id'][0]]], {'fields': ['phone', 'mobile']}
                    )[0]
                    
                    if partner.get('phone'):
                        employee_data['work_phone'] = partner['phone']
                    elif partner.get('mobile'):
                        employee_data['mobile_phone'] = partner['mobile']
                
                # Set job title based on user
                if 'admin' in user['login'].lower():
                    employee_data['job_title'] = 'System Administrator'
                else:
                    employee_data['job_title'] = 'Pharmacy Cashier'
                
                employee_id = models.execute_kw(DB, uid, PASSWORD,
                    'hr.employee', 'create',
                    [employee_data]
                )
                
                print(f"  ✓ Created employee: {user['name']}")
                created += 1
                
            except Exception as e:
                print(f"  ⚠️  Could not create employee for {user['name']}: {str(e)[:60]}")
        
        print(f"\n  Summary: {created} created, {existing} already existed")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:80]}")
        return False

def test_hr_features(uid, models):
    """Test HR module features"""
    print("\n🧪 Testing HR Module Features...")
    
    try:
        # Test 1: Count employees
        employee_count = models.execute_kw(DB, uid, PASSWORD,
            'hr.employee', 'search_count', [[]]
        )
        print(f"  ✓ Total Employees: {employee_count}")
        
        # Test 2: List employees
        employees = models.execute_kw(DB, uid, PASSWORD,
            'hr.employee', 'search_read',
            [[]],
            {'fields': ['name', 'job_title', 'work_email'], 'limit': 10}
        )
        
        if employees:
            print(f"\n  Employee List:")
            for emp in employees:
                job = emp.get('job_title') or 'No title'
                email = emp.get('work_email') or 'No email'
                print(f"    - {emp['name']}: {job} ({email})")
        
        # Test 3: Check departments
        dept_count = models.execute_kw(DB, uid, PASSWORD,
            'hr.department', 'search_count', [[]]
        )
        print(f"\n  ✓ Departments: {dept_count}")
        
        # Test 4: Check if employees linked to users
        linked_count = models.execute_kw(DB, uid, PASSWORD,
            'hr.employee', 'search_count',
            [[['user_id', '!=', False]]]
        )
        print(f"  ✓ Employees linked to users: {linked_count}")
        
        # Test 5: Check job positions
        job_count = models.execute_kw(DB, uid, PASSWORD,
            'hr.job', 'search_count', [[]]
        )
        print(f"  ✓ Job Positions: {job_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:80]}")
        return False

def create_pharmacy_departments(uid, models):
    """Create pharmacy-specific departments"""
    print("\n🏢 Creating Pharmacy Departments...")
    
    departments = [
        {'name': 'Pharmacy', 'code': 'PHARM'},
        {'name': 'Administration', 'code': 'ADMIN'},
        {'name': 'Sales & POS', 'code': 'SALES'},
    ]
    
    try:
        created = 0
        for dept_data in departments:
            # Check if exists
            existing = models.execute_kw(DB, uid, PASSWORD,
                'hr.department', 'search',
                [[['name', '=', dept_data['name']]]]
            )
            
            if existing:
                print(f"  ✓ Department exists: {dept_data['name']}")
                continue
            
            # Create department
            dept_id = models.execute_kw(DB, uid, PASSWORD,
                'hr.department', 'create',
                [dept_data]
            )
            print(f"  ✓ Created department: {dept_data['name']}")
            created += 1
        
        print(f"\n  Summary: {created} departments created")
        
        # Assign employees to departments
        print("\n  Assigning employees to departments...")
        
        # Get departments
        pharmacy_dept = models.execute_kw(DB, uid, PASSWORD,
            'hr.department', 'search',
            [[['name', '=', 'Pharmacy']]]
        )
        
        sales_dept = models.execute_kw(DB, uid, PASSWORD,
            'hr.department', 'search',
            [[['name', '=', 'Sales & POS']]]
        )
        
        admin_dept = models.execute_kw(DB, uid, PASSWORD,
            'hr.department', 'search',
            [[['name', '=', 'Administration']]]
        )
        
        # Assign cashiers to Sales & POS
        if sales_dept:
            cashiers = models.execute_kw(DB, uid, PASSWORD,
                'hr.employee', 'search',
                [[['job_title', '=', 'Pharmacy Cashier']]]
            )
            
            if cashiers:
                models.execute_kw(DB, uid, PASSWORD,
                    'hr.employee', 'write',
                    [cashiers, {'department_id': sales_dept[0]}]
                )
                print(f"  ✓ Assigned {len(cashiers)} cashiers to Sales & POS")
        
        # Assign admin to Administration
        if admin_dept:
            admins = models.execute_kw(DB, uid, PASSWORD,
                'hr.employee', 'search',
                [[['job_title', '=', 'System Administrator']]]
            )
            
            if admins:
                models.execute_kw(DB, uid, PASSWORD,
                    'hr.employee', 'write',
                    [admins, {'department_id': admin_dept[0]}]
                )
                print(f"  ✓ Assigned {len(admins)} admin(s) to Administration")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:80]}")
        return False

def main():
    print("=" * 70)
    print("🇰🇪 INSTALLING HR MODULE FOR PHARMACY")
    print("=" * 70)
    print()
    
    uid, models = connect()
    if not uid:
        return
    
    # Install HR module
    if not install_hr_module(uid, models):
        print("\n❌ Failed to install HR module")
        return
    
    # Create employee records
    create_employee_records(uid, models)
    
    # Create departments
    create_pharmacy_departments(uid, models)
    
    # Test HR features
    test_hr_features(uid, models)
    
    print("\n" + "=" * 70)
    print("✅ HR MODULE SETUP COMPLETE!")
    print("=" * 70)
    print("\n📋 What's Available Now:")
    print("  • Employee records for all users")
    print("  • Pharmacy departments structure")
    print("  • Job positions tracking")
    print("  • Employee attendance (if needed)")
    print("  • Leave management (if needed)")
    print("\n🌐 Access HR:")
    print("  1. Login to Odoo: http://localhost:8069")
    print("  2. Go to 'Employees' app")
    print("  3. View all staff members")
    print("=" * 70)

if __name__ == '__main__':
    main()
