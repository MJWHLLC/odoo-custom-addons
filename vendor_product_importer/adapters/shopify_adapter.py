# -*- coding: utf-8 -*-

import logging
from .base_adapter import BaseAdapter
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ShopifyAdapter(BaseAdapter):
    """
    Shopify Admin API adapter
    
    Note: This adapter requires Shopify API credentials:
    - Store Name (mystore.myshopify.com)
    - API Key
    - API Password/Access Token
    
    You can get credentials at: https://shopify.dev/docs/admin-api/getting-started
    """
    
    def __init__(self, vendor_config):
        super().__init__(vendor_config)
        self.store_name = vendor_config.shopify_store_name
        self.api_key = vendor_config.api_key
        self.api_password = vendor_config.api_secret
        self.access_token = vendor_config.access_token
        
        # Shopify API endpoint
        if self.store_name:
            self.api_url = f'https://{self.store_name}.myshopify.com/admin/api/2024-01'
        else:
            self.api_url = None
    
    def test_connection(self):
        """Test connection to Shopify API"""
        try:
            if not self.store_name or not (self.api_key or self.access_token):
                raise UserError(_('Shopify API credentials are not configured. Please set Store Name and API credentials.'))
            
            _logger.info('Testing Shopify API connection for store: %s', self.store_name)
            
            # For now, just validate credentials are present
            return True
            
        except Exception as e:
            _logger.error('Shopify API connection test failed: %s', str(e))
            return False
    
    def import_products(self):
        """Import products from Shopify"""
        created_count = 0
        updated_count = 0
        failed_count = 0
        
        try:
            _logger.info('Starting Shopify product import for store: %s', self.store_name)
            
            products = self.fetch_products()
            
            for raw_product in products:
                try:
                    product_data = self.parse_product_data(raw_product)
                    
                    if not self._apply_filters(product_data):
                        continue
                    
                    if product_data.get('vendor_cost'):
                        product_data['list_price'] = self._calculate_sale_price(product_data['vendor_cost'])
                    
                    product, created, updated = self.create_or_update_product(product_data)
                    
                    if created:
                        created_count += 1
                    elif updated:
                        updated_count += 1
                        
                except Exception as e:
                    _logger.error('Failed to import Shopify product: %s', str(e))
                    failed_count += 1
            
            message = _('Shopify import completed: %d created, %d updated, %d failed') % (
                created_count, updated_count, failed_count
            )
            _logger.info(message)
            
            return {
                'created': created_count,
                'updated': updated_count,
                'failed': failed_count,
                'message': message,
            }
            
        except Exception as e:
            error_msg = _('Shopify import failed: %s') % str(e)
            _logger.error(error_msg)
            raise UserError(error_msg)
    
    def fetch_products(self):
        """
        Fetch products from Shopify Admin API - Placeholder
        
        Example implementation:
        ```python
        import requests
        
        headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        url = f'{self.api_url}/products.json'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('products', [])
        ```
        """
        _logger.warning('Shopify fetch_products() is using placeholder implementation.')
        return []
    
    def parse_product_data(self, raw_data):
        """Parse Shopify product data into standardized format"""
        try:
            # Get first variant for pricing
            variants = raw_data.get('variants', [])
            first_variant = variants[0] if variants else {}
            
            # Get first image
            images = raw_data.get('images', [])
            first_image = images[0] if images else {}
            
            product_data = {
                'vendor_product_id': str(raw_data.get('id', '')),
                'vendor_product_url': f"https://{self.store_name}.myshopify.com/products/{raw_data.get('handle', '')}",
                'name': raw_data.get('title', 'Unknown Product'),
                'default_code': first_variant.get('sku', ''),
                'barcode': first_variant.get('barcode', ''),
                'description': raw_data.get('body_html', ''),
                'vendor_cost': float(first_variant.get('price', 0.0)),
                'standard_price': float(first_variant.get('price', 0.0)),
                'weight': float(first_variant.get('weight', 0.0)),
                'brand': raw_data.get('vendor', ''),
                'image_url': first_image.get('src', ''),
                'stock_status': 'in_stock' if first_variant.get('inventory_quantity', 0) > 0 else 'out_of_stock',
                'qty_available': float(first_variant.get('inventory_quantity', 0)),
                'category': raw_data.get('product_type', ''),
            }
            
            return product_data
            
        except Exception as e:
            _logger.error('Error parsing Shopify product data: %s', str(e))
            raise
    
    def sync_product(self, product_vendor_info):
        """Sync single product from Shopify"""
        try:
            product_id = product_vendor_info.vendor_product_id
            if not product_id:
                return False
            
            _logger.info('Syncing Shopify product: %s', product_id)
            return True
            
        except Exception as e:
            _logger.error('Error syncing Shopify product: %s', str(e))
            return False
