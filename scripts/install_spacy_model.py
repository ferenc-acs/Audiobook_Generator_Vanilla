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
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_spacy_model():
    """
    Install the spaCy language model required for sentence segmentation.
    
    This installs the small English model (en_core_web_sm) which is efficient
    for sentence boundary detection.
    """
    try:
        # Check if spaCy is installed
        logger.info("Checking for spaCy installation...")
        try:
            import spacy
            logger.info(f"spaCy is installed (version {spacy.__version__})")
        except ImportError:
            logger.warning("spaCy is not installed. Installing spaCy...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
            logger.info("spaCy has been installed.")
        
        # Check if the language model is installed
        logger.info("Checking for language model...")
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            logger.info("Language model 'en_core_web_sm' is already installed.")
        except OSError:
            # Model not found, need to download it
            logger.info("Language model not found. Downloading 'en_core_web_sm'...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            logger.info("Language model 'en_core_web_sm' has been installed.")
            
        # Verify installation was successful
        import spacy
        nlp = spacy.load("en_core_web_sm", disable=["ner", "tagger"])
        test_text = "This is a test sentence. This is another one!"
        doc = nlp(test_text)
        sentence_count = len(list(doc.sents))
        logger.info(f"Verification successful. Found {sentence_count} sentences in test text.")
        
        return True
    except Exception as e:
        logger.error(f"Error installing spaCy model: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting spaCy model installation...")
    success = install_spacy_model()
    
    if success:
        logger.info("✅ spaCy language model installation completed successfully.")
        print("\nThe spaCy language model (en_core_web_sm) has been installed.")
        print("This enables enhanced sentence segmentation for improved audiobook generation.")
    else:
        logger.error("❌ spaCy language model installation failed.")
        print("\nThere was an error installing the spaCy language model.")
        print("You can try installing it manually with these commands:")
        print("  pip install spacy")
        print("  python -m spacy download en_core_web_sm")
        sys.exit(1)