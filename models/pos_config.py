# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timezone as dt_timezone


class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    # Pharmacy Settings
    is_pharmacy_pos = fields.Boolean(
        string='Pharmacy POS',
        help='Enable pharmacy-specific features'
    )
    enforce_prescription_check = fields.Boolean(
        string='Enforce Prescription Check',
        default=True,
        help='Require prescription validation for prescription-only medicines'
    )
    require_pharmacist_validation = fields.Boolean(
        string='Require Pharmacist Validation',
        default=True,
        help='Require pharmacist to validate orders with prescription items'
    )
    enable_expiry_check = fields.Boolean(
        string='Enable Expiry Date Check',
        default=True,
        help='Check and warn about expiring products'
    )
    expiry_warning_days = fields.Integer(
        string='Expiry Warning Days',
        default=180,
        help='Warn if product expires within this many days'
    )
    block_expired_sales = fields.Boolean(
        string='Block Expired Product Sales',
        default=True,
        help='Prevent sale of expired products'
    )
    
    # Batch/Lot Management
    enforce_lot_selection = fields.Boolean(
        string='Enforce Batch/Lot Selection',
        default=True,
        help='Require batch/lot selection for pharmaceutical products'
    )
    use_fefo_logic = fields.Boolean(
        string='Use FEFO Logic',
        default=True,
        help='First Expired, First Out - suggest earliest expiry batches'
    )
    
    # Insurance
    enable_insurance = fields.Boolean(
        string='Enable Insurance Claims',
        help='Allow insurance payment method'
    )
    allowed_insurance_ids = fields.Many2many(
        'insurance.provider',
        string='Allowed Insurance Providers'
    )
    auto_create_insurance_claim = fields.Boolean(
        string='Auto-Create Insurance Claims',
        default=True,
        help='Automatically create insurance claim on order confirmation'
    )
    
    # Patient Safety
    show_allergy_alerts = fields.Boolean(
        string='Show Allergy Alerts',
        default=True,
        help='Display patient allergy warnings'
    )
    enable_interaction_check = fields.Boolean(
        string='Enable Drug Interaction Check',
        default=True,
        help='Check for potential drug interactions based on recent purchases'
    )
    interaction_check_days = fields.Integer(
        string='Interaction Check Period (days)',
        default=30,
        help='Check patient purchases within this many days for interactions'
    )
    
    # KRA ETR Integration
    etr_enabled = fields.Boolean(
        string='Enable ETR Integration',
        help='Kenya Revenue Authority Electronic Tax Register'
    )
    etr_cu_serial = fields.Char(
        string='ETR Control Unit Serial Number',
        help='Serial number of the ETR control unit'
    )
    etr_api_url = fields.Char(
        string='ETR API URL',
        help='URL for ETR API integration'
    )
    
    # M-PESA Payment Integration
    mpesa_enabled = fields.Boolean(
        string='Enable M-PESA Payments',
        help='Accept M-PESA mobile money payments'
    )
    mpesa_paybill = fields.Char(
        string='M-PESA Paybill/Till Number',
        help='Your M-PESA business number'
    )
    mpesa_shortcode = fields.Char(string='M-PESA Shortcode')
    mpesa_api_key = fields.Char(string='M-PESA Consumer Key')
    mpesa_api_secret = fields.Char(string='M-PESA Consumer Secret')
    mpesa_passkey = fields.Char(string='M-PESA Passkey')
    mpesa_environment = fields.Selection([
        ('sandbox', 'Sandbox/Test'),
        ('production', 'Production'),
    ], string='M-PESA Environment', default='sandbox')

    @api.depends('session_ids', 'session_ids.stop_at')
    def _compute_last_session(self):
        """
        Override to handle cases where stop_at is False (open sessions).
        This prevents AttributeError when trying to call astimezone() on a boolean.
        """
        for pos_config in self:
            session = self.env['pos.session'].search(
                [('config_id', '=', pos_config.id)],
                order='stop_at desc',
                limit=1
            )
            if session and session.stop_at:
                # Only process if stop_at is actually set (not False)
                timezone = dt_timezone.utc
                if self.env.user.tz:
                    try:
                        from zoneinfo import ZoneInfo
                        timezone = ZoneInfo(self.env.user.tz)
                    except Exception:
                        pass
                pos_config.last_session_closing_date = session.stop_at.astimezone(timezone).date()
                pos_config.last_session_closing_cash = session.cash_register_balance_end_real
            else:
                # Session is open or doesn't exist
                pos_config.last_session_closing_date = False
                pos_config.last_session_closing_cash = 0
