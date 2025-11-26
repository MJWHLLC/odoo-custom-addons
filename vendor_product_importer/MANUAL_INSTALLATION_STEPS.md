# Manual Installation Steps for Vendor Product Importer

## ✅ Prerequisites Completed
- ✅ Module files created in: `C:/Users/MJWil/odoo_custom_addons/vendor_product_importer/`
- ✅ Python dependencies installed: `beautifulsoup4`, `lxml`
- ✅ Odoo server is running on port 8069

---

## 🚀 Installation Steps

### Option A: Install via Odoo Web Interface (Recommended)

#### Step 1: Restart Odoo Service (Requires Admin)
**Open Command Prompt as Administrator** and run:
```cmd
net stop odoo-server-17.0
net start odoo-server-17.0
```

Or use Services Manager:
1. Press `Win + R`, type `services.msc`, press Enter
2. Find "odoo-server-17.0"
3. Right-click → Restart

#### Step 2: Access Odoo
1. Open browser: http://localhost:8069
2. Login with your admin credentials

#### Step 3: Enable Developer Mode
1. Go to Settings (⚙️ icon)
2. Scroll down to "Developer Tools"
3. Click "Activate the developer mode"

#### Step 4: Update Apps List
1. Go to Apps menu
2. Click "Update Apps List" button (top-right)
3. Click "Update" in the confirmation dialog
4. Wait for the update to complete

#### Step 5: Install the Module
1. In Apps menu, remove the "Apps" filter
2. Search for "Vendor Product Importer"
3. Click "Install" button
4. Wait for installation to complete

#### Step 6: Verify Installation
1. Check that "Vendor Importer" menu appears in the main menu
2. Go to Vendor Importer → Configuration → Price Tiers
3. Verify 4 default price tiers are loaded

---

### Option B: Install via Command Line

#### Step 1: Stop Odoo Service (Requires Admin)
```cmd
net stop odoo-server-17.0
```

#### Step 2: Install Module via CLI
```cmd
cd "C:\Program Files\Odoo 17.0.20250119\server"
python odoo-bin -c odoo.conf -d YOUR_DATABASE_NAME -i vendor_product_importer --stop-after-init
```

Replace `YOUR_DATABASE_NAME` with your actual database name.

#### Step 3: Start Odoo Service
```cmd
net start odoo-server-17.0
```

#### Step 4: Verify Installation
1. Open browser: http://localhost:8069
2. Login and check "Vendor Importer" menu

---

## 🔍 Troubleshooting

### Module Not Appearing in Apps List

**Solution 1: Clear Browser Cache**
- Press `Ctrl + Shift + Delete`
- Clear cache and reload

**Solution 2: Check Module Path**
```cmd
# Verify module exists
dir "C:\Users\MJWil\odoo_custom_addons\vendor_product_importer"
```

**Solution 3: Check odoo.conf**
- Open: `C:\Program Files\Odoo 17.0.20250119\server\odoo.conf`
- Verify line: `addons_path = c:\program files\odoo 17.0.20250119\server\odoo\addons,C:\Users\MJWil\odoo_custom_addons`

### Installation Errors

**Check Odoo Log:**
```cmd
type "C:\Program Files\Odoo 17.0.20250119\server\odoo.log"
```

**Common Issues:**

1. **Missing Dependencies**
   ```cmd
   pip install beautifulsoup4 lxml requests
   ```

2. **Python Syntax Errors**
   - Check odoo.log for specific file and line number
   - Review the error message

3. **XML Parsing Errors**
   - Check odoo.log for XML file name
   - Verify XML syntax is correct

4. **Database Errors**
   - Ensure PostgreSQL service is running
   - Check database connection in odoo.conf

---

## ✅ Post-Installation Checklist

After successful installation:

- [ ] "Vendor Importer" menu appears
- [ ] Can access Vendors → Vendors
- [ ] Can access Configuration → Price Tiers
- [ ] 4 default price tiers are visible
- [ ] Can create a new vendor
- [ ] No errors in odoo.log

---

## 🎯 Quick Start After Installation

### 1. Review Default Price Tiers
- Go to: Vendor Importer → Configuration → Price Tiers
- Review the 4 default tiers:
  - Tier 1: $0-$50 (40% markup)
  - Tier 2: $51-$200 (30% markup)
  - Tier 3: $201-$500 (25% markup)
  - Tier 4: $501+ (20% markup)

### 2. Create Your First Vendor
- Go to: Vendor Importer → Vendors → Vendors
- Click "Create"
- Fill in:
  - Name: e.g., "Amazon US"
  - Vendor Type: "Amazon"
  - Website URL: https://www.amazon.com
  - API Configuration (if you have credentials)

### 3. Test Connection
- Click "Test Connection" button
- Verify connection succeeds

### 4. Run First Import
- Click "Import Products" button
- Configure import settings
- Click "Preview" to see what will be imported
- Click "Import" to execute

### 5. Review Results
- Go to: Vendor Importer → Vendors → Import Logs
- Check statistics and any errors
- Go to: Vendor Importer → Products → Imported Products
- Verify products were created

---

## 📞 Need Help?

If you encounter issues:

1. **Check Odoo Log:**
   ```
   C:\Program Files\Odoo 17.0.20250119\server\odoo.log
   ```

2. **Check Module Files:**
   ```
   C:\Users\MJWil\odoo_custom_addons\vendor_product_importer\
   ```

3. **Verify Dependencies:**
   ```cmd
   pip list | findstr "beautifulsoup4 lxml requests"
   ```

4. **Check Service Status:**
   ```cmd
   sc query odoo-server-17.0
   ```

---

## 🎉 Success!

Once installed, you'll have:
- ✅ Multi-vendor product import system
- ✅ Automated tiered pricing
- ✅ Weekly scheduled imports
- ✅ Comprehensive logging
- ✅ Complete user interface

**Ready to import products and maintain profitable pricing!**
