# Quick Start: Getting Shop & Inventory Menus Visible

## Current Status ✅
- ✅ Server running at: http://localhost:8069
- ✅ All modules installed: Accounting, Inventory, Purchase, Point of Sale
- ✅ Pharmacy module loaded

## Problem
You don't see **Inventory** or **Point of Sale** menus in the Odoo interface.

## Solution: 3-Step Quick Fix

### Step 1: Access Odoo Web Interface

1. Open your browser
2. Go to: **http://localhost:8069**
3. Login:
   - Username: `admin`
   - Password: `admin` (or whatever password you set)

### Step 2: Install Chart of Accounts (REQUIRED)

**Why?** POS requires a bank/cash journal which is created by the accounting chart.

1. **Click the grid icon** (☰) in top-left → **Apps**
2. **Remove the "Apps" filter** (click the X on the "Apps" pill/tag)
3. **Search**: Type "accounting" in the search box
4. **Find "Accounting"** app (with calculator icon)
5. **Click "Activate"** or **"Install"**
6. A wizard appears:
   - **Company Name**: Options Pharmacy
   - **Country**: 🇰🇪 Kenya
   - **Chart of Accounts**: Select "Kenya - Chart of Accounts"
   - Click **Apply**
7. Wait for installation (~30-60 seconds)

### Step 3: Verify Menus are Now Visible

After accounting is installed, refresh the page. You should now see:

**Top Menu Bar:**
- 🏠 **Discuss**
- 📧 **Contacts**
- 📦 **Inventory** ← YOU NEED THIS
- 🛒 **Purchase** ← YOU NEED THIS  
- 🛍️ **Point of Sale** ← YOU NEED THIS
- 💰 **Accounting** ← NEW
- ⚙️ **Settings**

**If you still don't see them:**

1. Click **Grid Icon** (☰) → **Apps**
2. Remove "Apps" filter
3. Search for **"Inventory Management"**
4. Click **Install** (if not already)
5. Search for **"Purchase"**
6. Click **Install** (if not already)
7. Search for **"Point of Sale"**
8. Click **Install** (if not already)

---

## What To Do Next

Once you see the menus, follow the [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md) starting from **Step 3**.

Or quick path:

### Quick Path: Get Selling FAST

1. **Create POS Config:**
   - Point of Sale → Configuration → Point of Sale
   - Click Create
   - Name: `Main Counter`
   - Enable: Cash Control ✅
   - Save

2. **Open POS:**
   - Point of Sale → Dashboard
   - Click your config
   - Enter opening balance: `10000`
   - Start selling!

3. **If no products visible in POS:**
   - The test data loaded products (Paracetamol, Amoxicillin, etc.)
   - But they have ZERO stock
   - You need to add stock first (see below)

### Adding Stock Without Purchase Orders (Quick Method)

1. **Go to:** Inventory → Operations → Inventory Adjustments
2. **Click:** Create
3. **Add products:**
   - Product: Paracetamol 500mg Tablets
   - Counted Quantity: 1000
   - Lot/Batch: BATCH2024001
4. **Click:** Apply
5. **Repeat** for other products
6. Now products will show in POS!

---

## Troubleshooting

**"I clicked Install on Accounting but nothing happened"**
- Wait 30 seconds - installation takes time
- Check bottom-right corner for progress indicator
- Refresh the browser page

**"Apps button doesn't show apps, only shows blank"**
- Click the search bar
- Remove the "Apps" filter (there's an X on it)
- Now you see all modules

**"I see the menus but Point of Sale is greyed out"**
- You need to create a POS configuration first
- Point of Sale → Configuration → Point of Sale → Create

**"Products don't show in POS"**
- Products need stock (On Hand > 0)
- Use Inventory Adjustment (quick method above)
- Or create Purchase Order (proper method in full guide)

---

**Current Date:** January 7, 2026
**Server:** http://localhost:8069
**Database:** pharmacy_kenya
**Module:** pos_demo v18.0.1.0.0
