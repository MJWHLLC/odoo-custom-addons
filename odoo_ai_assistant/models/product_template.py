"""Product Template extension for AI features."""
from odoo import models, fields, api
import json


class ProductTemplate(models.Model):
    """Extend Product Template with AI capabilities."""
    
    _inherit = 'product.template'
    
    def action_generate_ai_description(self):
        """Generate product description using AI."""
        self.ensure_one()
        
        # Prepare context data
        context_data = {
            'product_name': self.name,
            'category': self.categ_id.name if self.categ_id else '',
            'features': [],
        }
        
        # Add features from product attributes if available
        if self.attribute_line_ids:
            for line in self.attribute_line_ids:
                for value in line.value_ids:
                    context_data['features'].append(f"{line.attribute_id.name}: {value.name}")
        
        # Create conversation
        conversation = self.env['ai.conversation'].create_and_generate({
            'prompt': self.name,
            'conversation_type': 'product_description',
            'context_data': json.dumps(context_data),
            'related_model': 'product.template',
            'related_record_id': self.id,
        })
        
        # Update product description if successful
        if conversation.success and conversation.response:
            self.description_sale = conversation.response
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'AI description generated and applied!',
                    'type': 'success',
                    'sticky': False,
                }
            }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error',
                'message': conversation.error_message or 'Failed to generate description',
                'type': 'danger',
                'sticky': True,
            }
        }
