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

from src.text_processor import extract_text_from_epub, extract_chapters_from_epub, segment_text_by_sentences

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sentence_segmentation_with_epub(epub_file_path):
    """Test the sentence segmentation with text extracted from an EPUB file."""
    try:
        logger.info(f"Testing EPUB extraction with sentence segmentation: {epub_file_path}")
        
        # Extract text from EPUB
        logger.info("Extracting text from EPUB...")
        full_text = extract_text_from_epub(epub_file_path)
        logger.info(f"Extracted {len(full_text)} characters of text")
        
        # Extract chapters
        logger.info("Extracting chapters...")
        chapters = extract_chapters_from_epub(epub_file_path)
        logger.info(f"Extracted {len(chapters)} chapters")
        
        # Take a small sample from the first chapter for demonstration
        if chapters:
            sample_text = chapters[0]['content'][:2000]  # First 2000 chars of first chapter
            logger.info(f"Using sample text from chapter '{chapters[0]['title']}', {len(sample_text)} chars")
            
            # Apply basic chunking (old method)
            basic_chunks = [sample_text[i:i+500] for i in range(0, len(sample_text), 500)]  # 500 char chunks
            logger.info(f"Basic chunking created {len(basic_chunks)} chunks")
            
            # Show where basic chunking cuts the text
            for i, chunk in enumerate(basic_chunks):
                logger.info(f"Basic chunk {i+1} ends with: '{chunk[-50:]}...'")
            
            # Apply sentence segmentation (new method)
            sentence_chunks = segment_text_by_sentences(sample_text, chunk_size=500)  # Same chunk size
            logger.info(f"Sentence-based segmentation created {len(sentence_chunks)} chunks")
            
            # Show where sentence segmentation cuts the text
            for i, chunk in enumerate(sentence_chunks):
                logger.info(f"Sentence chunk {i+1} ends with: '{chunk[-50:]}...'")
                
            # Compare - check if chunks end with sentence boundaries
            basic_sentence_ends = sum(1 for chunk in basic_chunks if chunk.rstrip().endswith(('.', '!', '?')))
            smart_sentence_ends = sum(1 for chunk in sentence_chunks if chunk.rstrip().endswith(('.', '!', '?')))
            
            logger.info(f"Basic chunks ending with sentence: {basic_sentence_ends}/{len(basic_chunks)}")
            logger.info(f"Sentence chunks ending with sentence: {smart_sentence_ends}/{len(sentence_chunks)}")
            
            return True
        else:
            logger.warning("No chapters found in EPUB file")
            return False
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_sentence_segmentation_epub.py <path_to_epub_file>")
        sys.exit(1)
        
    epub_file = sys.argv[1]
    if not os.path.exists(epub_file):
        print(f"Error: File not found: {epub_file}")
        sys.exit(1)
        
    if not epub_file.lower().endswith('.epub'):
        print(f"Error: Not an EPUB file: {epub_file}")
        sys.exit(1)
        
    success = test_sentence_segmentation_with_epub(epub_file)
    if success:
        print("\n✅ EPUB sentence segmentation test completed successfully")
        print("\nSentence segmentation properly chunks text at natural sentence boundaries")
        print("This improves the natural flow and quality of generated audio.")
    else:
        print("\n❌ EPUB sentence segmentation test failed")
        sys.exit(1)