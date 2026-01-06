# Cashier Balance & Payment Mode Setup Guide

## Overview
This module now supports:
1. **Daily Session Balance Management** - Cashiers can open/close sessions with cash counting
2. **Multiple Payment Methods** - Cash, Card, M-PESA, and Insurance payments
3. **Insurance Integration** - Automatic insurance claim creation from payments

## Setup Instructions

### 1. Configure Payment Methods

#### Standard Payment Methods (Already in Odoo)
Navigate to: **Point of Sale > Configuration > Payment Methods**

Make sure you have these payment methods configured:
- **Cash** - Default cash payment
- **Card/Bank** - For card payments (Visa, Mastercard, etc.)
- **M-PESA** - Mobile money payment (set type as Bank)

#### Configure Insurance Payment Method

1. Go to **Point of Sale > Configuration > Payment Methods**
2. Click **Create**
3. Fill in the details:
   - **Name**: Insurance Payment (or NHIF, AAR, etc.)
   - **Type**: Bank (or create custom type)
   - **Is Insurance**: ☑️ Check this box
   - **Linked Insurance Providers**: Select applicable insurance providers
4. **Save**

You can create multiple insurance payment methods for different providers:
- NHIF Payment
- AAR Insurance Payment
- Jubilee Insurance Payment
- etc.

### 2. Assign Payment Methods to POS

1. Go to **Point of Sale > Configuration > Point of Sale**
2. Open your POS configuration
3. In the **Payments** tab:
   - Add all payment methods you want available (Cash, Card, M-PESA, Insurance)
4. **Save**

### 3. Enable Cash Control for Daily Balances

1. Go to **Point of Sale > Configuration > Point of Sale**
2. Open your POS configuration
3. Enable **Cash Control**: ☑️
   - This allows cashiers to open sessions with starting cash
   - And close sessions with cash counting
4. **Save**

## Daily Operations

### Opening a Session

1. Go to **Point of Sale > Cashier Sessions** or click "New Session"
2. Select your POS
3. Enter the **Opening Cash** amount (count your starting cash)
4. Add any **Opening Notes** if needed
5. Click **Open Session**

### Making Sales with Different Payment Methods

During sales in POS:
1. Add products to cart
2. Click **Payment**
3. Select payment method:
   - **Cash** - For cash payments
   - **Card** - For card payments
   - **M-PESA** - Enter M-PESA transaction ID
   - **Insurance** - Select insurance provider, enter member number

### Insurance Payments
When using insurance payment:
1. Select the insurance payment method
2. System will prompt for:
   - Insurance Provider (if not auto-filled)
   - Member/Policy Number
   - Pre-authorization number (optional)
3. System automatically creates an insurance claim
4. Patient co-pay (if any) should be collected via Cash/Card/M-PESA

### Closing a Session

1. Go to your open session
2. Click **Close**
3. System shows:
   - Total Sales
   - Expected Cash (based on cash transactions)
   - Card Total
   - M-PESA Total
   - Insurance Total
4. **Count Your Cash** and enter the amount in **Counted Cash**
5. System automatically calculates the **Cash Difference**
   - Green: Balanced (within 1 cent)
   - Red: Discrepancy detected
6. Add **Closing Notes** if there are any discrepancies
7. Click **Close Session**

## Session Summary Reports

After closing, you can view:
- **Total Sales** - All sales for the day
- **Prescription Sales** - Sales with prescription items
- **OTC Sales** - Over-the-counter sales
- **Insurance Sales** - Total insurance claims
- **Cash Difference** - Any cash over/short

Click **Insurance Claims** button to view all insurance claims for the session.

## Security & Permissions

### Cashier Role (group_pos_user)
- ✓ Open and close their own sessions
- ✓ Enter opening/closing cash amounts
- ✓ View their session summaries
- ✓ Process all payment types
- ✓ View insurance claims (read-only)

### Manager Role (group_pos_manager)
- ✓ All cashier permissions
- ✓ View all sessions
- ✓ Modify payment methods
- ✓ Manage insurance claims
- ✓ Full access to session reports

## Tips for Best Practices

1. **Always count cash at opening** - Prevents end-of-day discrepancies
2. **Record M-PESA transaction IDs** - For reconciliation and disputes
3. **Verify insurance details** - Member numbers and pre-auth before processing
4. **Document discrepancies** - Use closing notes to explain any cash differences
5. **Daily reconciliation** - Close sessions daily, don't leave them open overnight

## Troubleshooting

### Can't open session without opening cash
- Ensure Cash Control is enabled in POS configuration
- Enter a valid opening cash amount (can be 0)

### Insurance payment not creating claim
- Check that payment method has "Is Insurance" checked
- Ensure insurance provider is selected
- Verify customer is marked as patient

### Cash difference alerts
- Recount physical cash
- Check if all cash transactions are recorded
- Review if any transactions were recorded incorrectly
- Document variance in closing notes

## Sample Insurance Claim Workflow

1. Customer presents prescription + insurance card
2. Add prescription items to cart
3. Click Payment
4. Select "Insurance Payment" method
5. Enter:
   - Provider: NHIF
   - Member Number: 123456789
   - Pre-auth: (if applicable)
6. If there's a co-pay, add additional payment (Cash/Card/M-PESA)
7. Complete sale
8. System creates insurance claim automatically
9. Manager can submit claims to insurance provider later

## Report Access

- **Cashier Sessions**: Point of Sale > Cashier Sessions
- **Insurance Claims**: Reports > Insurance Claims Report
- **Daily Sales Summary**: Automatically shown in session closing
