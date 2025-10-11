"""
Setup configuration for mkfile package
"""
from setuptools import setup, Extension
from setuptools.dist import Distribution
from pathlib import Path
import traceback
from pathlib import Path
import os
import sys
import shutil

# with open('MANIFEST.in', 'w') as fm:
#         fm.write("""include README.md
# include __version__.py
# recursive-include mkfile *.pyd
# recursive-include mkfile *.so
# recursive-include mkfile *.ini
# recursive-include mkfile *.jpg
# include mkfile/__init__.py
# include mkfile/__main__.py
# include mkfile/__version__.py

# # Exclude source files untuk binary distribution
# global-exclude *.py[cod]
# global-exclude *.c
# global-exclude *.pyx
# global-exclude __pycache__
# global-exclude *.so
# global-exclude .git*
# global-exclude *.ini

# # Include LICENSE if exists (optional)
# include LICENSE*
# exclude LICENSE.rst""")

NAME = 'mkfile'

shutil.copy2('__version__.py', NAME)

# Read version from __init__.py
def get_version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    NAME = 'mkfile'
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if not version_file.is_file():
            version_file = Path(__file__).parent / NAME / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "2.0"

# Custom Distribution class for binary-only wheel
class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

print(f"NAME   : {NAME}")
print(f"VERSION: {get_version()}")

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# # Read version from __init__.py
# version = {}
# with open("mkfile/__init__.py") as f:
#     for line in f:
#         if line.startswith("__version__"):
#             exec(line, version)
#             break

_extensions = []
extensions = None

try:
    from Cython.Build import cythonize
    # shutil.copy2(f"{NAME}/mkfile.py", f'{NAME}/mkfile.pyx')
    _extensions = [
        Extension('mkfile.mkfile', ['mkfile/mkfile.pyx']),
    ]
    extensions = cythonize(
        _extensions,
        compiler_directives={
            'language_level': '3',
            'embedsignature': True,
        }
    )
#     with open('MANIFEST.in', 'w') as fm:
#         fm.write("""include README.md
# include __version__.py
# recursive-include mkfile *.pyd
# recursive-include mkfile *.so
# recursive-include mkfile *.ini
# recursive-include mkfile *.jpg
# include mkfile/__init__.py
# include mkfile/__main__.py
# include mkfile/__version__.py
# exclude mkfile/mkfile.py
# exclude mkfile/mkfile.pyx

# # Exclude source files untuk binary distribution
# global-exclude *.py[cod]
# global-exclude *.c
# global-exclude *.pyx
# global-exclude __pycache__
# global-exclude *.so
# global-exclude .git*
# global-exclude *.ini
# global-exclude mkfile.py
# global-exclude mkfile.pyx

# # Include LICENSE if exists (optional)
# include LICENSE*
# exclude LICENSE.rst""")
        
except Exception as e:
    print("Error build ext:", e)
    shutil.copy2(f"{NAME}/mkfile.pyx", f'{NAME}/mkfile.py')

setup(
    name='mkfile',
    # version=version.get('__version__', '2.0.0'),
    version=get_version(),
    author='cumulus13',
    author_email='cumulus13@gmail.com',
    description='Advanced file creator with brace expansion and notification support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cumulus13/mkfile',
    packages=[NAME],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Filesystems',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Environment :: Console',
    ],
    keywords='file creation, command-line, brace expansion, developer tools',
    python_requires='>=3.6',
    install_requires=[],
    extras_require={
        'notifications': ['gntp>=1.0.3'],
        'clipboard': ['clipboard>=0.0.4'],
        'licface': ['licface'],
        'full': ['gntp>=1.0.3', 'clipboard>=0.0.4', 'licface'],
    },
    entry_points={
        'console_scripts': [
            'mkfile=mkfile.__main__:usage',
        ],
    },
    include_package_data=True,
    project_urls={
        'Bug Reports': 'https://github.com/cumulus13/mkfile/issues',
        'Source': 'https://github.com/cumulus13/mkfile',
    },
    ext_modules=extensions,
    zip_safe=False,
    distclass=BinaryDistribution,
    # Sertakan file .pyd
    package_data={
        'mkfile': ['mkfile.pyx', 'mkfile.jpg', 'mkfile.ini', f'*{sys.version_info.major}{sys.version_info.minor}*.pyd'] if sys.platform == 'win32' else [f'*{sys.version_info.major}{sys.version_info.minor}*.so'],
    },
)