# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ControlledDrugsRegister(models.Model):
    _name = 'controlled.drugs.register'
    _description = 'Controlled Drugs Register (PPB Requirement)'
    _order = 'date desc, id desc'
    
    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now,
        index=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Controlled Drug',
        required=True,
        domain=[('is_controlled_substance', '=', True)],
        index=True
    )
    product_generic_name = fields.Char(
        string='Generic Name',
        related='product_id.product_tmpl_id.drug_generic_name',
        readonly=True
    )
    product_strength = fields.Char(
        string='Strength',
        related='product_id.product_tmpl_id.drug_strength',
        readonly=True
    )
    drug_schedule = fields.Selection(
        string='Schedule',
        related='product_id.product_tmpl_id.drug_schedule',
        readonly=True
    )
    
    # Transaction Type
    transaction_type = fields.Selection([
        ('receipt', 'Receipt/Purchase'),
        ('dispensing', 'Dispensing'),
        ('return', 'Return from Patient'),
        ('destruction', 'Destruction/Disposal'),
        ('adjustment', 'Stock Adjustment'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
    ], string='Transaction Type', required=True)
    
    # Quantities
    quantity_received = fields.Float(
        string='Quantity Received',
        help='Quantity received (purchases, returns, transfers in)'
    )
    quantity_dispensed = fields.Float(
        string='Quantity Dispensed',
        help='Quantity dispensed (sales, transfers out, destruction)'
    )
    running_balance = fields.Float(
        string='Running Balance',
        help='Calculated running balance after this transaction'
    )
    
    # Prescription Details (for dispensing transactions)
    prescription_id = fields.Many2one(
        'pharmacy.prescription',
        string='Prescription Reference'
    )
    patient_name = fields.Char(string='Patient Name')
    patient_id_number = fields.Char(
        string='Patient ID Number',
        help='National ID or Passport'
    )
    prescriber_name = fields.Char(string='Prescriber Name')
    prescriber_license = fields.Char(string='Prescriber License No.')
    
    # Purchase/Receipt Details
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier_rank', '>', 0)]
    )
    purchase_order_ref = fields.Char(string='Purchase Order Reference')
    invoice_ref = fields.Char(string='Invoice Reference')
    lot_id = fields.Many2one(
        'stock.lot',
        string='Batch/Lot',
        domain="[('product_id', '=', product_id)]"
    )
    
    # Authorization & Compliance
    authorized_by = fields.Many2one(
        'res.users',
        string='Authorized/Recorded By',
        default=lambda self: self.env.user,
        required=True
    )
    witnessed_by = fields.Many2one(
        'res.users',
        string='Witnessed By',
        help='Second person witness (required for destruction)'
    )
    remarks = fields.Text(
        string='Remarks',
        help='Additional notes or reasons'
    )
    
    # Links to source documents
    pos_order_id = fields.Many2one(
        'pos.order',
        string='POS Order',
        readonly=True
    )
    stock_picking_id = fields.Many2one(
        'stock.picking',
        string='Stock Transfer',
        readonly=True
    )
    
    @api.model
    def create(self, vals):
        """Calculate running balance on creation"""
        record = super().create(vals)
        record._compute_running_balance()
        return record
    
    def write(self, vals):
        """Recalculate running balance on updates"""
        res = super().write(vals)
        if any(field in vals for field in ['quantity_received', 'quantity_dispensed', 'date', 'product_id']):
            self._compute_running_balance()
        return res
    
    def _compute_running_balance(self):
        """Calculate running balance for each product"""
        for record in self:
            # Get all previous transactions for this product
            previous_records = self.search([
                ('product_id', '=', record.product_id.id),
                ('date', '<', record.date),
            ], order='date asc, id asc')
            
            # Calculate balance
            balance = 0.0
            for prev in previous_records:
                balance += (prev.quantity_received or 0.0)
                balance -= (prev.quantity_dispensed or 0.0)
            
            # Add current transaction
            balance += (record.quantity_received or 0.0)
            balance -= (record.quantity_dispensed or 0.0)
            
            record.running_balance = balance
            
            # Update subsequent records
            subsequent_records = self.search([
                ('product_id', '=', record.product_id.id),
                ('date', '>', record.date),
            ], order='date asc, id asc')
            
            for subsequent in subsequent_records:
                balance += (subsequent.quantity_received or 0.0)
                balance -= (subsequent.quantity_dispensed or 0.0)
                subsequent.running_balance = balance
    
    @api.constrains('quantity_received', 'quantity_dispensed', 'transaction_type')
    def _check_quantities(self):
        """Validate quantities based on transaction type"""
        for record in self:
            if record.transaction_type in ['receipt', 'return', 'transfer_in', 'adjustment']:
                if not record.quantity_received or record.quantity_received <= 0:
                    raise ValidationError(
                        _('Quantity received must be positive for %s transactions') % record.transaction_type
                    )
                if record.quantity_dispensed:
                    raise ValidationError(
                        _('Quantity dispensed should be zero for %s transactions') % record.transaction_type
                    )
            
            elif record.transaction_type in ['dispensing', 'destruction', 'transfer_out']:
                if not record.quantity_dispensed or record.quantity_dispensed <= 0:
                    raise ValidationError(
                        _('Quantity dispensed must be positive for %s transactions') % record.transaction_type
                    )
                if record.quantity_received:
                    raise ValidationError(
                        _('Quantity received should be zero for %s transactions') % record.transaction_type
                    )
    
    @api.constrains('transaction_type', 'prescription_id', 'patient_name')
    def _check_dispensing_requirements(self):
        """Ensure dispensing transactions have required patient info"""
        for record in self:
            if record.transaction_type == 'dispensing':
                if not record.patient_name:
                    raise ValidationError(
                        _('Patient name is required for dispensing transactions')
                    )
                if not record.prescriber_name:
                    raise ValidationError(
                        _('Prescriber name is required for dispensing transactions')
                    )
    
    @api.constrains('transaction_type', 'witnessed_by')
    def _check_destruction_witness(self):
        """Ensure destruction transactions have a witness"""
        for record in self:
            if record.transaction_type == 'destruction':
                if not record.witnessed_by:
                    raise ValidationError(
                        _('Destruction transactions must be witnessed by a second person')
                    )
                if record.witnessed_by == record.authorized_by:
                    raise ValidationError(
                        _('Witness must be different from the person recording the destruction')
                    )
