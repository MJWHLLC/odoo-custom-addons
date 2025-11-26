# Odoo 17 Custom Addons

This repository contains custom Odoo 17 modules developed for enhanced functionality.

## 📦 Modules

### 1. Vendor Product Importer
**Version:** 17.0.1.0.0  
**Category:** Sales/Sales

A comprehensive module for importing and maintaining products from online vendors with automated pricing.

**Features:**
- Multi-platform support (Amazon, eBay, Shopify, Generic HTML scraping)
- Intelligent product matching (SKU, EAN, UPC, name similarity)
- Tiered pricing based on cost ranges (4 default tiers)
- Weekly automated updates
- Legal compliance filtering
- Conflict resolution for duplicate products
- Comprehensive logging and reporting

**[View Module Documentation →](vendor_product_importer/README.md)**

### 2. Odoo 3D CAD Integration
**Version:** 17.0.1.0.0  
**Category:** Manufacturing

Integration module for 3D CAD functionality in Odoo.

**[View Module Documentation →](odoo_3d_cad_integration/README.md)**

## 🚀 Installation

### Prerequisites
- Odoo 17.0
- Python 3.10+
- PostgreSQL

### Quick Install

1. **Clone this repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/odoo-custom-addons.git
   cd odoo-custom-addons
   ```

2. **Add to Odoo addons path:**
   
   Edit your `odoo.conf`:
   ```ini
   addons_path = /path/to/odoo/addons,/path/to/odoo-custom-addons
   ```

3. **Install dependencies:**
   ```bash
   # For Vendor Product Importer
   pip install beautifulsoup4 lxml requests
   
   # Optional platform SDKs
   pip install amazon-paapi5-python-sdk ebaysdk ShopifyAPI
   ```

4. **Restart Odoo:**
   ```bash
   sudo systemctl restart odoo
   # or
   ./odoo-bin -c odoo.conf
   ```

5. **Install modules:**
   - Go to Apps menu in Odoo
   - Click "Update Apps List"
   - Search for the module name
   - Click "Install"

## 📖 Documentation

Each module contains detailed documentation:
- `README.md` - Module overview and features
- `INSTALLATION_GUIDE.md` - Detailed installation instructions
- `MANUAL_INSTALLATION_STEPS.md` - Step-by-step manual installation

## 🔧 Configuration

### Vendor Product Importer
1. Go to Vendor Importer → Configuration → Price Tiers
2. Review and adjust the 4 default pricing tiers
3. Add vendors: Vendor Importer → Vendors → Create
4. Configure API credentials or scraping selectors
5. Run test import

### Odoo 3D CAD Integration
See module-specific documentation for configuration details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

These modules are licensed under LGPL-3.

## 🐛 Issues

If you encounter any issues, please report them in the GitHub Issues section.

## 📧 Support

For support and questions, please open an issue on GitHub.

## 🎯 Compatibility

- **Odoo Version:** 17.0
- **Python Version:** 3.10+
- **Database:** PostgreSQL 12+

## 📊 Module Statistics

| Module | Files | Lines of Code | Status |
|--------|-------|---------------|--------|
| Vendor Product Importer | 36 | ~6,000 | ✅ Complete |
| Odoo 3D CAD Integration | TBD | TBD | ✅ Complete |

## 🔄 Updates

Check the individual module directories for version history and changelogs.

---

**Made with ❤️ for Odoo 17**
