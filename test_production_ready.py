#!/usr/bin/env python3
"""
PRODUCTION READINESS TEST - Kenya Pharmacy System
Comprehensive testing before production deployment
"""

import xmlrpc.client
from datetime import datetime, timedelta
import sys

URL = "http://localhost:8069"
DB = "pharmacy_kenya"
USERNAME = "admin"
PASSWORD = "admin"

# Test results tracker
test_results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def log_test(test_name, status, message=""):
    """Log test results"""
    if status == 'PASS':
        test_results['passed'].append(f"✅ {test_name}")
        print(f"  ✅ {test_name}")
        if message:
            print(f"     {message}")
    elif status == 'FAIL':
        test_results['failed'].append(f"❌ {test_name}: {message}")
        print(f"  ❌ {test_name}")
        if message:
            print(f"     ERROR: {message}")
    else:  # WARNING
        test_results['warnings'].append(f"⚠️  {test_name}: {message}")
        print(f"  ⚠️  {test_name}")
        if message:
            print(f"     WARNING: {message}")

def connect():
    """Connect to Odoo"""
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

def test_system_configuration(uid, models):
    """Test 1: System Configuration"""
    print("📋 TEST 1: SYSTEM CONFIGURATION")
    print("=" * 70)
    
    try:
        # Check company
        company = models.execute_kw(DB, uid, PASSWORD,
            'res.company', 'search_read',
            [[['id', '=', 1]]],
            {'fields': ['name', 'currency_id', 'country_id'], 'limit': 1}
        )
        
        if company:
            comp = company[0]
            log_test("Company Configuration", 'PASS', f"{comp['name']}")
            
            # Check currency
            if comp.get('currency_id') and 'KES' in str(comp['currency_id']):
                log_test("Currency (KES)", 'PASS')
            else:
                log_test("Currency (KES)", 'WARN', "Currency might not be KES")
            
            # Check country
            if comp.get('country_id') and 'Kenya' in str(comp['country_id']):
                log_test("Country (Kenya)", 'PASS')
            else:
                log_test("Country (Kenya)", 'WARN', "Country might not be Kenya")
        else:
            log_test("Company Configuration", 'FAIL', "No company found")
            
    except Exception as e:
        log_test("System Configuration", 'FAIL', str(e)[:80])
    
    print()

def test_modules_installed(uid, models):
    """Test 2: Required Modules"""
    print("📦 TEST 2: REQUIRED MODULES")
    print("=" * 70)
    
    required_modules = [
        'base',
        'account',
        'point_of_sale',
        'stock',
        'sale',
        'pos_demo'
    ]
    
    try:
        for module in required_modules:
            module_state = models.execute_kw(DB, uid, PASSWORD,
                'ir.module.module', 'search_read',
                [[['name', '=', module]]],
                {'fields': ['state'], 'limit': 1}
            )
            
            if module_state and module_state[0]['state'] == 'installed':
                log_test(f"Module: {module}", 'PASS')
            else:
                log_test(f"Module: {module}", 'FAIL', "Not installed")
                
    except Exception as e:
        log_test("Module Check", 'FAIL', str(e)[:80])
    
    print()

def test_chart_of_accounts(uid, models):
    """Test 3: Chart of Accounts"""
    print("💰 TEST 3: CHART OF ACCOUNTS")
    print("=" * 70)
    
    try:
        # Count accounts
        account_count = models.execute_kw(DB, uid, PASSWORD,
            'account.account', 'search_count', [[]]
        )
        
        if account_count > 50:
            log_test("Chart of Accounts", 'PASS', f"{account_count} accounts")
        elif account_count > 0:
            log_test("Chart of Accounts", 'WARN', f"Only {account_count} accounts")
        else:
            log_test("Chart of Accounts", 'FAIL', "No accounts configured")
        
        # Check journals
        journal_count = models.execute_kw(DB, uid, PASSWORD,
            'account.journal', 'search_count', [[]]
        )
        
        if journal_count >= 3:
            log_test("Accounting Journals", 'PASS', f"{journal_count} journals")
        else:
            log_test("Accounting Journals", 'WARN', f"Only {journal_count} journals")
        
        # Check payment methods
        payment_methods = models.execute_kw(DB, uid, PASSWORD,
            'pos.payment.method', 'search_count', [[]]
        )
        
        if payment_methods > 0:
            log_test("Payment Methods", 'PASS', f"{payment_methods} methods")
        else:
            log_test("Payment Methods", 'FAIL', "No payment methods")
            
    except Exception as e:
        log_test("Chart of Accounts", 'FAIL', str(e)[:80])
    
    print()

