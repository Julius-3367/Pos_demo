# Pos Demo - Pharmacy Point of Sale Module for Odoo 18

## Overview

A comprehensive Pharmacy Point of Sale extension for Odoo 18, specifically designed for pharmacies in Kenya. This module extends Odoo's native POS functionality with pharmacy-specific features while ensuring compliance with Kenyan pharmaceutical and tax regulations.

## Features

### 📋 Prescription Management
- **Digital Prescription Tracking**: Create, validate, and track prescriptions
- **Pharmacist Validation**: Require pharmacist approval for prescription-only medicines
- **Prescription Dispensing**: Track dispensed quantities against prescribed amounts
- **Prescription History**: View patient prescription history

### 💊 Pharmaceutical Product Management
- **Drug Classification**: PPB drug schedules (Schedule 1, 2, POM, P, OTC)
- **Clinical Information**: Active ingredients, contraindications, drug interactions
- **Storage Requirements**: Temperature and special storage tracking
- **Generic Names**: Track both brand and generic drug names

### 📦 Batch & Expiry Management
- **Lot/Batch Tracking**: Track medication batches with manufacturing and expiry dates
- **FEFO Logic**: First Expired, First Out inventory management
- **Expiry Alerts**: Automatic alerts for products expiring within 6 months
- **Expiry Reports**: View expiring and expired products

### 🏥 Insurance Claims Processing
- **Multiple Providers**: Support for NHIF and private insurance companies
- **Automated Claims**: Auto-generate insurance claims from POS orders
- **Co-payment Calculation**: Automatic patient co-payment calculation
- **Claim Tracking**: Track claim status from submission to payment
- **Pre-authorization**: Support for pre-authorization requirements

### 🔒 Controlled Drugs Register
- **PPB Compliance**: Automatic controlled drugs register as per PPB requirements
- **Automatic Entries**: Auto-create register entries on dispensing
- **Transaction Tracking**: Track receipts, dispensing, returns, destruction
- **Running Balance**: Maintain running balance for each controlled substance
- **Audit Trail**: Complete audit trail with authorization tracking

### 👥 Patient Management
- **Patient Records**: Comprehensive patient profiles
- **Allergy Tracking**: Record and display patient allergies
- **Medical History**: Track chronic conditions and medical history
- **Drug Interaction Checking**: Check for potential interactions with recent purchases
- **Insurance Information**: Store patient insurance details

### 💳 Payment Integration
- **M-PESA Integration**: STK Push payment support (configurable)
- **Multiple Payment Methods**: Cash, card, M-PESA, insurance
- **KRA ETR**: Electronic Tax Register integration (configurable)

### 📊 Reports & Compliance
- **PPB Monthly Returns**: Generate PPB-required monthly reports
- **Controlled Drugs Report**: Detailed controlled substances register
- **Insurance Claims Summary**: Claims by provider and status
- **Expiry Analysis**: Products expiring within specified periods
- **Therapeutic Class Sales**: Sales analysis by therapeutic category

## Installation

### Prerequisites
- Odoo 18.0
- Python 3.10+
- PostgreSQL 12+

### Installation Steps

1. **Copy Module to Addons Directory**
   ```bash
   cp -r Pos_demo /opt/odoo/odoo/addons/custom/
   ```

2. **Update Apps List**
   - Go to Odoo Apps menu
   - Click "Update Apps List"

3. **Install Module**
   - Search for "Pos Demo - Pharmacy Point of Sale"
   - Click "Install"

4. **Configure POS**
   - Go to Point of Sale > Configuration > Point of Sale
   - Open your POS configuration
   - Go to "Pharmacy Settings" tab
   - Enable "Pharmacy POS"
   - Configure settings as needed

## Configuration

### Basic Pharmacy Setup

1. **Enable Pharmacy Features**
   - POS > Configuration > Point of Sale > [Your POS] > Pharmacy Settings
   - Check "Pharmacy POS"
   - Enable desired features (prescription check, expiry check, etc.)

2. **Set Up Insurance Providers**
   - Pharmacy > Insurance > Insurance Providers
   - Add your insurance providers (NHIF, AAR, Britam, etc.)
   - Configure co-payment percentages and claim submission methods

3. **Configure Product Categories**
   - Products > Configuration > Product Categories
   - Use provided pharmaceutical categories or create custom ones

4. **Set Up Products**
   - For each pharmaceutical product:
     - Check "Is Pharmaceutical Product"
     - Fill in generic name, strength, dosage form
     - Select drug schedule (PPB classification)
     - Add clinical information

### User Roles & Permissions

The module provides 4 user groups:

1. **Pharmacy Cashier**: Basic POS access
2. **Pharmacy Technician**: Can manage inventory and create prescriptions
3. **Pharmacist**: Can validate prescriptions and access controlled drugs register
4. **Pharmacy Manager**: Full access to all pharmacy features

