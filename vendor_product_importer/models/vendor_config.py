# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class VendorConfig(models.Model):
    _name = 'vendor.config'
    _description = 'Vendor Configuration'
    _order = 'name'

    name = fields.Char(string='Vendor Name', required=True, index=True)
    active = fields.Boolean(string='Active', default=True)
    vendor_type = fields.Selection([
        ('amazon', 'Amazon'),
        ('ebay', 'eBay'),
        ('shopify', 'Shopify'),
        ('generic', 'Generic Website'),
    ], string='Vendor Type', required=True, default='generic')
    
    # Connection Details
    website_url = fields.Char(string='Website URL', required=True)
    api_endpoint = fields.Char(string='API Endpoint')
    api_key = fields.Char(string='API Key')
    api_secret = fields.Char(string='API Secret')
    access_token = fields.Char(string='Access Token')
    
    # Amazon Specific
    amazon_associate_tag = fields.Char(string='Amazon Associate Tag')
    amazon_marketplace = fields.Selection([
        ('US', 'United States'),
        ('UK', 'United Kingdom'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('JP', 'Japan'),
        ('CA', 'Canada'),
        ('CN', 'China'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('IN', 'India'),
        ('BR', 'Brazil'),
        ('MX', 'Mexico'),
        ('AU', 'Australia'),
    ], string='Amazon Marketplace', default='US')
    
    # eBay Specific
    ebay_site_id = fields.Selection([
        ('0', 'United States'),
        ('3', 'United Kingdom'),
        ('77', 'Germany'),
        ('71', 'France'),
        ('15', 'Australia'),
        ('2', 'Canada'),
        ('100', 'eBay Motors'),
    ], string='eBay Site ID', default='0')
    
    # Shopify Specific
    shopify_store_name = fields.Char(string='Shopify Store Name')
    
    # Generic Scraping Configuration
    product_list_url = fields.Char(string='Product List URL')
    product_list_selector = fields.Char(string='Product List CSS Selector', 
                                        help='CSS selector for product items on listing page')
    product_link_selector = fields.Char(string='Product Link Selector',
                                       help='CSS selector for product detail page link')
    
    # Product Field Selectors (for generic scraping)
    name_selector = fields.Char(string='Product Name Selector')
    price_selector = fields.Char(string='Price Selector')
    description_selector = fields.Char(string='Description Selector')
    image_selector = fields.Char(string='Image Selector')
    sku_selector = fields.Char(string='SKU Selector')
    ean_selector = fields.Char(string='EAN/UPC Selector')
    category_selector = fields.Char(string='Category Selector')
    
    # Import Settings
    import_frequency = fields.Selection([
        ('manual', 'Manual Only'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], string='Import Frequency', default='weekly', required=True)
    
    last_import_date = fields.Datetime(string='Last Import Date', readonly=True)
    next_import_date = fields.Datetime(string='Next Import Date', compute='_compute_next_import_date', store=True)
    
    auto_update_prices = fields.Boolean(string='Auto Update Prices', default=True,
                                       help='Automatically update product prices on import')
    auto_update_stock = fields.Boolean(string='Auto Update Stock', default=False,
                                      help='Automatically update stock levels on import')
    auto_create_products = fields.Boolean(string='Auto Create Products', default=True,
                                         help='Automatically create new products if not found')
    
    # Filtering
    category_filter = fields.Char(string='Category Filter',
                                  help='Comma-separated list of categories to import')
    exclude_categories = fields.Char(string='Exclude Categories',
                                    help='Comma-separated list of categories to exclude')
    min_price = fields.Float(string='Minimum Price', default=0.0)
    max_price = fields.Float(string='Maximum Price', default=0.0)
    
    # Legal Compliance
    exclude_keywords = fields.Text(string='Exclude Keywords',
                                  help='One keyword per line. Products containing these keywords will be excluded')
    exclude_brands = fields.Text(string='Exclude Brands',
                                help='One brand per line. Products from these brands will be excluded')
    
    # Statistics
    product_count = fields.Integer(string='Products Imported', compute='_compute_product_count')
    import_log_ids = fields.One2many('vendor.import.log', 'vendor_id', string='Import Logs')
    import_log_count = fields.Integer(string='Import Logs', compute='_compute_import_log_count')
    
    # Partner (Supplier)
    partner_id = fields.Many2one('res.partner', string='Supplier', 
                                 help='Link to supplier partner record')
    
    # Notes
    notes = fields.Text(string='Notes')
    
    @api.depends('import_frequency', 'last_import_date')
    def _compute_next_import_date(self):
        from datetime import timedelta
        for record in self:
            if record.import_frequency == 'manual' or not record.last_import_date:
                record.next_import_date = False
            elif record.import_frequency == 'daily':
                record.next_import_date = record.last_import_date + timedelta(days=1)
            elif record.import_frequency == 'weekly':
                record.next_import_date = record.last_import_date + timedelta(weeks=1)
            elif record.import_frequency == 'monthly':
                record.next_import_date = record.last_import_date + timedelta(days=30)
    
    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['product.vendor.info'].search_count([
                ('vendor_id', '=', record.id)
            ])
    
    def _compute_import_log_count(self):
        for record in self:
            record.import_log_count = len(record.import_log_ids)
    
    @api.constrains('website_url')
    def _check_website_url(self):
        for record in self:
            if record.website_url and not record.website_url.startswith(('http://', 'https://')):
                raise ValidationError(_('Website URL must start with http:// or https://'))
    
    def action_test_connection(self):
        """Test connection to vendor"""
        self.ensure_one()
        try:
            adapter = self._get_adapter()
            result = adapter.test_connection()
            if result:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Connection to %s successful!') % self.name,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': _('Connection to %s failed!') % self.name,
                        'type': 'danger',
                        'sticky': False,
                    }
                }
        except Exception as e:
            _logger.error('Connection test failed for vendor %s: %s', self.name, str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Connection failed: %s') % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_import_products(self):
        """Manual import trigger"""
        self.ensure_one()
        return {
            'name': _('Import Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_vendor_id': self.id,
            }
        }
    
    def action_view_products(self):
        """View products from this vendor"""
        self.ensure_one()
        vendor_info_ids = self.env['product.vendor.info'].search([
            ('vendor_id', '=', self.id)
        ]).mapped('product_tmpl_id').ids
        
        return {
            'name': _('Products from %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', vendor_info_ids)],
            'context': {'search_default_vendor_id': self.id}
        }
    
    def action_view_import_logs(self):
        """View import logs"""
        self.ensure_one()
        return {
            'name': _('Import Logs - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.import.log',
            'view_mode': 'tree,form',
            'domain': [('vendor_id', '=', self.id)],
            'context': {'default_vendor_id': self.id}
        }
    
    def _get_adapter(self):
        """Get the appropriate adapter for this vendor"""
        adapter_class = self.env['vendor.adapter.base']
        
        if self.vendor_type == 'amazon':
            from ..adapters.amazon_adapter import AmazonAdapter
            return AmazonAdapter(self)
        elif self.vendor_type == 'ebay':
            from ..adapters.ebay_adapter import EbayAdapter
            return EbayAdapter(self)
        elif self.vendor_type == 'shopify':
            from ..adapters.shopify_adapter import ShopifyAdapter
            return ShopifyAdapter(self)
        else:
            from ..adapters.generic_adapter import GenericAdapter
            return GenericAdapter(self)
    
    def cron_import_products(self):
        """Scheduled action to import products"""
        vendors = self.search([
            ('active', '=', True),
            ('import_frequency', '!=', 'manual'),
            '|',
            ('next_import_date', '<=', fields.Datetime.now()),
            ('last_import_date', '=', False),
        ])
        
        for vendor in vendors:
            try:
                _logger.info('Starting scheduled import for vendor: %s', vendor.name)
                vendor._run_import()
            except Exception as e:
                _logger.error('Scheduled import failed for vendor %s: %s', vendor.name, str(e))
    
    def _run_import(self):
        """Execute the import process"""
        self.ensure_one()
        
        # Create import log
        import_log = self.env['vendor.import.log'].create({
            'vendor_id': self.id,
            'state': 'in_progress',
        })
        
        try:
            adapter = self._get_adapter()
            result = adapter.import_products()
            
            # Update import log
            import_log.write({
                'state': 'done',
                'products_created': result.get('created', 0),
                'products_updated': result.get('updated', 0),
                'products_failed': result.get('failed', 0),
                'end_date': fields.Datetime.now(),
                'notes': result.get('message', 'Import completed successfully'),
            })
            
            # Update last import date
            self.last_import_date = fields.Datetime.now()
            
            _logger.info('Import completed for vendor %s: %d created, %d updated, %d failed',
                        self.name, result.get('created', 0), result.get('updated', 0), result.get('failed', 0))
            
        except Exception as e:
            _logger.error('Import failed for vendor %s: %s', self.name, str(e))
            import_log.write({
                'state': 'failed',
                'end_date': fields.Datetime.now(),
                'notes': 'Import failed: %s' % str(e),
            })
            raise
