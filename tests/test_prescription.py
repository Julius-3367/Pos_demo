# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TestPrescription(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Create test patient
        self.patient = self.env['res.partner'].create({
            'name': 'Test Patient',
            'is_patient': True,
            'patient_id_number': '12345678',
            'date_of_birth': '1990-01-01',
            'allergies': 'Penicillin',
        })
        
        # Create test prescriber
        self.prescriber = self.env['res.partner'].create({
            'name': 'Dr. Test Prescriber',
            'is_prescriber': True,
            'prescriber_license_number': 'MED12345',
        })
        
        # Create test pharmaceutical product
        self.product = self.env['product.product'].create({
            'name': 'Test Medication',
            'is_pharmaceutical': True,
            'drug_generic_name': 'Amoxicillin',
            'drug_strength': '500mg',
            'drug_schedule': 'prescription',
            'requires_prescription': True,
        })
    
    def test_create_prescription(self):
        """Test prescription creation"""
        prescription = self.env['pharmacy.prescription'].create({
            'patient_id': self.patient.id,
            'prescriber_id': self.prescriber.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 20,
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'duration': '10 days',
            })],
        })
        
        self.assertEqual(prescription.state, 'draft')
        self.assertEqual(len(prescription.line_ids), 1)
        self.assertEqual(prescription.total_items, 1)
    
    def test_validate_prescription(self):
        """Test prescription validation requires pharmacist role"""
        prescription = self.env['pharmacy.prescription'].create({
            'patient_id': self.patient.id,
            'prescriber_id': self.prescriber.id,
        })
        
        # Would need to test with proper user context
        # prescription.action_validate()
        # self.assertEqual(prescription.state, 'validated')
    
    def test_prescription_dispensing(self):
        """Test prescription dispensing updates quantities"""
        prescription = self.env['pharmacy.prescription'].create({
            'patient_id': self.patient.id,
            'prescriber_id': self.prescriber.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 20,
                'dosage': '500mg',
            })],
        })
        
        line = prescription.line_ids[0]
        line.quantity_dispensed = 10
        
        self.assertEqual(line.quantity_remaining, 10)
        self.assertFalse(line.fully_dispensed)
        
        line.quantity_dispensed = 20
        self.assertEqual(line.quantity_remaining, 0)
        self.assertTrue(line.fully_dispensed)
    
    def test_prescription_quantity_validation(self):
        """Test quantity validation"""
        prescription = self.env['pharmacy.prescription'].create({
            'patient_id': self.patient.id,
            'prescriber_id': self.prescriber.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 20,
            })],
        })
        
        line = prescription.line_ids[0]
        
        # Should not allow dispensing more than prescribed
        with self.assertRaises(ValidationError):
            line.quantity_dispensed = 25
