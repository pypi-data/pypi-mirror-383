# trojanrat_scripts/cli.py (Version 2 - More User-Friendly)

import os
import shutil
from pathlib import Path
import importlib.resources

def main():
    """
    Copies the script file into the user's current working directory
    and provides clear feedback on the location.
    """
    try:
        # Get the current folder where the command is being run
        current_folder = Path(os.getcwd())
        
        # Define the full destination path for the file
        destination_file = current_folder / "all_ai_scripts.txt"
        
        # --- NEW: Add this print statement for debugging ---
        print(f"Attempting to create file at: {destination_file}")
        
        # Find the source file within the installed package
        with importlib.resources.path("trojanrat_scripts", "all_ai_scripts.txt") as source_file:
            # Copy the file
            shutil.copy(source_file, destination_file)
            
        print(f"✅ Success! 'all_ai_scripts.txt' has been created.")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Could not create the file. Please check folder permissions.")