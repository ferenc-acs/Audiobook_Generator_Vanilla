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

import sys
import os
import logging

# Add the project root to the path so we can import the src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.text_processor import extract_text_from_epub, extract_chapters_from_epub

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_epub_extraction(epub_file_path):
    """Test the EPUB extraction functions with the given file path."""
    try:
        logger.info(f"Testing EPUB text extraction from: {epub_file_path}")
        
        # Test basic text extraction
        logger.info("Attempting to extract full text...")
        text = extract_text_from_epub(epub_file_path)
        logger.info(f"Successfully extracted {len(text)} characters of text")
        
        # Test chapter extraction
        logger.info("Attempting to extract chapters...")
        chapters = extract_chapters_from_epub(epub_file_path)
        logger.info(f"Successfully extracted {len(chapters)} chapters")
        
        # Print chapter information
        for i, chapter in enumerate(chapters):
            logger.info(f"Chapter {i+1}: {chapter['title']} - {len(chapter['content'])} characters")
        
        return True
    except Exception as e:
        logger.error(f"Error during EPUB extraction: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_epub_extraction.py <path_to_epub_file>")
        sys.exit(1)
        
    epub_file = sys.argv[1]
    if not os.path.exists(epub_file):
        print(f"Error: File not found: {epub_file}")
        sys.exit(1)
        
    if not epub_file.lower().endswith('.epub'):
        print(f"Error: Not an EPUB file: {epub_file}")
        sys.exit(1)
        
    success = test_epub_extraction(epub_file)
    if success:
        print("✅ EPUB extraction test completed successfully")
    else:
        print("❌ EPUB extraction test failed")
        sys.exit(1)