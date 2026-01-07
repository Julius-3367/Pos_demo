# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PharmacyPOSController(http.Controller):
    
    @http.route('/pos_demo/verify_insurance', type='json', auth='user')
    def verify_insurance_eligibility(self, member_number, provider_id):
        """
        Verify insurance eligibility via API integration
        
        Args:
            member_number: Insurance member/policy number
            provider_id: Insurance provider ID
            
        Returns:
            dict: Eligibility status and coverage details
        """
        try:
            provider = request.env['insurance.provider'].browse(provider_id)
            
            if not provider.exists():
                return {'error': 'Invalid insurance provider'}
            
            # TODO: Implement actual API integration based on provider
            # For now, return mock verification
            
            if provider.claim_submission_method == 'api' and provider.api_endpoint:
                # API integration logic here
                pass
            
            # Mock response
            return {
                'eligible': True,
                'coverage_percentage': provider.coverage_percentage,
                'copay_percentage': provider.copay_percentage,
                'requires_preauth': provider.requires_preauth,
                'preauth_threshold': provider.preauth_threshold,
                'member_name': 'Verified Member',
                'valid_until': '2026-12-31',
            }
            
        except Exception as e:
            _logger.error(f"Insurance verification error: {str(e)}")
            return {'error': str(e)}
    
    @http.route('/pos_demo/get_patient_history', type='json', auth='user')
    def get_patient_purchase_history(self, patient_id, days=30):
        """
        Get patient's recent purchase history for interaction checking
        
        Args:
            patient_id: Partner/patient ID
            days: Number of days to look back
            
        Returns:
            dict: Recent purchases
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            orders = request.env['pos.order'].search([
                ('partner_id', '=', patient_id),
                ('date_order', '>=', cutoff_date),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ], order='date_order desc')
            
            products = []
            for order in orders:
                for line in order.lines:
                    if line.product_id.is_pharmaceutical:
                        products.append({
                            'product_id': line.product_id.id,
                            'product_name': line.product_id.name,
                            'generic_name': line.product_id.product_tmpl_id.drug_generic_name,
                            'date': order.date_order.strftime('%Y-%m-%d'),
                            'interactions': line.product_id.product_tmpl_id.drug_interactions,
                        })
            
            return {'products': products}
            
        except Exception as e:
            _logger.error(f"Patient history error: {str(e)}")
            return {'error': str(e)}
