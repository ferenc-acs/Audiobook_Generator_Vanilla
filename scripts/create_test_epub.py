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

import os
import sys
import logging
from ebooklib import epub

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.text_processor import extract_text_from_epub, extract_chapters_from_epub

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_epub(output_path="test_book.epub"):
    """Create a simple EPUB file with test content"""
    # Create a new EPUB book
    book = epub.EpubBook()
    
    # Set metadata
    book.set_identifier('test123456')
    book.set_title('Test EPUB Book')
    book.set_language('en')
    book.add_author('Test Author')
    
    # Create chapters
    chapters = []
    for i in range(1, 4):
        # Create chapter
        c = epub.EpubHtml(title=f'Chapter {i}', file_name=f'chapter_{i}.xhtml', lang='en')
        c.content = f'''
        <html>
        <head>
            <title>Chapter {i}</title>
        </head>
        <body>
            <h1>Chapter {i}</h1>
            <p>This is the content of chapter {i}. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
            <p>Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
        </body>
        </html>
        '''
        
        # Add chapter to the book
        book.add_item(c)
        chapters.append(c)
    
    # Add chapters to the book
    book.toc = [(epub.Section('Chapters'), chapters)]
    
    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Define CSS style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Arial, sans-serif;
    }
    h1 {
        font-size: 2em;
        font-weight: bold;
    }
    '''
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    
    # Create spine
    book.spine = ['nav'] + chapters
    
    # Write the EPUB file
    epub.write_epub(output_path, book, {})
    logger.info(f"Created test EPUB at {output_path}")
    
    return output_path

def test_extraction(epub_path):
    """Test extraction with our modified functions"""
    # Test text extraction
    logger.info("Testing text extraction...")
    text = extract_text_from_epub(epub_path)
    logger.info(f"Extracted {len(text)} characters of text")
    
    # Test chapter extraction
    logger.info("Testing chapter extraction...")
    chapters = extract_chapters_from_epub(epub_path)
    logger.info(f"Extracted {len(chapters)} chapters")
    
    # Print chapter information
    for i, chapter in enumerate(chapters):
        logger.info(f"Chapter {i+1}: {chapter['title']} - {len(chapter['content'])} characters")
    
    logger.info("Tests completed successfully!")

if __name__ == "__main__":
    # Create input directory if it doesn't exist
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "input")
    os.makedirs(input_dir, exist_ok=True)
    
    # Create the test EPUB file
    epub_path = os.path.join(input_dir, "test_book.epub")
    epub_path = create_test_epub(epub_path)
    
    # Test our extraction
    test_extraction(epub_path)
    
    print(f"\nTest EPUB file created at: {epub_path}")
    print("You can now use this file to test the audiobook generator:")
    print(f"uv run python -m src.main {epub_path}")