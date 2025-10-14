#!/usr/bin/env python3
"""
PyProtectorX v1.1.0 - Command Line Interface
Copyright (c) 2025 Zain Alkhalil (VIP). All Rights Reserved.
"""

import sys
import os
import argparse
from pathlib import Path

try:
    import PyProtectorX
except ImportError:
    print("❌ Error: PyProtectorX module not found!")
    print("Please install it first: pip install PyProtectorX")
    sys.exit(1)


LOADER_TEMPLATE = '''#!/usr/bin/env python3
# Protected by PyProtectorX v1.1.0
import PyProtectorX

__encrypted__ = b"""{encrypted_data}"""

if __name__ == "__main__":
    try:
        PyProtectorX.Run(__encrypted__)
    except Exception as e:
        print(f"Error executing protected code: {{e}}")
        sys.exit(1)
'''


def encrypt_file(input_path, output_path=None):
    """Encrypt a Python file"""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"❌ Error: File '{input_path}' not found!")
        return False
    
    if not input_file.suffix == '.py':
        print(f"❌ Error: File must be a Python file (.py)")
        return False
    
    # Read source code
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Encrypt
    try:
        print(f"🔒 Encrypting '{input_file.name}'...")
        encrypted = PyProtectorX.dumps(source_code)
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        return False
    
    # Generate output filename
    if output_path is None:
        output_path = input_file.parent / f"{input_file.stem}_Enc.py"
    else:
        output_path = Path(output_path)
    
    # Create protected file
    try:
        protected_code = LOADER_TEMPLATE.format(
            encrypted_data=encrypted.decode('utf-8')
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(protected_code)
        
        print(f"✅ Successfully encrypted!")
        print(f"📁 Output: {output_path}")
        print(f"📊 Original size: {len(source_code)} bytes")
        print(f"📊 Encrypted size: {len(protected_code)} bytes")
        return True
        
    except Exception as e:
        print(f"❌ Error writing output file: {e}")
        return False


def decrypt_and_show(encrypted_file):
    """Decrypt and display code (for testing)"""
    try:
        with open(encrypted_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract encrypted data
        start = content.find('b"""') + 4
        end = content.find('"""', start)
        encrypted_data = content[start:end].encode('utf-8')
        
        # Decrypt
        code_obj = PyProtectorX.loads(encrypted_data)
        print("✅ Decryption successful!")
        print("\n--- Decrypted Code Object Info ---")
        print(f"Type: {type(code_obj)}")
        print(f"Name: {code_obj.co_name}")
        print(f"Filename: {code_obj.co_filename}")
        
    except Exception as e:
        print(f"❌ Decryption failed: {e}")


def show_info():
    """Show system information"""
    info = PyProtectorX.get_system_info()
    print("\n" + "="*50)
    print("🔒 PyProtectorX v1.1.0")
    print("="*50)
    print(f"Architecture: {info['architecture']}")
    print(f"OS: {info['os']}")
    print(f"64-bit: {info['is_64bit']}")
    print(f"Python: {sys.version.split()[0]}")
    print("="*50)
    print("Website: https://pyprotector.netlify.app")
    print("Author: Zain Alkhalil (VIP)")
    print("="*50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='PyProtectorX - Ultimate Python Code Protection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  pyprotectorx encrypt script.py              # Encrypt script.py -> script_Enc.py
  pyprotectorx encrypt script.py -o out.py    # Encrypt with custom output name
  pyprotectorx info                           # Show system information
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a Python file')
    encrypt_parser.add_argument('input', help='Input Python file')
    encrypt_parser.add_argument('-o', '--output', help='Output file name (optional)')
    
    # Info command
    subparsers.add_parser('info', help='Show system information')
    
    decrypt_parser.add_argument('input', help='Encrypted Python file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'encrypt':
        encrypt_file(args.input, args.output)
    elif args.command == 'info':
        show_info()


if __name__ == "__main__":
    main()