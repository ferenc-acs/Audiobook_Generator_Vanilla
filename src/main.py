import argparse
import logging
from pathlib import Path
from src.text_processor import check_supported_format, process_text_file, extract_chapters
from src.audio_generator import AudioGenerator

# Configure root logger initially to capture early messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Convert DOCX, EPUB, or Markdown files to audiobook')
    parser.add_argument('input_file', type=str, help='Path to input document')
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default="output",
        help='Directory to save the generated audiobook files (default: output)'
    )
    parser.add_argument(
        '--voice',
        type=str,
        default="ash",
        choices=["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"],
        help='Voice model to use for TTS (default: nova)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show detected chapters without generating audio'
    )
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        '-v', '--verbose',
        action='store_const',
        dest='loglevel',
        const=logging.DEBUG,
        help='Enable detailed debug logging'
    )
    verbosity_group.add_argument(
        '-q', '--quiet',
        action='store_const',
        dest='loglevel',
        const=logging.WARNING,
        help='Suppress informational messages, only show warnings and errors'
    )

    args = parser.parse_args()

    # Reconfigure logging based on verbosity arguments
    log_level = args.loglevel if args.loglevel else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s', force=True)

    try:
        input_path = Path(args.input_file)
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True) # Ensure output dir exists

        if not input_path.exists():
            raise FileNotFoundError(f"Input file {input_path} not found")

        if not check_supported_format(str(input_path)):
            raise ValueError("Unsupported file format. Only DOCX, MARKDOWN and EPUB are supported")

        logger.info(f"Processing file: {input_path}")
        logger.debug(f"Output directory: {output_path}")
        logger.debug(f"Selected voice: {args.voice}")
        
        # --- Extract Chapters ---
        logger.info("Extracting chapters...")
        chapters = extract_chapters(str(input_path))
        logger.info(f"Found {len(chapters)} chapters")
        if not chapters:
            logger.warning("No chapters found in the document.")
            return # Exit if no chapters

        # --- Dry Run Option ---
        if args.dry_run:
            logger.info("--- Dry Run Mode ---")
            logger.info("Detected chapters:")
            for i, chapter in enumerate(chapters):
                logger.info(f"  Chapter {i+1}: {chapter.get('title', 'Untitled Chapter')}")
            logger.info("Dry run complete. No audio files generated.")
            return # Exit after dry run

        # --- Generate Audio ---
        logger.info("Starting audiobook generation...")
        # Pass output directory and voice to the generator
        generator = AudioGenerator(input_file=str(input_path), output_dir=str(output_path), voice=args.voice)
        
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
                 logger.warning("Combined full audiobook file was not created.") # Warn if combine failed
        else:
            logger.error("Audiobook generation failed or produced no chapter files")


    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise # Re-raise exception for debugging

if __name__ == "__main__":
    main()