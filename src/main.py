import argparse
import logging
from pathlib import Path
from .text_processor import extract_chapters
from .audio_generator import AudioGenerator
from .config import Config

def setup_logging(verbose: bool, quiet: bool):
    log_level = logging.INFO
    if verbose:
        log_level = logging.DEBUG
    elif quiet:
        log_level = logging.WARNING
        
    logging.basicConfig(level=log_level, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Suppress overly verbose logs from libraries if not in verbose mode
    if not verbose:
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("keyring").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

def main():
    parser = argparse.ArgumentParser(description="Convert text documents to audiobooks.")
    parser.add_argument("input_file", help="Path to the input document (DOCX, EPUB, Markdown).")
    parser.add_argument("-o", "--output-dir", default="output", help="Directory to save generated audio files (default: output).")
    parser.add_argument("--voice", default="nova", choices=["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse"], help="TTS voice model (default: nova).")
    parser.add_argument("--dry-run", action="store_true", help="Detect chapters and list them without generating audio.")
    parser.add_argument("--debug-synthesis", action="store_true", help="Log synthesis input text and instructions to a debug file. If used with --dry-run, only logs info without API calls.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable detailed debug logging.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress informational messages, show only warnings/errors.")
    
    args = parser.parse_args()
    
    setup_logging(args.verbose, args.quiet)
    logger = logging.getLogger(__name__)
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    try:
        # Validate API key early
        Config.validate_key()
        logger.info(f"Using voice: {args.voice}")
        if args.debug_synthesis:
            logger.info("Synthesis debug logging enabled.")

        # Extract chapters directly using the function
        chapters = extract_chapters(str(input_path))
        
        if not chapters:
            logger.warning("No chapters detected or text extracted. Cannot generate audio.")
            return

        if args.dry_run:
            logger.info("--- Dry Run Mode --- ")
            logger.info(f"Detected {len(chapters)} chapters:")
            for i, chapter in enumerate(chapters):
                title = chapter.get('title', f'Chapter {i+1}')
                content_preview = chapter.get('content', '')[:100].replace('\n', ' ') + "..."
                logger.info(f"  {i+1}. {title} (Preview: {content_preview})")
            
            # If both dry-run and debug-synthesis are enabled, log debug info without synthesis
            if args.debug_synthesis:
                logger.info("Logging synthesis debug info (dry run)...")
                # Instantiate generator just for logging
                generator = AudioGenerator(
                    output_dir=args.output_dir, 
                    input_file=args.input_file, 
                    voice=args.voice, 
                    debug_log=True # Enable debug logging in the generator
                )
                generator.log_synthesis_debug_info(chapters)
                logger.info(f"Synthesis debug info logged to: {generator.debug_log_file}")
            else:
                 logger.info("Dry run complete. No audio generated.")
            return # Exit after dry run

        # --- Normal Audio Generation --- 
        logger.info(f"Starting audiobook generation for {len(chapters)} chapters...")
        generator = AudioGenerator(
            output_dir=args.output_dir, 
            input_file=args.input_file, 
            voice=args.voice, 
            debug_log=args.debug_synthesis # Pass the debug flag
        )
        
        chapter_paths = generator.generate_audiobook_by_chapters(chapters)
        
        if chapter_paths:
            logger.info(f"Successfully generated {len(chapter_paths)} chapter audio files in '{generator.chapters_dir}'.")
            # The combine_chapters method is called within generate_audiobook_by_chapters if successful
            combined_file_path = generator.output_dir / f"{input_path.stem}_full.mp3"
            if combined_file_path.exists():
                logger.info(f"Combined audiobook saved as '{combined_file_path}'.")
            if args.debug_synthesis:
                 logger.info(f"Synthesis debug info logged to: {generator.debug_log_file}")
        else:
            logger.error("Audiobook generation failed.")
            
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}") # Log full traceback for unexpected errors

if __name__ == "__main__":
    main()