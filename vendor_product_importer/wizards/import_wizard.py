# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class VendorImportWizard(models.TransientModel):
    _name = 'vendor.import.wizard'
    _description = 'Vendor Import Wizard'

    vendor_id = fields.Many2one('vendor.config', string='Vendor', required=True)
    import_type = fields.Selection([
        ('full', 'Full Import'),
        ('update_only', 'Update Existing Only'),
        ('new_only', 'New Products Only'),
    ], string='Import Type', default='full', required=True)
    
    test_mode = fields.Boolean(string='Test Mode', default=False,
                               help='Run import without creating/updating products')
    max_products = fields.Integer(string='Maximum Products', default=0,
                                  help='Limit number of products to import (0 = no limit)')
    
    # Preview
    preview_count = fields.Integer(string='Products Found', readonly=True)
    preview_message = fields.Text(string='Preview', readonly=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('preview', 'Preview'),
        ('done', 'Done'),
    ], string='State', default='draft')
    
    # Results
    products_created = fields.Integer(string='Products Created', readonly=True)
    products_updated = fields.Integer(string='Products Updated', readonly=True)
    products_failed = fields.Integer(string='Products Failed', readonly=True)
    import_log_id = fields.Many2one('vendor.import.log', string='Import Log', readonly=True)
    
    def action_preview(self):
        """Preview products that will be imported"""
        self.ensure_one()
        
        try:
            adapter = self.vendor_id._get_adapter()
            products = adapter.fetch_products()
            
            if self.max_products > 0:
                products = products[:self.max_products]
            
            self.preview_count = len(products)
            self.preview_message = _('Found %d products ready to import from %s') % (
                len(products), self.vendor_id.name
            )
            self.state = 'preview'
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'vendor.import.wizard',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
            
        except Exception as e:
            raise UserError(_('Preview failed: %s') % str(e))
    
    def action_import(self):
        """Execute the import"""
        self.ensure_one()
        
        try:
            # Create import log
            import_log = self.env['vendor.import.log'].create({
                'vendor_id': self.vendor_id.id,
                'state': 'in_progress',
                'import_type': 'manual',
            })
            
            # Run import
            if self.test_mode:
                result = self._test_import()
            else:
                result = self._run_import()
            
            # Update import log
            import_log.write({
                'state': 'done',
                'products_created': result.get('created', 0),
                'products_updated': result.get('updated', 0),
                'products_failed': result.get('failed', 0),
                'end_date': fields.Datetime.now(),
                'notes': result.get('message', ''),
            })
            
            # Update wizard
            self.write({
                'products_created': result.get('created', 0),
                'products_updated': result.get('updated', 0),
                'products_failed': result.get('failed', 0),
                'import_log_id': import_log.id,
                'state': 'done',
            })
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'vendor.import.wizard',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
            
        except Exception as e:
            _logger.error('Import failed: %s', str(e))
            raise UserError(_('Import failed: %s') % str(e))
    
    def _run_import(self):
        """Run actual import"""
        adapter = self.vendor_id._get_adapter()
        
        # Temporarily modify vendor settings based on wizard options
        original_auto_create = self.vendor_id.auto_create_products
        original_auto_update = self.vendor_id.auto_update_prices
        
        if self.import_type == 'update_only':
            self.vendor_id.auto_create_products = False
            self.vendor_id.auto_update_prices = True
        elif self.import_type == 'new_only':
            self.vendor_id.auto_create_products = True
            self.vendor_id.auto_update_prices = False
        
        try:
            result = adapter.import_products()
            return result
        finally:
            # Restore original settings
            self.vendor_id.auto_create_products = original_auto_create
            self.vendor_id.auto_update_prices = original_auto_update
    
    def _test_import(self):
        """Test import without creating/updating products"""
        adapter = self.vendor_id._get_adapter()
        products = adapter.fetch_products()
        
        if self.max_products > 0:
            products = products[:self.max_products]
        
        created = 0
        updated = 0
        failed = 0
        
        for raw_product in products:
            try:
                product_data = adapter.parse_product_data(raw_product)
                
                # Check if product exists
                existing = adapter._find_existing_product(product_data)
                
                if existing:
                    updated += 1
                else:
                    created += 1
                    
            except Exception as e:
                _logger.error('Test import failed for product: %s', str(e))
                failed += 1
        
        message = _('Test import completed: %d would be created, %d would be updated, %d failed') % (
            created, updated, failed
        )
        
        return {
            'created': created,
            'updated': updated,
            'failed': failed,
            'message': message,
        }
    
    def action_view_import_log(self):
        """View the import log"""
        self.ensure_one()
        
        return {
            'name': _('Import Log'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.import.log',
            'res_id': self.import_log_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_products(self):
        """View imported products"""
        self.ensure_one()
        
        if not self.import_log_id:
            return
        
        product_ids = self.import_log_id.import_line_ids.mapped('product_tmpl_id').ids
        
        return {
            'name': _('Imported Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', product_ids)],
        }
