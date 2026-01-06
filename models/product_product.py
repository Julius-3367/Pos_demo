# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    manufacturer_id = fields.Many2one(
        'res.partner',
        string='Manufacturer',
        domain=[('is_company', '=', True)],
        help='Manufacturing company'
    )