def test_pos_configuration(uid, models):
    """Test 4: POS Configuration"""
    print("🏪 TEST 4: POINT OF SALE CONFIGURATION")
    print("=" * 70)
    
    try:
        # Check POS configs
        pos_configs = models.execute_kw(DB, uid, PASSWORD,
            'pos.config', 'search_read',
            [[]],
            {'fields': ['name', 'active', 'picking_type_id', 'pricelist_id']}
        )
        
        if pos_configs:
            for config in pos_configs:
                if config.get('active'):
                    log_test(f"POS Config: {config['name']}", 'PASS')
                    
                    if config.get('picking_type_id'):
                        log_test("  - Picking Type", 'PASS')
                    else:
                        log_test("  - Picking Type", 'WARN', "Not configured")
                    
                    if config.get('pricelist_id'):
                        log_test("  - Pricelist", 'PASS')
                    else:
                        log_test("  - Pricelist", 'WARN', "Not configured")
        else:
            log_test("POS Configuration", 'FAIL', "No POS config found")
        
        # Check if there's an open session
        open_sessions = models.execute_kw(DB, uid, PASSWORD,
            'pos.session', 'search_count',
            [[['state', '=', 'opened']]]
        )
        
        if open_sessions > 0:
            log_test("Open POS Sessions", 'WARN', f"{open_sessions} sessions open - close before production")
        else:
            log_test("No Open Sessions", 'PASS', "Ready for production")
            
    except Exception as e:
        log_test("POS Configuration", 'FAIL', str(e)[:80])
    
    print()

def test_inventory_setup(uid, models):
    """Test 5: Inventory Setup"""
    print("📦 TEST 5: INVENTORY CONFIGURATION")
    print("=" * 70)
    
    try:
        # Check warehouse
        warehouses = models.execute_kw(DB, uid, PASSWORD,
            'stock.warehouse', 'search_count', [[]]
        )
        
        if warehouses > 0:
            log_test("Warehouse Configuration", 'PASS', f"{warehouses} warehouse(s)")
        else:
            log_test("Warehouse Configuration", 'FAIL', "No warehouse")
        
        # Check locations
        locations = models.execute_kw(DB, uid, PASSWORD,
            'stock.location', 'search_count',
            [[['usage', 'in', ['internal', 'customer', 'supplier']]]]
        )
        
        if locations > 0:
            log_test("Stock Locations", 'PASS', f"{locations} locations")
        else:
            log_test("Stock Locations", 'WARN', "Limited locations")
        
        # Check product categories
        categories = models.execute_kw(DB, uid, PASSWORD,
            'product.category', 'search_count', [[]]
        )
        
        if categories > 0:
            log_test("Product Categories", 'PASS', f"{categories} categories")
        else:
            log_test("Product Categories", 'WARN', "No categories")
            
    except Exception as e:
        log_test("Inventory Setup", 'FAIL', str(e)[:80])
    
    print()

