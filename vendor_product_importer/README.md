# Vendor Product Importer Module

## Overview
This Odoo 19 module automates the import and maintenance of product pages from online vendors (Amazon, eBay, Shopify, and generic websites) while ensuring profitable pricing through tiered pricing rules.

## Features
- **Multi-Platform Support**: Amazon, eBay, Shopify, and generic HTML scraping
- **Automated Imports**: Weekly scheduled imports with configurable frequency
- **Tiered Pricing**: Cost-based pricing tiers with automatic profit margin calculation
- **Product Matching**: Intelligent matching by SKU, EAN, UPC, or name similarity
- **Vendor Management**: Track multiple vendors per product and automatically select best price
- **Legal Compliance**: Configurable filters for keywords, brands, and categories
- **Comprehensive Logging**: Detailed import logs with success/failure tracking

## Installation

### Prerequisites
```bash
pip install beautifulsoup4
pip install requests
pip install lxml
```

### Install Module
1. Copy the `vendor_product_importer` folder to your Odoo addons directory
2. Restart Odoo server
3. Go to Apps menu
4. Update Apps List
5. Search for "Vendor Product Importer"
6. Click Install

## Configuration

### 1. Set Up Price Tiers
Navigate to: **Vendor Importer > Configuration > Price Tiers**

Create pricing tiers based on cost ranges:
- Tier 1: $0-$50 → 40% markup
- Tier 2: $51-$200 → 30% markup
- Tier 3: $201-$500 → 25% markup
- Tier 4: $501+ → 20% markup

### 2. Configure Vendors
Navigate to: **Vendor Importer > Vendors**

For Amazon:
- Set Vendor Type to "Amazon"
- Enter API credentials (Access Key, Secret Key, Associate Tag)
- Select marketplace (US, UK, etc.)
- Configure import frequency (Weekly recommended)

For Generic Websites:
- Set Vendor Type to "Generic Website"
- Enter product list URL
- Configure CSS selectors for product data extraction

### 3. Set Up Field Mappings (Optional)
Navigate to: **Vendor Importer > Configuration > Field Mappings**

Map vendor fields to Odoo product fields with optional transformations.

## Usage

### Manual Import
1. Go to **Vendor Importer > Vendors**
2. Select a vendor
3. Click "Import Products" button
4. Review import results in Import Logs

### Automated Import
- Imports run automatically based on configured frequency
- Default: Every Sunday at 2:00 AM
- View scheduled actions in **Settings > Technical > Automation > Scheduled Actions**

### View Import Logs
Navigate to: **Vendor Importer > Import Logs**
- View import statistics
- Check for errors
- Review created/updated products

## Module Structure

```
vendor_product_importer/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── vendor_config.py          # Vendor configuration
│   ├── price_tier.py              # Tiered pricing rules
│   ├── product_vendor_info.py     # Vendor-product relationships
│   ├── product_template.py        # Extended product model
│   ├── import_log.py              # Import history
│   └── product_mapping.py         # Field mapping configuration
├── adapters/
│   ├── base_adapter.py            # Base adapter class
│   ├── amazon_adapter.py          # Amazon integration
│   ├── ebay_adapter.py            # eBay integration
│   ├── shopify_adapter.py         # Shopify integration
│   └── generic_adapter.py         # Generic HTML scraper
├── wizards/
│   ├── import_wizard.py           # Manual import wizard
│   └── price_update_wizard.py     # Bulk price update
├── views/
│   ├── vendor_config_views.xml
│   ├── price_tier_views.xml
│   ├── product_vendor_info_views.xml
│   ├── import_log_views.xml
│   ├── product_template_views.xml
│   └── menu_views.xml
├── data/
│   ├── price_tier_data.xml        # Default pricing tiers
│   └── ir_cron.xml                # Scheduled actions
└── security/
    └── ir.model.access.csv        # Access rights
```

## Technical Details

### Price Calculation
1. Product cost retrieved from vendor
2. Appropriate price tier selected based on cost range
3. Markup applied according to tier rules
4. Minimum profit constraints enforced
5. Price rounded according to tier settings

### Product Matching
Products are matched using the following priority:
1. Exact SKU match
2. Exact EAN/UPC match
3. Exact barcode match
4. Name similarity (fuzzy matching)

### Legal Compliance
Products are filtered based on:
- Excluded keywords (configurable)
- Excluded brands (configurable)
- Excluded categories (configurable)
- Price range filters

## Support
For issues or questions, please contact your system administrator.

## License
LGPL-3

## Version
19.0.1.0.0
