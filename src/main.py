import argparse
import logging
from pathlib import Path
from src.text_processor import check_supported_format, process_text_file
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
        text = process_text_file(str(input_path))
        
        logger.info("Starting audiobook generation...")
        generator = AudioGenerator(input_file=str(input_path))
        output_path = generator.generate_audiobook(text)
        
        if output_path and output_path.exists():
            logger.info(f"Audiobook successfully created: {output_path}")
        else:
            logger.error("Audiobook generation failed")

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()