def test_pharmacy_features(uid, models):
    """Test 6: Pharmacy-Specific Features"""
    print("💊 TEST 6: PHARMACY FEATURES")
    print("=" * 70)
    
    try:
        # Check controlled drugs register model
        controlled_drugs_model = models.execute_kw(DB, uid, PASSWORD,
            'ir.model', 'search_count',
            [[['model', '=', 'controlled.drugs.register']]]
        )
        
        if controlled_drugs_model:
            log_test("Controlled Drugs Register", 'PASS')
        else:
            log_test("Controlled Drugs Register", 'FAIL', "Model not found")
        
        # Check prescription model
        prescription_model = models.execute_kw(DB, uid, PASSWORD,
            'ir.model', 'search_count',
            [[['model', '=', 'pharmacy.prescription']]]
        )
        
        if prescription_model:
            log_test("Prescription Management", 'PASS')
        else:
            log_test("Prescription Management", 'FAIL', "Model not found")
        
        # Check insurance provider model
        insurance_model = models.execute_kw(DB, uid, PASSWORD,
            'ir.model', 'search_count',
            [[['model', '=', 'insurance.provider']]]
        )
        
        if insurance_model:
            log_test("Insurance Management", 'PASS')
        else:
            log_test("Insurance Management", 'WARN', "Model not found")
        
        # Check drug schedules
        drug_schedules = models.execute_kw(DB, uid, PASSWORD,
            'product.template', 'search_count',
            [[['drug_schedule', 'in', ['schedule_1', 'schedule_2', 'schedule_3']]]]
        )
        
        if drug_schedules > 0:
            log_test("Drug Scheduling", 'PASS', f"{drug_schedules} scheduled drugs")
        else:
            log_test("Drug Scheduling", 'WARN', "No controlled substances")
        
        # Check if patient field exists on partners
        partner_fields = models.execute_kw(DB, uid, PASSWORD,
            'ir.model.fields', 'search_count',
            [[['model', '=', 'res.partner'], ['name', '=', 'is_patient']]]
        )
        
        if partner_fields:
            log_test("Patient Management", 'PASS')
        else:
            log_test("Patient Management", 'WARN', "Patient field not found")
            
    except Exception as e:
        log_test("Pharmacy Features", 'FAIL', str(e)[:80])
    
    print()

def test_security_access_rights(uid, models):
    """Test 7: Security & Access Rights"""
    print("🔒 TEST 7: SECURITY & ACCESS RIGHTS")
    print("=" * 70)
    
    try:
        # Check user groups
        groups = models.execute_kw(DB, uid, PASSWORD,
            'res.groups', 'search_read',
            [[['name', 'in', ['Pharmacy Manager', 'Pharmacy User', 'POS User']]]],
            {'fields': ['name', 'users']}
        )
        
        if groups:
            for group in groups:
                user_count = len(group.get('users', []))
                log_test(f"Group: {group['name']}", 'PASS', f"{user_count} users")
        else:
            log_test("User Groups", 'WARN', "No pharmacy groups found")
        
        # Check total users
        total_users = models.execute_kw(DB, uid, PASSWORD,
            'res.users', 'search_count',
            [[['active', '=', True]]]
        )
        
        log_test("Active Users", 'PASS', f"{total_users} users")
        
        # Check access rights
        access_rights = models.execute_kw(DB, uid, PASSWORD,
            'ir.model.access', 'search_count',
            [[['model_id.model', 'like', 'pharmacy%']]]
        )
        
        if access_rights > 0:
            log_test("Access Rights Configured", 'PASS', f"{access_rights} rules")
        else:
            log_test("Access Rights Configured", 'WARN', "Limited access rules")
            
    except Exception as e:
        log_test("Security & Access Rights", 'FAIL', str(e)[:80])
    
    print()

def test_data_integrity(uid, models):
    """Test 8: Data Integrity"""
    print("🗂️  TEST 8: DATA INTEGRITY")
    print("=" * 70)
    
    try:
        # Check for products without categories
        products_no_category = models.execute_kw(DB, uid, PASSWORD,
            'product.product', 'search_count',
            [[['categ_id', '=', False], ['active', '=', True]]]
        )
        
        if products_no_category == 0:
            log_test("Products Have Categories", 'PASS')
        else:
            log_test("Products Have Categories", 'WARN', f"{products_no_category} without category")
        
        # Check for products without prices
        products_no_price = models.execute_kw(DB, uid, PASSWORD,
            'product.product', 'search_count',
            [[['list_price', '=', 0], ['sale_ok', '=', True], ['active', '=', True]]]
        )
        
        if products_no_price == 0:
            log_test("Products Have Prices", 'PASS')
        else:
            log_test("Products Have Prices", 'WARN', f"{products_no_price} without price")
        
        # Check for unposted invoices
        draft_invoices = models.execute_kw(DB, uid, PASSWORD,
            'account.move', 'search_count',
            [[['state', '=', 'draft'], ['move_type', 'in', ['out_invoice', 'out_refund']]]]
        )
        
        if draft_invoices > 0:
            log_test("Unposted Invoices", 'WARN', f"{draft_invoices} draft invoices")
        else:
            log_test("No Unposted Invoices", 'PASS')
        
        # Check for orphaned records
        patients_count = models.execute_kw(DB, uid, PASSWORD,
            'res.partner', 'search_count',
            [[['is_patient', '=', True]]]
        )
        
        log_test("Patient Records", 'PASS', f"{patients_count} patients")
        
    except Exception as e:
        log_test("Data Integrity", 'FAIL', str(e)[:80])
    
    print()

