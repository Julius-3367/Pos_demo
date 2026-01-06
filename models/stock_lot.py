# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class StockLot(models.Model):
    _inherit = 'stock.lot'
    
    manufacturing_date = fields.Date(string='Manufacturing Date')
    expiry_date = fields.Date(
        string='Expiry Date',
        required=False,
        help='Product expiry date - required for pharmaceutical products'
    )
    batch_number = fields.Char(
        string='Batch Number',
        help='Manufacturer batch number'
    )
    purchase_price = fields.Float(
        string='Purchase Price',
        help='Unit purchase price for this batch'
    )
    days_to_expiry = fields.Integer(
        string='Days to Expiry',
        compute='_compute_days_to_expiry',
        store=True
    )
    expiry_alert = fields.Boolean(
        string='Expiry Alert',
        compute='_compute_expiry_alert',
        store=True,
        help='Alert if expiring within threshold'
    )
    is_expired = fields.Boolean(
        string='Is Expired',
        compute='_compute_is_expired',
        store=True
    )
    
    @api.depends('expiry_date')
    def _compute_days_to_expiry(self):
        """Calculate days remaining until expiry"""
        today = date.today()
        for lot in self:
            if lot.expiry_date:
                delta = lot.expiry_date - today
                lot.days_to_expiry = delta.days
            else:
                lot.days_to_expiry = 0
    
    @api.depends('days_to_expiry')
    def _compute_expiry_alert(self):
        """Alert if expiring within 6 months (180 days)"""
        for lot in self:
            lot.expiry_alert = 0 < lot.days_to_expiry <= 180
    
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        """Check if lot is expired"""
        today = date.today()
        for lot in self:
            if lot.expiry_date:
                lot.is_expired = lot.expiry_date < today
            else:
                lot.is_expired = False
    
    @api.constrains('expiry_date', 'manufacturing_date')
    def _check_dates(self):
        """Ensure expiry date is after manufacturing date"""
        for lot in self:
            if lot.manufacturing_date and lot.expiry_date:
                if lot.expiry_date <= lot.manufacturing_date:
                    raise models.ValidationError(
                        'Expiry date must be after manufacturing date'
                    )
