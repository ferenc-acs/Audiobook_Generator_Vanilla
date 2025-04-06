from typing import Optional, List, Dict, Tuple
from docx import Document
from ebooklib import epub
import logging
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}")
        raise

def extract_chapters_from_docx(file_path: str) -> List[Dict[str, str]]:
    """Extract chapters from a DOCX file based on heading styles."""
    try:
        doc = Document(file_path)
        chapters = []
        current_chapter = {"title": "Untitled Chapter", "content": []}
        
        for para in doc.paragraphs:
            # Check if this paragraph is a heading (potential chapter marker)
            # Safely check if style exists before accessing its name
            if para.style and para.style.name.startswith('Heading') and para.text.strip():
                # If we have content in the current chapter, save it
                if current_chapter["content"]:
                    current_chapter["content"] = '\n'.join(current_chapter["content"])
                    chapters.append(current_chapter)
                
                # Start a new chapter
                current_chapter = {"title": para.text.strip(), "content": []}
            else:
                # Add content to the current chapter
                if para.text.strip():
                    current_chapter["content"].append(para.text)
        
        # Add the last chapter if it has content
        if current_chapter["content"]:
            current_chapter["content"] = '\n'.join(current_chapter["content"])
            chapters.append(current_chapter)
            
        # If no chapters were detected, treat the entire document as one chapter
        if not chapters:
            chapters.append({
                "title": "Complete Document",
                "content": '\n'.join([para.text for para in doc.paragraphs])
            })
            
        return chapters
    except Exception as e:
        logger.error(f"DOCX chapter extraction error: {str(e)}")
        raise

def extract_text_from_epub(file_path: str) -> str:
    try:
        book = epub.read_epub(file_path)
        text = []
        for item in book.get_items():
            # Check media type instead of using ITEM_DOCUMENT constant
            if item.media_type and item.media_type.lower() in ['application/xhtml+xml', 'text/html']:
                text.append(item.get_content().decode('utf-8'))
        return '\n\n'.join(text)
    except Exception as e:
        logger.error(f"EPUB extraction error: {str(e)}")
        raise

def extract_chapters_from_epub(file_path: str) -> List[Dict[str, str]]:
    """Extract chapters from an EPUB file."""
    try:
        book = epub.read_epub(file_path)
        chapters = []
        toc = []
        
        # Try to extract table of contents if method is available
        # Some versions of ebooklib may not have this method
        try:
            if hasattr(book, 'get_toc'):
                toc = book.get_toc()
            else:
                # If get_toc isn't available, we'll rely on other methods
                logger.info("get_toc method not available in this ebooklib version")
                toc = []
        except Exception as e:
            logger.warning(f"Failed to extract EPUB table of contents: {str(e)}")
        
        # If we have a table of contents with chapters
        if toc:
            chapter_items = {}
            
            # Map all document items by href
            for item in book.get_items():
                # Check media type instead of using ITEM_DOCUMENT constant
                if item.media_type and item.media_type.lower() in ['application/xhtml+xml', 'text/html']:
                    chapter_items[item.get_name()] = item
            
            # Process each TOC entry as a chapter
            for title, href, _ in toc:
                href_parts = href.split('#')
                item_href = href_parts[0]
                
                if item_href in chapter_items:
                    content = chapter_items[item_href].get_content().decode('utf-8')
                    # Clean HTML content
                    soup = BeautifulSoup(content, 'html.parser')
                    text_content = soup.get_text('\n', strip=True)
                    
                    chapters.append({
                        "title": title,
                        "content": text_content
                    })
        
        # If no chapters were found through TOC, try to identify chapters by content
        if not chapters:
            # Process each HTML document as a potential chapter
            sorted_items = sorted(
                [item for item in book.get_items() if item.media_type and item.media_type.lower() in ['application/xhtml+xml', 'text/html']],
                key=lambda x: x.get_name()
            )
            
            for i, item in enumerate(sorted_items):
                content = item.get_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                
                # Try to find chapter title in the content
                title_elem = soup.find(['h1', 'h2', 'h3', 'header'])
                title = f"Chapter {i+1}"
                if title_elem and title_elem.get_text().strip():
                    title = title_elem.get_text().strip()
                
                text_content = soup.get_text('\n', strip=True)
                if text_content.strip():
                    chapters.append({
                        "title": title,
                        "content": text_content
                    })
        
        # If still no chapters, treat the entire book as one chapter
        if not chapters:
            all_text = extract_text_from_epub(file_path)
            chapters.append({
                "title": "Complete Book",
                "content": all_text
            })
            
        return chapters
    except Exception as e:
        logger.error(f"EPUB chapter extraction error: {str(e)}")
        raise

