# AIbot-Odoo Integration Complete Guide

This guide provides complete instructions for integrating the AIbot Flask application with your Odoo instance.

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [AIbot Setup](#aibot-setup)
5. [Odoo Module Installation](#odoo-module-installation)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Usage Examples](#usage-examples)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

## Overview

The integration connects your Odoo ERP system with the AIbot Flask application, enabling AI-powered features throughout Odoo:

- **Product Description Generation**: Automatically create compelling product descriptions
- **Email Generation**: Generate professional emails for CRM and sales
- **Document Generation**: Create legal and business documents
- **General AI Assistant**: Get help with any business question

## Architecture

```
┌─────────────────┐         REST API          ┌──────────────────┐
│                 │    (HTTP + API Key)       │                  │
│  Odoo Server    │◄─────────────────────────►│  AIbot Flask     │
│                 │                            │  Application     │
│  - AI Module    │                            │  - API Routes    │
│  - Models       │                            │  - Model Client  │
│  - Controllers  │                            │  - Auth          │
└─────────────────┘                            └──────────────────┘
                                                        │
                                                        ▼
                                               ┌──────────────────┐
                                               │  GitHub Models   │
                                               │  API             │
                                               └──────────────────┘
```

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended) or Windows Server
- **Python**: 3.8 or higher
- **Odoo**: Version 17.0
- **Network**: AIbot and Odoo on same server or network

### Required Packages

**For AIbot:**
```bash
pip install flask python-dotenv requests flask-mail flask-wtf
```

**For Odoo Module:**
```bash
pip install requests
```

## AIbot Setup

### Step 1: Prepare AIbot Application

1. **Navigate to AIbot directory:**
   ```bash
   cd /path/to/AIbot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Configure Environment Variables

Create a `.env` file in the AIbot directory:

```bash
# Flask Configuration
FLASK_SECRET_KEY=your-very-secure-secret-key-here
FLASK_ENV=production

# GitHub Models API Configuration
GITHUB_MODEL_API_TOKEN=your-github-models-api-token
GITHUB_MODEL_NAME=gpt-4  # or your preferred model

# Odoo Integration API Key
ODOO_API_KEY=your-secure-odoo-api-key-here

# Email Configuration (Optional)
MAIL_SERVER=localhost
MAIL_PORT=25
MAIL_USE_TLS=false
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# Authentication (Optional - for web interface)
AUTH_USERNAME=admin
AUTH_PASSWORD=your-admin-password
```

**Important Notes:**
- Generate a strong `ODOO_API_KEY` (at least 32 characters)
- Keep the API key secure and never commit it to version control
- Use the same API key in both AIbot and Odoo configuration

### Step 3: Test AIbot

1. **Start AIbot:**
   ```bash
   python app.py
   ```

2. **Verify it's running:**
   ```bash
   curl http://localhost:5000/api/v1/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "AIbot",
     "version": "1.0"
   }
   ```

3. **Test with API key:**
   ```bash
   curl -H "X-API-Key: your-odoo-api-key" \
        -H "Content-Type: application/json" \
        -X POST \
        -d '{"prompt":"Hello, AI!"}' \
        http://localhost:5000/api/v1/generate
   ```

### Step 4: Set Up as System Service (Production)

Create a systemd service file `/etc/systemd/system/aibot.service`:

```ini
[Unit]
Description=AIbot Flask Application
After=network.target

[Service]
Type=simple
User=odoo
WorkingDirectory=/path/to/AIbot
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aibot
sudo systemctl start aibot
sudo systemctl status aibot
```

## Odoo Module Installation

### Step 1: Copy Module to Odoo

```bash
# Copy the module to Odoo addons directory
sudo cp -r odoo-custom-addons/odoo_ai_assistant /opt/odoo/addons/

# Set proper permissions
sudo chown -R odoo:odoo /opt/odoo/addons/odoo_ai_assistant
```

### Step 2: Update Odoo Apps List

1. **Restart Odoo:**
   ```bash
   sudo systemctl restart odoo
   ```

2. **Log in to Odoo as Administrator**

3. **Activate Developer Mode:**
   - Go to Settings
   - Scroll to bottom
   - Click "Activate the developer mode"

4. **Update Apps List:**
   - Go to Apps
   - Click "Update Apps List"
   - Click "Update" in the dialog

### Step 3: Install the Module

1. **Search for the module:**
   - In Apps, remove the "Apps" filter
   - Search for "Odoo AI Assistant"

2. **Install:**
   - Click "Install" button
   - Wait for installation to complete

## Configuration

### Step 1: Configure AI Assistant in Odoo

1. **Navigate to AI Configuration:**
   - Go to AI Assistant menu (top menu bar)
   - Click Configuration > AI Configuration

2. **Create New Configuration:**
   - Click "Create"
   - Fill in the details:
     - **Name**: "AIbot Production" (or any name)
     - **AIbot URL**: `http://localhost:5000` (or your AIbot URL)
     - **API Key**: The same key you set in AIbot's `.env` file
     - **Timeout**: 30 (seconds)
   - Click "Save"

3. **Test Connection:**
   - Click "Test Connection" button
   - You should see a success notification
   - Check "Last Test Result" field for details

### Step 2: Verify Integration

1. **Check Conversation Menu:**
   - Go to AI Assistant > Conversations
   - You should see an empty list (ready for conversations)

2. **Test from Product:**
   - Go to Sales > Products > Products
   - Open any product
   - You should see "AI Description" button in the button box

## Testing

### Test 1: Product Description Generation

1. **Create or open a product:**
   - Go to Sales > Products > Products
   - Create a new product or open existing one
   - Set product name: "Premium Wireless Headphones"

