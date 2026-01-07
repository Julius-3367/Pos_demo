#!/usr/bin/env python3
"""
Pharmacy POS Demo - Complete Test Script for Kenya
This script performs a complete end-to-end test with Kenyan names
"""

import xmlrpc.client
import random
from datetime import datetime, timedelta

# Odoo Connection Settings
URL = 'http://localhost:8069'
DB = 'pharmacy_kenya'
USERNAME = 'admin'
PASSWORD = 'admin'

# Kenyan Names for Testing
KENYAN_FIRST_NAMES = ['Wanjiku', 'Kamau', 'Njeri', 'Ochieng', 'Akinyi', 'Mwangi', 'Wambui', 'Otieno', 'Chebet', 'Kipchoge']
KENYAN_LAST_NAMES = ['Kariuki', 'Odhiambo', 'Kimani', 'Maina', 'Njoroge', 'Wanjiru', 'Onyango', 'Mutua', 'Wafula', 'Koech']
KENYAN_PRESCRIBERS = ['Dr. James Mwangi', 'Dr. Grace Wanjiru', 'Dr. Peter Ochieng', 'Dr. Mary Akinyi']

def connect():
    """Connect to Odoo"""
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        raise Exception("Failed to authenticate")
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    return uid, models

def execute_kw(models, uid, model, method, args, kwargs=None):
    """Execute Odoo method"""
    if kwargs is None:
        kwargs = {}
    return models.execute_kw(DB, uid, PASSWORD, model, method, args, kwargs)

def create_patients(models, uid, count=10):
    """Create Kenyan patients"""
    print(f"\n🏥 Creating {count} Kenyan Patients...")
    patient_ids = []
    
    for i in range(count):
        first_name = random.choice(KENYAN_FIRST_NAMES)
        last_name = random.choice(KENYAN_LAST_NAMES)
        name = f"{first_name} {last_name}"
        
        patient_data = {
            'name': name,
            'is_patient': True,
            'phone': f"+254{random.randint(700000000, 799999999)}",
            'email': f"{first_name.lower()}.{last_name.lower()}@example.co.ke",
            'street': f"{random.randint(1, 100)} Kenyatta Avenue",
            'city': random.choice(['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']),
            'country_id': execute_kw(models, uid, 'res.country', 'search', [[('code', '=', 'KE')]])[0],
        }
        
        patient_id = execute_kw(models, uid, 'res.partner', 'create', [patient_data])
        patient_ids.append(patient_id)
        print(f"  ✓ Created patient: {name} (ID: {patient_id})")
    
    return patient_ids

def create_prescribers(models, uid):
    """Create Kenyan prescribers (doctors)"""
    print("\n👨‍⚕️ Creating Kenyan Prescribers...")
    prescriber_ids = []
    
    for doctor_name in KENYAN_PRESCRIBERS:
        prescriber_data = {
            'name': doctor_name,
            'is_prescriber': True,
            'prescriber_license_number': f"KMC/{random.randint(10000, 99999)}",
            'phone': f"+254{random.randint(700000000, 799999999)}",
            'email': f"{doctor_name.split()[1].lower()}@hospital.co.ke",
        }
        
        prescriber_id = execute_kw(models, uid, 'res.partner', 'create', [prescriber_data])
        prescriber_ids.append(prescriber_id)
        print(f"  ✓ Created prescriber: {doctor_name} (License: {prescriber_data['prescriber_license_number']})")
    
    return prescriber_ids

