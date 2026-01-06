# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_patient = fields.Boolean(string='Is Patient')
    is_prescriber = fields.Boolean(string='Is Prescriber')
    
    # Patient Information
    patient_id_number = fields.Char(
        string='ID/Passport Number',
        help='National ID or Passport number'
    )
    date_of_birth = fields.Date(string='Date of Birth')
    blood_group = fields.Selection([
        ('a_positive', 'A+'),
        ('a_negative', 'A-'),
        ('b_positive', 'B+'),
        ('b_negative', 'B-'),
        ('ab_positive', 'AB+'),
        ('ab_negative', 'AB-'),
        ('o_positive', 'O+'),
        ('o_negative', 'O-'),
    ], string='Blood Group')
    
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    
    allergies = fields.Text(
        string='Known Allergies',
        help='List known drug allergies or other allergies'
    )
    medical_conditions = fields.Text(
        string='Medical Conditions',
        help='Chronic or significant medical conditions'
    )
    
    # Insurance Information
    insurance_provider_id = fields.Many2one(
        'insurance.provider',
        string='Primary Insurance Provider'
    )
    insurance_member_number = fields.Char(string='Insurance Member/Policy Number')
    insurance_valid_until = fields.Date(string='Insurance Valid Until')
    insurance_active = fields.Boolean(
        string='Insurance Active',
        compute='_compute_insurance_active',
        store=True
    )
    
    # Prescriber Information
    prescriber_license_number = fields.Char(
        string='Medical License Number',
        help='License number from Medical Practitioners and Dentists Board'
    )
    prescriber_specialty = fields.Char(
        string='Medical Specialty',
        help='e.g., General Practitioner, Pediatrician, etc.'
    )
    
    # Prescription History
    prescription_ids = fields.One2many(
        'pharmacy.prescription',
        'patient_id',
        string='Prescriptions'
    )
    prescription_count = fields.Integer(
        string='Prescription Count',
        compute='_compute_prescription_count'
    )
    
    @api.depends('insurance_valid_until')
    def _compute_insurance_active(self):
        """Check if insurance is currently active"""
        from datetime import date
        today = date.today()
        for partner in self:
            if partner.insurance_valid_until:
                partner.insurance_active = partner.insurance_valid_until >= today
            else:
                partner.insurance_active = False
    
    def _compute_prescription_count(self):
        """Count prescriptions for this patient"""
        for partner in self:
            partner.prescription_count = len(partner.prescription_ids)
    
    def action_view_prescriptions(self):
        """Open prescriptions view for this patient"""
        self.ensure_one()
        return {
            'name': 'Prescriptions',
            'type': 'ir.actions.act_window',
            'res_model': 'pharmacy.prescription',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