Assign users to appropriate groups in Settings > Users & Companies > Users

### M-PESA Configuration (Optional)

1. Go to POS Configuration > Pharmacy Settings > M-PESA Configuration
2. Enable M-PESA
3. Enter:
   - Paybill/Till Number
   - Consumer Key
   - Consumer Secret
   - Passkey
4. Select environment (Sandbox/Production)

### KRA ETR Configuration (Optional)

1. Go to POS Configuration > Pharmacy Settings > KRA ETR Integration
2. Enable ETR
3. Enter ETR Control Unit Serial Number
4. Configure API URL (if using API integration)

## Usage

### Creating a Prescription

1. Go to Pharmacy > Prescriptions
2. Click "Create"
3. Select patient and prescriber
4. Add prescription lines with:
   - Medication
   - Quantity
   - Dosage instructions
   - Frequency and duration
5. Save

### Dispensing from POS

1. Open POS
2. Select customer/patient
3. Add products to cart
4. For prescription items:
   - System will prompt for prescription selection
   - Select appropriate prescription
5. Process payment
6. Prescription quantities are automatically updated

### Processing Insurance Claims

1. **Automatic Method** (if enabled):
   - Claims are auto-created on order confirmation
   - No manual intervention needed

2. **Manual Method**:
   - Go to Pharmacy > Insurance > Insurance Claims
   - Create new claim
   - Link to POS order
   - Enter patient and insurance details
   - Submit claim

### Viewing Controlled Drugs Register

1. Go to Pharmacy > Controlled Drugs Register
2. View all transactions for controlled substances
3. Filter by product, date range, or transaction type
4. Export for PPB compliance

## Data Models

### Main Models

- `pharmacy.prescription`: Prescription records
- `pharmacy.prescription.line`: Individual prescription items
- `insurance.provider`: Insurance company details
- `insurance.claim`: Insurance claims
- `insurance.claim.line`: Claim line items
- `controlled.drugs.register`: PPB-required controlled drugs register

### Extended Models

- `product.template`: Added pharmaceutical fields
- `product.product`: Added manufacturer tracking
- `stock.lot`: Added expiry tracking and alerts
- `res.partner`: Added patient and prescriber information
- `pos.order`: Added prescription and insurance fields
- `pos.config`: Added pharmacy configuration

## Reports

### Available Reports

1. **Prescription Report**: Printable prescription with patient details
2. **Controlled Drugs Register**: PPB-compliant register report
3. **PPB Monthly Returns**: Monthly controlled substances report
4. **Insurance Claims Report**: Claim summary by provider
5. **Expiry Analysis**: Products expiring within specified period

### Generating Reports

- Go to the relevant menu
- Select record(s)
- Click "Print" > Select report type

## Compliance

### Kenya Pharmacy and Poisons Board (PPB)

- Drug classification according to PPB schedules
- Controlled drugs register maintenance
- Monthly returns reporting
- Prescription tracking and validation

### Kenya Revenue Authority (KRA)

- ETR integration support
- VAT handling
- Receipt generation with QR codes

### Data Protection

- Patient data encryption
- Access controls
- Audit trails
- GDPR/Data Protection Act compliance

## Troubleshooting

### Common Issues

1. **Prescription validation failing**
   - Ensure user has "Pharmacist" role
   - Check prescription is in "draft" state

2. **Insurance claim not created**
   - Verify insurance provider is configured
   - Check auto-create setting in POS config
   - Ensure patient has insurance details

3. **Expiry alerts not showing**
   - Verify expiry check is enabled in POS config
   - Check lot/batch has expiry date set
   - Ensure expiry warning days is configured

4. **M-PESA payment failing**
   - Verify M-PESA credentials are correct
   - Check phone number format (254XXXXXXXXX)
   - Ensure API endpoints are reachable

## Support & Development

### Technical Requirements

- Odoo 18.0
- Python libraries: standard Odoo dependencies
- External APIs (optional):
  - Safaricom Daraja API for M-PESA
  - KRA TIMS API for ETR
  - Insurance provider APIs

### Customization

The module is designed to be customizable. Common customization points:

- Additional drug schedules or classifications
- Custom insurance claim formats
- Modified prescription templates
- Extended patient information
- Additional reports

### Future Enhancements

Planned features:
- Electronic prescription transmission
- Real-time insurance eligibility verification
- Inventory forecasting based on prescription patterns
- Drug interaction database integration
- Multi-location pharmacy management

## License

LGPL-3

## Credits

**Author**: Your Company
**Version**: 18.0.1.0.0
**Date**: January 6, 2026
**Prepared for**: Options Pharmacy, Kenya

---

For support, contact your Odoo administrator or module developer.
