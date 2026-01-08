#!/usr/bin/env python3
"""
Test Controlled Drugs Register - PPB Compliance
Creates test data for controlled substances tracking
"""

import xmlrpc.client
from datetime import datetime, timedelta
import random

# Configuration
URL = "http://localhost:8069"
DB = "pharmacy_kenya"
USERNAME = "admin"
PASSWORD = "admin"

def connect():
    """Connect to Odoo"""
    print("🔌 Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        print("❌ Authentication failed!")
        return None, None
    print(f"✓ Connected (UID: {uid})")
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    return uid, models

def create_controlled_drugs(uid, models):
    """Create controlled drug products"""
    print("\n💊 Creating Controlled Drug Products...")
    
    controlled_drugs = [
        {
            'name': 'Morphine Sulphate 10mg Tablets',
            'drug_generic_name': 'Morphine Sulphate',
            'drug_strength': '10mg',
            'drug_schedule': 'schedule_1',  # Most restricted
            'ppb_registration_number': 'PPB/KE/2023/001',
            'list_price': 150.00,
            'type': 'consu',
            'available_in_pos': True,
        },
        {
            'name': 'Pethidine Injection 50mg/ml',
            'drug_generic_name': 'Pethidine HCL',
            'drug_strength': '50mg/ml',
            'drug_schedule': 'schedule_1',
            'ppb_registration_number': 'PPB/KE/2023/002',
            'list_price': 200.00,
            'type': 'consu',
            'available_in_pos': True,
        },
        {
            'name': 'Diazepam 10mg Tablets',
            'drug_generic_name': 'Diazepam',
            'drug_strength': '10mg',
            'drug_schedule': 'schedule_2',
            'ppb_registration_number': 'PPB/KE/2023/003',
            'list_price': 50.00,
            'type': 'consu',
            'available_in_pos': True,
        },
        {
            'name': 'Tramadol 50mg Capsules',
            'drug_generic_name': 'Tramadol HCL',
            'drug_strength': '50mg',
            'drug_schedule': 'schedule_2',
            'ppb_registration_number': 'PPB/KE/2023/004',
            'list_price': 80.00,
            'type': 'consu',
            'available_in_pos': True,
        },
        {
            'name': 'Codeine Phosphate 30mg Tablets',
            'drug_generic_name': 'Codeine Phosphate',
            'drug_strength': '30mg',
            'drug_schedule': 'schedule_2',
            'ppb_registration_number': 'PPB/KE/2023/005',
            'list_price': 60.00,
            'type': 'consu',
            'available_in_pos': True,
        }
    ]
    
    products = []
    for drug_data in controlled_drugs:
        # Check if exists
        existing = models.execute_kw(DB, uid, PASSWORD,
            'product.template', 'search',
            [[['name', '=', drug_data['name']]]]
        )
        
        if existing:
            print(f"  ⚠️  {drug_data['name']} already exists")
            products.append(existing[0])
        else:
            product_id = models.execute_kw(DB, uid, PASSWORD,
                'product.template', 'create',
                [drug_data]
            )
            products.append(product_id)
            print(f"  ✓ Created {drug_data['name']} (Schedule {drug_data['drug_schedule']})")
    
    return products

def create_register_entries(uid, models):
    """Create Controlled Drugs Register entries"""
    print("\n📋 Creating Controlled Drugs Register Entries...")
    
    # Get controlled drug products
    controlled_products = models.execute_kw(DB, uid, PASSWORD,
        'product.product', 'search_read',
        [[['is_controlled_substance', '=', True]]],
        {'fields': ['id', 'name', 'display_name']}
    )
    
    if not controlled_products:
        print("❌ No controlled drugs found!")
        return []
    
    print(f"  Found {len(controlled_products)} controlled drug(s)")
    
    # Get some patients and prescribers
    patients = models.execute_kw(DB, uid, PASSWORD,
        'res.partner', 'search_read',
        [[['is_patient', '=', True]]],
        {'fields': ['id', 'name', 'patient_id_number'], 'limit': 5}
    )
    
    prescribers = models.execute_kw(DB, uid, PASSWORD,
        'res.partner', 'search_read',
        [[['is_prescriber', '=', True]]],
        {'fields': ['id', 'name', 'prescriber_license_number'], 'limit': 3}
    )
    
    # Get admin user
    admin_user = models.execute_kw(DB, uid, PASSWORD,
        'res.users', 'search',
        [[['login', '=', 'admin']]]
    )[0]
    
    # Get another user for witnessing (or create one)
    all_users = models.execute_kw(DB, uid, PASSWORD,
        'res.users', 'search',
        [[['id', '!=', admin_user]]], {'limit': 1}
    )
    
    witness_user = all_users[0] if all_users else admin_user
    
    # Create supplier if doesn't exist
    supplier_id = models.execute_kw(DB, uid, PASSWORD,
        'res.partner', 'search',
        [[['name', '=', 'Pharma Distributors Ltd']]]
    )
    
    if not supplier_id:
        supplier_id = models.execute_kw(DB, uid, PASSWORD,
            'res.partner', 'create',
            [{
                'name': 'Pharma Distributors Ltd',
                'is_company': True,
                'supplier_rank': 1,
            }]
        )
    else:
        supplier_id = supplier_id[0]
    
    entries = []
    entry_count = 0
    
    # For each controlled drug, create a series of transactions
    for product in controlled_products[:3]:  # Test with first 3 products
        print(f"\n  📦 Processing: {product['display_name']}")
        
        # 1. Initial Receipt/Purchase
        base_date = datetime.now() - timedelta(days=30)
        receipt_data = {
            'date': base_date.strftime('%Y-%m-%d %H:%M:%S'),
            'product_id': product['id'],
            'transaction_type': 'receipt',
            'quantity_received': 500.0,
            'quantity_dispensed': 0.0,
            'supplier_id': supplier_id,
            'invoice_ref': f'INV-{random.randint(1000, 9999)}',
            'authorized_by': admin_user,
            'remarks': 'Initial stock purchase from authorized distributor'
        }
        
        entry_id = models.execute_kw(DB, uid, PASSWORD,
            'controlled.drugs.register', 'create',
            [receipt_data]
        )
        entries.append(entry_id)
        entry_count += 1
        print(f"    ✓ Receipt: 500 units received")
        
        # 2. Multiple Dispensing Transactions
        running_qty = 500.0
        for i in range(5):
            if patients and prescribers:
                patient = random.choice(patients)
                prescriber = random.choice(prescribers)
                qty = random.randint(10, 50)
                
                dispensing_date = base_date + timedelta(days=i*5 + random.randint(1, 3))
                
                dispensing_data = {
                    'date': dispensing_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'product_id': product['id'],
                    'transaction_type': 'dispensing',
                    'quantity_received': 0.0,
                    'quantity_dispensed': float(qty),
                    'patient_name': patient['name'],
                    'patient_id_number': patient.get('patient_id_number', 'N/A'),
                    'prescriber_name': prescriber['name'],
                    'prescriber_license': prescriber.get('prescriber_license_number', 'N/A'),
                    'authorized_by': admin_user,
                    'remarks': f'Dispensed as per prescription'
                }
                
                entry_id = models.execute_kw(DB, uid, PASSWORD,
                    'controlled.drugs.register', 'create',
                    [dispensing_data]
                )
                entries.append(entry_id)
                entry_count += 1
                running_qty -= qty
                print(f"    ✓ Dispensing #{i+1}: {qty} units to {patient['name']}")
        
        # 3. Stock Adjustment (if needed) - negative adjustment for damages
        if random.random() > 0.5:
            adjustment_date = base_date + timedelta(days=28)
            adjustment_data = {
                'date': adjustment_date.strftime('%Y-%m-%d %H:%M:%S'),
                'product_id': product['id'],
                'transaction_type': 'destruction',
                'quantity_received': 0.0,
                'quantity_dispensed': random.randint(1, 5),
                'authorized_by': admin_user,
                'witnessed_by': witness_user,  # Required for destruction - must be different person
                'remarks': 'Damaged stock - expired tablets destroyed as per PPB guidelines'
            }
            
            entry_id = models.execute_kw(DB, uid, PASSWORD,
                'controlled.drugs.register', 'create',
                [adjustment_data]
            )
            entries.append(entry_id)
            entry_count += 1
            print(f"    ✓ Destruction: Stock destroyed (PPB compliance)")
    
    print(f"\n  ✅ Created {entry_count} register entries")
    return entries

def display_summary(uid, models):
    """Display summary of controlled drugs register"""
    print("\n" + "="*60)
    print("📊 CONTROLLED DRUGS REGISTER SUMMARY")
    print("="*60)
    
    # Count by transaction type
    transaction_types = [
        ('receipt', 'Receipts/Purchases'),
        ('dispensing', 'Dispensing'),
        ('adjustment', 'Adjustments'),
        ('destruction', 'Destruction'),
    ]
    
    print("\n📈 Transaction Types:")
    for code, name in transaction_types:
        count = models.execute_kw(DB, uid, PASSWORD,
            'controlled.drugs.register', 'search_count',
            [[['transaction_type', '=', code]]]
        )
        if count > 0:
            print(f"  • {name:20} : {count:3} transactions")
    
    # Count by drug schedule
    print("\n💊 By Drug Schedule:")
    schedules = [
        ('schedule_1', 'Schedule 1 (Most Restricted)'),
        ('schedule_2', 'Schedule 2'),
        ('schedule_3', 'Schedule 3'),
    ]
    
    for code, name in schedules:
        count = models.execute_kw(DB, uid, PASSWORD,
            'controlled.drugs.register', 'search_count',
            [[['drug_schedule', '=', code]]]
        )
        if count > 0:
            print(f"  • {name:35} : {count:3} entries")
    
    # Get products with balance
    print("\n📦 Current Stock Balances:")
    controlled_products = models.execute_kw(DB, uid, PASSWORD,
        'product.product', 'search_read',
        [[['is_controlled_substance', '=', True]]],
        {'fields': ['id', 'display_name'], 'limit': 10}
    )
    
    for product in controlled_products:
        # Get latest entry for this product
        latest = models.execute_kw(DB, uid, PASSWORD,
            'controlled.drugs.register', 'search_read',
            [[['product_id', '=', product['id']]]],
            {'fields': ['running_balance'], 'limit': 1, 'order': 'date desc'}
        )
        
        if latest:
            balance = latest[0]['running_balance']
            print(f"  • {product['display_name']:40} : {balance:6.0f} units")
    
    # Total entries
    total = models.execute_kw(DB, uid, PASSWORD,
        'controlled.drugs.register', 'search_count',
        [[]]
    )
    
    print("\n" + "="*60)
    print(f"📋 Total Register Entries: {total}")
    print("="*60)
    
    print("\n✅ CONTROLLED DRUGS REGISTER TEST COMPLETED!")
    print("\n📌 Next Steps:")
    print("  1. Go to Pharmacy > Controlled Drugs Register")
    print("  2. View all transactions with running balances")
    print("  3. Generate PPB compliance reports")
    print("  4. Verify audit trail for each controlled substance")

def main():
    print("="*60)
    print("🇰🇪 CONTROLLED DRUGS REGISTER - PPB COMPLIANCE TEST")
    print("="*60)
    
    uid, models = connect()
    if not uid:
        return
    
    # Create controlled drug products
    create_controlled_drugs(uid, models)
    
    # Create register entries
    create_register_entries(uid, models)
    
    # Display summary
    display_summary(uid, models)

if __name__ == '__main__':
    main()
