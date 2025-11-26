# Vendor Product Importer - Installation & Setup Guide

## Overview
This module enables automated import and maintenance of products from online vendors (Amazon, eBay, Shopify, and generic websites) with intelligent tiered pricing to ensure profitability.

## Prerequisites

### System Requirements
- Odoo 17.0
- Python 3.10+
- PostgreSQL 12+

### Python Dependencies
```bash
pip install beautifulsoup4
pip install requests
pip install lxml
```

### Optional (for full Amazon integration)
```bash
pip install amazon-paapi5-python-sdk
```

## Installation Steps

### 1. Copy Module to Addons Directory
The module is already in your custom addons directory:
```
C:/Users/MJWil/odoo_custom_addons/vendor_product_importer/
```

### 2. Update Odoo Apps List
1. Restart Odoo server
2. Log in to Odoo as Administrator
3. Go to **Apps** menu
4. Click **Update Apps List**
5. Click **Update** in the confirmation dialog

### 3. Install the Module
1. In the Apps menu, search for "Vendor Product Importer"
2. Click **Install**
3. Wait for installation to complete

## Configuration

### Step 1: Configure Price Tiers

Navigate to: **Vendor Importer > Configuration > Price Tiers**

Create the following default tiers (or customize as needed):

**Tier 1: Low Cost Items**
- Min Cost: $0.00
- Max Cost: $50.00
- Markup: 40%
- Rounding: $X.99

**Tier 2: Medium Cost Items**
- Min Cost: $50.01
- Max Cost: $200.00
- Markup: 30%
- Rounding: $X.99

**Tier 3: High Cost Items**
- Min Cost: $200.01
- Max Cost: $500.00
- Markup: 25%
- Rounding: $X.99

**Tier 4: Premium Items**
- Min Cost: $500.01
- Max Cost: $0.00 (unlimited)
- Markup: 20%
- Rounding: $X.99

### Step 2: Configure Amazon Vendor

Navigate to: **Vendor Importer > Vendors > Create**

**Basic Information:**
- Name: Amazon US (or your marketplace)
- Vendor Type: Amazon
- Active: ✓

**Amazon Configuration:**
- Amazon Marketplace: United States
- API Key: [Your Access Key]
- API Secret: [Your Secret Key]
- Amazon Associate Tag: [Your Associate Tag]

**Import Settings:**
- Import Frequency: Weekly
- Auto Update Prices: ✓
- Auto Create Products: ✓

**Filtering (Optional):**
- Minimum Price: $5.00
- Maximum Price: $1000.00
- Exclude Keywords: (one per line)
  ```
  adult
  tobacco
  weapons
  ```
- Exclude Brands: (one per line)
  ```
  [brands to exclude]
  ```

### Step 3: Test Connection
1. Open your configured vendor
2. Click **Test Connection** button
3. Verify success message

### Step 4: Run First Import
1. Click **Import Products** button
2. Review import wizard
3. Click **Import**
4. Monitor import log

## Amazon API Setup

### Getting Amazon Product Advertising API Credentials

1. **Sign up for Amazon Associates Program:**
   - Visit: https://affiliate-program.amazon.com/
   - Complete registration
   - Get your Associate Tag

2. **Request Product Advertising API Access:**
   - Visit: https://affiliate-program.amazon.com/assoc_credentials/home
   - Request API access
   - Wait for approval (usually 1-2 days)

3. **Get API Credentials:**
   - Access Key ID
   - Secret Access Key
   - Associate Tag (Partner Tag)

4. **Enter in Odoo:**
   - API Key = Access Key ID
   - API Secret = Secret Access Key
   - Amazon Associate Tag = Your Associate Tag

### Important Amazon API Notes

- **Rate Limits:** 1 request per second for PA-API 5.0
- **Requirements:** Must have qualifying sales to maintain API access
- **Marketplaces:** Separate credentials for each marketplace
- **Cost:** Free for associates with qualifying sales

## Usage

