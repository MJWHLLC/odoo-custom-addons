"""AI Conversation Model for tracking AI interactions."""
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AIConversation(models.Model):
    """Track AI conversations and history."""
    
    _name = 'ai.conversation'
    _description = 'AI Conversation'
    _order = 'create_date desc'
    _rec_name = 'title'
    
    title = fields.Char(
        string='Title',
        compute='_compute_title',
        store=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        ondelete='cascade'
    )
    
    prompt = fields.Text(
        string='Prompt',
        required=True
    )
    
    response = fields.Text(
        string='Response',
        readonly=True
    )
    
    conversation_type = fields.Selection([
        ('general', 'General Q&A'),
        ('product_description', 'Product Description'),
        ('email', 'Email Generation'),
        ('document', 'Document Generation'),
        ('customer_support', 'Customer Support'),
    ], string='Type', required=True, default='general')
    
    document_type = fields.Char(
        string='Document Type'
    )
    
    jurisdiction = fields.Char(
        string='Jurisdiction'
    )
    
    context_data = fields.Text(
        string='Context Data',
        help='Additional context provided with the request'
    )
    
    related_model = fields.Char(
        string='Related Model',
        help='Odoo model this conversation is related to (e.g., product.template)'
    )
    
    related_record_id = fields.Integer(
        string='Related Record ID',
        help='ID of the related record'
    )
    
    success = fields.Boolean(
        string='Success',
        default=True
    )
    
    error_message = fields.Text(
        string='Error Message'
    )
    
    duration_ms = fields.Integer(
        string='Duration (ms)',
        help='Time taken to generate response in milliseconds'
    )
    
    @api.depends('prompt', 'conversation_type')
    def _compute_title(self):
        """Generate title from prompt."""
        for record in self:
            if record.prompt:
                # Take first 50 characters of prompt as title
                title = record.prompt[:50]
                if len(record.prompt) > 50:
                    title += '...'
                record.title = title
            else:
                record.title = f"New {record.conversation_type.replace('_', ' ').title()}"
    
    def generate_response(self):
        """Generate AI response for this conversation."""
        self.ensure_one()
        
        config = self.env['ai.config'].get_active_config()
        
        import time
        start_time = time.time()
        
        try:
            # Prepare request data based on conversation type
            if self.conversation_type == 'product_description':
                endpoint = '/api/v1/generate/product-description'
                data = {
                    'product_name': self.prompt,
                }
                if self.context_data:
                    import json
                    try:
                        context = json.loads(self.context_data)
                        data.update(context)
                    except json.JSONDecodeError:
                        pass
            
            elif self.conversation_type == 'email':
                endpoint = '/api/v1/generate/email'
                data = {
                    'purpose': self.prompt,
                }
                if self.context_data:
                    import json
                    try:
                        context = json.loads(self.context_data)
                        data.update(context)
                    except json.JSONDecodeError:
                        pass
            
            elif self.conversation_type == 'document':
                endpoint = '/api/v1/generate/document'
                data = {
                    'document_type': self.document_type or 'General',
                    'jurisdiction': self.jurisdiction or 'Federal',
                    'additional_info': self.prompt,
                }
                if self.context_data:
                    import json
                    try:
                        context = json.loads(self.context_data)
                        data.update(context)
                    except json.JSONDecodeError:
                        pass
            
            else:  # general or customer_support
                endpoint = '/api/v1/generate'
                data = {
                    'prompt': self.prompt,
                    'document_type': self.document_type or 'General',
                    'jurisdiction': self.jurisdiction or 'Federal',
                }
                if self.context_data:
                    import json
                    try:
                        data['context'] = json.loads(self.context_data)
                    except json.JSONDecodeError:
                        pass
            
            # Call AIbot API
            result = config.call_aibot_api(endpoint, data)
            
            # Extract response based on endpoint
            if self.conversation_type == 'product_description':
                response_text = result.get('description', '')
            elif self.conversation_type == 'email':
                response_text = result.get('email_content', '')
            elif self.conversation_type == 'document':
                response_text = result.get('document_content', '')
            else:
                response_text = result.get('response', '')
            
            # Calculate duration
            duration = int((time.time() - start_time) * 1000)
            
            # Update conversation
            self.write({
                'response': response_text,
                'success': result.get('success', True),
                'duration_ms': duration,
            })
            
            _logger.info(f"AI response generated successfully in {duration}ms")
            
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            
            self.write({
                'success': False,
                'error_message': error_msg,
                'duration_ms': duration,
            })
            
            _logger.error(f"Failed to generate AI response: {error_msg}")
            raise ValidationError(f"Failed to generate AI response: {error_msg}")
    
    @api.model
    def create_and_generate(self, vals):
        """Create conversation and generate response immediately."""
        conversation = self.create(vals)
        conversation.generate_response()
        return conversation
