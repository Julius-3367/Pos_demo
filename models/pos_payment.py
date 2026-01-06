# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'
    
    # Add insurance as a payment type
    is_insurance = fields.Boolean(
        string='Insurance Payment',
        help='This payment method represents insurance claims'
    )
    insurance_provider_ids = fields.Many2many(
        'insurance.provider',
        string='Linked Insurance Providers',
        help='Insurance providers that use this payment method'
    )
    
    @api.constrains('is_insurance', 'is_cash_count')
    def _check_insurance_not_cash(self):
        """Insurance payments should not be counted as cash"""
        for method in self:
            if method.is_insurance and method.is_cash_count:
                raise ValidationError(_('Insurance payment methods cannot be cash-counted.'))


class PosPayment(models.Model):
    _inherit = 'pos.payment'
    
    # Insurance payment details
    insurance_claim_id = fields.Many2one(
        'insurance.claim',
        string='Insurance Claim',
        help='Linked insurance claim for this payment'
    )
    insurance_provider_id = fields.Many2one(
        'insurance.provider',
        string='Insurance Provider',
        help='Insurance provider for this payment'
    )
    insurance_member_number = fields.Char(
        string='Member Number',
        help='Insurance member/policy number'
    )
    insurance_preauth = fields.Char(
        string='Pre-authorization',
        help='Pre-authorization number from insurance'
    )
    is_insurance_payment = fields.Boolean(
        string='Is Insurance Payment',
        compute='_compute_is_insurance',
        store=True
    )
    
    # M-PESA payment details
    mpesa_transaction_id = fields.Char(
        string='M-PESA Transaction ID',
        help='M-PESA confirmation code'
    )
    mpesa_phone = fields.Char(
        string='M-PESA Phone Number',
        help='Phone number used for M-PESA payment'
    )
    
    @api.depends('payment_method_id', 'payment_method_id.is_insurance')
    def _compute_is_insurance(self):
        """Determine if this is an insurance payment"""
        for payment in self:
            payment.is_insurance_payment = payment.payment_method_id.is_insurance
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override to create insurance claim if needed"""
        payments = super(PosPayment, self).create(vals_list)
        
        for payment in payments:
            # Auto-create insurance claim for insurance payments
            if payment.is_insurance_payment and not payment.insurance_claim_id:
                if payment.pos_order_id and payment.insurance_provider_id:
                    claim = self.env['insurance.claim'].create({
                        'patient_id': payment.pos_order_id.partner_id.id,
                        'insurance_provider_id': payment.insurance_provider_id.id,
                        'member_number': payment.insurance_member_number or '',
                        'preauth_number': payment.insurance_preauth,
                        'patient_copay': payment.pos_order_id.patient_copay or 0.0,
                        'date': fields.Date.today(),
                    })
                    payment.insurance_claim_id = claim.id
                    payment.pos_order_id.insurance_claim_id = claim.id
                    
                    # Create claim lines from order lines
                    for line in payment.pos_order_id.lines:
                        self.env['insurance.claim.line'].create({
                            'claim_id': claim.id,
                            'product_id': line.product_id.id,
                            'quantity': line.qty,
                            'price_unit': line.price_unit,
                            'discount': line.discount,
                            'claimed_amount': line.price_subtotal,
                        })
        
        return payments
    
    def action_view_insurance_claim(self):
        """Open the linked insurance claim"""
        self.ensure_one()
        if not self.insurance_claim_id:
            raise ValidationError(_('No insurance claim linked to this payment.'))
        
        return {
            'name': _('Insurance Claim'),
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.claim',
            'res_id': self.insurance_claim_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
