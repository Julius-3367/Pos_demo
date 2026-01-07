# Complete Setup Guide - Pharmacy POS System

Follow these steps in order to fully configure your pharmacy Point of Sale system.

## Step 1: Install Chart of Accounts ✅ REQUIRED FIRST

1. **Access Odoo Web Interface:**
   - Open browser: http://localhost:8069
   - Login with admin credentials

2. **Install Accounting with Kenya Chart of Accounts:**
   - Click on **Apps** menu (grid icon in top left)
   - Search for "accounting"
   - Click **Install** on the "Accounting" app
   - During installation, it will ask you to configure:
     - **Company Name:** Options Pharmacy
     - **Country:** Kenya 🇰🇪
     - **Chart of Accounts:** Select "Kenya - Chart of Accounts"
     - **Bank Account:** Add your bank details (or skip for now)
   - Click **Apply**

## Step 2: Access Inventory and Purchase Apps

After installing accounting, you should see these menu items at the top:

- **Inventory** 📦 - Stock management, transfers, adjustments
- **Purchase** 🛒 - Purchase orders, vendors, goods receiving
- **Point of Sale** 🛍️ - Cashier interface (POS)
- **Accounting** 💰 - Invoices, payments, reports

**If you don't see them:** Click the grid icon (Apps menu) → search for "inventory" or "purchase" → click **Install**

## Step 3: Configure Point of Sale

### Option A: Automatic Configuration (After Chart of Accounts)

1. Uncomment this line in `__manifest__.py`:
   ```python
   'data/pos_config_data.xml',  # Uncomment this line
   ```

2. Upgrade the module:
   ```bash
   cd /opt/odoo/odoo
   python3 odoo-bin -d pharmacy_kenya -u pos_demo --db_host=localhost --db_user=julius --db_password=julius --addons-path=/opt/odoo/odoo/addons,/opt/odoo/odoo/addons/custom --stop-after-init
   ```

3. Start the server again

### Option B: Manual Configuration (Recommended for Learning)

1. Go to **Point of Sale → Configuration → Point of Sale**
2. Click **Create**
3. Configure as follows:

   **Basic Settings:**
   - Name: `Pharmacy Main Counter`
   - Available Products: `All products`
   
   **Cash Control:**
   - ✅ Enable **Cash Control** (track opening/closing balances)
   
   **Receipt:**
   - ✅ Enable **Automatic Receipt Printing**
   - Header:
     ```
     Options Pharmacy - Kenya
     Reg. No: PPB/PH/12345
     PIN: P051234567X
     Tel: +254 712 345 678
     ```
   - Footer:
     ```
     Thank you for your visit!
     For inquiries, call: +254 712 345 678
     Operating Hours: Mon-Sat 8:00-20:00
     ```
   
   **Payment Methods:**
   - Cash ✅ (automatically created)
   - Card ✅ (add if needed: Configuration → Payment Methods → Create)
   - Insurance ✅ (add custom: Configuration → Payment Methods → Create)

4. Click **Save**

## Step 4: Add Initial Stock via Purchase Orders

### 4.1 Create a Vendor/Supplier

1. Go to **Purchase → Configuration → Vendors** (or **Contacts**)
2. Click **Create**
3. Fill in:
   - Name: `Kenya Pharmaceutical Distributors`
   - Company Type: `Company`
   - Phone: `+254 20 123 4567`
   - Email: `sales@kpdistrib.co.ke`
4. Click **Save**

### 4.2 Create Products (If Not Already Loaded)

The test data already loaded these products:
- Paracetamol 500mg Tablets
- Amoxicillin 250mg Capsules
- Ciprofloxacin 500mg Tablets
- Metformin 500mg Tablets
- Salbutamol Inhaler 100mcg

Check: **Inventory → Products → Products**

### 4.3 Create a Purchase Order

1. Go to **Purchase → Orders → Purchase Orders**
2. Click **Create**
3. Fill in:
   - Vendor: `Kenya Pharmaceutical Distributors`
   - Products: Add lines with:
     - Product: `Paracetamol 500mg Tablets`
     - Quantity: `1000`
     - Unit Price: `5.00` KES
   - Repeat for other products
4. Click **Confirm Order**

### 4.4 Receive the Goods

1. Click **Receive Products** button (or go to **Inventory → Operations → Receipts**)
2. For each product line:
   - Click **Detailed Operations** (list icon)
   - Enter **Lot/Serial Number:** `BATCH2024001`
   - Enter **Expiry Date:** (e.g., December 31, 2026)
   - Confirm quantity received
3. Click **Validate** to complete receipt

### 4.5 Verify Stock Levels

1. Go to **Inventory → Products → Products**
2. Open any product (e.g., Paracetamol)
3. Check:
   - **On Hand:** Should show the quantity received
   - **Forecasted:** Should match on hand
4. Go to **Inventory → Reporting → Lots/Serial Numbers** to see batch tracking

## Step 5: Test Complete Cashier Workflow

### 5.1 Open POS Session

1. Go to **Point of Sale → Dashboard**
2. Click on your POS configuration: **Pharmacy Main Counter**
3. It will ask for **Opening Balance:**
   - Enter: `10,000.00` KES (starting cash in register)
   - Click **Open Session**

### 5.2 Sell Products (POS Interface)

1. You'll see the POS interface with:
   - Product categories on left
   - Products in center
   - Shopping cart on right