### Manual Import
1. Go to **Vendor Importer > Vendors**
2. Select vendor
3. Click **Import Products**
4. Review results in Import Logs

### Automated Weekly Import
- Automatically runs every Sunday at 2:00 AM
- Configure in: **Settings > Technical > Automation > Scheduled Actions**
- Search for: "Import Products from Vendors"

### View Import Logs
1. Go to **Vendor Importer > Import Logs**
2. Filter by vendor, date, or status
3. Click log to see details
4. View created/updated products

### Manage Products
1. Go to **Sales > Products**
2. Filter by "Imported from Vendor"
3. View vendor information tab
4. See multiple vendor prices
5. Update prices from best vendor

## Troubleshooting

### Module Won't Install
- Check Odoo logs: `C:/Program Files/Odoo 17.0.20250119/server/odoo.log`
- Verify Python dependencies installed
- Restart Odoo server
- Update apps list again

### Amazon Connection Fails
- Verify API credentials are correct
- Check Associate Tag format
- Ensure API access is approved
- Check marketplace selection matches credentials

### No Products Imported
- Check import logs for errors
- Verify filters aren't too restrictive
- Check Amazon API has products for search terms
- Review excluded keywords/brands

### Price Calculation Issues
- Verify price tiers are configured
- Check tier cost ranges don't overlap
- Ensure markup percentages are set
- Review product cost from vendor

### Import is Slow
- Amazon API has rate limits (1 req/sec)
- Large imports take time
- Check network connection
- Review Odoo server resources

## Advanced Configuration

### Custom Price Formulas
In Price Tiers, use Python expressions:
```python
# Example: Cost + 30% + $5 fixed
cost * 1.3 + 5.0

# Example: Tiered with minimum
max(cost * 1.25, cost + 10.0)
```

### Field Mappings
Create custom field mappings for data transformation:
1. Go to **Vendor Importer > Configuration > Field Mappings**
2. Create mapping for vendor
3. Map vendor fields to Odoo fields
4. Apply transformations (uppercase, regex, etc.)

### Multiple Vendors per Product
- System automatically tracks all vendors
- Displays best price (lowest cost)
- Can switch primary vendor
- Maintains price history

## Maintenance

### Weekly Tasks
- Review import logs
- Check for failed imports
- Update excluded keywords/brands
- Verify price calculations

### Monthly Tasks
- Review price tier effectiveness
- Analyze profit margins
- Update vendor configurations
- Clean up discontinued products

### Quarterly Tasks
- Review Amazon API usage
- Update API credentials if needed
- Optimize import filters
- Performance tuning

## Support & Documentation

### Module Files
- `README.md` - General documentation
- `IMPLEMENTATION_STATUS.md` - Development status
- `INSTALLATION_GUIDE.md` - This file

### Odoo Documentation
- https://www.odoo.com/documentation/17.0/

### Amazon PA-API Documentation
- https://webservices.amazon.com/paapi5/documentation/

### Getting Help
- Check Odoo logs for errors
- Review import logs for details
- Consult module documentation
- Contact system administrator

## Security Notes

- API credentials are stored encrypted
- Access controlled by Odoo security groups
- Import logs track all changes
- Vendor data is company-specific

## Performance Tips

- Start with small product sets
- Use specific filters
- Schedule imports during off-hours
- Monitor server resources
- Use pagination for large imports

## Legal Compliance

- Respect vendor terms of service
- Follow Amazon Associates Program rules
- Comply with product restrictions
- Honor rate limits
- Maintain accurate product information

## Next Steps

1. ✅ Install module
2. ✅ Configure price tiers
3. ✅ Set up Amazon vendor
4. ✅ Test connection
5. ✅ Run first import
6. ✅ Review results
7. ✅ Configure automation
8. ✅ Monitor weekly imports

## Version Information

- **Module Version:** 17.0.1.0.0
- **Odoo Version:** 17.0
- **License:** LGPL-3
- **Author:** Your Company

---

**Congratulations!** Your vendor product importer is ready to use. Start importing products and maintaining profitable pricing automatically!
