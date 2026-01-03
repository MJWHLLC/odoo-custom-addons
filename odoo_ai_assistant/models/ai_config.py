"""AI Assistant Configuration Model."""
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)


class AIConfig(models.Model):
    """Configuration for AI Assistant integration with AIbot."""
    
    _name = 'ai.config'
    _description = 'AI Assistant Configuration'
    _rec_name = 'name'
    
    name = fields.Char(
        string='Configuration Name',
        required=True,
        default='AIbot Configuration'
    )
    
    aibot_url = fields.Char(
        string='AIbot URL',
        required=True,
        default='http://localhost:5000',
        help='URL where AIbot Flask application is running (e.g., http://localhost:5000)'
    )
    
    api_key = fields.Char(
        string='API Key',
        required=True,
        help='API key for authenticating with AIbot (set in ODOO_API_KEY environment variable)'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    timeout = fields.Integer(
        string='Request Timeout (seconds)',
        default=30,
        help='Timeout for API requests to AIbot'
    )
    
    last_test_date = fields.Datetime(
        string='Last Test Date',
        readonly=True
    )
    
    last_test_result = fields.Text(
        string='Last Test Result',
        readonly=True
    )
    
    @api.constrains('timeout')
    def _check_timeout(self):
        """Validate timeout value."""
        for record in self:
            if record.timeout < 1 or record.timeout > 300:
                raise ValidationError('Timeout must be between 1 and 300 seconds')
    
    def test_connection(self):
        """Test connection to AIbot API."""
        self.ensure_one()
        
        try:
            url = f"{self.aibot_url.rstrip('/')}/api/v1/health"
            headers = {'X-API-Key': self.api_key}
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.last_test_result = f"✓ Connection successful!\nService: {data.get('service')}\nVersion: {data.get('version')}"
                self.last_test_date = fields.Datetime.now()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'Connection to AIbot successful!',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                self.last_test_result = f"✗ Connection failed!\nStatus: {response.status_code}\nResponse: {response.text}"
                self.last_test_date = fields.Datetime.now()
                raise ValidationError(f"Connection failed with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"✗ Connection error: {str(e)}"
            self.last_test_result = error_msg
            self.last_test_date = fields.Datetime.now()
            raise ValidationError(error_msg)
    
    def call_aibot_api(self, endpoint, data):
        """
        Call AIbot API endpoint.
        
        Args:
            endpoint: API endpoint (e.g., '/api/v1/generate')
            data: Request payload dictionary
            
        Returns:
            Response data dictionary
        """
        self.ensure_one()
        
        if not self.active:
            raise ValidationError('AI Assistant configuration is not active')
        
        try:
            url = f"{self.aibot_url.rstrip('/')}{endpoint}"
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            _logger.info(f"Calling AIbot API: {url}")
            
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"AIbot API call failed: {str(e)}")
            raise ValidationError(f"Failed to communicate with AIbot: {str(e)}")
    
    @api.model
    def get_active_config(self):
        """Get the active AI configuration."""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            raise ValidationError(
                'No active AI Assistant configuration found. '
                'Please configure AI Assistant in Settings.'
            )
        return config
