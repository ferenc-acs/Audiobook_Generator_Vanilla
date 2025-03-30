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