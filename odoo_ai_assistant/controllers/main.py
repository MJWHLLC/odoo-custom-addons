"""Web controllers for AI Assistant."""
from odoo import http
from odoo.http import request
import json


class AIAssistantController(http.Controller):
    """Controller for AI Assistant web interface."""
    
    @http.route('/ai_assistant/generate', type='json', auth='user')
    def generate_response(self, prompt, conversation_type='general', **kwargs):
        """Generate AI response via AJAX."""
        try:
            conversation = request.env['ai.conversation'].create_and_generate({
                'prompt': prompt,
                'conversation_type': conversation_type,
                'document_type': kwargs.get('document_type'),
                'jurisdiction': kwargs.get('jurisdiction'),
                'context_data': json.dumps(kwargs.get('context', {})),
                'related_model': kwargs.get('related_model'),
                'related_record_id': kwargs.get('related_record_id'),
            })
            
            return {
                'success': conversation.success,
                'response': conversation.response,
                'conversation_id': conversation.id,
                'error': conversation.error_message,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    @http.route('/ai_assistant/history', type='json', auth='user')
    def get_history(self, limit=10, conversation_type=None):
        """Get conversation history for current user."""
        domain = [('user_id', '=', request.env.user.id)]
        if conversation_type:
            domain.append(('conversation_type', '=', conversation_type))
        
        conversations = request.env['ai.conversation'].search(
            domain,
            limit=limit,
            order='create_date desc'
        )
        
        return [{
            'id': conv.id,
            'title': conv.title,
            'prompt': conv.prompt,
            'response': conv.response,
            'type': conv.conversation_type,
            'date': conv.create_date.isoformat() if conv.create_date else None,
            'success': conv.success,
        } for conv in conversations]
