{
    'name': 'Odoo AI Assistant',
    'version': '17.0.1.0.0',
    'category': 'Productivity',
    'summary': 'AI-powered assistant integrated with AIbot for document generation, Q&A, and automation',
    'description': """
        Odoo AI Assistant
        =================
        
        Comprehensive AI integration for Odoo using the AIbot Flask application.
        
        Features:
        ---------
        * AI-powered chat interface accessible from any Odoo module
        * Product description generation
        * Email content generation
        * Legal and business document generation
        * Customer support assistance
        * Integration with Sales, CRM, Products, and other modules
        * Conversation history tracking
        * Multi-user support with authentication
        
        Configuration:
        --------------
        1. Set up AIbot Flask application on the same server
        2. Configure AIbot URL and API key in Settings > AI Assistant Configuration
        3. Start using AI features throughout Odoo
    """,
    'author': 'MJWHLLC',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'sale_management',
        'crm',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_config_views.xml',
        'views/ai_conversation_views.xml',
        'views/menu_views.xml',
        'views/product_template_views.xml',
        'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_ai_assistant/static/src/js/ai_assistant_widget.js',
            'odoo_ai_assistant/static/src/css/ai_assistant.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