def process_text_file(file_path: str) -> Optional[str]:
    """Legacy method to extract all text from a file without chapter segmentation."""
    if file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    if file_path.endswith('.epub'):
        return extract_text_from_epub(file_path)
    if file_path.lower().endswith(('.md', '.markdown')):
        return extract_text_from_markdown(file_path)
    return None

def extract_chapters(file_path: str) -> List[Dict[str, str]]:
    """Extract chapters from a document, segmenting by chapter boundaries."""
    if file_path.endswith('.docx'):
        return extract_chapters_from_docx(file_path)
    if file_path.endswith('.epub'):
        return extract_chapters_from_epub(file_path)
    if file_path.lower().endswith(('.md', '.markdown')):
        return extract_chapters_from_markdown(file_path)
    return []

def extract_text_from_markdown(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Markdown extraction error: {str(e)}")
        raise

def extract_chapters_from_markdown(file_path: str) -> List[Dict[str, str]]:
    """Extract chapters from a Markdown file based on headings."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Look for heading markers (# for h1, ## for h2, etc.)
        # We'll consider h1 or h2 as chapter headings
        chapter_pattern = re.compile(r'^(#{1,2})\s+(.+)$', re.MULTILINE)
        chapter_matches = list(chapter_pattern.finditer(content))
        
        chapters = []
        
        # If we found chapter headings
        if chapter_matches:
            for i, match in enumerate(chapter_matches):
                chapter_title = match.group(2).strip()
                start_pos = match.end()
                
                # Find the end of this chapter (start of next chapter or end of file)
                if i < len(chapter_matches) - 1:
                    end_pos = chapter_matches[i + 1].start()
                else:
                    end_pos = len(content)
                
                chapter_content = content[start_pos:end_pos].strip()
                chapters.append({
                    "title": chapter_title,
                    "content": chapter_content
                })
        
        # If no chapters were found, look for other patterns like "Chapter X" text
        if not chapters:
            chapter_text_pattern = re.compile(r'^(Chapter\s+\d+|Part\s+\d+|Book\s+\d+)(.*)$', re.MULTILINE | re.IGNORECASE)
            chapter_matches = list(chapter_text_pattern.finditer(content))
            
            if chapter_matches:
                for i, match in enumerate(chapter_matches):
                    chapter_title = match.group(0).strip()
                    start_pos = match.end()
                    
                    # Find the end of this chapter
                    if i < len(chapter_matches) - 1:
                        end_pos = chapter_matches[i + 1].start()
                    else:
                        end_pos = len(content)
                    
                    chapter_content = content[start_pos:end_pos].strip()
                    chapters.append({
                        "title": chapter_title,
                        "content": chapter_content
                    })
        
        # If still no chapters, treat the entire document as one chapter
        if not chapters:
            chapters.append({
                "title": "Complete Document",
                "content": content
            })
            
        return chapters
    except Exception as e:
        logger.error(f"Markdown chapter extraction error: {str(e)}")
        raise

def check_supported_format(file_path: str) -> bool:
    return file_path.lower().endswith(('.docx', '.epub', '.md', '.markdown'))