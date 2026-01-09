# CSRF Error Quick Fix Guide

## Error Message
```
RPC_ERROR
400 Bad Request
Session expired (invalid CSRF token)
```

## What Happened
The CSRF (Cross-Site Request Forgery) validation failed when trying to download a report or perform certain actions. This is typically a **browser-side issue** caused by cached JavaScript files.

## Quick Fixes (Try in Order)

### ✅ Fix 1: Hard Refresh (FASTEST)
**Do this first - works 90% of the time**

- **Linux/Windows:** Press `Ctrl + Shift + R`
- **Mac:** Press `Cmd + Shift + R`
- **What it does:** Clears browser cache and reloads all JavaScript

### ✅ Fix 2: Clear Browser Cache
1. Press `F12` to open Developer Tools
2. Right-click the refresh button in browser
3. Select "Empty Cache and Hard Reload"
4. Close Developer Tools

### ✅ Fix 3: Clear All Site Data
1. Press `F12` to open Developer Tools  
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Click "Clear storage" or "Clear site data"
4. Select all options
5. Click "Clear site data"
6. Refresh and login again

### ✅ Fix 4: Try Incognito/Private Window
1. Open new Incognito/Private browser window
2. Visit: `http://localhost:8069`
3. Login with admin/admin
4. Test if the issue persists

### ✅ Fix 5: Restart Browser
1. Close ALL browser windows
2. Reopen browser
3. Visit: `http://localhost:8069`

## What We Did on the Server
✅ Restarted Odoo to regenerate all assets  
✅ Verified reports are properly configured  
✅ Confirmed server is working correctly  

## Why This Happens
- Browser caches old JavaScript files
- Session cookies become stale
- Browser extensions interfere
- Multiple tabs with different sessions

## Prevention
- Always use hard refresh after server updates
- Close all tabs when logging out
- Avoid using multiple tabs with the same user

## Still Not Working?
Check the browser console for errors:
1. Press `F12`
2. Go to **Console** tab
3. Look for red error messages
4. Share the error details

---

**Last Updated:** January 8, 2026  
**Server Status:** ✅ Running and healthy
