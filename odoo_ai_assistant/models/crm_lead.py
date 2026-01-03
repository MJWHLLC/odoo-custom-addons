"""CRM Lead extension for AI features."""
from odoo import models, fields, api
import json


class CRMLead(models.Model):
    """Extend CRM Lead with AI capabilities."""
    
    _inherit = 'crm.lead'
    
    def action_generate_ai_email(self):
        """Generate follow-up email using AI."""
        self.ensure_one()
        
        # Prepare context data
        context_data = {
            'recipient_name': self.partner_id.name if self.partner_id else self.contact_name,
            'context': f"Lead: {self.name}\nStage: {self.stage_id.name}\nExpected Revenue: {self.expected_revenue}",
            'tone': 'professional',
        }
        
        # Determine email purpose based on stage
        if self.stage_id.is_won:
            purpose = 'Thank you email for won opportunity'
        elif self.probability < 50:
            purpose = 'Follow-up email to re-engage lead'
        else:
            purpose = 'Follow-up email for active opportunity'
        
        # Create conversation
        conversation = self.env['ai.conversation'].create_and_generate({
            'prompt': purpose,
            'conversation_type': 'email',
            'context_data': json.dumps(context_data),
            'related_model': 'crm.lead',
            'related_record_id': self.id,
        })
        
        if conversation.success and conversation.response:
            # Open email composer with AI-generated content
            return {
                'type': 'ir.actions.act_window',
                'name': 'Send Email',
                'res_model': 'mail.compose.message',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_model': 'crm.lead',
                    'default_res_id': self.id,
                    'default_body': conversation.response,
                    'default_partner_ids': [(6, 0, [self.partner_id.id])] if self.partner_id else [],
                }
            }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error',
                'message': conversation.error_message or 'Failed to generate email',
                'type': 'danger',
                'sticky': True,
            }
        }
    
    def action_ai_assistant(self):
        """Open AI assistant for this lead."""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'AI Assistant',
            'res_model': 'ai.conversation',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_conversation_type': 'customer_support',
                'default_related_model': 'crm.lead',
                'default_related_record_id': self.id,
                'default_context_data': json.dumps({
                    'lead_name': self.name,
                    'partner': self.partner_id.name if self.partner_id else self.contact_name,
                    'stage': self.stage_id.name,
                    'expected_revenue': self.expected_revenue,
                }),
            }
        }
