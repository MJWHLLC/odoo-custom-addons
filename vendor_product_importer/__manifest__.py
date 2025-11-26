# -*- coding: utf-8 -*-
{
    'name': 'Vendor Product Importer',
    'version': '17.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Import and maintain products from online vendors with automated pricing',
    'description': """
Vendor Product Importer
=======================
This module allows you to:
* Import products from multiple online vendors (Amazon, eBay, Shopify, etc.)
* Scrape product data from vendor websites
* Automatically calculate profitable prices using tiered pricing rules
* Schedule weekly product updates
* Match and merge products with existing catalog
* Track vendor pricing and automatically switch to best vendor
* Maintain product synchronization with vendor catalogs

Key Features:
-------------
* Multi-platform support (Amazon API, eBay API, Shopify API, Generic HTML scraping)
* Intelligent product matching (SKU, EAN, UPC, name similarity)
* Tiered pricing based on cost ranges
* Weekly automated updates
* Legal compliance filtering
* Conflict resolution for duplicate products
* Comprehensive logging and reporting
    """,
    'author': 'MJ Wilkerson Holdings LLC',
    'website': 'https://mj-wilkerson-holdings-llc.odoo.com',
    'maintainer': 'MJ Wilkerson Holdings LLC',
    'support': 'info@mj-wilkerson-holdings-llc.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'stock',
        'purchase',
        'sale_management',
    ],
    'external_dependencies': {
        'python': [
            'beautifulsoup4',
            'requests',
            'lxml',
        ],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/price_tier_data.xml',
        'data/ir_cron.xml',
        
        # Views
        'views/vendor_config_views.xml',
        'views/price_tier_views.xml',
        'views/product_vendor_info_views.xml',
        'views/import_log_views.xml',
        'views/product_template_views.xml',
        'views/menu_views.xml',
        
        # Wizards
        'wizards/import_wizard_views.xml',
        'wizards/price_update_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}
