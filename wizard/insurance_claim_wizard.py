# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InsuranceClaimWizard(models.TransientModel):
    _name = 'insurance.claim.wizard'
    _description = 'Insurance Claim Creation Wizard'
    
    pos_order_id = fields.Many2one(
        'pos.order',
        string='POS Order',
        required=True
    )
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        domain=[('is_patient', '=', True)]
    )
    insurance_provider_id = fields.Many2one(
        'insurance.provider',
        string='Insurance Provider',
        required=True
    )
    member_number = fields.Char(
        string='Member Number',
        required=True
    )
    preauth_number = fields.Char(string='Pre-authorization Number')
    preauth_amount = fields.Float(string='Pre-authorized Amount')
    
    copay_percentage = fields.Float(
        string='Co-payment %',
        related='insurance_provider_id.copay_percentage',
        readonly=True
    )
    
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_amounts'
    )
    patient_copay = fields.Float(
        string='Patient Co-payment',
        compute='_compute_amounts'
    )
    insurance_amount = fields.Float(
        string='Insurance Amount',
        compute='_compute_amounts'
    )
    
    @api.depends('pos_order_id', 'copay_percentage')
    def _compute_amounts(self):
        """Calculate claim amounts"""
        for wizard in self:
            if wizard.pos_order_id:
                wizard.total_amount = wizard.pos_order_id.amount_total
                wizard.patient_copay = wizard.total_amount * (wizard.copay_percentage / 100)
                wizard.insurance_amount = wizard.total_amount - wizard.patient_copay
            else:
                wizard.total_amount = 0
                wizard.patient_copay = 0
                wizard.insurance_amount = 0
    
    def action_create_claim(self):
        """Create insurance claim from wizard"""
        self.ensure_one()
        
        # Create claim
        claim = self.env['insurance.claim'].create({
            'patient_id': self.patient_id.id,
            'insurance_provider_id': self.insurance_provider_id.id,
            'member_number': self.member_number,
            'preauth_number': self.preauth_number,
            'preauth_amount': self.preauth_amount,
            'patient_copay': self.patient_copay,
            'pos_order_id': self.pos_order_id.id,
        })
        
        # Create claim lines from POS order lines
        for order_line in self.pos_order_id.lines:
            self.env['insurance.claim.line'].create({
                'claim_id': claim.id,
                'product_id': order_line.product_id.id,
                'quantity': order_line.qty,
                'unit_price': order_line.price_unit,
            })
        
        # Link claim to POS order
        self.pos_order_id.insurance_claim_id = claim.id
        
        # Open the created claim
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.claim',
            'res_id': claim.id,
            'view_mode': 'form',
            'target': 'current',
        }
