# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    """Extend invoices to link with prescriptions and insurance claims"""
    _inherit = 'account.move'
    
    prescription_id = fields.Many2one(
        'pharmacy.prescription',
        string='Prescription',
        help='Link invoice to prescription'
    )
    insurance_claim_id = fields.Many2one(
        'insurance.claim',
        string='Insurance Claim',
        help='Link invoice to insurance claim'
    )
    is_pharmacy_invoice = fields.Boolean(
        string='Pharmacy Invoice',
        compute='_compute_is_pharmacy_invoice',
        store=True
    )
    
    @api.depends('line_ids.product_id')
    def _compute_is_pharmacy_invoice(self):
        """Check if invoice contains pharmaceutical products"""
        for move in self:
            move.is_pharmacy_invoice = any(
                line.product_id.is_pharmaceutical 
                for line in move.line_ids 
                if line.product_id
            )


class AccountMoveLine(models.Model):
    """Extend invoice lines with batch/lot tracking"""
    _inherit = 'account.move.line'
    
    lot_id = fields.Many2one(
        'stock.lot',
        string='Batch/Lot',
        help='Batch/Lot number for pharmaceutical tracking'
    )
    expiry_date = fields.Date(
        string='Expiry Date',
        help='Product expiry date from batch/lot'
    )
