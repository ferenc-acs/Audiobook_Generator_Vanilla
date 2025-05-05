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

from src.text_processor import segment_text_by_sentences

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complex_segmentation():
    """
    Test sentence segmentation with complex literary text examples including
    various edge cases like quotes, ellipses, abbreviations, etc.
    """
    # Test cases - complex literary text with various edge cases
    test_texts = [
        # Basic test with mixed punctuation
        """This is a simple sentence. Here's another one! What about questions? Yes, they should work too.""",
        
        # Quotes and dialog
        """\"I can't believe it,\" she said. \"This is amazing!\" John smiled and replied, \"I told you so.\"""",
        
        # Ellipses and trailing spaces
        """The night was dark... stars filled the sky. The journey continues...   and so does the adventure.""",
        
        # Common abbreviations
        """Dr. Smith went to Washington D.C. with Mr. Johnson. They arrived at 3 p.m. and left at 5:30 a.m.""",
        
        # Mixed case after punctuation
        """The URL is example.com. download it now. The email is user@example.com. send a message.""",
        
        # Parenthetical sentences
        """The project was completed ahead of schedule. (This was unexpected.) The team celebrated.""",
        
        # Sentence with semicolons and complex structure
        """The house stood at the end of the lane; its windows dark, its doors locked; no one had lived there for years.""",
        
        # Literary excerpt with complex structure
        """
        Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world. It is a way I have of driving off the spleen and regulating the circulation. Whenever I find myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever I find myself involuntarily pausing before coffin warehouses, and bringing up the rear of every funeral I meet; and especially whenever my hypos get such an upper hand of me, that it requires a strong moral principle to prevent me from deliberately stepping into the street, and methodically knocking people's hats off—then, I account it high time to get to sea as soon as I can.
        """,
        
        # Long sentence that should be kept intact if possible
        """This is an extremely long sentence that goes on and on, using commas, semicolons, and other punctuation to join clauses together, incorporating various thoughts and ideas into a single flowing river of text that challenges the segmentation algorithm's ability to maintain its integrity while still ensuring that the resulting chunks are of a reasonable size for processing by the text-to-speech engine without breaking the natural flow of the narrative."""
    ]
    
    for i, test_text in enumerate(test_texts):
        logger.info(f"\nTest case #{i+1}:")
        logger.info(f"Text: {test_text[:100]}..." if len(test_text) > 100 else f"Text: {test_text}")
        
        # Test with a small chunk size to force chunking
        chunk_size = 200 if i < len(test_texts) - 1 else 400  # Use larger chunk for the last test case
        chunks = segment_text_by_sentences(test_text, chunk_size=chunk_size)
        
        logger.info(f"Created {len(chunks)} chunks with max size {chunk_size}")
        
        # Count how many chunks end with proper sentence boundary
        sentence_endings = 0
        partial_sentences = 0
        
        for j, chunk in enumerate(chunks):
            logger.info(f"  Chunk {j+1}: {len(chunk)} chars, ending with: '{chunk[-40:].strip()}'")
            
            # Check if chunk ends with sentence boundary
            if chunk.rstrip().endswith(('.', '!', '?', '"', "'")):
                sentence_endings += 1
            else:
                partial_sentences += 1
                logger.warning(f"  ⚠️ Chunk {j+1} doesn't end with a sentence boundary")
                
        logger.info(f"Chunks ending with sentence boundary: {sentence_endings}/{len(chunks)} ({sentence_endings/len(chunks)*100:.1f}%)")
        if partial_sentences > 0:
            logger.warning(f"Found {partial_sentences} chunks that might break sentences unnaturally")
        
    logger.info("\nComplex segmentation testing complete.")
    return True

if __name__ == "__main__":
    logger.info("Testing sentence segmentation with complex literary examples")
    
    success = test_complex_segmentation()
    
    if success:
        print("\n✅ Complex sentence segmentation test completed")
        print("Review the log output to see how well the segmentation handles various cases.")
    else:
        print("\n❌ Complex sentence segmentation test failed")
        sys.exit(1)