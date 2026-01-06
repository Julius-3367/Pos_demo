# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PrescriptionDispenseWizard(models.TransientModel):
    _name = 'prescription.dispense.wizard'
    _description = 'Prescription Dispensing Wizard'
    
    prescription_id = fields.Many2one(
        'pharmacy.prescription',
        string='Prescription',
        required=True
    )
    line_ids = fields.One2many(
        'prescription.dispense.wizard.line',
        'wizard_id',
        string='Items to Dispense'
    )
    
    @api.model
    def default_get(self, fields_list):
        """Populate wizard with prescription lines"""
        res = super().default_get(fields_list)
        
        if self.env.context.get('active_id'):
            prescription = self.env['pharmacy.prescription'].browse(
                self.env.context['active_id']
            )
            
            lines = []
            for line in prescription.line_ids:
                if line.quantity_remaining > 0:
                    lines.append((0, 0, {
                        'prescription_line_id': line.id,
                        'product_id': line.product_id.id,
                        'quantity_prescribed': line.quantity,
                        'quantity_already_dispensed': line.quantity_dispensed,
                        'quantity_to_dispense': line.quantity_remaining,
                    }))
            
            res.update({
                'prescription_id': prescription.id,
                'line_ids': lines,
            })
        
        return res
    
    def action_dispense(self):
        """Process dispensing"""
        self.ensure_one()
        
        # Create POS order or update prescription quantities
        # This is a placeholder - actual POS integration would be in JavaScript
        
        for line in self.line_ids:
            if line.quantity_to_dispense > 0:
                line.prescription_line_id.quantity_dispensed += line.quantity_to_dispense
        
        self.prescription_id.action_dispense()
        
        return {'type': 'ir.actions.act_window_close'}


class PrescriptionDispenseWizardLine(models.TransientModel):
    _name = 'prescription.dispense.wizard.line'
    _description = 'Prescription Dispensing Wizard Line'
    
    wizard_id = fields.Many2one(
        'prescription.dispense.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    prescription_line_id = fields.Many2one(
        'pharmacy.prescription.line',
        string='Prescription Line',
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    quantity_prescribed = fields.Float(
        string='Prescribed',
        readonly=True
    )
    quantity_already_dispensed = fields.Float(
        string='Already Dispensed',
        readonly=True
    )
    quantity_to_dispense = fields.Float(
        string='Quantity to Dispense',
        required=True
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Batch/Lot',
        domain="[('product_id', '=', product_id)]"
    )
