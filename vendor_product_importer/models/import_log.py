# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class VendorImportLog(models.Model):
    _name = 'vendor.import.log'
    _description = 'Vendor Import Log'
    _order = 'create_date desc'

    name = fields.Char(string='Import Reference', compute='_compute_name', store=True)
    vendor_id = fields.Many2one('vendor.config', string='Vendor', required=True, ondelete='cascade', index=True)
    
    # Dates
    start_date = fields.Datetime(string='Start Date', default=fields.Datetime.now, readonly=True)
    end_date = fields.Datetime(string='End Date', readonly=True)
    duration = fields.Float(string='Duration (minutes)', compute='_compute_duration', store=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, index=True)
    
    # Statistics
    products_found = fields.Integer(string='Products Found', default=0, readonly=True)
    products_created = fields.Integer(string='Products Created', default=0, readonly=True)
    products_updated = fields.Integer(string='Products Updated', default=0, readonly=True)
    products_skipped = fields.Integer(string='Products Skipped', default=0, readonly=True)
    products_failed = fields.Integer(string='Products Failed', default=0, readonly=True)
    
    # Details
    import_type = fields.Selection([
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled'),
        ('api', 'API Triggered'),
    ], string='Import Type', default='manual')
    
    notes = fields.Text(string='Notes')
    error_log = fields.Text(string='Error Log', readonly=True)
    
    # Import Details
    import_line_ids = fields.One2many('vendor.import.log.line', 'import_log_id', string='Import Lines')
    import_line_count = fields.Integer(string='Import Lines', compute='_compute_import_line_count')
    
    @api.depends('vendor_id', 'create_date')
    def _compute_name(self):
        for record in self:
            if record.vendor_id and record.create_date:
                record.name = '%s - %s' % (record.vendor_id.name, 
                                          fields.Datetime.to_string(record.create_date))
            else:
                record.name = 'Import Log'
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration = delta.total_seconds() / 60.0
            else:
                record.duration = 0.0
    
    def _compute_import_line_count(self):
        for record in self:
            record.import_line_count = len(record.import_line_ids)
    
    def action_view_import_lines(self):
        """View import lines"""
        self.ensure_one()
        return {
            'name': _('Import Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.import.log.line',
            'view_mode': 'tree,form',
            'domain': [('import_log_id', '=', self.id)],
            'context': {'default_import_log_id': self.id}
        }
    
    def action_view_created_products(self):
        """View products created in this import"""
        self.ensure_one()
        product_ids = self.import_line_ids.filtered(
            lambda l: l.state == 'created'
        ).mapped('product_tmpl_id').ids
        
        return {
            'name': _('Created Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', product_ids)],
        }
    
    def action_view_updated_products(self):
        """View products updated in this import"""
        self.ensure_one()
        product_ids = self.import_line_ids.filtered(
            lambda l: l.state == 'updated'
        ).mapped('product_tmpl_id').ids
        
        return {
            'name': _('Updated Products'),
            'type': 'ir.actions.client',
            'res_model': 'product.template',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', product_ids)],
        }


class VendorImportLogLine(models.Model):
    _name = 'vendor.import.log.line'
    _description = 'Vendor Import Log Line'
    _order = 'create_date desc'

    import_log_id = fields.Many2one('vendor.import.log', string='Import Log', required=True, ondelete='cascade', index=True)
    vendor_id = fields.Many2one(related='import_log_id.vendor_id', string='Vendor', store=True, readonly=True)
    
    # Product Information
    product_tmpl_id = fields.Many2one('product.template', string='Product', ondelete='set null', index=True)
    vendor_product_id = fields.Char(string='Vendor Product ID')
    vendor_product_name = fields.Char(string='Vendor Product Name')
    vendor_sku = fields.Char(string='Vendor SKU')
    
    # Status
    state = fields.Selection([
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('skipped', 'Skipped'),
        ('failed', 'Failed'),
    ], string='Status', required=True, index=True)
    
    # Details
    vendor_cost = fields.Float(string='Vendor Cost')
    calculated_price = fields.Float(string='Calculated Price')
    
    # Error Information
    error_message = fields.Text(string='Error Message')
    
    # Notes
    notes = fields.Text(string='Notes')
