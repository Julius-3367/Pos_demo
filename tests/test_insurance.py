# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestInsurance(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Create test insurance provider
        self.provider = self.env['insurance.provider'].create({
            'name': 'Test Insurance',
            'code': 'TEST',
            'provider_type': 'private',
            'copay_percentage': 20,
        })
        
        # Create test patient
        self.patient = self.env['res.partner'].create({
            'name': 'Test Patient',
            'is_patient': True,
            'insurance_provider_id': self.provider.id,
            'insurance_member_number': 'MEM12345',
        })
        
        # Create test product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100,
        })
    
    def test_create_insurance_provider(self):
        """Test insurance provider creation"""
        self.assertEqual(self.provider.coverage_percentage, 80)
        self.assertEqual(self.provider.copay_percentage, 20)
    
    def test_create_insurance_claim(self):
        """Test insurance claim creation"""
        claim = self.env['insurance.claim'].create({
            'patient_id': self.patient.id,
            'insurance_provider_id': self.provider.id,
            'member_number': 'MEM12345',
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'unit_price': 100,
            })],
        })
        
        self.assertEqual(claim.state, 'draft')
        self.assertEqual(claim.total_amount, 100)
    
    def test_insurance_amounts_calculation(self):
        """Test insurance amount calculations"""
        claim = self.env['insurance.claim'].create({
            'patient_id': self.patient.id,
            'insurance_provider_id': self.provider.id,
            'member_number': 'MEM12345',
            'patient_copay': 20,
            'approved_amount': 100,
        })
        
        self.assertEqual(claim.insurance_payment, 80)
    
    def test_claim_submission(self):
        """Test claim submission workflow"""
        claim = self.env['insurance.claim'].create({
            'patient_id': self.patient.id,
            'insurance_provider_id': self.provider.id,
            'member_number': 'MEM12345',
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'unit_price': 100,
            })],
        })
        
        claim.action_submit()
        self.assertEqual(claim.state, 'submitted')
        self.assertIsNotNone(claim.submission_date)
