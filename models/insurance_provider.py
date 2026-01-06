# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InsuranceProvider(models.Model):
    _name = 'insurance.provider'
    _description = 'Insurance Provider'
    _order = 'name'
    
    name = fields.Char(
        string='Provider Name',
        required=True,
        help='Insurance company name'
    )
    code = fields.Char(
        string='Provider Code',
        required=True,
        help='Unique code for this provider'
    )
    provider_type = fields.Selection([
        ('nhif', 'NHIF (National Hospital Insurance Fund)'),
        ('private', 'Private Insurance'),
        ('corporate', 'Corporate/Company Insurance'),
    ], string='Provider Type', required=True)
    
    # Contact Information
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Partner',
        domain=[('is_company', '=', True)]
    )
    contact_person = fields.Char(string='Contact Person')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    
    # Coverage Terms
    copay_percentage = fields.Float(
        string='Standard Co-payment %',
        help='Default patient co-payment percentage',
        default=10.0
    )
    coverage_percentage = fields.Float(
        string='Coverage %',
        compute='_compute_coverage_percentage',
        store=True
    )
    requires_preauth = fields.Boolean(
        string='Requires Pre-authorization',
        help='Claims require pre-authorization'
    )
    preauth_threshold = fields.Float(
        string='Pre-auth Threshold',
        help='Amount above which pre-authorization is required'
    )
    
    # Claims Processing
    claim_submission_method = fields.Selection([
        ('api', 'API Integration'),
        ('portal', 'Web Portal'),
        ('email', 'Email'),
        ('manual', 'Manual/Physical'),
    ], string='Claim Submission Method', default='manual')
    
    api_endpoint = fields.Char(
        string='API Endpoint',
        help='URL for API submissions'
    )
    api_key = fields.Char(string='API Key')
    portal_url = fields.Char(string='Portal URL')
    submission_email = fields.Char(string='Claims Submission Email')
    
    # Processing times
    average_processing_days = fields.Integer(
        string='Average Processing Days',
        default=14
    )
    
    # Status
    active = fields.Boolean(default=True)
    
    # Statistics
    claim_count = fields.Integer(
        string='Total Claims',
        compute='_compute_statistics'
    )
    total_claimed = fields.Float(
        string='Total Claimed Amount',
        compute='_compute_statistics'
    )
    
    @api.depends('copay_percentage')
    def _compute_coverage_percentage(self):
        """Calculate coverage percentage"""
        for provider in self:
            provider.coverage_percentage = 100.0 - provider.copay_percentage
    
    def _compute_statistics(self):
        """Compute claim statistics"""
        for provider in self:
            claims = self.env['insurance.claim'].search([
                ('insurance_provider_id', '=', provider.id)
            ])
            provider.claim_count = len(claims)
            provider.total_claimed = sum(claims.mapped('total_amount'))
    
    @api.constrains('copay_percentage')
    def _check_copay_percentage(self):
        """Validate copay percentage"""
        for provider in self:
            if provider.copay_percentage < 0 or provider.copay_percentage > 100:
                raise ValidationError(_('Co-payment percentage must be between 0 and 100'))
    
    @api.constrains('code')
    def _check_unique_code(self):
        """Ensure provider code is unique"""
        for provider in self:
            if self.search_count([('code', '=', provider.code), ('id', '!=', provider.id)]) > 0:
                raise ValidationError(_('Provider code must be unique'))
