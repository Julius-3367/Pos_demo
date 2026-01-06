# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InsuranceClaim(models.Model):
    _name = 'insurance.claim'
    _description = 'Insurance Claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    
    name = fields.Char(
        string='Claim Number',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    date = fields.Date(
        string='Claim Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    # Parties
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        domain=[('is_patient', '=', True)],
        tracking=True
    )
    insurance_provider_id = fields.Many2one(
        'insurance.provider',
        string='Insurance Provider',
        required=True,
        tracking=True
    )
    member_number = fields.Char(
        string='Member/Policy Number',
        required=True
    )
    
    # Authorization
    preauth_number = fields.Char(
        string='Pre-authorization Number',
        help='If pre-authorization was obtained'
    )
    preauth_amount = fields.Float(string='Pre-authorized Amount')
    
    # Financial
    total_amount = fields.Float(
        string='Total Claim Amount',
        compute='_compute_amounts',
        store=True
    )
    approved_amount = fields.Float(
        string='Approved Amount',
        tracking=True
    )
    rejected_amount = fields.Float(
        string='Rejected Amount',
        compute='_compute_rejected_amount',
        store=True
    )
    patient_copay = fields.Float(
        string='Patient Co-payment',
        help='Amount paid by patient'
    )
    insurance_payment = fields.Float(
        string='Insurance Payment',
        compute='_compute_insurance_payment',
        store=True
    )
    
    # Lines
    line_ids = fields.One2many(
        'insurance.claim.line',
        'claim_id',
        string='Claim Lines'
    )
    
    # POS Link
    pos_order_id = fields.Many2one(
        'pos.order',
        string='POS Order',
        readonly=True
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('partial', 'Partially Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid')
    ], default='draft', tracking=True, string='Status')
    
    submission_date = fields.Date(
        string='Submission Date',
        readonly=True,
        tracking=True
    )
    response_date = fields.Date(
        string='Response Date',
        readonly=True,
        tracking=True
    )
    payment_date = fields.Date(
        string='Payment Date',
        readonly=True,
        tracking=True
    )
    payment_reference = fields.Char(string='Payment Reference')
    
    rejection_reason = fields.Text(
        string='Rejection Reason',
        tracking=True
    )
    
    # Notes
    notes = fields.Text(string='Internal Notes')
    
    @api.model
    def create(self, vals):
        """Generate claim number sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.claim') or 'New'
        return super().create(vals)
    
    @api.depends('line_ids.amount')
    def _compute_amounts(self):
        """Calculate total claim amount"""
        for claim in self:
            claim.total_amount = sum(claim.line_ids.mapped('amount'))
    
    @api.depends('total_amount', 'approved_amount')
    def _compute_rejected_amount(self):
        """Calculate rejected amount"""
        for claim in self:
            claim.rejected_amount = claim.total_amount - claim.approved_amount
    
    @api.depends('approved_amount', 'patient_copay')
    def _compute_insurance_payment(self):
        """Calculate insurance payment amount"""
        for claim in self:
            claim.insurance_payment = claim.approved_amount - claim.patient_copay
    
    def action_submit(self):
        """Submit claim to insurance provider"""
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_('Cannot submit claim without line items'))
        
        self.write({
            'state': 'submitted',
            'submission_date': fields.Date.today()
        })
        
        self.message_post(
            body=_('Claim submitted to %s') % self.insurance_provider_id.name,
            subject=_('Claim Submitted')
        )
        
        # TODO: Integrate with insurance provider API if configured
        
    def action_approve(self):
        """Approve claim"""
        self.ensure_one()
        if not self.approved_amount:
            raise ValidationError(_('Please specify approved amount'))
        
        state = 'approved' if self.approved_amount == self.total_amount else 'partial'
        self.write({
            'state': state,
            'response_date': fields.Date.today()
        })
        
        self.message_post(
            body=_('Claim approved for %s') % self.approved_amount,
            subject=_('Claim Approved')
        )
    
    def action_reject(self):
        """Reject claim"""
        self.ensure_one()
        self.write({
            'state': 'rejected',
            'approved_amount': 0,
            'response_date': fields.Date.today()
        })
        
        self.message_post(
            body=_('Claim rejected: %s') % (self.rejection_reason or 'No reason provided'),
            subject=_('Claim Rejected')
        )
    
    def action_mark_paid(self):
        """Mark claim as paid"""
        self.ensure_one()
        if self.state not in ['approved', 'partial']:
            raise ValidationError(_('Only approved claims can be marked as paid'))
        
        self.write({
            'state': 'paid',
            'payment_date': fields.Date.today()
        })
        
        self.message_post(
            body=_('Payment received: %s') % (self.payment_reference or 'No reference'),
            subject=_('Payment Received')
        )
    
    def action_reset_to_draft(self):
        """Reset claim to draft"""
        self.ensure_one()
        self.state = 'draft'


class InsuranceClaimLine(models.Model):
    _name = 'insurance.claim.line'
    _description = 'Insurance Claim Line'
    
    claim_id = fields.Many2one(
        'insurance.claim',
        string='Claim',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    description = fields.Text(string='Description')
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0
    )
    unit_price = fields.Float(
        string='Unit Price',
        required=True
    )
    amount = fields.Float(
        string='Amount',
        compute='_compute_amount',
        store=True
    )
    
    # Claim specific
    approved = fields.Boolean(
        string='Approved',
        default=True
    )
    rejection_reason = fields.Char(string='Rejection Reason')
    
    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        """Calculate line amount"""
        for line in self:
            line.amount = line.quantity * line.unit_price
    
    @api.constrains('quantity', 'unit_price')
    def _check_values(self):
        """Validate line values"""
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('Quantity must be positive'))
            if line.unit_price < 0:
                raise ValidationError(_('Unit price cannot be negative'))
