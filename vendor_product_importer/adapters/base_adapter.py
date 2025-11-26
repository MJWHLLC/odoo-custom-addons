# -*- coding: utf-8 -*-

import logging
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BaseAdapter:
    """Base adapter class for vendor integrations"""
    
    def __init__(self, vendor_config):
        """
        Initialize adapter with vendor configuration
        
        :param vendor_config: vendor.config record
        """
        self.vendor = vendor_config
        self.env = vendor_config.env
    
    def test_connection(self):
        """
        Test connection to vendor
        
        :return: True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement test_connection()")
    
    def import_products(self):
        """
        Import products from vendor
        
        :return: Dictionary with import results
                 {'created': int, 'updated': int, 'failed': int, 'message': str}
        """
        raise NotImplementedError("Subclasses must implement import_products()")
    
    def sync_product(self, product_vendor_info):
        """
        Sync single product from vendor
        
        :param product_vendor_info: product.vendor.info record
        :return: True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement sync_product()")
    
    def fetch_products(self):
        """
        Fetch products from vendor
        
        :return: List of product dictionaries
        """
        raise NotImplementedError("Subclasses must implement fetch_products()")
    
    def parse_product_data(self, raw_data):
        """
        Parse raw product data into standardized format
        
        :param raw_data: Raw product data from vendor
        :return: Dictionary with standardized product data
        """
        raise NotImplementedError("Subclasses must implement parse_product_data()")
    
    def create_or_update_product(self, product_data):
        """
        Create or update product in Odoo
        
        :param product_data: Standardized product data dictionary
        :return: Tuple (product_template, created_flag, updated_flag)
        """
        try:
            # Check if product already exists
            product = self._find_existing_product(product_data)
            
            if product:
                # Update existing product
                if self.vendor.auto_update_prices:
                    self._update_product(product, product_data)
                    return (product, False, True)
                else:
                    return (product, False, False)
            else:
                # Create new product
                if self.vendor.auto_create_products:
                    product = self._create_product(product_data)
                    return (product, True, False)
                else:
                    return (None, False, False)
        
        except Exception as e:
            _logger.error('Error creating/updating product: %s', str(e))
            raise
    
    def _find_existing_product(self, product_data):
        """
        Find existing product by SKU, barcode, or name
        
        :param product_data: Product data dictionary
        :return: product.template record or None
        """
        ProductTemplate = self.env['product.template']
        
        # Try to find by default_code (SKU)
        if product_data.get('default_code'):
            product = ProductTemplate.search([
                ('default_code', '=', product_data['default_code'])
            ], limit=1)
            if product:
                return product
        
        # Try to find by barcode
        if product_data.get('barcode'):
            product = ProductTemplate.search([
                ('barcode', '=', product_data['barcode'])
            ], limit=1)
            if product:
                return product
        
        # Try to find by vendor product ID
        if product_data.get('vendor_product_id'):
            vendor_info = self.env['product.vendor.info'].search([
                ('vendor_id', '=', self.vendor.id),
                ('vendor_product_id', '=', product_data['vendor_product_id'])
            ], limit=1)
            if vendor_info:
                return vendor_info.product_tmpl_id
        
        return None
    
    def _create_product(self, product_data):
        """
        Create new product
        
        :param product_data: Product data dictionary
        :return: product.template record
        """
        ProductTemplate = self.env['product.template']
        
        # Prepare product values
        vals = {
            'name': product_data.get('name', 'Unnamed Product'),
            'default_code': product_data.get('default_code'),
            'barcode': product_data.get('barcode'),
            'description': product_data.get('description'),
            'description_sale': product_data.get('description_sale'),
            'list_price': product_data.get('list_price', 0.0),
            'standard_price': product_data.get('standard_price', 0.0),
            'weight': product_data.get('weight', 0.0),
            'volume': product_data.get('volume', 0.0),
            'is_imported': True,
            'sale_ok': True,
            'purchase_ok': True,
        }
        
        # Create product
        product = ProductTemplate.create(vals)
        
        # Create vendor info
        self._create_vendor_info(product, product_data)
        
        # Download and attach images if available
        if product_data.get('image_url'):
            self._download_product_image(product, product_data['image_url'])
        
        return product
    
    def _update_product(self, product, product_data):
        """
        Update existing product
        
        :param product: product.template record
        :param product_data: Product data dictionary
        """
        # Update vendor info
        vendor_info = self.env['product.vendor.info'].search([
            ('product_tmpl_id', '=', product.id),
            ('vendor_id', '=', self.vendor.id)
        ], limit=1)
        
        if vendor_info:
            self._update_vendor_info(vendor_info, product_data)
        else:
            self._create_vendor_info(product, product_data)
        
        # Update product price if configured
        if self.vendor.auto_update_prices and product_data.get('list_price'):
            product.list_price = product_data['list_price']
        
        # Update last sync date
        product.last_vendor_sync = self.env['ir.fields'].Datetime.now()
    
    def _create_vendor_info(self, product, product_data):
        """
        Create vendor info record
        
        :param product: product.template record
        :param product_data: Product data dictionary
        :return: product.vendor.info record
        """
        vendor_cost = product_data.get('vendor_cost', product_data.get('standard_price', 0.0))
        
        vals = {
            'product_tmpl_id': product.id,
            'vendor_id': self.vendor.id,
            'vendor_product_id': product_data.get('vendor_product_id'),
            'vendor_product_url': product_data.get('vendor_product_url'),
            'vendor_sku': product_data.get('vendor_sku', product_data.get('default_code')),
            'vendor_barcode': product_data.get('vendor_barcode', product_data.get('barcode')),
            'vendor_cost': vendor_cost,
            'vendor_product_name': product_data.get('name'),
            'vendor_description': product_data.get('description'),
            'vendor_category': product_data.get('category'),
            'vendor_brand': product_data.get('brand'),
            'vendor_weight': product_data.get('weight', 0.0),
            'vendor_qty_available': product_data.get('qty_available', 0.0),
            'vendor_stock_status': product_data.get('stock_status', 'in_stock'),
            'last_sync_date': self.env['ir.fields'].Datetime.now(),
            'sync_status': 'synced',
        }
        
        return self.env['product.vendor.info'].create(vals)
    
    def _update_vendor_info(self, vendor_info, product_data):
        """
        Update vendor info record
        
        :param vendor_info: product.vendor.info record
        :param product_data: Product data dictionary
        """
        vendor_cost = product_data.get('vendor_cost', product_data.get('standard_price', 0.0))
        
        vals = {
            'vendor_cost': vendor_cost,
            'vendor_product_name': product_data.get('name'),
            'vendor_description': product_data.get('description'),
            'vendor_qty_available': product_data.get('qty_available', 0.0),
            'vendor_stock_status': product_data.get('stock_status', 'in_stock'),
            'last_sync_date': self.env['ir.fields'].Datetime.now(),
            'sync_status': 'synced',
        }
        
        vendor_info.write(vals)
    
    def _download_product_image(self, product, image_url):
        """
        Download and attach product image
        
        :param product: product.template record
        :param image_url: URL of product image
        """
        try:
            import requests
            import base64
            
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                image_data = base64.b64encode(response.content)
                product.image_1920 = image_data
        except Exception as e:
            _logger.warning('Failed to download image for product %s: %s', product.name, str(e))
    
    def _apply_filters(self, product_data):
        """
        Apply vendor filters to product data
        
        :param product_data: Product data dictionary
        :return: True if product passes filters, False otherwise
        """
        # Check price range
        price = product_data.get('vendor_cost', 0.0)
        if self.vendor.min_price > 0 and price < self.vendor.min_price:
            return False
        if self.vendor.max_price > 0 and price > self.vendor.max_price:
            return False
        
        # Check excluded keywords
        if self.vendor.exclude_keywords:
            keywords = [k.strip().lower() for k in self.vendor.exclude_keywords.split('\n') if k.strip()]
            product_name = product_data.get('name', '').lower()
            product_desc = product_data.get('description', '').lower()
            
            for keyword in keywords:
                if keyword in product_name or keyword in product_desc:
                    _logger.info('Product filtered out by keyword: %s', keyword)
                    return False
        
        # Check excluded brands
        if self.vendor.exclude_brands:
            brands = [b.strip().lower() for b in self.vendor.exclude_brands.split('\n') if b.strip()]
            product_brand = product_data.get('brand', '').lower()
            
            if product_brand in brands:
                _logger.info('Product filtered out by brand: %s', product_brand)
                return False
        
        return True
    
    def _calculate_sale_price(self, cost):
        """
        Calculate sale price using price tiers
        
        :param cost: Product cost
        :return: Calculated sale price
        """
        price_tier_model = self.env['product.price.tier']
        return price_tier_model.calculate_price_for_product(cost, None, self.vendor)
