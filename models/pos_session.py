# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    # Opening Balance Details
    opening_cash = fields.Float(
        string='Opening Cash',
        help='Cash amount at session opening',
        readonly=True
    )
    opening_notes = fields.Text(
        string='Opening Notes',
        help='Notes about the opening balance'
    )
    
    # Closing Balance Details
    closing_cash_counted = fields.Float(
        string='Counted Cash',
        help='Actual cash counted at closing',
        readonly=True
    )
    closing_card_total = fields.Float(
        string='Card Payments Total',
        compute='_compute_closing_totals',
        store=True
    )
    closing_mpesa_total = fields.Float(
        string='M-PESA Total',
        compute='_compute_closing_totals',
        store=True
    )
    closing_insurance_total = fields.Float(
        string='Insurance Claims Total',
        compute='_compute_closing_totals',
        store=True
    )
    closing_notes = fields.Text(
        string='Closing Notes',
        help='Notes about the closing balance'
    )
    
    # Variance/Discrepancy
    cash_difference = fields.Float(
        string='Cash Difference',
        compute='_compute_cash_difference',
        store=True,
        help='Difference between expected and counted cash'
    )
    
    # Daily Summary
    total_sales = fields.Float(
        string='Total Sales',
        compute='_compute_session_summary',
        store=True
    )
    prescription_sales = fields.Float(
        string='Prescription Sales',
        compute='_compute_session_summary',
        store=True
    )
    otc_sales = fields.Float(
        string='OTC Sales',
        compute='_compute_session_summary',
        store=True
    )
    insurance_sales = fields.Float(
        string='Insurance Sales',
        compute='_compute_session_summary',
        store=True
    )
    
    @api.depends('order_ids', 'order_ids.payment_ids', 'order_ids.payment_ids.amount', 
                 'order_ids.payment_ids.payment_method_id')
    def _compute_closing_totals(self):
        """Compute totals by payment method"""
        for session in self:
            card_total = 0.0
            mpesa_total = 0.0
            insurance_total = 0.0
            
            # Get all payments from orders in this session
            for order in session.order_ids:
                for payment in order.payment_ids:
                    payment_method = payment.payment_method_id
                    if payment_method:
                        # Check if it's a bank/card payment
                        if hasattr(payment_method, 'type') and payment_method.type == 'bank':
                            if 'mpesa' in payment_method.name.lower() or 'mobile' in payment_method.name.lower():
                                mpesa_total += payment.amount
                            else:
                                card_total += payment.amount
                        # Check for insurance payment
                        elif hasattr(payment_method, 'is_insurance') and payment_method.is_insurance:
                            insurance_total += payment.amount
                        elif payment_method.name and 'insurance' in payment_method.name.lower():
                            insurance_total += payment.amount
                    
            session.closing_card_total = card_total
            session.closing_mpesa_total = mpesa_total
            session.closing_insurance_total = insurance_total
    
    @api.depends('cash_register_balance_end_real', 'cash_register_balance_end', 'closing_cash_counted')
    def _compute_cash_difference(self):
        """Compute cash discrepancy"""
        for session in self:
            if session.state == 'closed':
                expected = session.cash_register_balance_end or 0.0
                actual = session.closing_cash_counted or session.cash_register_balance_end_real or 0.0
                session.cash_difference = actual - expected
            else:
                session.cash_difference = 0.0
    
    @api.depends('order_ids', 'order_ids.amount_total', 'order_ids.has_prescription_items', 
                 'order_ids.insurance_amount')
    def _compute_session_summary(self):
        """Compute session sales summaries"""
        for session in self:
            total = 0.0
            prescription = 0.0
            otc = 0.0
            insurance = 0.0
            
            for order in session.order_ids:
                total += order.amount_total
                insurance += order.insurance_amount or 0.0
                
                if order.has_prescription_items:
                    prescription += order.amount_total
                else:
                    otc += order.amount_total
                    
            session.total_sales = total
            session.prescription_sales = prescription
            session.otc_sales = otc
            session.insurance_sales = insurance
    
    def action_pos_session_open(self):
        """Override to enforce opening balance entry"""
        # Check if opening cash is set for cash payment methods
        for session in self:
            if session.config_id.cash_control and not session.opening_cash and session.opening_cash != 0:
                raise ValidationError(_('Please enter the opening cash amount before opening the session.'))
        return super(PosSession, self).action_pos_session_open()
    
    def action_pos_session_closing_control(self):
        """Override to enforce closing cash count"""
        for session in self:
            if session.config_id.cash_control and session.closing_cash_counted == 0 and not session.closing_cash_counted:
                raise ValidationError(_('Please count and enter the closing cash amount before closing the session.'))
        return super(PosSession, self).action_pos_session_closing_control()
    
    def action_view_insurance_claims(self):
        """View insurance claims for this session"""
        self.ensure_one()
        insurance_claims = self.order_ids.mapped('insurance_claim_id')
        
        return {
            'name': _('Insurance Claims - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.claim',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', insurance_claims.ids)],
            'context': {'default_session_id': self.id}
        }


class PosSessionCashBalance(models.Model):
    """Denomination tracking for cash counting"""
    _name = 'pos.session.cash.balance'
    _description = 'POS Session Cash Denomination'
    
    session_id = fields.Many2one(
        'pos.session',
        string='Session',
        required=True,
        ondelete='cascade'
    )
    type = fields.Selection([
        ('opening', 'Opening'),
        ('closing', 'Closing')
    ], string='Type', required=True, default='closing')
    
    # Denominations - Kenyan Currency
    denomination_1000 = fields.Integer(string='KSh 1000 Notes', default=0)
    denomination_500 = fields.Integer(string='KSh 500 Notes', default=0)
    denomination_200 = fields.Integer(string='KSh 200 Notes', default=0)
    denomination_100 = fields.Integer(string='KSh 100 Notes', default=0)
    denomination_50 = fields.Integer(string='KSh 50 Notes', default=0)
    denomination_40 = fields.Integer(string='KSh 40 Coins', default=0)
    denomination_20 = fields.Integer(string='KSh 20 Coins', default=0)
    denomination_10 = fields.Integer(string='KSh 10 Coins', default=0)
    denomination_5 = fields.Integer(string='KSh 5 Coins', default=0)
    denomination_1 = fields.Integer(string='KSh 1 Coins', default=0)
    
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True
    )
    
    @api.depends('denomination_1000', 'denomination_500', 'denomination_200', 
                 'denomination_100', 'denomination_50', 'denomination_40',
                 'denomination_20', 'denomination_10', 'denomination_5', 
                 'denomination_1')
    def _compute_total_amount(self):
        """Calculate total from denominations"""
        for balance in self:
            total = (
                (balance.denomination_1000 * 1000) +
                (balance.denomination_500 * 500) +
                (balance.denomination_200 * 200) +
                (balance.denomination_100 * 100) +
                (balance.denomination_50 * 50) +
                (balance.denomination_40 * 40) +
                (balance.denomination_20 * 20) +
                (balance.denomination_10 * 10) +
                (balance.denomination_5 * 5) +
                (balance.denomination_1 * 1)
            )
            balance.total_amount = total
