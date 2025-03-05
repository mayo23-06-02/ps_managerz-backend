# dir_structure.py
import os

def print_directory_structure(start_path='.', indent='', exclude_dirs=['venv']):
    """
    Recursively print the directory structure starting from start_path, excluding specified directories.
    
    Args:
        start_path (str): The starting directory (default is current directory).
        indent (str): Indentation for nested levels (default is empty).
        exclude_dirs (list): List of directory names to exclude (default is ['venv']).
    """
    # Get all items in the directory
    items = sorted(os.listdir(start_path))
    
    for item in items:
        # Construct full path
        full_path = os.path.join(start_path, item)
        
        # Skip excluded directories
        if os.path.isdir(full_path) and item in exclude_dirs:
            continue
        
        # Print the item (file or folder)
        if os.path.isdir(full_path):
            # If it's a directory, print it and recurse
            print(f"{indent}📁 {item}/")
            print_directory_structure(full_path, indent + "  ", exclude_dirs)
        else:
            # If it's a file, just print it
            print(f"{indent}📄 {item}")

if __name__ == "__main__":
    # Start from the current directory, excluding 'venv'
    print("Directory Structure (excluding venv):")
    print_directory_structure()