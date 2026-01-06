# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PharmacyPrescription(models.Model):
    _name = 'pharmacy.prescription'
    _description = 'Pharmacy Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    
    name = fields.Char(
        string='Prescription Number',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    date = fields.Datetime(
        string='Prescription Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True
    )
    
    # Patient Information
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        domain=[('is_patient', '=', True)],
        tracking=True
    )
    patient_age = fields.Integer(
        string='Patient Age',
        compute='_compute_patient_age'
    )
    patient_allergies = fields.Text(
        string='Known Allergies',
        related='patient_id.allergies',
        readonly=True
    )
    
    # Prescriber Information
    prescriber_id = fields.Many2one(
        'res.partner',
        string='Prescriber',
        required=True,
        domain=[('is_prescriber', '=', True)],
        tracking=True
    )
    prescriber_license = fields.Char(
        string='Prescriber License No.',
        related='prescriber_id.prescriber_license_number',
        readonly=True
    )
    
    # Prescription Lines
    line_ids = fields.One2many(
        'pharmacy.prescription.line',
        'prescription_id',
        string='Prescription Items'
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('partial', 'Partially Dispensed'),
        ('dispensed', 'Fully Dispensed'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True, string='Status')
    
    # Validation
    validated_by = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
        tracking=True
    )
    validation_date = fields.Datetime(
        string='Validation Date',
        readonly=True
    )
    
    # Dispensing
    dispensed_by = fields.Many2one(
        'res.users',
        string='Dispensed By',
        readonly=True,
        tracking=True
    )
    dispensing_date = fields.Datetime(
        string='Dispensing Date',
        readonly=True
    )
    pos_order_ids = fields.One2many(
        'pos.order',
        'prescription_id',
        string='POS Orders'
    )
    
    # Digital copy
    prescription_image = fields.Binary(
        string='Prescription Image',
        help='Upload scanned or photographed prescription'
    )
    prescription_filename = fields.Char(string='Filename')
    
    # Clinical
    diagnosis = fields.Text(string='Diagnosis')
    special_instructions = fields.Text(
        string='Special Instructions',
        help='Special dispensing or administration instructions'
    )
    
    # Computed fields
    total_items = fields.Integer(
        string='Total Items',
        compute='_compute_totals'
    )
    dispensed_items = fields.Integer(
        string='Dispensed Items',
        compute='_compute_totals'
    )
    
    @api.model
    def create(self, vals):
        """Generate prescription number sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pharmacy.prescription') or 'New'
        return super().create(vals)
    
    @api.depends('patient_id.date_of_birth')
    def _compute_patient_age(self):
        """Calculate patient age from date of birth"""
        from datetime import date
        for prescription in self:
            if prescription.patient_id.date_of_birth:
                today = date.today()
                dob = prescription.patient_id.date_of_birth
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                prescription.patient_age = age
            else:
                prescription.patient_age = 0
    
    @api.depends('line_ids.quantity', 'line_ids.quantity_dispensed')
    def _compute_totals(self):
        """Compute total and dispensed items count"""
        for prescription in self:
            prescription.total_items = len(prescription.line_ids)
            prescription.dispensed_items = len(
                prescription.line_ids.filtered(lambda l: l.quantity_dispensed >= l.quantity)
            )
    
    def action_validate(self):
        """Validate prescription - requires pharmacist role"""
        self.ensure_one()
        if not self.env.user.has_group('pos_demo.group_pharmacist'):
            raise ValidationError(_('Only pharmacists can validate prescriptions'))
        
        self.write({
            'state': 'validated',
            'validated_by': self.env.user.id,
            'validation_date': fields.Datetime.now()
        })
        
        # Log activity
        self.message_post(
            body=_('Prescription validated by %s') % self.env.user.name,
            subject=_('Prescription Validated')
        )
    
    def action_dispense(self):
        """Mark prescription as dispensed"""
        self.ensure_one()
        fully_dispensed = all(line.quantity_dispensed >= line.quantity for line in self.line_ids)
        
        self.write({
            'state': 'dispensed' if fully_dispensed else 'partial',
            'dispensed_by': self.env.user.id,
            'dispensing_date': fields.Datetime.now()
        })
    
    def action_cancel(self):
        """Cancel prescription"""
        self.ensure_one()
        self.state = 'cancelled'
        self.message_post(
            body=_('Prescription cancelled'),
            subject=_('Prescription Cancelled')
        )
    
    def action_reset_to_draft(self):
        """Reset to draft"""
        self.ensure_one()
        self.state = 'draft'


class PharmacyPrescriptionLine(models.Model):
    _name = 'pharmacy.prescription.line'
    _description = 'Prescription Line Item'
    
    prescription_id = fields.Many2one(
        'pharmacy.prescription',
        string='Prescription',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Medication',
        required=True,
        domain=[('is_pharmaceutical', '=', True)]
    )
    product_generic_name = fields.Char(
        string='Generic Name',
        related='product_id.product_tmpl_id.drug_generic_name',
        readonly=True
    )
    
    # Quantities
    quantity = fields.Float(
        string='Quantity Prescribed',
        required=True,
        default=1.0
    )
    quantity_dispensed = fields.Float(
        string='Quantity Dispensed',
        default=0.0
    )
    quantity_remaining = fields.Float(
        string='Remaining',
        compute='_compute_remaining',
        store=True
    )
    
    # Dosage Instructions
    dosage = fields.Char(
        string='Dosage',
        help='e.g., 500mg, 2 tablets'
    )
    frequency = fields.Char(
        string='Frequency',
        help='e.g., Twice daily, Every 8 hours'
    )
    duration = fields.Char(
        string='Duration',
        help='e.g., 7 days, 2 weeks'
    )
    route = fields.Selection([
        ('oral', 'Oral'),
        ('topical', 'Topical'),
        ('injection_im', 'Injection - Intramuscular'),
        ('injection_iv', 'Injection - Intravenous'),
        ('injection_sc', 'Injection - Subcutaneous'),
        ('inhalation', 'Inhalation'),
        ('rectal', 'Rectal'),
        ('vaginal', 'Vaginal'),
        ('ophthalmic', 'Ophthalmic (Eye)'),
        ('otic', 'Otic (Ear)'),
        ('nasal', 'Nasal'),
        ('sublingual', 'Sublingual'),
        ('transdermal', 'Transdermal'),
    ], string='Route of Administration')
    
    instructions = fields.Text(
        string='Instructions',
        help='Additional instructions for patient'
    )
    
    # Status
    fully_dispensed = fields.Boolean(
        string='Fully Dispensed',
        compute='_compute_fully_dispensed',
        store=True
    )
    
    @api.depends('quantity', 'quantity_dispensed')
    def _compute_remaining(self):
        """Calculate remaining quantity to dispense"""
        for line in self:
            line.quantity_remaining = line.quantity - line.quantity_dispensed
    
    @api.depends('quantity', 'quantity_dispensed')
    def _compute_fully_dispensed(self):
        """Check if line is fully dispensed"""
        for line in self:
            line.fully_dispensed = line.quantity_dispensed >= line.quantity
    
    @api.constrains('quantity', 'quantity_dispensed')
    def _check_quantities(self):
        """Ensure quantities are valid"""
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('Quantity prescribed must be positive'))
            if line.quantity_dispensed < 0:
                raise ValidationError(_('Quantity dispensed cannot be negative'))
            if line.quantity_dispensed > line.quantity:
                raise ValidationError(_('Cannot dispense more than prescribed quantity'))
