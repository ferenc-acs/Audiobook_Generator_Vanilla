import argparse
import logging
from pathlib import Path
from src.text_processor import check_supported_format, process_text_file, extract_chapters
from src.audio_generator import AudioGenerator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Convert DOCX/EPUB files to audiobook')
    parser.add_argument('input_file', type=str, help='Path to input document')
    args = parser.parse_args()

    try:
        input_path = Path(args.input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file {input_path} not found")

        if not check_supported_format(str(input_path)):
            raise ValueError("Unsupported file format. Only DOCX, MARKDOWN and EPUB are supported")

        logger.info(f"Processing file: {input_path}")
        
        # Extract chapters from the input file
        logger.info("Extracting chapters...")
        chapters = extract_chapters(str(input_path))
        logger.info(f"Found {len(chapters)} chapters")
        
        # Generate audio for each chapter
        logger.info("Starting audiobook generation...")
        generator = AudioGenerator(input_file=str(input_path))
        
        # Generate audiobook by chapters
        chapter_paths = generator.generate_audiobook_by_chapters(chapters)
        
        if chapter_paths:
            logger.info(f"Successfully created {len(chapter_paths)} chapter audio files")
            logger.info(f"Chapter files are available in: {generator.chapters_dir}")
            
            # The full audiobook is automatically created by the generator
            full_path = generator.output_dir / f"{input_path.stem}_full.mp3"
            if full_path.exists():
                logger.info(f"Complete audiobook also created: {full_path}")
        else:
            logger.error("Audiobook generation failed")


    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()