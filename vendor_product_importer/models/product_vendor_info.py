# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductVendorInfo(models.Model):
    _name = 'product.vendor.info'
    _description = 'Product Vendor Information'
    _order = 'vendor_cost'

    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade', index=True)
    product_id = fields.Many2one('product.product', string='Product Variant', ondelete='cascade', index=True)
    vendor_id = fields.Many2one('vendor.config', string='Vendor', required=True, ondelete='cascade', index=True)
    
    # Vendor Product Information
    vendor_product_id = fields.Char(string='Vendor Product ID', index=True,
                                    help='Product ID/SKU from vendor system')
    vendor_product_url = fields.Char(string='Vendor Product URL',
                                     help='Direct link to product on vendor website')
    vendor_sku = fields.Char(string='Vendor SKU')
    vendor_barcode = fields.Char(string='Vendor Barcode/EAN/UPC')
    
    # Pricing
    vendor_cost = fields.Float(string='Vendor Cost', required=True, default=0.0,
                              help='Cost price from vendor')
    vendor_currency_id = fields.Many2one('res.currency', string='Vendor Currency',
                                        default=lambda self: self.env.company.currency_id)
    
    # Calculated Prices
    calculated_sale_price = fields.Float(string='Calculated Sale Price', compute='_compute_calculated_price', store=True)
    profit_margin = fields.Float(string='Profit Margin %', compute='_compute_profit_margin', store=True)
    
    # Stock Information
    vendor_qty_available = fields.Float(string='Vendor Stock', default=0.0)
    vendor_stock_status = fields.Selection([
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('limited', 'Limited Stock'),
        ('preorder', 'Pre-order'),
        ('discontinued', 'Discontinued'),
    ], string='Stock Status', default='in_stock')
    
    # Sync Information
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    sync_status = fields.Selection([
        ('synced', 'Synced'),
        ('pending', 'Pending'),
        ('error', 'Error'),
    ], string='Sync Status', default='pending')
    sync_error = fields.Text(string='Sync Error')
    
    # Vendor Product Details
    vendor_product_name = fields.Char(string='Vendor Product Name')
    vendor_description = fields.Html(string='Vendor Description')
    vendor_category = fields.Char(string='Vendor Category')
    vendor_brand = fields.Char(string='Vendor Brand')
    
    # Shipping
    vendor_weight = fields.Float(string='Vendor Weight')
    vendor_dimensions = fields.Char(string='Vendor Dimensions')
    vendor_shipping_cost = fields.Float(string='Vendor Shipping Cost')
    
    # Status
    active = fields.Boolean(string='Active', default=True)
    is_primary_vendor = fields.Boolean(string='Primary Vendor', default=False,
                                      help='Use this vendor as primary source for this product')
    
    # Notes
    notes = fields.Text(string='Notes')
    
    @api.depends('vendor_cost', 'product_tmpl_id', 'vendor_id')
    def _compute_calculated_price(self):
        """Calculate sale price using price tiers"""
        for record in self:
            if record.vendor_cost > 0:
                price_tier_model = self.env['product.price.tier']
                record.calculated_sale_price = price_tier_model.calculate_price_for_product(
                    record.vendor_cost,
                    record.product_tmpl_id,
                    record.vendor_id
                )
            else:
                record.calculated_sale_price = 0.0
    
    @api.depends('calculated_sale_price', 'vendor_cost')
    def _compute_profit_margin(self):
        """Calculate profit margin percentage"""
        for record in self:
            if record.vendor_cost > 0 and record.calculated_sale_price > 0:
                profit = record.calculated_sale_price - record.vendor_cost
                record.profit_margin = (profit / record.vendor_cost) * 100
            else:
                record.profit_margin = 0.0
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle primary vendor logic"""
        records = super(ProductVendorInfo, self).create(vals_list)
        
        for record in records:
            if record.is_primary_vendor:
                # Unset other primary vendors for same product
                other_vendors = self.search([
                    ('product_tmpl_id', '=', record.product_tmpl_id.id),
                    ('id', '!=', record.id),
                    ('is_primary_vendor', '=', True),
                ])
                other_vendors.write({'is_primary_vendor': False})
        
        return records
    
    def write(self, vals):
        """Override write to handle primary vendor logic"""
        result = super(ProductVendorInfo, self).write(vals)
        
        if vals.get('is_primary_vendor'):
            for record in self:
                # Unset other primary vendors for same product
                other_vendors = self.search([
                    ('product_tmpl_id', '=', record.product_tmpl_id.id),
                    ('id', '!=', record.id),
                    ('is_primary_vendor', '=', True),
                ])
                other_vendors.write({'is_primary_vendor': False})
        
        return result
    
    def action_set_as_primary(self):
        """Set this vendor as primary for the product"""
        self.ensure_one()
        self.is_primary_vendor = True
        return True
    
    def action_sync_from_vendor(self):
        """Manually sync product data from vendor"""
        self.ensure_one()
        try:
            adapter = self.vendor_id._get_adapter()
            result = adapter.sync_product(self)
            
            if result:
                self.write({
                    'sync_status': 'synced',
                    'last_sync_date': fields.Datetime.now(),
                    'sync_error': False,
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Product synced successfully from %s') % self.vendor_id.name,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                self.write({
                    'sync_status': 'error',
                    'sync_error': 'Sync failed - no data returned',
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': _('Failed to sync product from %s') % self.vendor_id.name,
                        'type': 'danger',
                        'sticky': False,
                    }
                }
        except Exception as e:
            _logger.error('Sync failed for product %s from vendor %s: %s',
                         self.product_tmpl_id.name, self.vendor_id.name, str(e))
            self.write({
                'sync_status': 'error',
                'sync_error': str(e),
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Sync failed: %s') % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_update_product_price(self):
        """Update product sale price based on calculated price"""
        self.ensure_one()
        if self.calculated_sale_price > 0:
            self.product_tmpl_id.list_price = self.calculated_sale_price
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Product price updated to %s') % self.calculated_sale_price,
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    @api.model
    def get_best_vendor_for_product(self, product_tmpl_id):
        """
        Get the best vendor for a product (lowest cost with stock)
        
        :param product_tmpl_id: product.template ID
        :return: product.vendor.info record or None
        """
        vendors = self.search([
            ('product_tmpl_id', '=', product_tmpl_id),
            ('active', '=', True),
            ('vendor_stock_status', 'in', ['in_stock', 'limited']),
        ], order='vendor_cost')
        
        return vendors[:1] if vendors else None
