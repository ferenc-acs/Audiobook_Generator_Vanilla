import sys
import os
import logging

# Add the project root to the path so we can import the src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def segment_text_with_spacy(text, chunk_size=4096):
    """
    Segment text at sentence boundaries using spaCy.
    
    Args:
        text (str): The text to segment
        chunk_size (int): Maximum size of each chunk in characters
        
    Returns:
        list: List of text chunks respecting sentence boundaries
    """
    try:
        import spacy
        # Load the small English model - efficient for sentence segmentation
        nlp = spacy.load("en_core_web_sm", disable=["ner", "tagger", "lemmatizer", "attribute_ruler"])
        # Only use the pipeline components we need for sentence segmentation
        nlp.max_length = len(text) + 100  # Ensure spaCy can process the full text
        
        # Process the text to get sentence boundaries
        doc = nlp(text)
        
        chunks = []
        current_chunk = ""
        
        for sent in doc.sents:
            sentence_text = sent.text
            
            # If adding this sentence exceeds chunk_size, save current chunk and start a new one
            if len(current_chunk) + len(sentence_text) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = sentence_text
            else:
                current_chunk += (" " if current_chunk else "") + sentence_text
        
        # Add the last chunk if it contains any text
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    except ImportError:
        logger.error("spaCy or en_core_web_sm model not installed. Run: pip install spacy && python -m spacy download en_core_web_sm")
        return None

def segment_text_fallback(text, chunk_size=4096):
    """
    Fallback method for text segmentation using regex pattern matching
    for basic sentence boundaries when spaCy is not available.
    
    Args:
        text (str): The text to segment
        chunk_size (int): Maximum size of each chunk in characters
        
    Returns:
        list: List of text chunks attempting to respect sentence boundaries
    """
    import re
    # Pattern to match sentence endings (period, question mark, exclamation mark followed by space or end of string)
    sentence_ends = re.compile(r'[.!?](?:\s|$)')
    
    chunks = []
    current_chunk = ""
    last_end = 0
    
    for match in sentence_ends.finditer(text):
        sentence_end = match.end()
        sentence = text[last_end:sentence_end]
        
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk += sentence
            
        last_end = sentence_end
    
    # Add any remaining text
    if last_end < len(text):
        remaining = text[last_end:]
        if len(current_chunk) + len(remaining) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            chunks.append(remaining)
        else:
            current_chunk += remaining
            
    # Add the last chunk if it contains any text
    if current_chunk and current_chunk not in chunks:
        chunks.append(current_chunk)
        
    return chunks

def test_segmentation(sample_text):
    """Test both segmentation methods and compare results"""
    # Try spaCy-based segmentation
    logger.info("Testing spaCy-based segmentation...")
    try:
        spacy_chunks = segment_text_with_spacy(sample_text, chunk_size=1000)  # Smaller chunk size for testing
        if spacy_chunks:
            logger.info(f"spaCy segmentation created {len(spacy_chunks)} chunks")
            for i, chunk in enumerate(spacy_chunks):
                logger.info(f"Chunk {i+1}: {len(chunk)} characters, ends with: '{chunk[-50:]}...'")
    except Exception as e:
        logger.error(f"Error in spaCy segmentation: {str(e)}")
        spacy_chunks = None
    
    # Test fallback segmentation
    logger.info("\nTesting fallback segmentation...")
    fallback_chunks = segment_text_fallback(sample_text, chunk_size=1000)  # Same chunk size
    logger.info(f"Fallback segmentation created {len(fallback_chunks)} chunks")
    for i, chunk in enumerate(fallback_chunks):
        logger.info(f"Chunk {i+1}: {len(chunk)} characters, ends with: '{chunk[-50:]}...'")
    
    # Compare the two methods
    if spacy_chunks:
        logger.info("\nComparison:")
        logger.info(f"spaCy chunks: {len(spacy_chunks)}, Fallback chunks: {len(fallback_chunks)}")
        
        # Check if chunks end with complete sentences
        spacy_sentence_ends = sum(1 for chunk in spacy_chunks if chunk.rstrip().endswith(('.', '!', '?')))
        fallback_sentence_ends = sum(1 for chunk in fallback_chunks if chunk.rstrip().endswith(('.', '!', '?')))
        
        logger.info(f"spaCy chunks ending with sentence: {spacy_sentence_ends}/{len(spacy_chunks)}")
        logger.info(f"Fallback chunks ending with sentence: {fallback_sentence_ends}/{len(fallback_chunks)}")

if __name__ == "__main__":
    # Sample text for testing
    sample_text = """
    This is a sample text for testing sentence segmentation. It contains multiple sentences with various punctuation marks! 
    Does it handle questions properly? Let's see how it works with longer content.
    
    This is a new paragraph. The segmentation should respect sentence boundaries while creating chunks of an appropriate size.
    Here's a very long sentence that goes on and on with multiple clauses, stretching the limits of what we might consider reasonable for a single sentence in English prose, but nonetheless serves as a good test for our sentence segmentation logic to ensure it can handle verbose and complex sentence structures like those found in some literary works or academic texts which tend to use complex and compound sentences with multiple dependent and independent clauses joined by conjunctions, commas, and semicolons; this helps us evaluate the robustness of our approach.
    
    Short sentence. Another short one! A third? Indeed.
    
    The end.
    """
    
    test_segmentation(sample_text)
    
    print("\nTest completed. If spaCy segmentation failed, install dependencies:")
    print("pip install spacy")
    print("python -m spacy download en_core_web_sm")