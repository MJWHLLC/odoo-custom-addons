# Odoo AI Assistant

Comprehensive AI integration for Odoo using the AIbot Flask application.

## Features

### Core Functionality
- **AI-powered Chat Interface**: Accessible from any Odoo module
- **Conversation History**: Track all AI interactions with full context
- **Multi-user Support**: Each user has their own conversation history
- **Flexible Configuration**: Easy setup and management

### AI Capabilities

#### 1. Product Management
- **AI Product Descriptions**: Generate compelling product descriptions automatically
- Accessible from product form view with one click
- Uses product name, category, and attributes as context

#### 2. CRM & Sales
- **AI Email Generation**: Create professional follow-up emails
- **Terms & Conditions**: Generate sales agreement terms automatically
- **Lead Assistant**: Get AI help for lead management
- Context-aware based on opportunity stage and details

#### 3. Document Generation
- Generate legal and business documents
- Support for contracts, agreements, policies
- Jurisdiction-aware content generation

#### 4. General Q&A
- Ask questions about your business
- Get assistance with Odoo workflows
- Customer support help

## Installation

### Prerequisites
1. **AIbot Flask Application** must be running on the same server
2. Python dependencies: `requests`

### Steps

1. **Install the Module**
   ```bash
   # Copy module to Odoo addons directory
   cp -r odoo_ai_assistant /path/to/odoo/addons/
   
   # Restart Odoo
   sudo systemctl restart odoo
   ```

2. **Activate Developer Mode**
   - Go to Settings > Activate Developer Mode

3. **Update Apps List**
   - Go to Apps > Update Apps List

4. **Install Module**
   - Search for "Odoo AI Assistant"
   - Click Install

5. **Configure AIbot Connection**
   - Go to AI Assistant > Configuration > AI Configuration
   - Create new configuration:
     - **AIbot URL**: `http://localhost:5000` (or your AIbot URL)
     - **API Key**: Your ODOO_API_KEY from AIbot environment
     - **Timeout**: 30 seconds (default)
   - Click "Test Connection" to verify

## AIbot Setup

### 1. Set Environment Variables

Create a `.env` file in your AIbot directory:

```bash
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here

# GitHub Models API (for AI functionality)
GITHUB_MODEL_API_TOKEN=your-github-token
GITHUB_MODEL_NAME=your-model-name

# Odoo Integration
ODOO_API_KEY=your-secure-api-key-here

# Email Configuration (optional)
MAIL_SERVER=localhost
MAIL_PORT=25
MAIL_USE_TLS=false
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

### 2. Start AIbot

```bash
cd /path/to/AIbot
python app.py
```

The AIbot will be available at `http://localhost:5000`

### 3. Verify API Endpoints

Test the health endpoint:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AIbot",
  "version": "1.0"
}
```

## Usage

### Product Descriptions

1. Open any product in Odoo
2. Click the "AI Description" button
3. AI will generate a description based on product details
4. Description is automatically applied to the product

### CRM Email Generation

1. Open a CRM lead/opportunity
2. Click "AI Email" button
3. AI generates contextual follow-up email
4. Email composer opens with AI-generated content
5. Review, edit if needed, and send

### Sales Order Terms

1. Open a sales order
2. Click "AI Terms" button
3. AI generates terms and conditions
4. Terms are added to the order notes

### General AI Assistant

1. Go to AI Assistant menu
2. Click "Conversations"
3. Create new conversation
4. Select conversation type
5. Enter your prompt
6. Click "Generate Response"

### From Other Modules

Look for the "AI Assistant" button in:
- CRM Leads
- Sales Orders
- Products
- And more!

## API Endpoints

The AIbot provides these endpoints for Odoo integration:

### Health Check
```
GET /api/v1/health
```

### General Generation
```
POST /api/v1/generate
Content-Type: application/json
X-API-Key: your-api-key

{
  "prompt": "Your question",
  "document_type": "General",
  "jurisdiction": "Federal"
}
```

### Product Description
```
POST /api/v1/generate/product-description
Content-Type: application/json
X-API-Key: your-api-key

{
  "product_name": "Product Name",
  "category": "Category",
  "features": ["feature1", "feature2"]
}
```

### Email Generation
```
POST /api/v1/generate/email
Content-Type: application/json
X-API-Key: your-api-key

{
  "purpose": "Follow-up email",
  "recipient_name": "John Doe",
  "tone": "professional"
}
```

### Document Generation
```
POST /api/v1/generate/document
Content-Type: application/json
X-API-Key: your-api-key

{
  "document_type": "Contract",
  "jurisdiction": "Federal",
  "parties": ["Party 1", "Party 2"],
  "terms": "Key terms..."
}
```

## Troubleshooting

### Connection Failed

1. **Check AIbot is Running**
   ```bash
   curl http://localhost:5000/api/v1/health
   ```

2. **Verify API Key**
   - Ensure ODOO_API_KEY in AIbot matches configuration in Odoo

3. **Check Firewall**
   - Ensure port 5000 is accessible

### Slow Responses

1. **Increase Timeout**
   - Go to AI Configuration
   - Increase timeout value (default: 30 seconds)

2. **Check AIbot Logs**
   - Look for errors in AIbot console output

### API Errors

1. **Check AIbot Logs**
   - Review Flask application logs for errors

2. **Verify GitHub Models Configuration**
   - Ensure GITHUB_MODEL_API_TOKEN is valid
   - Check GITHUB_MODEL_NAME is correct

## Security

- **API Key**: Always use a strong, unique API key
- **HTTPS**: Use HTTPS in production environments
- **Firewall**: Restrict AIbot access to Odoo server only
- **Environment Variables**: Never commit secrets to version control

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review AIbot and Odoo logs
3. Verify configuration settings

## License

LGPL-3

## Author

MJWHLLC
