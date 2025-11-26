# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Vendor Information
    vendor_info_ids = fields.One2many('product.vendor.info', 'product_tmpl_id', string='Vendor Information')
    vendor_count = fields.Integer(string='Vendor Count', compute='_compute_vendor_count')
    primary_vendor_id = fields.Many2one('vendor.config', string='Primary Vendor', 
                                       compute='_compute_primary_vendor', store=True)
    
    # Import Information
    is_imported = fields.Boolean(string='Imported from Vendor', default=False)
    last_vendor_sync = fields.Datetime(string='Last Vendor Sync', readonly=True)
    
    # Best Price Information
    best_vendor_cost = fields.Float(string='Best Vendor Cost', compute='_compute_best_vendor_cost', store=True)
    best_vendor_id = fields.Many2one('vendor.config', string='Best Vendor', 
                                     compute='_compute_best_vendor_cost', store=True)
    
    def _compute_vendor_count(self):
        for record in self:
            record.vendor_count = len(record.vendor_info_ids)
    
    @api.depends('vendor_info_ids', 'vendor_info_ids.is_primary_vendor')
    def _compute_primary_vendor(self):
        for record in self:
            primary = record.vendor_info_ids.filtered(lambda v: v.is_primary_vendor)
            record.primary_vendor_id = primary[:1].vendor_id if primary else False
    
    @api.depends('vendor_info_ids', 'vendor_info_ids.vendor_cost', 'vendor_info_ids.vendor_stock_status')
    def _compute_best_vendor_cost(self):
        for record in self:
            best_vendor_info = self.env['product.vendor.info'].get_best_vendor_for_product(record.id)
            if best_vendor_info:
                record.best_vendor_cost = best_vendor_info.vendor_cost
                record.best_vendor_id = best_vendor_info.vendor_id
            else:
                record.best_vendor_cost = 0.0
                record.best_vendor_id = False
    
    def action_view_vendors(self):
        """View all vendors for this product"""
        self.ensure_one()
        return {
            'name': _('Vendors - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.vendor.info',
            'view_mode': 'tree,form',
            'domain': [('product_tmpl_id', '=', self.id)],
            'context': {'default_product_tmpl_id': self.id}
        }
    
    def action_sync_from_vendors(self):
        """Sync product data from all vendors"""
        self.ensure_one()
        for vendor_info in self.vendor_info_ids:
            try:
                vendor_info.action_sync_from_vendor()
            except Exception as e:
                _logger.error('Failed to sync product %s from vendor %s: %s',
                            self.name, vendor_info.vendor_id.name, str(e))
        
        self.last_vendor_sync = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Product synced from all vendors'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_update_price_from_best_vendor(self):
        """Update product price based on best vendor cost"""
        self.ensure_one()
        if self.best_vendor_cost > 0:
            price_tier_model = self.env['product.price.tier']
            new_price = price_tier_model.calculate_price_for_product(
                self.best_vendor_cost,
                self,
                self.best_vendor_id
            )
            self.list_price = new_price
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Price updated to %s based on best vendor') % new_price,
                    'type': 'success',
                    'sticky': False,
                }
            }
