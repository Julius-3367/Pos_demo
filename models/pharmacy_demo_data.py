# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PharmacyDemoData(models.TransientModel):
    _name = 'pharmacy.demo.data'
    _description = 'Generate Demo Data with Kenyan Names'
    
    def action_generate_demo_data(self):
        """Generate comprehensive demo data with Kenyan names"""
        _logger.info("Starting demo data generation with Kenyan names...")
        
        # Create Patients
        patients = self._create_patients()
        _logger.info(f"Created {len(patients)} patients")
        
        # Create Prescribers
        prescribers = self._create_prescribers()
        _logger.info(f"Created {len(prescribers)} prescribers")
        
        # Create Pharmaceutical Products
        products = self._create_products()
        _logger.info(f"Created {len(products)} products")
        
        # Create Product Lots with Expiry Dates
# #        lots = self._create_lots(products)
#         _logger.info(f"Created {len(lots)} lots/batches")
        
        # Create Prescriptions
        prescriptions = self._create_prescriptions(patients, prescribers, products)
        _logger.info(f"Created {len(prescriptions)} prescriptions")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Demo Data Created',
                'message': f'Successfully created demo data: {len(patients)} patients, {len(prescribers)} doctors, {len(products)} products, {len(prescriptions)} prescriptions',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _create_patients(self):
        """Create patient records with Kenyan names"""
        Partner = self.env['res.partner']
        
        patients_data = [
            {
                'name': 'Wanjiku Kamau',
                'is_patient': True,
                'patient_id_number': '28456789',
                'date_of_birth': '1985-03-15',
                'gender': 'female',
                'blood_group': 'o_positive',
                'phone': '0712345678',
                'email': 'wanjiku.kamau@example.com',
                'allergies': 'Penicillin',
                'medical_conditions': 'Hypertension',
                'insurance_provider_id': self.env.ref('pos_demo.insurance_provider_nhif', raise_if_not_found=False).id,
                'insurance_member_number': 'NHIF001234',
            },
            {
                'name': 'Kipchoge Rotich',
                'is_patient': True,
                'patient_id_number': '31245678',
                'date_of_birth': '1978-07-22',
                'gender': 'male',
                'blood_group': 'a_positive',
                'phone': '0723456789',
                'email': 'kipchoge.rotich@example.com',
                'allergies': 'Sulfa drugs',
                'medical_conditions': 'Type 2 Diabetes',
                'insurance_provider_id': self.env.ref('pos_demo.insurance_provider_aar', raise_if_not_found=False).id,
                'insurance_member_number': 'AAR567890',
            },
            {
                'name': 'Amina Hassan',
                'is_patient': True,
                'patient_id_number': '29876543',
                'date_of_birth': '1992-11-30',
                'gender': 'female',
                'blood_group': 'b_positive',
                'phone': '0734567890',
                'email': 'amina.hassan@example.com',
                'allergies': '',
                'medical_conditions': '',
                'insurance_provider_id': self.env.ref('pos_demo.insurance_provider_britam', raise_if_not_found=False).id,
                'insurance_member_number': 'BRT123456',
            },
            {
                'name': 'Omondi Otieno',
                'is_patient': True,
                'patient_id_number': '27654321',
                'date_of_birth': '1988-05-18',
                'gender': 'male',
                'blood_group': 'ab_positive',
                'phone': '0745678901',
                'email': 'omondi.otieno@example.com',
                'allergies': 'Aspirin',
                'medical_conditions': 'Asthma',
            },
            {
                'name': 'Chebet Koech',
                'is_patient': True,
                'patient_id_number': '30123456',
                'date_of_birth': '1995-09-10',
                'gender': 'female',
                'blood_group': 'o_negative',
                'phone': '0756789012',
                'email': 'chebet.koech@example.com',
                'allergies': '',
                'medical_conditions': '',
            },
            {
                'name': 'Mwangi Njoroge',
                'is_patient': True,
                'patient_id_number': '26789012',
                'date_of_birth': '1980-02-28',
                'gender': 'male',
                'blood_group': 'a_negative',
                'phone': '0767890123',
                'email': 'mwangi.njoroge@example.com',
                'medical_conditions': 'High Cholesterol',
            },
        ]
        
        patients = []
        for data in patients_data:
            patient = Partner.create(data)
            patients.append(patient)
        
        return patients
    
    def _create_prescribers(self):
        """Create prescriber/doctor records with Kenyan names"""
        Partner = self.env['res.partner']
        
        prescribers_data = [
            {
                'name': 'Dr. James Muthoni',
                'is_prescriber': True,
                'prescriber_license_number': 'KMPDB/2015/12345',
                'prescriber_specialty': 'General Practitioner',
                'phone': '0701234567',
                'email': 'dr.muthoni@hospital.co.ke',
            },
            {
                'name': 'Dr. Sarah Wambui',
                'is_prescriber': True,
                'prescriber_license_number': 'KMPDB/2018/23456',
                'prescriber_specialty': 'Internal Medicine',
                'phone': '0702345678',
                'email': 'dr.wambui@hospital.co.ke',
            },
            {
                'name': 'Dr. Peter Kiplagat',
                'is_prescriber': True,
                'prescriber_license_number': 'KMPDB/2012/34567',
                'prescriber_specialty': 'Pediatrician',
                'phone': '0703456789',
                'email': 'dr.kiplagat@hospital.co.ke',
            },
            {
                'name': 'Dr. Grace Akinyi',
                'is_prescriber': True,
                'prescriber_license_number': 'KMPDB/2020/45678',
                'prescriber_specialty': 'Family Medicine',
                'phone': '0704567890',
                'email': 'dr.akinyi@hospital.co.ke',
            },
        ]
        
        prescribers = []
        for data in prescribers_data:
            prescriber = Partner.create(data)
            prescribers.append(prescriber)
        
        return prescribers
    
    def _create_products(self):
        """Create pharmaceutical products"""
        Product = self.env['product.product']
        
        products_data = [
            {
                'name': 'Panadol 500mg Tablets',
                'is_pharmaceutical': True,
                'drug_generic_name': 'Paracetamol',
                'drug_strength': '500mg',
                'drug_dosage_form': 'tablet',
                'drug_schedule': 'otc',
                'therapeutic_class': 'Analgesic/Antipyretic',
                'list_price': 50.00,
                'standard_price': 30.00,
                
                'tracking': 'lot',
                'active_ingredients': 'Paracetamol 500mg',
            },
            {
                'name': 'Amoxil 250mg Capsules',
                'is_pharmaceutical': True,
                'drug_generic_name': 'Amoxicillin',
                'drug_strength': '250mg',
                'drug_dosage_form': 'capsule',
                'drug_schedule': 'prescription',
                'therapeutic_class': 'Antibiotic - Penicillin',
                'list_price': 150.00,
                'standard_price': 90.00,
                
                'tracking': 'lot',
                'active_ingredients': 'Amoxicillin Trihydrate 250mg',
                'contraindications': 'Penicillin allergy',
            },
            {
                'name': 'Metformin 500mg Tablets',
                'is_pharmaceutical': True,
                'drug_generic_name': 'Metformin',
                'drug_strength': '500mg',
                'drug_dosage_form': 'tablet',
                'drug_schedule': 'prescription',
                'therapeutic_class': 'Antidiabetic',
                'list_price': 80.00,
                'standard_price': 50.00,
                
                'tracking': 'lot',
                'active_ingredients': 'Metformin Hydrochloride 500mg',
            },
            {
                'name': 'Amlodipine 5mg Tablets',
                'is_pharmaceutical': True,
                'drug_generic_name': 'Amlodipine',
                'drug_strength': '5mg',
                'drug_dosage_form': 'tablet',
                'drug_schedule': 'prescription',
                'therapeutic_class': 'Antihypertensive - Calcium Channel Blocker',
                'list_price': 120.00,
                'standard_price': 75.00,
                
                'tracking': 'lot',
                'active_ingredients': 'Amlodipine Besylate 5mg',
            },
            {
                'name': 'Tramadol 50mg Capsules',
                'is_pharmaceutical': True,
                'drug_generic_name': 'Tramadol',
                'drug_strength': '50mg',
                'drug_dosage_form': 'capsule',
                'drug_schedule': 'schedule_2',
                'therapeutic_class': 'Opioid Analgesic',
                'list_price': 200.00,
                'standard_price': 120.00,
                
                'tracking': 'lot',
                'active_ingredients': 'Tramadol Hydrochloride 50mg',
                'contraindications': 'Respiratory depression, acute intoxication',
            },
            {
                'name': 'Cetrizine 10mg Tablets',
                'is_pharmaceutical': True,
                'drug_generic_name': 'Cetirizine',
                'drug_strength': '10mg',
                'drug_dosage_form': 'tablet',
                'drug_schedule': 'pharmacy',
                'therapeutic_class': 'Antihistamine',
                'list_price': 60.00,
                'standard_price': 35.00,
                
                'tracking': 'lot',
                'active_ingredients': 'Cetirizine Hydrochloride 10mg',
            },
        ]
        
        products = []
        for data in products_data:
            product = Product.create(data)
            products.append(product)
        
        return products
    
