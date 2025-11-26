# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PriceTier(models.Model):
    _name = 'product.price.tier'
    _description = 'Product Price Tier'
    _order = 'min_cost'

    name = fields.Char(string='Tier Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Cost Range
    min_cost = fields.Float(string='Minimum Cost', required=True, default=0.0,
                           help='Minimum product cost for this tier (inclusive)')
    max_cost = fields.Float(string='Maximum Cost', required=True, default=0.0,
                           help='Maximum product cost for this tier (inclusive). Use 0 for unlimited')
    
    # Pricing Strategy
    pricing_method = fields.Selection([
        ('percentage', 'Percentage Markup'),
        ('fixed', 'Fixed Amount'),
        ('formula', 'Custom Formula'),
    ], string='Pricing Method', required=True, default='percentage')
    
    markup_percentage = fields.Float(string='Markup Percentage', default=30.0,
                                    help='Percentage to add to cost price (e.g., 30 for 30%)')
    fixed_amount = fields.Float(string='Fixed Amount', default=0.0,
                               help='Fixed amount to add to cost price')
    
    # Custom Formula (for advanced users)
    price_formula = fields.Text(string='Price Formula',
                               help='Python expression to calculate price. Available variables: cost, product\n'
                                    'Example: cost * 1.3 + 5.0')
    
    # Rounding
    round_price = fields.Boolean(string='Round Price', default=True)
    rounding_method = fields.Selection([
        ('up', 'Round Up'),
        ('down', 'Round Down'),
        ('nearest', 'Round to Nearest'),
    ], string='Rounding Method', default='nearest')
    rounding_precision = fields.Float(string='Rounding Precision', default=0.99,
                                     help='Round to nearest value (e.g., 0.99 for $X.99 pricing)')
    
    # Minimum Profit
    min_profit_amount = fields.Float(string='Minimum Profit Amount', default=0.0,
                                    help='Ensure minimum profit amount')
    min_profit_percentage = fields.Float(string='Minimum Profit Percentage', default=0.0,
                                        help='Ensure minimum profit percentage')
    
    # Category Specific
    categ_ids = fields.Many2many('product.category', string='Product Categories',
                                 help='Apply this tier only to specific categories. Leave empty for all categories')
    
    # Vendor Specific
    vendor_ids = fields.Many2many('vendor.config', string='Vendors',
                                  help='Apply this tier only to specific vendors. Leave empty for all vendors')
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    
    # Notes
    notes = fields.Text(string='Notes')
    
    @api.constrains('min_cost', 'max_cost')
    def _check_cost_range(self):
        for record in self:
            if record.max_cost > 0 and record.min_cost > record.max_cost:
                raise ValidationError(_('Minimum cost cannot be greater than maximum cost.'))
    
    @api.constrains('markup_percentage')
    def _check_markup_percentage(self):
        for record in self:
            if record.pricing_method == 'percentage' and record.markup_percentage < 0:
                raise ValidationError(_('Markup percentage cannot be negative.'))
    
    def calculate_sale_price(self, cost, product=None, vendor=None):
        """
        Calculate sale price based on tier rules
        
        :param cost: Product cost price
        :param product: product.template record (optional)
        :param vendor: vendor.config record (optional)
        :return: Calculated sale price
        """
        self.ensure_one()
        
        # Check if tier applies to this product/vendor
        if self.categ_ids and product and product.categ_id not in self.categ_ids:
            return None
        
        if self.vendor_ids and vendor and vendor not in self.vendor_ids:
            return None
        
        # Calculate base price
        if self.pricing_method == 'percentage':
            price = cost * (1 + self.markup_percentage / 100.0)
        elif self.pricing_method == 'fixed':
            price = cost + self.fixed_amount
        elif self.pricing_method == 'formula' and self.price_formula:
            try:
                # Safe eval with limited scope
                safe_dict = {
                    'cost': cost,
                    'product': product,
                    'vendor': vendor,
                }
                price = eval(self.price_formula, {"__builtins__": {}}, safe_dict)
            except Exception as e:
                _logger.error('Error evaluating price formula for tier %s: %s', self.name, str(e))
                price = cost * (1 + self.markup_percentage / 100.0)
        else:
            price = cost * (1 + self.markup_percentage / 100.0)
        
        # Apply minimum profit constraints
        if self.min_profit_amount > 0:
            min_price = cost + self.min_profit_amount
            price = max(price, min_price)
        
        if self.min_profit_percentage > 0:
            min_price = cost * (1 + self.min_profit_percentage / 100.0)
            price = max(price, min_price)
        
        # Apply rounding
        if self.round_price:
            price = self._round_price(price)
        
        return price
    
    def _round_price(self, price):
        """Round price according to tier settings"""
        self.ensure_one()
        
        if self.rounding_precision <= 0:
            return price
        
        if self.rounding_method == 'up':
            # Round up to nearest precision
            import math
            return math.ceil(price / self.rounding_precision) * self.rounding_precision
        elif self.rounding_method == 'down':
            # Round down to nearest precision
            import math
            return math.floor(price / self.rounding_precision) * self.rounding_precision
        else:
            # Round to nearest precision
            return round(price / self.rounding_precision) * self.rounding_precision
    
    @api.model
    def get_applicable_tier(self, cost, product=None, vendor=None):
        """
        Find the most applicable tier for given cost and context
        
        :param cost: Product cost price
        :param product: product.template record (optional)
        :param vendor: vendor.config record (optional)
        :return: price.tier record or None
        """
        domain = [
            ('active', '=', True),
            ('min_cost', '<=', cost),
            '|',
            ('max_cost', '=', 0),
            ('max_cost', '>=', cost),
        ]
        
        # Filter by category if product provided
        if product and product.categ_id:
            domain = [
                '&',
                '|',
                ('categ_ids', '=', False),
                ('categ_ids', 'in', product.categ_id.ids),
            ] + domain
        
        # Filter by vendor if provided
        if vendor:
            domain = [
                '&',
                '|',
                ('vendor_ids', '=', False),
                ('vendor_ids', 'in', vendor.ids),
            ] + domain
        
        # Get tiers ordered by specificity (most specific first)
        tiers = self.search(domain, order='sequence, min_cost desc')
        
        # Return most specific tier
        for tier in tiers:
            if tier.categ_ids and product and product.categ_id in tier.categ_ids:
                return tier
            if tier.vendor_ids and vendor and vendor in tier.vendor_ids:
                return tier
        
        # Return first general tier
        return tiers[:1] if tiers else None
    
    @api.model
    def calculate_price_for_product(self, cost, product=None, vendor=None):
        """
        Calculate sale price for a product using appropriate tier
        
        :param cost: Product cost price
        :param product: product.template record (optional)
        :param vendor: vendor.config record (optional)
        :return: Calculated sale price or cost if no tier found
        """
        tier = self.get_applicable_tier(cost, product, vendor)
        if tier:
            price = tier.calculate_sale_price(cost, product, vendor)
            if price:
                return price
        
        # Fallback: return cost with default 30% markup
        return cost * 1.3
