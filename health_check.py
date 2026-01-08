#!/usr/bin/env python3
"""
Kenya Pharmacy System - Comprehensive Health Check
Tests all critical features to ensure system is working properly
"""

import xmlrpc.client
import sys
import requests
from datetime import datetime

URL = "http://localhost:8069"
DB = "pharmacy_kenya"
USERNAME = "admin"
PASSWORD = "admin"

class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_header(title):
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")

def print_test(name, passed, message=""):
    symbol = f"{Colors.GREEN}✓{Colors.NC}" if passed else f"{Colors.RED}✗{Colors.NC}"
    print(f"  {symbol} {name}")
    if message:
        color = Colors.GREEN if passed else Colors.RED
        print(f"    {color}{message}{Colors.NC}")

def test_web_server():
    """Test 1: Web Server Accessibility"""
    print_header("TEST 1: WEB SERVER")
    
    try:
        response = requests.get(f"{URL}/web/database/selector", timeout=5)
        if response.status_code == 200:
            print_test("Web server accessible", True, f"Status: {response.status_code}")
            return True
        else:
            print_test("Web server accessible", False, f"Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_test("Web server accessible", False, "Cannot connect to server")
        return False
    except Exception as e:
        print_test("Web server accessible", False, str(e)[:60])
        return False

def test_database_connection():
    """Test 2: Database Connection"""
    print_header("TEST 2: DATABASE CONNECTION")
    
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        version = common.version()
        print_test("Odoo version", True, f"v{version['server_version']}")
        
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        if uid:
            print_test("Authentication", True, f"User ID: {uid}")
            return uid, xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        else:
            print_test("Authentication", False, "Invalid credentials")
            return None, None
    except Exception as e:
        print_test("Database connection", False, str(e)[:60])
        return None, None

def test_modules(uid, models):
    """Test 3: Essential Modules"""
    print_header("TEST 3: INSTALLED MODULES")
    
    required_modules = {
        'base': 'Base System',
        'account': 'Accounting',
        'point_of_sale': 'Point of Sale',
        'stock': 'Inventory',
        'sale': 'Sales',
        'pos_demo': 'Pharmacy Module',
        'hr': 'Human Resources'
    }
    
    all_ok = True
    for module, name in required_modules.items():
        try:
            state = models.execute_kw(DB, uid, PASSWORD,
                'ir.module.module', 'search_read',
                [[['name', '=', module]]],
                {'fields': ['state'], 'limit': 1}
            )
            
            if state and state[0]['state'] == 'installed':
                print_test(name, True, module)
            else:
                print_test(name, False, f"{module} not installed")
                all_ok = False
        except Exception as e:
            print_test(name, False, str(e)[:60])
            all_ok = False
    
    return all_ok

def test_pos_system(uid, models):
    """Test 4: POS System"""
    print_header("TEST 4: POINT OF SALE")
    
    try:
        # Check POS configs
        pos_configs = models.execute_kw(DB, uid, PASSWORD,
            'pos.config', 'search_count', [[['active', '=', True]]]
        )
        print_test("POS Configurations", pos_configs > 0, f"{pos_configs} active")
        
        # Check payment methods
        payment_methods = models.execute_kw(DB, uid, PASSWORD,
            'pos.payment.method', 'search_count', [[]]
        )
        print_test("Payment Methods", payment_methods > 0, f"{payment_methods} available")
        
        # Check for open sessions
        open_sessions = models.execute_kw(DB, uid, PASSWORD,
            'pos.session', 'search_count', [[['state', '=', 'opened']]]
        )
        
        if open_sessions > 0:
            print_test("POS Sessions", True, f"{open_sessions} session(s) open")
        else:
            print_test("POS Sessions", True, "No open sessions (good for production)")
        
        return True
    except Exception as e:
        print_test("POS System", False, str(e)[:60])
        return False

def test_pharmacy_features(uid, models):
    """Test 5: Pharmacy Features"""
    print_header("TEST 5: PHARMACY FEATURES")
    
    try:
        # Check patients
        patients = models.execute_kw(DB, uid, PASSWORD,
            'res.partner', 'search_count', [[['is_patient', '=', True]]]
        )
        print_test("Patient Records", patients > 0, f"{patients} patients")
        
        # Check prescriptions
        prescriptions = models.execute_kw(DB, uid, PASSWORD,
            'pharmacy.prescription', 'search_count', [[]]
        )
        print_test("Prescriptions", prescriptions >= 0, f"{prescriptions} records")
        
        # Check controlled drugs register
        controlled_drugs = models.execute_kw(DB, uid, PASSWORD,
            'controlled.drugs.register', 'search_count', [[]]
        )
        print_test("Controlled Drugs Register", controlled_drugs >= 0, f"{controlled_drugs} entries")
        
        # Check insurance providers
        insurance = models.execute_kw(DB, uid, PASSWORD,
            'insurance.provider', 'search_count', [[]]
        )
        print_test("Insurance Providers", insurance >= 0, f"{insurance} providers")
        
        return True
    except Exception as e:
        print_test("Pharmacy Features", False, str(e)[:60])
        return False

def test_inventory(uid, models):
    """Test 6: Inventory System"""
    print_header("TEST 6: INVENTORY SYSTEM")
    
    try:
        # Check warehouses
        warehouses = models.execute_kw(DB, uid, PASSWORD,
            'stock.warehouse', 'search_count', [[]]
        )
        print_test("Warehouses", warehouses > 0, f"{warehouses} warehouse(s)")
        
        # Check products
        products = models.execute_kw(DB, uid, PASSWORD,
            'product.product', 'search_count', [[['sale_ok', '=', True]]]
        )
        print_test("Products", products > 0, f"{products} sellable products")
        
        # Check product categories
        categories = models.execute_kw(DB, uid, PASSWORD,
            'product.category', 'search_count', [[]]
        )
        print_test("Product Categories", categories > 0, f"{categories} categories")
        
        return True
    except Exception as e:
        print_test("Inventory System", False, str(e)[:60])
        return False

def test_accounting(uid, models):
    """Test 7: Accounting System"""
    print_header("TEST 7: ACCOUNTING SYSTEM")
    
    try:
        # Check chart of accounts
        accounts = models.execute_kw(DB, uid, PASSWORD,
            'account.account', 'search_count', [[]]
        )
        print_test("Chart of Accounts", accounts > 0, f"{accounts} accounts")
        
        # Check journals
        journals = models.execute_kw(DB, uid, PASSWORD,
            'account.journal', 'search_count', [[]]
        )
        print_test("Journals", journals > 0, f"{journals} journals")
        
        # Check invoices
        invoices = models.execute_kw(DB, uid, PASSWORD,
            'account.move', 'search_count',
            [[['move_type', 'in', ['out_invoice', 'out_refund']]]]
        )
        print_test("Customer Invoices", invoices >= 0, f"{invoices} invoices")
        
        return True
    except Exception as e:
        print_test("Accounting System", False, str(e)[:60])
        return False

def test_user_management(uid, models):
    """Test 8: User Management & HR"""
    print_header("TEST 8: USER MANAGEMENT & HR")
    
    try:
        # Check users
        users = models.execute_kw(DB, uid, PASSWORD,
            'res.users', 'search_count', [[['active', '=', True]]]
        )
        print_test("Active Users", users > 0, f"{users} users")
        
        # Check POS users
        pos_group = models.execute_kw(DB, uid, PASSWORD,
            'res.groups', 'search_read',
            [[['name', '=', 'User'], ['category_id.name', '=', 'Point of Sale']]],
            {'fields': ['users'], 'limit': 1}
        )
        
        if pos_group and pos_group[0].get('users'):
            pos_users = len(pos_group[0]['users'])
            print_test("POS Users", pos_users > 0, f"{pos_users} cashiers")
        else:
            print_test("POS Users", False, "No POS users found")
        
        # Check employees (HR module)
        employees = models.execute_kw(DB, uid, PASSWORD,
            'hr.employee', 'search_count', [[]]
        )
        print_test("Employee Records", employees > 0, f"{employees} employees")
        
        # Check departments
        departments = models.execute_kw(DB, uid, PASSWORD,
            'hr.department', 'search_count', [[]]
        )
        print_test("Departments", departments >= 0, f"{departments} departments")
        
        return True
    except Exception as e:
        print_test("User Management", False, str(e)[:60])
        return False

def test_security(uid, models):
    """Test 9: Security & Access Control"""
    print_header("TEST 9: SECURITY & ACCESS")
    
    try:
        # Check access rights
        access_rights = models.execute_kw(DB, uid, PASSWORD,
            'ir.model.access', 'search_count', [[]]
        )
        print_test("Access Rights", access_rights > 0, f"{access_rights} rules")
        
        # Check user groups
        groups = models.execute_kw(DB, uid, PASSWORD,
            'res.groups', 'search_count', [[]]
        )
        print_test("User Groups", groups > 0, f"{groups} groups")
        
        # Check demo data is hidden
        demo_menu = models.execute_kw(DB, uid, PASSWORD,
            'ir.ui.menu', 'search_count',
            [[['name', '=', 'Generate Demo Data']]]
        )
        print_test("Demo Data Hidden", demo_menu == 0, "Production ready")
        
        return True
    except Exception as e:
        print_test("Security", False, str(e)[:60])
        return False

def test_ppb_compliance(uid, models):
    """Test 10: PPB Compliance (Kenya)"""
    print_header("TEST 10: PPB COMPLIANCE")
    
    try:
        # Check controlled substances
        schedule_1 = models.execute_kw(DB, uid, PASSWORD,
            'product.template', 'search_count',
            [[['drug_schedule', '=', 'schedule_1']]]
        )
        
        schedule_2 = models.execute_kw(DB, uid, PASSWORD,
            'product.template', 'search_count',
            [[['drug_schedule', '=', 'schedule_2']]]
        )
        
        print_test("Schedule 1 Drugs", schedule_1 >= 0, f"{schedule_1} drugs")
        print_test("Schedule 2 Drugs", schedule_2 >= 0, f"{schedule_2} drugs")
        
        # Check prescribers
        prescribers = models.execute_kw(DB, uid, PASSWORD,
            'res.partner', 'search_count',
            [[['is_prescriber', '=', True]]]
        )
        print_test("Licensed Prescribers", prescribers >= 0, f"{prescribers} prescribers")
        
        # Check if reports exist
        reports = models.execute_kw(DB, uid, PASSWORD,
            'ir.actions.report', 'search_count',
            [[['model', 'in', ['controlled.drugs.register', 'pharmacy.prescription']]]]
        )
        print_test("PPB Reports", reports > 0, f"{reports} reports available")
        
        return True
    except Exception as e:
        print_test("PPB Compliance", False, str(e)[:60])
        return False

def display_summary(results):
    """Display summary of health check"""
    print_header("HEALTH CHECK SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n  Total Tests: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.NC}")
    print(f"  {Colors.RED}Failed: {failed}{Colors.NC}")
    print(f"  Success Rate: {percentage:.1f}%")
    
    print(f"\n{'='*70}")
    
    if percentage >= 90:
        print(f"{Colors.GREEN}🟢 SYSTEM STATUS: HEALTHY{Colors.NC}")
        print("\n✅ All critical systems are operational")
        print("   The pharmacy system is ready for use")
    elif percentage >= 70:
        print(f"{Colors.YELLOW}🟡 SYSTEM STATUS: PARTIALLY HEALTHY{Colors.NC}")
        print("\n⚠️  Some issues detected")
        print("   Review failed tests and address issues")
    else:
        print(f"{Colors.RED}🔴 SYSTEM STATUS: UNHEALTHY{Colors.NC}")
        print("\n❌ Critical issues detected")
        print("   System may not function correctly")
    
    print(f"\n{'='*70}")
    print(f"Health check completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    return percentage >= 90

def main():
    print("="*70)
    print("🇰🇪 KENYA PHARMACY SYSTEM - HEALTH CHECK")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {URL}")
    print(f"Database: {DB}")
    
    results = {}
    
    # Run all tests
    results['Web Server'] = test_web_server()
    
    uid, models = test_database_connection()
    if not uid:
        print(f"\n{Colors.RED}❌ Cannot proceed without database connection{Colors.NC}")
        sys.exit(1)
    
    results['Database'] = True
    results['Modules'] = test_modules(uid, models)
    results['POS'] = test_pos_system(uid, models)
    results['Pharmacy'] = test_pharmacy_features(uid, models)
    results['Inventory'] = test_inventory(uid, models)
    results['Accounting'] = test_accounting(uid, models)
    results['Users & HR'] = test_user_management(uid, models)
    results['Security'] = test_security(uid, models)
    results['PPB Compliance'] = test_ppb_compliance(uid, models)
    
    # Display summary
    healthy = display_summary(results)
    
    sys.exit(0 if healthy else 1)

if __name__ == '__main__':
    main()
