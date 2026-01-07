# -*- coding: utf-8 -*-
{
    'name': 'Pos Demo - Pharmacy Point of Sale',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Comprehensive Pharmacy POS for Kenyan pharmacies with prescription management, insurance claims, and PPB compliance',
    'description': """
        Pharmacy Point of Sale Module for Odoo 18
        ==========================================
        
        Features:
        ---------
        * Prescription Management
        * Insurance Claims Processing (NHIF & Private)
        * Controlled Drugs Register (PPB Compliance)
        * Expiry Date Management (FEFO)
        * Patient Records & Allergy Alerts
        * Drug Interaction Warnings
        * Batch/Lot Tracking with Expiry Dates
        * Pharmacist Validation Workflow
        * PPB Monthly Returns Reports
        * Purchase Order Management
        * Inventory Valuation & Stock Control
        * Barcode Support
        
        Designed for: Options Pharmacy, Kenya
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'stock',
        'stock_account',
        'purchase',
        'purchase_stock',
        'product',
        'account',
        'sale',
        'contacts',
        'web',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/product_categories.xml',
        'data/drug_schedules.xml',
        'data/insurance_providers.xml',
        'data/sequence.xml',
        'data/payment_methods.xml',
        # 'data/pos_config_data.xml',  # Install chart of accounts first, then uncomment and upgrade
        'data/test_data_kenya.xml',
        
        # Views
        'views/product_views.xml',
        'views/prescription_views.xml',
        'views/pos_config_views.xml',
        'views/pos_session_views.xml',
        'views/insurance_views.xml',
        'views/controlled_drugs_views.xml',
        'views/res_partner_views.xml',
        'views/accounting_views.xml',
        'views/reports_menu.xml',
        'views/demo_data_views.xml',
        
        # Reports
        'reports/prescription_report.xml',
        'reports/controlled_drugs_report.xml',
        'reports/ppb_returns.xml',
        'reports/insurance_claims_report.xml',
        
        # Wizards
        # 'wizard/prescription_wizard_views.xml',  # Temporarily disabled
        'wizard/insurance_claim_wizard_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_demo/static/src/js/**/*',
            'pos_demo/static/src/xml/**/*',
            'pos_demo/static/src/css/**/*',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
