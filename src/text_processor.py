from typing import Optional
from docx import Document
from ebooklib import epub
import logging

logger = logging.getLogger(__name__)

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}")
        raise

def extract_text_from_epub(file_path: str) -> str:
    try:
        book = epub.read_epub(file_path)
        text = []
        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                text.append(item.get_content().decode('utf-8'))
        return '\n\n'.join(text)
    except Exception as e:
        logger.error(f"EPUB extraction error: {str(e)}")
        raise

def process_text_file(file_path: str) -> Optional[str]:
    if file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    if file_path.endswith('.epub'):
        return extract_text_from_epub(file_path)
    if file_path.lower().endswith(('.md', '.markdown')):
        return extract_text_from_markdown(file_path)
    return None

def extract_text_from_markdown(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Markdown extraction error: {str(e)}")
        raise

def check_supported_format(file_path: str) -> bool:
    return file_path.lower().endswith(('.docx', '.epub', '.md', '.markdown'))