# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Pharmaceutical Classification
    is_pharmaceutical = fields.Boolean(
        string='Is Pharmaceutical Product',
        help='Check if this product is a pharmaceutical product'
    )
    drug_generic_name = fields.Char(string='Generic Name')
    drug_strength = fields.Char(
        string='Strength',
        help='e.g., 500mg, 10ml, 250mg/5ml'
    )
    drug_dosage_form = fields.Selection([
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('suspension', 'Suspension'),
        ('injection', 'Injection'),
        ('cream', 'Cream/Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('suppository', 'Suppository'),
        ('patch', 'Transdermal Patch'),
        ('powder', 'Powder'),
        ('solution', 'Solution'),
        ('other', 'Other'),
    ], string='Dosage Form')
    
    drug_schedule = fields.Selection([
        ('schedule_1', 'Schedule 1 (Controlled - High Risk)'),
        ('schedule_2', 'Schedule 2 (Controlled - Moderate Risk)'),
        ('prescription', 'Prescription Only Medicine (POM)'),
        ('pharmacy', 'Pharmacy Medicine (P)'),
        ('otc', 'Over The Counter (OTC)'),
    ], string='Drug Schedule (PPB)', help='Kenya Pharmacy and Poisons Board classification')
    
    # Regulatory
    ppb_registration_number = fields.Char(
        string='PPB Registration No.',
        help='Kenya Pharmacy and Poisons Board registration number'
    )
    requires_prescription = fields.Boolean(
        string='Requires Prescription',
        compute='_compute_requires_prescription',
        store=True
    )
    is_controlled_substance = fields.Boolean(
        string='Controlled Substance',
        compute='_compute_controlled_substance',
        store=True,
        help='Schedule 1 or 2 drugs requiring special register'
    )
    
    # Storage and Handling
    requires_refrigeration = fields.Boolean(
        string='Requires Refrigeration',
        help='Store between 2°C and 8°C'
    )
    storage_conditions = fields.Text(
        string='Storage Conditions',
        help='Specific storage requirements'
    )
    
    # Clinical Information
    active_ingredients = fields.Text(string='Active Ingredients')
    contraindications = fields.Text(
        string='Contraindications',
        help='Conditions or factors that increase risks'
    )
    drug_interactions = fields.Text(
        string='Drug Interactions',
        help='Known interactions with other medications'
    )
    side_effects = fields.Text(string='Common Side Effects')
    
    # Therapeutic Classification
    therapeutic_class = fields.Char(
        string='Therapeutic Class',
        help='e.g., Analgesic, Antibiotic, Antihypertensive'
    )
    
    @api.depends('drug_schedule')
    def _compute_requires_prescription(self):
        """Compute whether prescription is required based on drug schedule"""
        for record in self:
            record.requires_prescription = record.drug_schedule in [
                'schedule_1', 'schedule_2', 'prescription'
            ]
    
    @api.depends('drug_schedule')
    def _compute_controlled_substance(self):
        """Compute whether drug is a controlled substance"""
        for record in self:
            record.is_controlled_substance = record.drug_schedule in [
                'schedule_1', 'schedule_2'
            ]
