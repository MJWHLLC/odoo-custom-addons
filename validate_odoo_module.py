"""
Odoo Module Validation Script
Validates the odoo_ai_assistant module structure and syntax
"""
import ast
import os
import sys
import xml.etree.ElementTree as ET

def validate_python_file(filepath):
    """Validate Python file syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax Error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_xml_file(filepath):
    """Validate XML file syntax"""
    try:
        ET.parse(filepath)
        return True, "OK"
    except ET.ParseError as e:
        return False, f"XML Parse Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_file_exists(filepath):
    """Check if file exists"""
    return os.path.exists(filepath)

def main():
    """Validate Odoo module"""
    module_path = 'odoo_ai_assistant'
    
    print("=" * 70)
    print("Odoo AI Assistant Module Validation")
    print("=" * 70)
    
    # Required files structure
    required_files = {
        'Python Files': [
            f'{module_path}/__init__.py',
            f'{module_path}/__manifest__.py',
            f'{module_path}/models/__init__.py',
            f'{module_path}/models/ai_config.py',
            f'{module_path}/models/ai_conversation.py',
            f'{module_path}/models/product_template.py',
            f'{module_path}/models/crm_lead.py',
            f'{module_path}/models/sale_order.py',
            f'{module_path}/controllers/__init__.py',
            f'{module_path}/controllers/main.py',
        ],
        'XML Files': [
            f'{module_path}/views/menu_views.xml',
            f'{module_path}/views/ai_config_views.xml',
            f'{module_path}/views/ai_conversation_views.xml',
            f'{module_path}/views/product_template_views.xml',
            f'{module_path}/views/crm_lead_views.xml',
            f'{module_path}/views/sale_order_views.xml',
        ],
        'Security Files': [
            f'{module_path}/security/ir.model.access.csv',
        ],
        'Documentation': [
            f'{module_path}/README.md',
            f'{module_path}/static/description/index.html',
        ]
    }
    
    all_valid = True
    
    # Check file existence
    print("\n1. Checking File Structure...")
    print("-" * 70)
    for category, files in required_files.items():
        print(f"\n{category}:")
        for filepath in files:
            exists = check_file_exists(filepath)
            status = "✓" if exists else "✗"
            print(f"  {status} {filepath}")
            if not exists:
                all_valid = False
    
    # Validate Python files
    print("\n\n2. Validating Python Syntax...")
    print("-" * 70)
    for filepath in required_files['Python Files']:
        if check_file_exists(filepath):
            valid, message = validate_python_file(filepath)
            status = "✓ PASS" if valid else "✗ FAIL"
            print(f"{status}: {filepath}")
            if not valid:
                print(f"  Error: {message}")
                all_valid = False
    
    # Validate XML files
    print("\n\n3. Validating XML Syntax...")
    print("-" * 70)
    for filepath in required_files['XML Files']:
        if check_file_exists(filepath):
            valid, message = validate_xml_file(filepath)
            status = "✓ PASS" if valid else "✗ FAIL"
            print(f"{status}: {filepath}")
            if not valid:
                print(f"  Error: {message}")
                all_valid = False
    
    # Check manifest file
    print("\n\n4. Validating Manifest...")
    print("-" * 70)
    manifest_path = f'{module_path}/__manifest__.py'
    if check_file_exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_code = f.read()
            manifest_dict = {}
            exec(manifest_code, manifest_dict)
            
            required_keys = ['name', 'version', 'depends', 'data']
            for key in required_keys:
                if key in manifest_dict:
                    print(f"  ✓ {key}: {manifest_dict[key]}")
                else:
                    print(f"  ✗ Missing required key: {key}")
                    all_valid = False
        except Exception as e:
            print(f"  ✗ Error reading manifest: {e}")
            all_valid = False
    
    # Check security file
    print("\n\n5. Validating Security Rules...")
    print("-" * 70)
    security_file = f'{module_path}/security/ir.model.access.csv'
    if check_file_exists(security_file):
        try:
            with open(security_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if len(lines) > 1:  # Header + at least one rule
                print(f"  ✓ Security rules defined: {len(lines) - 1} rules")
            else:
                print(f"  ⚠ Warning: No security rules defined")
        except Exception as e:
            print(f"  ✗ Error reading security file: {e}")
            all_valid = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_valid:
        print("✓ Module validation PASSED!")
        print("\nThe module is ready for installation in Odoo.")
        print("\nNext steps:")
        print("1. Copy module to Odoo addons directory")
        print("2. Restart Odoo")
        print("3. Update Apps List")
        print("4. Install 'Odoo AI Assistant' module")
        return 0
    else:
        print("✗ Module validation FAILED!")
        print("\nPlease fix the errors above before installing.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
