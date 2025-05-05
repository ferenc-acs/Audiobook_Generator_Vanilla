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
Script to check if the OpenAI API key is properly stored in the system's credential store.
"""

import keyring
import logging

SERVICE_NAME = "audiobook_generator"
ACCOUNT_NAME = "openai_api"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_credentials():
    """
    Check if credentials exist in the system's secure credential store.
    """
    # Try to get the key from the credential store
    key = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
    
    if key:
        # Mask the key for secure logging
        masked_key = key[:4] + '*' * (len(key) - 8) + key[-4:] if len(key) >= 8 else "[INVALID KEY]"
        logger.info(f"API key found in credential store: {masked_key}")
        logger.info(f"Key length: {len(key)}")
        return True
    else:
        logger.warning("No API key found in credential store")
        return False

if __name__ == "__main__":
    print("=== OpenAI API Key Check ===\n")
    if check_credentials():
        print("\nSuccess! Your API key is properly stored in the system's credential store.")
    else:
        print("\nNo API key found in the credential store. Please run 'python scripts/setup_credentials.py' to set it up.")