# trojanrat_scripts/cli.py

import os
import shutil
from pathlib import Path
import importlib.resources

def main():
    """
    This function copies the script file from the package directly
    into the user's current working directory.
    """
    try:
        # 1. Get the current folder where the command is being run
        current_folder = Path(os.getcwd())
        
        # 2. Define the destination file path
        destination_file = current_folder / "all_ai_scripts.txt"
        
        # 3. Find the source file within the installed package
        with importlib.resources.path("trojanrat_scripts", "all_ai_scripts.txt") as source_file:
            # 4. Copy the file
            shutil.copy(source_file, destination_file)
            
        print(f"✅ Success! 'all_ai_scripts.txt' has been created in your current folder.")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Could not create the file. Please check folder permissions.")