def create_prescriptions(models, uid, patient_ids, prescriber_ids, count=5):
    """Create prescriptions with Kenyan patient and prescriber names"""
    print(f"\n📋 Creating {count} Prescriptions...")
    prescription_ids = []
    
    # Get some products
    product_ids = execute_kw(models, uid, 'product.product', 'search', [[('available_in_pos', '=', True)]], {'limit': 10})
    
    for i in range(count):
        patient_id = random.choice(patient_ids)
        prescriber_id = random.choice(prescriber_ids)
        
        prescription_data = {
            'patient_id': patient_id,
            'prescriber_id': prescriber_id,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        prescription_id = execute_kw(models, uid, 'pharmacy.prescription', 'create', [prescription_data])
        
        # Add prescription lines
        for j in range(random.randint(1, 3)):
            if product_ids:
                product_id = random.choice(product_ids)
                line_data = {
                    'prescription_id': prescription_id,
                    'product_id': product_id,
                    'quantity': random.randint(1, 3),
                    'dosage': f"{random.choice([250, 500, 1000])}mg",
                    'frequency': random.choice(['Once daily', 'Twice daily', 'Three times daily']),
                    'duration': random.choice(['5 days', '7 days', '10 days', '14 days']),
                }
                execute_kw(models, uid, 'pharmacy.prescription.line', 'create', [line_data])
        
        prescription_ids.append(prescription_id)
        patient_name = execute_kw(models, uid, 'res.partner', 'read', [patient_id], {'fields': ['name']})[0]['name']
        prescriber_name = execute_kw(models, uid, 'res.partner', 'read', [prescriber_id], {'fields': ['name']})[0]['name']
        print(f"  ✓ Created prescription for {patient_name} by {prescriber_name}")
    
    return prescription_ids

def create_insurance_claims(models, uid, patient_ids, count=3):
    """Create insurance claims"""
    print(f"\n🏥 Creating {count} Insurance Claims...")
    claim_ids = []
    
    # Get insurance providers
    provider_ids = execute_kw(models, uid, 'insurance.provider', 'search', [[]])
    if not provider_ids:
        print("  ⚠️ No insurance providers found. Skipping insurance claims.")
        return claim_ids
    
    for i in range(count):
        patient_id = random.choice(patient_ids)
        provider_id = random.choice(provider_ids)
        
        claim_data = {
            'patient_id': patient_id,
            'insurance_provider_id': provider_id,
            'member_number': f"MEM{random.randint(100000, 999999)}",
            'date': datetime.now().strftime('%Y-%m-%d'),
        }
        
        claim_id = execute_kw(models, uid, 'insurance.claim', 'create', [claim_data])
        claim_ids.append(claim_id)
        
        patient_name = execute_kw(models, uid, 'res.partner', 'read', [patient_id], {'fields': ['name']})[0]['name']
        provider_name = execute_kw(models, uid, 'insurance.provider', 'read', [provider_id], {'fields': ['name']})[0]['name']
        print(f"  ✓ Created claim for {patient_name} with {provider_name}")
    
    return claim_ids

def print_summary(models, uid):
    """Print summary of created data"""
    print("\n" + "="*60)
    print("📊 PHARMACY POS DEMO - DATA SUMMARY")
    print("="*60)
    
    patient_count = execute_kw(models, uid, 'res.partner', 'search_count', [[('is_patient', '=', True)]])
    prescriber_count = execute_kw(models, uid, 'res.partner', 'search_count', [[('is_prescriber', '=', True)]])
    prescription_count = execute_kw(models, uid, 'pharmacy.prescription', 'search_count', [[]])
    insurance_count = execute_kw(models, uid, 'insurance.claim', 'search_count', [[]])
    product_count = execute_kw(models, uid, 'product.product', 'search_count', [[('available_in_pos', '=', True)]])
    
    print(f"👥 Patients:        {patient_count}")
    print(f"👨‍⚕️ Prescribers:     {prescriber_count}")
    print(f"📋 Prescriptions:   {prescription_count}")
    print(f"🏥 Insurance Claims: {insurance_count}")
    print(f"💊 Products:        {product_count}")
    print("="*60)
    
    # Print some sample patients
    print("\n📋 Sample Patients:")
    patients = execute_kw(models, uid, 'res.partner', 'search_read', 
                         [[('is_patient', '=', True)]], 
                         {'fields': ['name', 'phone', 'city'], 'limit': 5})
    for patient in patients:
        print(f"  • {patient['name']:20} | {patient.get('phone', 'N/A'):15} | {patient.get('city', 'N/A')}")
    
    # Print sample prescribers
    print("\n👨‍⚕️ Sample Prescribers:")
    prescribers = execute_kw(models, uid, 'res.partner', 'search_read', 
                            [[('is_prescriber', '=', True)]], 
                            {'fields': ['name', 'prescriber_license_number']})
    for prescriber in prescribers:
        print(f"  • {prescriber['name']:20} | License: {prescriber.get('prescriber_license_number', 'N/A')}")
    
    # Print insurance providers
    print("\n🏥 Insurance Providers:")
    providers = execute_kw(models, uid, 'insurance.provider', 'search_read', 
                          [[]], 
                          {'fields': ['name', 'code']})
    for provider in providers:
        print(f"  • {provider['name']:25} | Code: {provider.get('code', 'N/A')}")

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🇰🇪 PHARMACY POS DEMO - KENYA TEST DATA GENERATOR")
    print("="*60)
    print(f"Database: {DB}")
    print(f"URL: {URL}")
    
    try:
        # Connect to Odoo
        print("\n🔌 Connecting to Odoo...")
        uid, models = connect()
        print(f"✓ Connected successfully (UID: {uid})")
        
        # Setup admin permissions
        print("\n🔑 Setting up admin permissions...")
        try:
            # Get the Pharmacy Manager group
            manager_group = execute_kw(models, uid, 'ir.model.data', 'search_read',
                                        [[['name', '=', 'group_pharmacy_manager'], ['module', '=', 'pos_demo']]],
                                        {'fields': ['res_id']})
            
            if manager_group:
                group_id = manager_group[0]['res_id']
                # Get admin user
                admin_user_id = execute_kw(models, uid, 'res.users', 'search', [[['login', '=', 'admin']]])[0]
                # Add admin to Pharmacy Manager group
                execute_kw(models, uid, 'res.users', 'write', [[admin_user_id], {'groups_id': [(4, group_id)]}])
                print(f"  ✓ Added admin to Pharmacy Manager group")
            else:
                print("  ⚠ Pharmacy Manager group not found")
        except Exception as e:
            print(f"  ⚠ Could not set permissions: {e}")
        
        # Create test data
        patient_ids = create_patients(models, uid, count=15)
        prescriber_ids = create_prescribers(models, uid)
        prescription_ids = create_prescriptions(models, uid, patient_ids, prescriber_ids, count=10)
        claim_ids = create_insurance_claims(models, uid, patient_ids, count=5)
        
        # Print summary
        print_summary(models, uid)
        
        print("\n✅ TEST DATA GENERATION COMPLETED SUCCESSFULLY!")
        print("\n📌 Next Steps:")
        print("  1. Login to http://localhost:8069 with admin/admin")
        print("  2. Go to Pharmacy menu to view created data")
        print("  3. Set up Chart of Accounts (Accounting > Configuration > Chart of Accounts)")
        print("  4. Create a POS Configuration (Point of Sale > Configuration > Point of Sale)")
        print("  5. Open POS session and test the pharmacy features")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
