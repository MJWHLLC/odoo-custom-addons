"""Sale Order extension for AI features."""
from odoo import models, fields, api
import json


class SaleOrder(models.Model):
    """Extend Sale Order with AI capabilities."""
    
    _inherit = 'sale.order'
    
    def action_generate_ai_terms(self):
        """Generate terms and conditions using AI."""
        self.ensure_one()
        
        # Prepare context data
        parties = [
            self.company_id.name,
            self.partner_id.name,
        ]
        
        terms = f"""
        Order Total: {self.amount_total} {self.currency_id.name}
        Payment Terms: {self.payment_term_id.name if self.payment_term_id else 'Immediate'}
        Delivery: {self.commitment_date or 'As per agreement'}
        """
        
        context_data = {
            'parties': parties,
            'terms': terms,
        }
        
        # Create conversation
        conversation = self.env['ai.conversation'].create_and_generate({
            'prompt': 'Generate terms and conditions for this sales order',
            'conversation_type': 'document',
            'document_type': 'Sales Agreement',
            'jurisdiction': self.company_id.country_id.name if self.company_id.country_id else 'Federal',
            'context_data': json.dumps(context_data),
            'related_model': 'sale.order',
            'related_record_id': self.id,
        })
        
        if conversation.success and conversation.response:
            self.note = conversation.response
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Terms and conditions generated!',
                    'type': 'success',
                    'sticky': False,
                }
            }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error',
                'message': conversation.error_message or 'Failed to generate terms',
                'type': 'danger',
                'sticky': True,
            }
        }
    
    def action_ai_assistant(self):
        """Open AI assistant for this sale order."""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'AI Assistant',
            'res_model': 'ai.conversation',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_conversation_type': 'general',
                'default_related_model': 'sale.order',
                'default_related_record_id': self.id,
                'default_context_data': json.dumps({
                    'order_name': self.name,
                    'customer': self.partner_id.name,
                    'total': f"{self.amount_total} {self.currency_id.name}",
                    'state': self.state,
                }),
            }
        }
