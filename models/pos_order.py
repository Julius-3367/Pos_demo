# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    # Prescription Management
    prescription_id = fields.Many2one(
        'pharmacy.prescription',
        string='Prescription',
        help='Linked prescription if order contains prescription items'
    )
    has_prescription_items = fields.Boolean(
        string='Has Prescription Items',
        compute='_compute_prescription_items',
        store=True
    )
    prescription_validated = fields.Boolean(
        string='Prescription Validated',
        help='Prescription has been validated by pharmacist'
    )
    
    # Insurance Processing
    insurance_claim_id = fields.Many2one(
        'insurance.claim',
        string='Insurance Claim',
        readonly=True
    )
    insurance_provider_id = fields.Many2one(
        'insurance.provider',
        string='Insurance Provider'
    )
    insurance_member_number = fields.Char(string='Insurance Member Number')
    patient_copay = fields.Float(
        string='Patient Co-payment',
        help='Amount paid by patient (not covered by insurance)'
    )
    insurance_amount = fields.Float(
        string='Insurance Covered Amount',
        help='Amount to be claimed from insurance'
    )
    has_insurance = fields.Boolean(
        string='Has Insurance',
        compute='_compute_has_insurance'
    )
    
    # Pharmacy Staff
    dispensed_by = fields.Many2one(
        'res.users',
        string='Dispensed By',
        help='Staff member who dispensed the medication'
    )
    validated_by = fields.Many2one(
        'res.users',
        string='Validated By (Pharmacist)',
        help='Pharmacist who validated the prescription'
    )
    
    # Controlled Substances
    has_controlled_substances = fields.Boolean(
        string='Has Controlled Substances',
        compute='_compute_controlled_substances',
        store=True
    )
    
    @api.depends('lines.product_id.product_tmpl_id.requires_prescription')
    def _compute_prescription_items(self):
        """Check if order contains prescription-only items"""
        for order in self:
            order.has_prescription_items = any(
                line.product_id.product_tmpl_id.requires_prescription 
                for line in order.lines
            )
    
    @api.depends('lines.product_id.product_tmpl_id.is_controlled_substance')
    def _compute_controlled_substances(self):
        """Check if order contains controlled substances"""
        for order in self:
            order.has_controlled_substances = any(
                line.product_id.product_tmpl_id.is_controlled_substance 
                for line in order.lines
            )
    
    @api.depends('insurance_provider_id')
    def _compute_has_insurance(self):
        """Check if order uses insurance"""
        for order in self:
            order.has_insurance = bool(order.insurance_provider_id)
    
    def _create_controlled_drugs_register_entries(self):
        """Create controlled drugs register entries for controlled substances"""
        ControlledDrugsRegister = self.env['controlled.drugs.register']
        
        for order in self:
            for line in order.lines.filtered(
                lambda l: l.product_id.product_tmpl_id.is_controlled_substance
            ):
                # Get prescription details if available
                patient_name = order.partner_id.name if order.partner_id else 'Walk-in Customer'
                patient_id = order.partner_id.patient_id_number if order.partner_id else ''
                prescriber_name = ''
                prescriber_license = ''
                
                if order.prescription_id:
                    prescriber_name = order.prescription_id.prescriber_id.name
                    prescriber_license = order.prescription_id.prescriber_license
                
                ControlledDrugsRegister.create({
                    'date': order.date_order,
                    'product_id': line.product_id.id,
                    'transaction_type': 'dispensing',
                    'quantity_dispensed': line.qty,
                    'prescription_id': order.prescription_id.id if order.prescription_id else False,
                    'patient_name': patient_name,
                    'patient_id_number': patient_id,
                    'prescriber_name': prescriber_name,
                    'prescriber_license': prescriber_license,
                    'pos_order_id': order.id,
                    'authorized_by': order.dispensed_by.id if order.dispensed_by else self.env.user.id,
                    'remarks': f'POS Sale - Order {order.name}',
                })
    
    def _create_insurance_claim(self):
        """Create insurance claim for orders with insurance"""
        InsuranceClaim = self.env['insurance.claim']
        
        for order in self:
            if order.insurance_provider_id and not order.insurance_claim_id:
                # Create claim
                claim = InsuranceClaim.create({
                    'patient_id': order.partner_id.id,
                    'insurance_provider_id': order.insurance_provider_id.id,
                    'member_number': order.insurance_member_number,
                    'patient_copay': order.patient_copay,
                    'pos_order_id': order.id,
                    'date': fields.Date.today(),
                })
                
                # Create claim lines
                for line in order.lines:
                    self.env['insurance.claim.line'].create({
                        'claim_id': claim.id,
                        'product_id': line.product_id.id,
                        'quantity': line.qty,
                        'unit_price': line.price_unit,
                    })
                
                # Link claim to order
                order.insurance_claim_id = claim.id
                
                # Auto-submit if configured
                if order.session_id.config_id.auto_create_insurance_claim:
                    claim.action_submit()
    
    def _update_prescription_dispensed_quantity(self):
        """Update prescription with dispensed quantities"""
        for order in self:
            if order.prescription_id:
                for order_line in order.lines:
                    # Find matching prescription line
                    prescription_line = order.prescription_id.line_ids.filtered(
                        lambda l: l.product_id == order_line.product_id
                    )
                    if prescription_line:
                        prescription_line.quantity_dispensed += order_line.qty
                
                # Update prescription state
                order.prescription_id.action_dispense()
    
    @api.model
    def create(self, vals):
        """Override create to handle pharmacy-specific logic"""
        order = super().create(vals)
        return order
    
    def write(self, vals):
        """Override write to handle state changes"""
        res = super().write(vals)
        
        # Handle order confirmation
        if vals.get('state') == 'paid':
            for order in self:
                # Create controlled drugs register entries
                if order.has_controlled_substances:
                    order._create_controlled_drugs_register_entries()
                
                # Create insurance claim
                if order.has_insurance:
                    order._create_insurance_claim()
                
                # Update prescription
                if order.prescription_id:
                    order._update_prescription_dispensed_quantity()
        
        return res


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    lot_id = fields.Many2one(
        'stock.lot',
        string='Batch/Lot',
        help='Batch or lot number for this line'
    )
    expiry_date = fields.Date(
        string='Expiry Date',
        related='lot_id.expiry_date',
        readonly=True
    )
    is_pharmaceutical = fields.Boolean(
        string='Is Pharmaceutical',
        related='product_id.product_tmpl_id.is_pharmaceutical',
        readonly=True
    )
    requires_prescription = fields.Boolean(
        string='Requires Prescription',
        related='product_id.product_tmpl_id.requires_prescription',
        readonly=True
    )