#    def _create_lots(self, products):
        """Create lots/batches with expiry dates"""
        from datetime import datetime, timedelta
        StockLot = self.env['stock.lot']
        
        lots = []
        for product in products:
            # Create 2-3 lots per product with different expiry dates
            for i in range(2):
                # Some expiring soon, some normal
                days_to_expiry = 365 if i == 0 else 150  # First lot normal, second expiring soon
                
                lot_data = {
                    'name': f'LOT-{product.id}-{i+1:03d}',
                    'product_id': product.id,
                    'company_id': self.env.company.id,
                    'batch_number': f'BATCH{product.id}{i+1:02d}2025',
                    'manufacturing_date': datetime.now() - timedelta(days=180),
                    'expiry_date': datetime.now() + timedelta(days=days_to_expiry),
                    'purchase_price': product.standard_price,
                }
                lot = StockLot.create(lot_data)
                lots.append(lot)
                
                # Create stock for this lot
                self._create_stock_for_lot(product, lot, quantity=100)
        
        return lots
    
    def _create_stock_for_lot(self, product, lot, quantity):
        """Create stock quant for a lot"""
        StockQuant = self.env['stock.quant']
        location = self.env.ref('stock.stock_location_stock')
        
        StockQuant.create({
            'product_id': product.id,
            'location_id': location.id,
            'lot_id': lot.id,
            'quantity': quantity,
        })
    
    def _create_prescriptions(self, patients, prescribers, products):
        """Create sample prescriptions"""
        Prescription = self.env['pharmacy.prescription']
        from datetime import datetime, timedelta
        
        prescriptions_data = [
            {
                'patient_id': patients[0].id,  # Wanjiku Kamau
                'prescriber_id': prescribers[0].id,  # Dr. Muthoni
                'diagnosis': 'Upper Respiratory Tract Infection',
                'line_ids': [
                    (0, 0, {
                        'product_id': products[1].id,  # Amoxil
                        'quantity': 21,
                        'dosage': '250mg',
                        'frequency': 'Three times daily',
                        'duration': '7 days',
                        'route': 'oral',
                        'instructions': 'Take after meals',
                    }),
                    (0, 0, {
                        'product_id': products[0].id,  # Panadol
                        'quantity': 12,
                        'dosage': '500mg',
                        'frequency': 'Every 6 hours as needed',
                        'duration': '3 days',
                        'route': 'oral',
                        'instructions': 'For fever and pain',
                    }),
                ],
            },
            {
                'patient_id': patients[1].id,  # Kipchoge Rotich
                'prescriber_id': prescribers[1].id,  # Dr. Wambui
                'diagnosis': 'Type 2 Diabetes Mellitus',
                'line_ids': [
                    (0, 0, {
                        'product_id': products[2].id,  # Metformin
                        'quantity': 60,
                        'dosage': '500mg',
                        'frequency': 'Twice daily',
                        'duration': '30 days',
                        'route': 'oral',
                        'instructions': 'Take with meals',
                    }),
                ],
            },
            {
                'patient_id': patients[0].id,  # Wanjiku Kamau (hypertension)
                'prescriber_id': prescribers[0].id,
                'diagnosis': 'Essential Hypertension',
                'line_ids': [
                    (0, 0, {
                        'product_id': products[3].id,  # Amlodipine
                        'quantity': 30,
                        'dosage': '5mg',
                        'frequency': 'Once daily',
                        'duration': '30 days',
                        'route': 'oral',
                        'instructions': 'Take in the morning',
                    }),
                ],
            },
            {
                'patient_id': patients[3].id,  # Omondi Otieno
                'prescriber_id': prescribers[2].id,  # Dr. Kiplagat
                'diagnosis': 'Chronic Back Pain',
                'special_instructions': 'Controlled substance - verify ID',
                'line_ids': [
                    (0, 0, {
                        'product_id': products[4].id,  # Tramadol
                        'quantity': 20,
                        'dosage': '50mg',
                        'frequency': 'Twice daily',
                        'duration': '10 days',
                        'route': 'oral',
                        'instructions': 'Do not exceed prescribed dose',
                    }),
                ],
            },
            {
                'patient_id': patients[2].id,  # Amina Hassan
                'prescriber_id': prescribers[3].id,  # Dr. Akinyi
                'diagnosis': 'Allergic Rhinitis',
                'line_ids': [
                    (0, 0, {
                        'product_id': products[5].id,  # Cetirizine
                        'quantity': 30,
                        'dosage': '10mg',
                        'frequency': 'Once daily at bedtime',
                        'duration': '30 days',
                        'route': 'oral',
                        'instructions': 'May cause drowsiness',
                    }),
                ],
            },
        ]
        
        prescriptions = []
        for data in prescriptions_data:
            prescription = Prescription.create(data)
            prescriptions.append(prescription)
        
        return prescriptions