2. **Add products to cart:**
   - Click on `Paracetamol 500mg` → Select batch (if multiple)
   - Click on `Amoxicillin 250mg` 
   - Adjust quantities using +/- buttons

3. **Process Payment:**
   - Click **Payment** button (bottom right)
   - Select payment method:
     - **Cash:** Enter amount received (e.g., 1000 KES)
     - System shows change to give
   - Click **Validate**

4. **Print Receipt:**
   - Receipt prints automatically (if configured)
   - Or click **Print Receipt** button

5. **Repeat** for 5-10 sales transactions

### 5.3 Close POS Session

1. Click **☰** menu (top left) → **Close Session**
2. System shows:
   - **Expected Cash:** Opening balance + cash sales
   - **Counted Cash:** Enter actual cash in register (e.g., 15,450.00)
   - **Difference:** System calculates variance
3. Review:
   - Total sales
   - Payment method breakdown
   - Product quantities sold
4. Click **Close Session & Post Entries**

### 5.4 View Reports

1. Go to **Point of Sale → Reporting → Orders**
   - See all sales transactions
   - Filter by date, cashier, products

2. Go to **Point of Sale → Reporting → Sessions**
   - See session details
   - Cash flow analysis
   - Variance tracking

## Step 6: Test Pharmacy-Specific Features

### 6.1 Prescription Management

1. Go to **Pharmacy → Prescriptions**
2. Click **Create** → Fill in:
   - Patient Name: `John Kamau`
   - Date: Today
   - Doctor: `Dr. Sarah Mwangi`
   - Prescription Lines:
     - Drug: `Amoxicillin 250mg Capsules`
     - Dosage: `250mg`
     - Frequency: `3 times daily`
     - Duration: `7 days`
     - Quantity: `21` capsules
3. Click **Validate Prescription** (requires pharmacist role)
4. Click **Dispense** → This creates a POS order
5. Process payment in POS

### 6.2 Insurance Claims

1. Go to **Pharmacy → Insurance → Providers**
2. Verify NHIF and private insurers are loaded

3. Create a claim:
   - Go to **Pharmacy → Insurance → Claims**
   - Click **Create**
   - Patient: Select/create patient with insurance
   - Policy Number: `NHIF/12345678`
   - Items: Add prescribed medicines
   - Insurance Coverage: `80%` (patient pays 20%)
   - Click **Submit Claim**

### 6.3 Controlled Drugs Register (PPB Compliance)

1. Go to **Pharmacy → Controlled Drugs → Register**
2. Every sale of controlled drugs (Schedule 1/2) auto-records here
3. View entries:
   - Patient name
   - Doctor details
   - Drug, batch, quantity
   - Prescription reference

4. Generate PPB Report:
   - Go to **Pharmacy → Controlled Drugs → PPB Returns Report**
   - Select date range
   - Click **Generate Report**

### 6.4 Expiry Management (FEFO)

1. Go to **Inventory → Reporting → Lots/Serial Numbers**
2. Filter by **Expiry Date** to see batches expiring soon
3. System automatically suggests earliest expiry batch when selling (FEFO)

4. View expiring stock:
   - Go to **Pharmacy → Inventory → Expiring Stock**
   - Shows products expiring in next 180 days
   - Plan discounts or returns

## Troubleshooting

### Issue: "I don't see Inventory or Purchase menus"

**Solution:**
1. Go to **Apps** menu
2. Remove **Apps** filter
3. Search for "Inventory Management"
4. Click **Install**
5. Repeat for "Purchase" app

### Issue: "Cannot create POS config - no bank journal"

**Solution:**
1. You MUST install Chart of Accounts first (Step 1)
2. Go to **Accounting → Configuration → Journals**
3. Verify you have at least one Bank or Cash journal
4. If not: **Create → Type: Bank → Save**

### Issue: "Products not showing in POS"

**Solution:**
1. Check product is **Available in POS:**
   - Go to **Inventory → Products → Products**
   - Open product
   - Check **☑ Available in POS** is enabled
   - Check **Product Type** is `Storable Product`
2. Verify product has stock (On Hand > 0)

### Issue: "Cannot validate POS order - inventory error"

**Solution:**
1. Go to **Inventory → Configuration → Settings**
2. Enable **Storage Locations** (if using multiple locations)
3. Verify POS config has correct **Default Location** set
4. Check product has stock in that location

## Next Steps

✅ **System is now fully operational!**

### Recommended Actions:

1. **Add More Products:**
   - Import your full product catalog
   - Configure categories (Prescription, OTC, Medical Devices)
   - Set pricing and reorder levels

2. **Configure Users & Roles:**
   - Create cashier accounts (no back-office access)
   - Create pharmacist accounts (can validate prescriptions)
   - Set up access rights

3. **Setup Reorder Rules:**
   - Go to **Inventory → Configuration → Reorder Rules**
   - Set minimum stock levels
   - Auto-generate purchase orders when low

4. **Configure Barcode Scanner:**
   - Enable **Barcode** in Inventory settings
   - Print barcode labels for products
   - Use scanner in POS for faster checkout

5. **Customize Reports:**
   - Configure PPB monthly returns format
   - Setup automated email reports
   - Dashboard widgets for management

## Support

For issues or questions:
- Check Odoo Community Forum: https://www.odoo.com/forum
- Odoo Documentation: https://www.odoo.com/documentation/18.0
- Pharmacy Module Repository: [Your GitHub Repo]

---

**Last Updated:** January 7, 2026
**Module Version:** 18.0.1.0.0
**Odoo Version:** 18.0 Community
