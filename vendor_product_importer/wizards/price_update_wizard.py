# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PriceUpdateWizard(models.TransientModel):
    _name = 'price.update.wizard'
    _description = 'Bulk Price Update Wizard'

    update_scope = fields.Selection([
        ('all', 'All Imported Products'),
        ('vendor', 'Products from Specific Vendor'),
        ('selection', 'Selected Products'),
    ], string='Update Scope', default='selection', required=True)
    
    vendor_id = fields.Many2one('vendor.config', string='Vendor')
    product_ids = fields.Many2many('product.template', string='Products')
    
    price_source = fields.Selection([
        ('best_vendor', 'Best Vendor Cost'),
        ('primary_vendor', 'Primary Vendor Cost'),
        ('manual', 'Manual Price'),
    ], string='Price Source', default='best_vendor', required=True)
    
    manual_price = fields.Float(string='Manual Price', default=0.0)
    apply_tiers = fields.Boolean(string='Apply Price Tiers', default=True,
                                 help='Calculate sale price using configured price tiers')
    
    # Preview
    products_to_update = fields.Integer(string='Products to Update', compute='_compute_products_to_update')
    preview_lines = fields.One2many('price.update.wizard.line', 'wizard_id', string='Preview')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('preview', 'Preview'),
        ('done', 'Done'),
    ], string='State', default='draft')
    
    # Results
    products_updated = fields.Integer(string='Products Updated', readonly=True)
    products_failed = fields.Integer(string='Products Failed', readonly=True)
    
    @api.depends('update_scope', 'vendor_id', 'product_ids')
    def _compute_products_to_update(self):
        for wizard in self:
            products = wizard._get_products()
            wizard.products_to_update = len(products)
    
    def _get_products(self):
        """Get products based on update scope"""
        self.ensure_one()
        
        if self.update_scope == 'all':
            return self.env['product.template'].search([('is_imported', '=', True)])
        elif self.update_scope == 'vendor':
            if not self.vendor_id:
                return self.env['product.template']
            vendor_info = self.env['product.vendor.info'].search([
                ('vendor_id', '=', self.vendor_id.id)
            ])
            return vendor_info.mapped('product_tmpl_id')
        else:  # selection
            return self.product_ids
    
    def action_preview(self):
        """Preview price changes"""
        self.ensure_one()
        
        products = self._get_products()
        
        # Clear existing preview lines
        self.preview_lines.unlink()
        
        # Create preview lines
        preview_vals = []
        for product in products:
            current_price = product.list_price
            new_price = self._calculate_new_price(product)
            
            if new_price != current_price:
                preview_vals.append({
                    'wizard_id': self.id,
                    'product_id': product.id,
                    'current_price': current_price,
                    'new_price': new_price,
                    'price_change': new_price - current_price,
                    'price_change_percent': ((new_price - current_price) / current_price * 100) if current_price > 0 else 0,
                })
        
        self.env['price.update.wizard.line'].create(preview_vals)
        self.state = 'preview'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'price.update.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_update_prices(self):
        """Execute price update"""
        self.ensure_one()
        
        updated = 0
        failed = 0
        
        for line in self.preview_lines:
            try:
                line.product_id.list_price = line.new_price
                updated += 1
            except Exception as e:
                _logger.error('Failed to update price for product %s: %s', 
                            line.product_id.name, str(e))
                failed += 1
        
        self.write({
            'products_updated': updated,
            'products_failed': failed,
            'state': 'done',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'price.update.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def _calculate_new_price(self, product):
        """Calculate new price for product"""
        self.ensure_one()
        
        if self.price_source == 'manual':
            return self.manual_price
        
        # Get vendor cost
        if self.price_source == 'best_vendor':
            cost = product.best_vendor_cost
            vendor = product.best_vendor_id
        else:  # primary_vendor
            vendor_info = product.vendor_info_ids.filtered(lambda v: v.is_primary_vendor)
            if vendor_info:
                cost = vendor_info[0].vendor_cost
                vendor = vendor_info[0].vendor_id
            else:
                cost = product.standard_price
                vendor = None
        
        if cost <= 0:
            return product.list_price  # Keep current price if no cost
        
        # Apply price tiers if enabled
        if self.apply_tiers:
            price_tier_model = self.env['product.price.tier']
            return price_tier_model.calculate_price_for_product(cost, product, vendor)
        else:
            return cost


class PriceUpdateWizardLine(models.TransientModel):
    _name = 'price.update.wizard.line'
    _description = 'Price Update Preview Line'
    _order = 'price_change_percent desc'

    wizard_id = fields.Many2one('price.update.wizard', string='Wizard', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.template', string='Product', required=True)
    product_name = fields.Char(related='product_id.name', string='Product Name', readonly=True)
    
    current_price = fields.Float(string='Current Price', readonly=True)
    new_price = fields.Float(string='New Price', readonly=True)
    price_change = fields.Float(string='Price Change', readonly=True)
    price_change_percent = fields.Float(string='Change %', readonly=True)
