"""
mkfile - Create blank files with notification support
Cross-platform file creation utility with clipboard integration

Author: licface (licface@yahoo.com)
Version: 2.0
"""

import sys
import os
import re
import traceback
from pathlib import Path
from typing import List, Tuple, Optional
import traceback
import argparse
try:
    from licface import CustomRichHelpFormatter
except:
    CustomRichHelpFormatter = argparse.RawTextHelpFormatter

try:
    import clipboard
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False
    print("Warning: clipboard module not available. Install with: pip install clipboard")

try:
    import gntp.notifier
    HAS_GROWL = True
except ImportError:
    HAS_GROWL = False
    print("Warning: gntp module not available. Install with: pip install gntp")

NAME = 'mkfile'

def get_version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
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

__version__ = get_version()
__filename__ = Path(__file__).name


class FileCreator:
    """Handles file creation with notification support"""
    
    def __init__(self):
        self.icon_path = Path(__file__).parent / 'mkfile.jpg'
        self.growl = None
        
        if HAS_GROWL:
            self._init_growl()
    
    def _init_growl(self):
        """Initialize Growl notifier"""
        try:
            self.growl = gntp.notifier.GrowlNotifier(
                applicationName='mkfile',
                notifications=['create'],
                defaultNotifications=['create'],
                applicationIcon=str(self.icon_path.as_uri()) if self.icon_path.exists() else None
            )
            self.growl.register()
        except Exception as e:
            print(f"Warning: Could not initialize Growl: {e}")
            self.growl = None
    
    def parse_brace_expansion(self, text: str) -> List[str]:
        """
        Parse brace expansion patterns like: 
        - dir/{file1,file2,file3}.txt
        - dir{file1,file2,file3} (assumes dir/ prefix)
        Also handles spaces after commas and validates the pattern
        Returns: List of expanded filenames
        """
        pattern = r'([^{]*)\{([^}]+)\}([^{]*)'
        match = re.search(pattern, text)
        
        if not match:
            return [text]
        
        prefix = match.group(1)
        items_str = match.group(2)
        suffix = match.group(3)
        
        # If prefix doesn't end with / or \, assume it's a directory name
        # and add the separator
        if prefix and not prefix.endswith(('/', '\\')):
            prefix = prefix + '/'
        
        # Split by comma and strip whitespace, also handle space-separated items
        # Split by comma first
        parts = items_str.split(',')
        items = []
        for part in parts:
            # Each comma-separated part might have space-separated items
            sub_items = part.strip().split()
            items.extend(sub_items)
        
        # Expand into individual files
        expanded = []
        for item in items:
            if item:  # Skip empty items
                filepath = f"{prefix}{item}{suffix}"
                expanded.append(filepath)
        
        return expanded
    
    def create_file(self, filepath: str) -> bool:
        """
        Create a blank file, creating parent directories if needed
        
        Args:
            filepath: Path to file to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(filepath)
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create the file
            file_path.touch(exist_ok=True)
            
            # Copy absolute path to clipboard
            if HAS_CLIPBOARD:
                try:
                    clipboard.copy(str(file_path.absolute()))
                except Exception as e:
                    print(f"Warning: Could not copy to clipboard: {e}")
            
            # Send notification
            self._notify(str(file_path))
            
            print(f'✓ File created: "{file_path.absolute()}"')
            return True
            
        except Exception as e:
            print(f'✗ Error creating file "{filepath}": {e}')
            if '--debug' in sys.argv:
                print(traceback.format_exc())
            return False
    
    def _notify(self, filepath: str):
        """Send desktop notification"""
        if self.growl and HAS_GROWL:
            try:
                self.growl.notify(
                    noteType='create',
                    title='mkfile',
                    description=f'File created: "{Path(filepath).name}"',
                    icon=str(self.icon_path.as_uri()) if self.icon_path.exists() else None,
                    sticky=False,
                    priority=1,
                )
            except Exception as e:
                if '--debug' in sys.argv:
                    print(f"Notification error: {e}")
    
    def create_files(self, files: List[str]) -> int:
        """
        Create multiple files
        
        Returns:
            Number of successfully created files
        """
        success_count = 0
        all_files = []
        
        # First, expand all brace patterns
        for file_arg in files:
            if '{' in file_arg and '}' in file_arg:
                expanded = self.parse_brace_expansion(file_arg)
                all_files.extend(expanded)
            else:
                all_files.append(file_arg)
        
        # Then create all files
        for filepath in all_files:
            if self.create_file(filepath):
                success_count += 1
        
        return success_count


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description='Create blank files with notification support',
        formatter_class=CustomRichHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.txt                       # Create single file
  %(prog)s file1.txt file2.py file3       # Create multiple files
  %(prog)s dir/subdir/file.txt            # Create with directories
  %(prog)s dir/{a,b,c}.txt                # Brace expansion (creates dir/a.txt, dir/b.txt, dir/c.txt)
  %(prog)s dotenv/{__init__.py,core.py}   # Create package structure
  
Note: Use forward slashes (/) for directories, even on Windows.
        """
    )
    
    parser.add_argument(
        'files',
        metavar='FILE',
        nargs='*',
        help='File(s) to create. Supports brace expansion.'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'mkfile v{__version__}'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Show detailed error messages'
    )
    
    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    if not args.files:
        parser.print_help()
        return 0
    
    # Join all arguments to reconstruct brace patterns split by shell
    # Example: ['dotenv{a,', 'b', 'c}'] becomes 'dotenv{a, b c}'
    joined_args = ' '.join(args.files)
    
    # Now parse for brace patterns in the reconstructed string
    file_list = []
    current = []
    in_braces = False
    
    for char in joined_args:
        if char == '{':
            in_braces = True
            current.append(char)
        elif char == '}':
            in_braces = False
            current.append(char)
        elif char == ' ' and not in_braces:
            if current:
                file_list.append(''.join(current))
                current = []
        else:
            current.append(char)
    
    if current:
        file_list.append(''.join(current))
    
    # Create files
    creator = FileCreator()
    success_count = creator.create_files(file_list)
    
    total_expected = sum(
        len(creator.parse_brace_expansion(f)) if '{' in f and '}' in f else 1 
        for f in file_list
    )
    
    print(f"\n{success_count}/{total_expected} file(s) created successfully")
    
    return 0 if success_count == total_expected else 1


if __name__ == '__main__':
    sys.exit(main())