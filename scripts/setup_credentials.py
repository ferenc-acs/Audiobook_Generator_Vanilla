#
#    Audiobook Generator Vanilla: A Python application that converts text documents (DOCX, EPUB, Markdown) into audiobooks using OpenAI's text-to-speech API.
#    Copyright (C) 2025 Ferenc Acs <pass.schist2954@eagereverest.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

#!/usr/bin/env python
"""
Setup script to securely store OpenAI API key in the system's credential store.
This script will read the API key from .env file (if exists) and store it securely.
"""

import os
import sys
import keyring
import getpass
from pathlib import Path
from dotenv import load_dotenv

SERVICE_NAME = "audiobook_generator"
ACCOUNT_NAME = "openai_api"


def setup_credentials():
    """
    Set up credentials in the system's secure credential store.
    Will attempt to read from .env file first, then prompt if not found.
    """
    # Try to load from .env file first
    env_path = Path(__file__).parent.parent / '.env'
    key_from_env = None
    
    if env_path.exists():
        load_dotenv(env_path)
        key_from_env = os.getenv('OPENAI_API_KEY')
    
    if key_from_env:
        print(f"Found API key in .env file.")
        use_existing = input("Would you like to store this key in the system's credential store? (y/n): ").lower() == 'y'
        
        if use_existing:
            api_key = key_from_env
        else:
            api_key = getpass.getpass("Enter your OpenAI API key: ")
    else:
        print("No API key found in .env file.")
        api_key = getpass.getpass("Enter your OpenAI API key: ")
    
    if not api_key:
        print("Error: API key cannot be empty.")
        return False
    
    try:
        # Store the API key in the system's credential store
        keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, api_key)
        print("API key successfully stored in the system's credential store.")
        
        # Ask if user wants to remove the key from .env file
        if key_from_env and env_path.exists():
            remove_from_env = input("Would you like to remove the API key from the .env file for added security? (y/n): ").lower() == 'y'
            
            if remove_from_env:
                # Read the .env file
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                
                # Write back without the API key line
                with open(env_path, 'w') as f:
                    for line in lines:
                        if not line.startswith('OPENAI_API_KEY='):
                            f.write(line)
                    # Add a comment to indicate where the key is stored
                    f.write('# OPENAI_API_KEY is now stored in the system credential store\n')
                
                print("API key removed from .env file.")
        
        return True
    except Exception as e:
        print(f"Error storing API key: {str(e)}")
        return False


if __name__ == "__main__":
    print("=== OpenAI API Key Setup ===")
    print("This script will store your OpenAI API key securely in your system's credential store.")
    print("The key will be accessible only to this application and protected by your system's security.")
    print()
    
    if setup_credentials():
        print("\nSetup complete! Your API key is now stored securely.")
        print("You can run this script again at any time to update your API key.")
    else:
        print("\nSetup failed. Please try again.")
        sys.exit(1)