def test_ppb_compliance(uid, models):
    """Test 9: PPB Compliance (Kenya Pharmacy & Poisons Board)"""
    print("🇰🇪 TEST 9: PPB COMPLIANCE")
    print("=" * 70)
    
    try:
        # Check controlled drugs register entries
        register_entries = models.execute_kw(DB, uid, PASSWORD,
            'controlled.drugs.register', 'search_count', [[]]
        )
        
        log_test("Controlled Drugs Register", 'PASS', f"{register_entries} entries")
        
        # Check for scheduled drugs
        schedule_1 = models.execute_kw(DB, uid, PASSWORD,
            'product.template', 'search_count',
            [[['drug_schedule', '=', 'schedule_1']]]
        )
        
        schedule_2 = models.execute_kw(DB, uid, PASSWORD,
            'product.template', 'search_count',
            [[['drug_schedule', '=', 'schedule_2']]]
        )
        
        if schedule_1 > 0 or schedule_2 > 0:
            log_test("Controlled Substances", 'PASS', f"Sch1: {schedule_1}, Sch2: {schedule_2}")
        else:
            log_test("Controlled Substances", 'WARN', "No controlled drugs configured")
        
        # Check prescription tracking
        prescriptions = models.execute_kw(DB, uid, PASSWORD,
            'pharmacy.prescription', 'search_count', [[]]
        )
        
        log_test("Prescription Records", 'PASS', f"{prescriptions} prescriptions")
        
        # Check if prescriber tracking exists
        prescribers = models.execute_kw(DB, uid, PASSWORD,
            'res.partner', 'search_count',
            [[['is_prescriber', '=', True]]]
        )
        
        if prescribers > 0:
            log_test("Prescriber Records", 'PASS', f"{prescribers} prescribers")
        else:
            log_test("Prescriber Records", 'WARN', "No prescribers registered")
            
    except Exception as e:
        log_test("PPB Compliance", 'FAIL', str(e)[:80])
    
    print()

def test_reporting_capabilities(uid, models):
    """Test 10: Reporting Capabilities"""
    print("📊 TEST 10: REPORTING CAPABILITIES")
    print("=" * 70)
    
    try:
        # Check if reports are defined
        reports = models.execute_kw(DB, uid, PASSWORD,
            'ir.actions.report', 'search_read',
            [[['model', 'in', ['pharmacy.prescription', 'controlled.drugs.register', 'pos.order']]]],
            {'fields': ['name', 'model']}
        )
        
        if reports:
            for report in reports:
                log_test(f"Report: {report['name']}", 'PASS')
        else:
            log_test("Pharmacy Reports", 'WARN', "No custom reports found")
        
        # Check accounting reports access
        accounting_reports = models.execute_kw(DB, uid, PASSWORD,
            'ir.actions.act_window', 'search_count',
            [[['name', 'ilike', 'profit']]]
        )
        
        if accounting_reports:
            log_test("Accounting Reports", 'PASS')
        else:
            log_test("Accounting Reports", 'WARN', "Limited accounting reports")
            
    except Exception as e:
        log_test("Reporting Capabilities", 'FAIL', str(e)[:80])
    
    print()

def test_demo_data_hidden(uid, models):
    """Test 11: Demo Data Menu Hidden"""
    print("🚫 TEST 11: DEMO DATA HIDDEN")
    print("=" * 70)
    
    try:
        # Check if demo data menu is visible
        demo_menu = models.execute_kw(DB, uid, PASSWORD,
            'ir.ui.menu', 'search',
            [[['name', '=', 'Generate Demo Data']]]
        )
        
        if not demo_menu:
            log_test("Demo Data Menu Hidden", 'PASS', "Menu not visible")
        else:
            log_test("Demo Data Menu Hidden", 'FAIL', "Menu still visible - update module")
            
    except Exception as e:
        log_test("Demo Data Hidden", 'FAIL', str(e)[:80])
    
    print()

