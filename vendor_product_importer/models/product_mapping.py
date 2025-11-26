# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductFieldMapping(models.Model):
    _name = 'product.field.mapping'
    _description = 'Product Field Mapping'
    _order = 'sequence, vendor_id'

    name = fields.Char(string='Mapping Name', required=True)
    vendor_id = fields.Many2one('vendor.config', string='Vendor', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # Source Field (from vendor)
    vendor_field_name = fields.Char(string='Vendor Field Name', required=True,
                                    help='Field name from vendor data (e.g., "title", "price", "description")')
    vendor_field_type = fields.Selection([
        ('text', 'Text'),
        ('html', 'HTML'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('image', 'Image URL'),
    ], string='Vendor Field Type', default='text')
    
    # Target Field (Odoo product field)
    odoo_field_name = fields.Selection([
        ('name', 'Product Name'),
        ('default_code', 'Internal Reference'),
        ('barcode', 'Barcode'),
        ('list_price', 'Sales Price'),
        ('standard_price', 'Cost'),
        ('description', 'Description'),
        ('description_sale', 'Sales Description'),
        ('weight', 'Weight'),
        ('volume', 'Volume'),
        ('categ_id', 'Product Category'),
    ], string='Odoo Field', required=True)
    
    # Transformation
    apply_transformation = fields.Boolean(string='Apply Transformation', default=False)
    transformation_type = fields.Selection([
        ('uppercase', 'Convert to Uppercase'),
        ('lowercase', 'Convert to Lowercase'),
        ('title', 'Title Case'),
        ('strip', 'Strip Whitespace'),
        ('multiply', 'Multiply by Factor'),
        ('divide', 'Divide by Factor'),
        ('add', 'Add Value'),
        ('subtract', 'Subtract Value'),
        ('regex', 'Regular Expression'),
        ('python', 'Python Expression'),
    ], string='Transformation Type')
    
    transformation_value = fields.Char(string='Transformation Value',
                                      help='Value to use in transformation (e.g., factor, regex pattern, python code)')
    
    # Default Value
    use_default = fields.Boolean(string='Use Default if Empty', default=False)
    default_value = fields.Char(string='Default Value')
    
    # Validation
    is_required = fields.Boolean(string='Required', default=False,
                                 help='Skip product if this field is empty')
    
    notes = fields.Text(string='Notes')
    
    def apply_mapping(self, vendor_data):
        """
        Apply this mapping to vendor data
        
        :param vendor_data: Dictionary of vendor data
        :return: Transformed value or None
        """
        self.ensure_one()
        
        # Get value from vendor data
        value = vendor_data.get(self.vendor_field_name)
        
        # Check if required
        if self.is_required and not value:
            raise ValueError(_('Required field %s is missing') % self.vendor_field_name)
        
        # Use default if empty
        if not value and self.use_default:
            value = self.default_value
        
        # Apply transformation
        if value and self.apply_transformation:
            value = self._apply_transformation(value)
        
        return value
    
    def _apply_transformation(self, value):
        """Apply transformation to value"""
        self.ensure_one()
        
        try:
            if self.transformation_type == 'uppercase':
                return str(value).upper()
            elif self.transformation_type == 'lowercase':
                return str(value).lower()
            elif self.transformation_type == 'title':
                return str(value).title()
            elif self.transformation_type == 'strip':
                return str(value).strip()
            elif self.transformation_type == 'multiply':
                factor = float(self.transformation_value or 1.0)
                return float(value) * factor
            elif self.transformation_type == 'divide':
                factor = float(self.transformation_value or 1.0)
                return float(value) / factor if factor != 0 else value
            elif self.transformation_type == 'add':
                amount = float(self.transformation_value or 0.0)
                return float(value) + amount
            elif self.transformation_type == 'subtract':
                amount = float(self.transformation_value or 0.0)
                return float(value) - amount
            elif self.transformation_type == 'regex':
                import re
                pattern = self.transformation_value
                if pattern:
                    match = re.search(pattern, str(value))
                    return match.group(0) if match else value
                return value
            elif self.transformation_type == 'python':
                # Safe eval with limited scope
                safe_dict = {'value': value}
                return eval(self.transformation_value, {"__builtins__": {}}, safe_dict)
            else:
                return value
        except Exception as e:
            _logger.error('Error applying transformation %s to value %s: %s',
                         self.transformation_type, value, str(e))
            return value
    
    @api.model
    def get_mappings_for_vendor(self, vendor_id):
        """Get all active mappings for a vendor"""
        return self.search([
            ('vendor_id', '=', vendor_id),
            ('active', '=', True),
        ], order='sequence')
    
    @api.model
    def map_vendor_data_to_product(self, vendor_id, vendor_data):
        """
        Map vendor data to Odoo product fields
        
        :param vendor_id: vendor.config ID
        :param vendor_data: Dictionary of vendor data
        :return: Dictionary of Odoo product field values
        """
        mappings = self.get_mappings_for_vendor(vendor_id)
        product_vals = {}
        
        for mapping in mappings:
            try:
                value = mapping.apply_mapping(vendor_data)
                if value is not None:
                    product_vals[mapping.odoo_field_name] = value
            except Exception as e:
                _logger.error('Error applying mapping %s: %s', mapping.name, str(e))
                if mapping.is_required:
                    raise
        
        return product_vals
