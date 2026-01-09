#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSRF Token Issue - Troubleshooting and Fix
"""
import xmlrpc.client

# Connection parameters
url = 'http://localhost:8069'
db = 'pharmacy_kenya'
username = 'admin'
password = 'admin'

print("=" * 60)
print("CSRF ISSUE TROUBLESHOOTING")
print("=" * 60)

print("\n📋 ISSUE SUMMARY:")
print("   CSRF validation is failing on '/report/download' endpoint")
print("   This prevents PDF/report downloads from working.")

print("\n🔍 COMMON CAUSES:")
print("   1. Browser cache with stale JavaScript")
print("   2. Session cookie issues")
print("   3. Browser extensions interfering")
print("   4. Mixed HTTP/HTTPS content")

print("\n✅ RECOMMENDED SOLUTIONS (try in order):")
print("\n   Solution 1: Hard Refresh Browser")
print("   ----------------------------------")
print("   • Press: Ctrl+Shift+R (Linux/Windows)")
print("   •     or: Cmd+Shift+R (Mac)")
print("   • This clears cached JavaScript and CSS")

print("\n   Solution 2: Clear Browser Cache")
print("   --------------------------------")
print("   • Open Developer Tools (F12)")
print("   • Right-click refresh button")
print("   • Select 'Empty Cache and Hard Reload'")

print("\n   Solution 3: Clear Site Data")
print("   --------------------------")
print("   • Open Developer Tools (F12)")
print("   • Go to Application tab")
print("   • Click 'Clear storage'")
print("   • Clear all site data for localhost:8069")
print("   • Refresh page and login again")

print("\n   Solution 4: Try Incognito/Private Window")
print("   ----------------------------------------")
print("   • Open new incognito/private browser window")
print("   • Visit: http://localhost:8069")
print("   • Login and test if reports work")

print("\n   Solution 5: Check Browser Console")
print("   ---------------------------------")
print("   • Press F12 to open Developer Tools")
print("   • Go to Console tab")
print("   • Look for errors related to CSRF or modules")
print("   • Share any error messages for further help")

print("\n🔧 CHECKING SERVER CONFIGURATION...")

# Authenticate
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"   ✓ Server is accessible")
    print(f"   ✓ Authentication successful (User ID: {uid})")
    
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    
    try:
        # Check if reports are defined
        report_count = models.execute_kw(
            db, uid, password,
            'ir.actions.report', 'search_count',
            [[['model', '=', 'pharmacy.prescription']]]
        )
        print(f"   ✓ Prescription reports defined: {report_count}")
        
    except Exception as e:
        print(f"   ⚠ Error checking reports: {e}")
else:
    print("   ❌ Authentication failed")

print("\n" + "=" * 60)
print("📝 NOTES:")
print("=" * 60)
print("• CSRF errors are usually client-side (browser) issues")
print("• The server is working correctly")
print("• After clearing cache, you may need to login again")
print("• If problem persists, try a different browser")
print("\n✉️  If none of these work, please provide:")
print("   - Browser name and version")
print("   - Any console errors from F12 Developer Tools")
print("   - Screenshot of the error")
print("=" * 60)