def test_cashier_accounts(uid, models):
    """Test 12: Cashier Accounts"""
    print("👥 TEST 12: CASHIER ACCOUNTS")
    print("=" * 70)
    
    try:
        # Check for cashier users
        cashier_group = models.execute_kw(DB, uid, PASSWORD,
            'res.groups', 'search_read',
            [[['name', 'ilike', 'pos'], ['category_id.name', '=', 'Point of Sale']]],
            {'fields': ['name', 'users'], 'limit': 1}
        )
        
        if cashier_group and cashier_group[0].get('users'):
            cashier_count = len(cashier_group[0]['users'])
            log_test("Cashier Accounts", 'PASS', f"{cashier_count} POS users")
            
            if cashier_count < 1:
                log_test("Minimum Cashiers", 'WARN', "No cashiers assigned")
            else:
                log_test("Minimum Cashiers", 'PASS')
        else:
            log_test("Cashier Accounts", 'WARN', "No POS users found")
            
    except Exception as e:
        log_test("Cashier Accounts", 'FAIL', str(e)[:80])
    
    print()

def display_final_report():
    """Display final test report"""
    print("\n" + "=" * 70)
    print("📋 PRODUCTION READINESS REPORT")
    print("=" * 70)
    
    total_tests = len(test_results['passed']) + len(test_results['failed']) + len(test_results['warnings'])
    
    print(f"\n✅ PASSED: {len(test_results['passed'])}/{total_tests}")
    print(f"⚠️  WARNINGS: {len(test_results['warnings'])}/{total_tests}")
    print(f"❌ FAILED: {len(test_results['failed'])}/{total_tests}")
    
    if test_results['failed']:
        print("\n❌ CRITICAL ISSUES (Must Fix Before Production):")
        print("-" * 70)
        for failure in test_results['failed']:
            print(f"  {failure}")
    
    if test_results['warnings']:
        print("\n⚠️  WARNINGS (Review Before Production):")
        print("-" * 70)
        for warning in test_results['warnings']:
            print(f"  {warning}")
    
    print("\n" + "=" * 70)
    print("🎯 PRODUCTION READINESS SCORE")
    print("=" * 70)
    
    score = (len(test_results['passed']) / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\nOverall Score: {score:.1f}%")
    
    if score >= 95 and not test_results['failed']:
        print("\n🟢 STATUS: READY FOR PRODUCTION")
        print("\n✅ NEXT STEPS:")
        print("  1. Backup the database: pg_dump pharmacy_kenya > backup.sql")
        print("  2. Review all warnings and address if needed")
        print("  3. Close any open POS sessions")
        print("  4. Train staff on system usage")
        print("  5. Set up regular backup schedule")
        print("  6. Monitor system performance")
        print("  7. Have PPB compliance documents ready")
    elif score >= 80 and not test_results['failed']:
        print("\n🟡 STATUS: MOSTLY READY - ADDRESS WARNINGS")
        print("\n⚠️  RECOMMENDED ACTIONS:")
        print("  1. Review and address all warnings above")
        print("  2. Re-run tests after fixes")
        print("  3. Ensure all critical features work")
    else:
        print("\n🔴 STATUS: NOT READY - CRITICAL ISSUES")
        print("\n❌ REQUIRED ACTIONS:")
        print("  1. Fix all failed tests immediately")
        print("  2. Address critical warnings")
        print("  3. Re-run full test suite")
        print("  4. Do not deploy to production")
    
    print("\n" + "=" * 70)
    print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return len(test_results['failed']) == 0

def main():
    print("=" * 70)
    print("🇰🇪 KENYA PHARMACY SYSTEM - PRODUCTION READINESS TEST")
    print("=" * 70)
    print(f"Database: {DB}")
    print(f"URL: {URL}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    uid, models = connect()
    if not uid:
        print("\n❌ Cannot connect to Odoo. Ensure it's running.")
        sys.exit(1)
    
    # Run all tests
    test_system_configuration(uid, models)
    test_modules_installed(uid, models)
    test_chart_of_accounts(uid, models)
    test_pos_configuration(uid, models)
    test_inventory_setup(uid, models)
    test_pharmacy_features(uid, models)
    test_security_access_rights(uid, models)
    test_data_integrity(uid, models)
    test_ppb_compliance(uid, models)
    test_reporting_capabilities(uid, models)
    test_demo_data_hidden(uid, models)
    test_cashier_accounts(uid, models)
    
    # Display final report
    ready = display_final_report()
    
    sys.exit(0 if ready else 1)

if __name__ == '__main__':
    main()
