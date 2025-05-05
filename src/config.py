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

from pathlib import Path
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import keyring

# Load .env from project root (fallback method)
load_dotenv(Path(__file__).parent.parent / '.env')

logger = logging.getLogger(__name__)

# Constants for keyring
SERVICE_NAME = "audiobook_generator"
ACCOUNT_NAME = "openai_api"

class Config:
    @staticmethod
    def mask_api_key(key: str) -> str:
        """Mask API key for secure logging"""
        if not key or len(key) < 8:
            return "[EMPTY OR INVALID KEY]"
        # Show only first 4 and last 4 characters, mask the rest
        return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"
        
    @staticmethod
    def get_openai_key() -> str:
        """Retrieve OpenAI API key from system credential store or .env file"""
        # First try to get the key from the system credential store
        key = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
        source = "credential store"
        
        # Fall back to .env file if not found in credential store
        if not key:
            raw_key = os.getenv('OPENAI_API_KEY', '')
            key = raw_key.strip()
            source = "ENV" if raw_key == key else ".env"
            
            # If key is found in .env, log a recommendation to use the secure storage
            if key:
                logger.info("API key found in environment. For better security, consider using the credential store.")
                logger.info("Run 'python scripts/setup_credentials.py' to set up secure credential storage.")
        
        masked_key = Config.mask_api_key(key)
        logger.debug(f"API key (masked): '{masked_key}' (length: {len(key) if key else 0})")
        logger.debug(f"Loaded OpenAI key from {source}")
        return key

    @staticmethod
    def validate_key() -> None:
        """Validate the presence of OpenAI API key in credential store or .env file"""
        # First check if key exists in credential store
        key_in_store = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
        if key_in_store:
            return
            
        # Fall back to .env file
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        if not os.path.exists(env_path):
            raise FileNotFoundError(f"Missing .env file at {env_path} and no key in credential store")
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError('OPENAI_API_KEY not found in environment configuration or credential store')
            
        # If we get here, the key exists in .env but not in credential store
        logger.warning("Using API key from .env file. For better security, run 'python scripts/setup_credentials.py'")