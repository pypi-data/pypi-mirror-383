from setuptools import setup, Extension
import platform

NAME = "PyProtectorX"
VERSION = "1.1.0"

LONG_DESCRIPTION = """
# PyProtectorX v1.1.0
🔒 Ultimate Python Code Protection System
Created by Zain Alkhalil (VIP)

## Features
- Multi-layer encryption with 4 protection levels
- Cross-platform support (Windows, Linux, macOS)
- Command-line interface for easy encryption
- Zero dependencies, pure C extension
- Built-in compression and watermarking

## Quick Start

### Python API
```python
import PyProtectorX
encrypted = PyProtectorX.dumps("print('Hello')")
PyProtectorX.Run(encrypted)
```

### CLI
```bash
pyprotectorx encrypt script.py
python script_Enc.py
```

Website: https://pyprotectorx.netlify.app/
"""

system = platform.system()
machine = platform.machine().lower()

extra_compile_args = []
extra_link_args = []

if system == "Windows":
    extra_compile_args = ['/O2', '/GL']
    extra_link_args = ['/LTCG']
else:
    extra_compile_args = ['-O3', '-fPIC', '-fvisibility=hidden', '-DNDEBUG']
    extra_link_args = ['-s']

if 'x86_64' in machine or 'amd64' in machine:
    extra_compile_args.append('-march=x86-64')
elif 'aarch64' in machine or 'arm64' in machine:
    extra_compile_args.append('-march=armv8-a')

setup(
    name=NAME,
    version=VERSION,
    description="Advanced Python Code Protection and Encryption",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Zain Alkhalil (VIP)",
    author_email="zainr56h@gmail.com",
    url="https://pyprotector.netlify.app",
    license="Proprietary",
    
    # C Extension
    ext_modules=[
        Extension(
            'PyProtectorX',
            sources=['main.c'],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args
        )
    ],
    
    # Python modules
    py_modules=['encrypt'],
    
    # CLI entry point
    entry_points={
        'console_scripts': [
            'pyprotectorx=encrypt:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: C',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    keywords='encryption protection security obfuscation code-protection',
    python_requires='>=3.6',
    zip_safe=False,
    
    project_urls={
        'Homepage': 'https://pyprotectorx.netlify.app/',
        'Bug Reports': 'https://t.me/VIP_TY',
        'Documentation': 'https://pyprotectorx.netlify.app/docs',
    },
)