2. **Generate AI Description:**
   - Click "AI Description" button
   - Wait for processing (5-10 seconds)
   - Check the "Sales Description" field
   - Should contain AI-generated description

3. **Verify Conversation:**
   - Go to AI Assistant > Conversations
   - You should see the conversation record
   - Check the prompt and response

### Test 2: CRM Email Generation

1. **Create or open a lead:**
   - Go to CRM > Leads
   - Create a new lead or open existing one

2. **Generate AI Email:**
   - Click "AI Email" button
   - Wait for processing
   - Email composer should open with AI-generated content

3. **Review and send:**
   - Review the generated email
   - Edit if needed
   - Send to customer

### Test 3: General AI Assistant

1. **Open AI Assistant:**
   - Go to AI Assistant > Conversations
   - Click "Create"

2. **Ask a question:**
   - Select Type: "General Q&A"
   - Enter prompt: "What are best practices for customer follow-up?"
   - Click "Generate Response"

3. **Review response:**
   - Check the response field
   - Verify it's relevant and helpful

## Usage Examples

### Example 1: Bulk Product Description Generation

```python
# In Odoo Python console or custom script
products = env['product.template'].search([('description_sale', '=', False)])
for product in products:
    try:
        product.action_generate_ai_description()
        env.cr.commit()
    except Exception as e:
        print(f"Failed for {product.name}: {e}")
```

### Example 2: Automated Email Follow-ups

```python
# Generate follow-up emails for stale leads
leads = env['crm.lead'].search([
    ('probability', '<', 50),
    ('date_last_stage_update', '<', fields.Date.today() - timedelta(days=7))
])
for lead in leads:
    lead.action_generate_ai_email()
```

### Example 3: API Call from External System

```bash
curl -X POST http://localhost:5000/api/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "prompt": "Generate a professional email for customer follow-up",
    "document_type": "Email",
    "context": {
      "customer_name": "John Doe",
      "last_contact": "2 weeks ago"
    }
  }'
```

## Troubleshooting

### Issue: "Connection Failed" Error

**Symptoms:**
- Test Connection fails
- "Failed to communicate with AIbot" error

**Solutions:**

1. **Check AIbot is running:**
   ```bash
   curl http://localhost:5000/api/v1/health
   ```

2. **Verify API key:**
   - Check `.env` file in AIbot
   - Check AI Configuration in Odoo
   - Ensure they match exactly

3. **Check firewall:**
   ```bash
   sudo ufw status
   sudo ufw allow 5000/tcp
   ```

4. **Check AIbot logs:**
   ```bash
   sudo journalctl -u aibot -f
   ```

### Issue: Slow Response Times

**Solutions:**

1. **Increase timeout in Odoo:**
   - Go to AI Configuration
   - Increase timeout to 60 seconds

2. **Check GitHub Models API:**
   - Verify API token is valid
   - Check rate limits

3. **Monitor AIbot performance:**
   ```bash
   htop  # Check CPU/memory usage
   ```

### Issue: "API Key Not Configured" Error

**Solution:**
- Ensure `ODOO_API_KEY` is set in AIbot's `.env` file
- Restart AIbot after changing environment variables

### Issue: Module Installation Fails

**Solutions:**

1. **Check dependencies:**
   ```bash
   pip install requests
   ```

2. **Check Odoo logs:**
   ```bash
   sudo tail -f /var/log/odoo/odoo-server.log
   ```

3. **Verify file permissions:**
   ```bash
   sudo chown -R odoo:odoo /opt/odoo/addons/odoo_ai_assistant
   ```

## Security Best Practices

### 1. API Key Security

- **Generate strong keys:**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- **Never commit keys to version control**
- **Rotate keys periodically**
- **Use different keys for dev/staging/production**

### 2. Network Security

- **Use HTTPS in production:**
  - Set up SSL certificate for AIbot
  - Update Odoo configuration to use `https://` URL

- **Restrict access:**
  ```bash
  # Allow only Odoo server IP
  sudo ufw allow from <odoo-server-ip> to any port 5000
  ```

### 3. Odoo Security

- **User permissions:**
  - Only give AI Assistant access to trusted users
  - Use Odoo's built-in access control

- **Audit logs:**
  - Monitor AI conversation history
  - Review generated content regularly

### 4. AIbot Security

- **Environment isolation:**
  - Run AIbot in virtual environment
  - Use separate system user

- **Rate limiting:**
  - Implement rate limiting in AIbot
  - Monitor for abuse

## Production Deployment Checklist

- [ ] AIbot running as systemd service
- [ ] Strong API key generated and configured
- [ ] HTTPS enabled for AIbot
- [ ] Firewall rules configured
- [ ] Odoo module installed and tested
- [ ] AI Configuration created and tested
- [ ] User permissions configured
- [ ] Backup procedures in place
- [ ] Monitoring set up
- [ ] Documentation provided to users

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly:**
   - Review conversation logs
   - Check for errors in AIbot logs
   - Monitor API usage

2. **Monthly:**
   - Update dependencies
   - Review and rotate API keys
   - Check disk space for logs

3. **Quarterly:**
   - Review security settings
   - Update documentation
   - Train users on new features

### Getting Help

1. **Check logs:**
   - AIbot: `sudo journalctl -u aibot -f`
   - Odoo: `/var/log/odoo/odoo-server.log`

2. **Test components individually:**
   - Test AIbot API directly
   - Test Odoo module in isolation

3. **Review documentation:**
   - This guide
   - Module README
   - AIbot documentation

## Conclusion

You now have a fully integrated AI assistant in your Odoo system! The integration provides powerful AI capabilities throughout your Odoo workflow, from product management to customer communication.

For questions or issues, refer to the troubleshooting section or check the component logs for detailed error messages.
