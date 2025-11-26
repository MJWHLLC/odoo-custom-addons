# -*- coding: utf-8 -*-

import logging
from .base_adapter import BaseAdapter
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class GenericAdapter(BaseAdapter):
    """
    Generic HTML scraper adapter using BeautifulSoup
    
    This adapter can scrape product data from any website using CSS selectors.
    Configure the selectors in the vendor configuration.
    """
    
    def __init__(self, vendor_config):
        super().__init__(vendor_config)
        self.product_list_url = vendor_config.product_list_url
        self.product_list_selector = vendor_config.product_list_selector
        self.product_link_selector = vendor_config.product_link_selector
        
        # Field selectors
        self.name_selector = vendor_config.name_selector
        self.price_selector = vendor_config.price_selector
        self.description_selector = vendor_config.description_selector
        self.image_selector = vendor_config.image_selector
        self.sku_selector = vendor_config.sku_selector
        self.ean_selector = vendor_config.ean_selector
        self.category_selector = vendor_config.category_selector
    
    def test_connection(self):
        """Test connection to website"""
        try:
            if not self.product_list_url:
                raise UserError(_('Product list URL is not configured.'))
            
            import requests
            response = requests.get(self.product_list_url, timeout=10)
            
            if response.status_code == 200:
                _logger.info('Successfully connected to: %s', self.product_list_url)
                return True
            else:
                _logger.error('Failed to connect. Status code: %d', response.status_code)
                return False
            
        except Exception as e:
            _logger.error('Connection test failed: %s', str(e))
            return False
    
    def import_products(self):
        """Import products from generic website"""
        created_count = 0
        updated_count = 0
        failed_count = 0
        
        try:
            _logger.info('Starting generic import from: %s', self.product_list_url)
            
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
                    _logger.error('Failed to import product: %s', str(e))
                    failed_count += 1
            
            message = _('Generic import completed: %d created, %d updated, %d failed') % (
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
            error_msg = _('Generic import failed: %s') % str(e)
            _logger.error(error_msg)
            raise UserError(error_msg)
    
    def fetch_products(self):
        """Fetch products from website using BeautifulSoup"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            products = []
            
            # Fetch product list page
            response = requests.get(self.product_list_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all product items
            if self.product_list_selector:
                product_items = soup.select(self.product_list_selector)
            else:
                _logger.warning('No product list selector configured')
                return []
            
            _logger.info('Found %d products on listing page', len(product_items))
            
            # Extract product URLs
            for item in product_items:
                try:
                    if self.product_link_selector:
                        link_element = item.select_one(self.product_link_selector)
                        if link_element and link_element.get('href'):
                            product_url = link_element['href']
                            
                            # Make absolute URL if relative
                            if not product_url.startswith('http'):
                                from urllib.parse import urljoin
                                product_url = urljoin(self.product_list_url, product_url)
                            
                            # Fetch product detail page
                            product_data = self._fetch_product_details(product_url)
                            if product_data:
                                products.append(product_data)
                    else:
                        # Try to extract data from listing page itself
                        product_data = self._extract_from_element(item)
                        if product_data:
                            products.append(product_data)
                            
                except Exception as e:
                    _logger.error('Error processing product item: %s', str(e))
                    continue
            
            return products
            
        except Exception as e:
            _logger.error('Error fetching products: %s', str(e))
            raise
    
    def _fetch_product_details(self, url):
        """Fetch and parse product detail page"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            return {
                'url': url,
                'soup': soup,
            }
            
        except Exception as e:
            _logger.error('Error fetching product details from %s: %s', url, str(e))
            return None
    
    def _extract_from_element(self, element):
        """Extract product data from HTML element"""
        return {
            'element': element,
            'url': self.product_list_url,
        }
    
    def parse_product_data(self, raw_data):
        """Parse scraped HTML data into standardized format"""
        try:
            soup = raw_data.get('soup')
            element = raw_data.get('element')
            url = raw_data.get('url', '')
            
            # Use soup for detail page, element for listing page
            source = soup if soup else element
            
            if not source:
                return {}
            
            # Extract fields using configured selectors
            name = self._extract_text(source, self.name_selector) or 'Unknown Product'
            price_text = self._extract_text(source, self.price_selector) or '0'
            description = self._extract_html(source, self.description_selector) or ''
            image_url = self._extract_attribute(source, self.image_selector, 'src') or ''
            sku = self._extract_text(source, self.sku_selector) or ''
            ean = self._extract_text(source, self.ean_selector) or ''
            category = self._extract_text(source, self.category_selector) or ''
            
            # Parse price (remove currency symbols and convert to float)
            import re
            price_clean = re.sub(r'[^\d.,]', '', price_text)
            price_clean = price_clean.replace(',', '.')
            try:
                price = float(price_clean)
            except ValueError:
                price = 0.0
            
            product_data = {
                'vendor_product_id': sku or url,
                'vendor_product_url': url,
                'name': name.strip(),
                'default_code': sku.strip() if sku else '',
                'barcode': ean.strip() if ean else '',
                'description': description,
                'vendor_cost': price,
                'standard_price': price,
                'image_url': image_url,
                'category': category.strip() if category else '',
                'stock_status': 'in_stock',
            }
            
            return product_data
            
        except Exception as e:
            _logger.error('Error parsing product data: %s', str(e))
            raise
    
    def _extract_text(self, source, selector):
        """Extract text content using CSS selector"""
        if not selector:
            return None
        try:
            element = source.select_one(selector)
            return element.get_text(strip=True) if element else None
        except Exception:
            return None
    
    def _extract_html(self, source, selector):
        """Extract HTML content using CSS selector"""
        if not selector:
            return None
        try:
            element = source.select_one(selector)
            return str(element) if element else None
        except Exception:
            return None
    
    def _extract_attribute(self, source, selector, attribute):
        """Extract attribute value using CSS selector"""
        if not selector:
            return None
        try:
            element = source.select_one(selector)
            return element.get(attribute) if element else None
        except Exception:
            return None
    
    def sync_product(self, product_vendor_info):
        """Sync single product from website"""
        try:
            product_url = product_vendor_info.vendor_product_url
            if not product_url:
                return False
            
            _logger.info('Syncing product from: %s', product_url)
            
            # Fetch and parse product page
            raw_data = self._fetch_product_details(product_url)
            if raw_data:
                product_data = self.parse_product_data(raw_data)
                self._update_vendor_info(product_vendor_info, product_data)
                return True
            
            return False
            
        except Exception as e:
            _logger.error('Error syncing product: %s', str(e))
            return False
