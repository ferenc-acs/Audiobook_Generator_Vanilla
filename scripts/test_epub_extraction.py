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