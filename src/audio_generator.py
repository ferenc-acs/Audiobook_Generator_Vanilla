import logging
import subprocess
import tempfile
import os
from openai import OpenAI
from typing import Optional, List, Dict
from pathlib import Path
from tqdm import tqdm
from src.config import Config

logger = logging.getLogger(__name__)

class AudioGenerator:
    def __init__(self, output_dir: str = "output", input_file: Optional[str] = None):
        Config.validate_key()
        self.client = OpenAI(api_key=Config.get_openai_key())
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.input_file = input_file
        
        # Create chapters subdirectory for individual chapter files
        self.chapters_dir = self.output_dir / "chapters"
        self.chapters_dir.mkdir(exist_ok=True)

    def _chunk_text(self, text: str, chunk_size: int = 4096) -> list[str]:
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def _synthesize_chunk(self, text: str, index: int, chapter_dir: Optional[Path] = None) -> Optional[Path]:
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text,
                instructions="Narrate like a professional audiobook speaker with clear articulation, proper pacing, and appropriate dramatic emphasis. Ensure the tone is engaging, the pronunciation is crisp, and the intonation matches the emotional context of the text. Use pauses effectively to enhance comprehension and maintain listener interest."
            )
            # Use chapter directory if provided, otherwise use the output directory
            target_dir = chapter_dir if chapter_dir else self.output_dir
            output_path = target_dir / f"chunk_{index}.mp3"
            response.stream_to_file(str(output_path))
            return output_path
        except Exception as e:
            # Mask API key in error messages
            error_msg = str(e)
            if 'Incorrect API key provided:' in error_msg and 'sk-' in error_msg:
                # Find the API key in the error message and mask it
                import re
                # Look for API key pattern (sk- followed by characters)
                api_key_match = re.search(r'(sk-[a-zA-Z0-9-_]+)', error_msg)
                if api_key_match:
                    api_key = api_key_match.group(1)
                    masked_key = Config.mask_api_key(api_key)
                    error_msg = error_msg.replace(api_key, masked_key)
            logger.error(f"Failed to synthesize chunk {index}: {error_msg}")
            return None

    def _create_chapter_indicator(self, chapter_title: str) -> str:
        """Create an end-of-chapter indicator text to be spoken at the end of each chapter."""
        return f"End of {chapter_title}."
    
    def generate_chapter_audio(self, chapter: Dict[str, str], chapter_index: int) -> Optional[Path]:
        """Generate audio for a single chapter."""
        # Create a unique subdirectory for this chapter
        chapter_dir = self.chapters_dir / f"chapter_{chapter_index}"
        chapter_dir.mkdir(exist_ok=True)
        
        # Get the chapter content and title
        chapter_title = chapter.get("title", f"Chapter {chapter_index}")
        chapter_content = chapter.get("content", "")
        
        if not chapter_content.strip():
            logger.warning(f"Chapter {chapter_title} has no content to process")
            return None
        
        # Add chapter indicator to the end of the chapter
        chapter_indicator = self._create_chapter_indicator(chapter_title)
        
        # Process the chapter content in chunks
        chunks = self._chunk_text(chapter_content)
        chunk_paths = []
        
        with tqdm(total=len(chunks)+1, desc=f"Synthesizing chapter {chapter_index}: {chapter_title}") as pbar:
            # Process the main chapter content
            for i, chunk in enumerate(chunks):
                chunk_path = self._synthesize_chunk(chunk, i, chapter_dir)
                if not chunk_path:
                    return None
                chunk_paths.append(chunk_path)
                pbar.update(1)
            
            # Process the chapter indicator
            indicator_path = self._synthesize_chunk(chapter_indicator, len(chunks), chapter_dir)
            if indicator_path:
                chunk_paths.append(indicator_path)
                pbar.update(1)
        
        # Create a temporary list file for FFmpeg concatenation
        list_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        try:
            for path in chunk_paths:
                abs_path = os.path.abspath(path)
                list_file.write(f"file '{abs_path}'\n")
            list_file.close()
            
            # Create sanitized chapter title for filename
            safe_title = "".join(c if c.isalnum() else "_" for c in chapter_title)
            safe_title = safe_title[:50]  # Limit length to avoid excessively long filenames
            
            # Generate the chapter output file
            chapter_filename = f"{chapter_index:02d}_{safe_title}.mp3"
            chapter_output_path = self.chapters_dir / chapter_filename
            
            subprocess.run(
                ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file.name, '-c', 'copy', str(chapter_output_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return chapter_output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg concatenation failed for chapter {chapter_title}: {e.stderr}")
            return None
        finally:
            os.unlink(list_file.name)
    
    def generate_audiobook(self, text: str) -> Optional[Path]:
        """Legacy method to generate a single audiobook file from text without chapter segmentation."""
        chunks = self._chunk_text(text)
        chunk_paths = []

        with tqdm(total=len(chunks), desc="Synthesizing audio") as pbar:
            for i, chunk in enumerate(chunks):
                chunk_path = self._synthesize_chunk(chunk, i)
                if not chunk_path:
                    return None
                chunk_paths.append(chunk_path)
                pbar.update(1)

        # Create a temporary list file for FFmpeg concatenation
        list_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        try:
            for path in chunk_paths:
                # Use absolute path to ensure FFmpeg can find the file
                abs_path = os.path.abspath(path)
                list_file.write(f"file '{abs_path}'\n")
            list_file.close()

            # Generate output filename based on input filename if available
            if self.input_file:
                input_path = Path(self.input_file)
                output_filename = f"{input_path.stem}.mp3"
            else:
                output_filename = "final_audiobook.mp3"
                
            final_path = self.output_dir / output_filename
            subprocess.run(
                ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file.name, '-c', 'copy', str(final_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg concatenation failed: {e.stderr}")
            return None
        finally:
            os.unlink(list_file.name)

        return final_path
        
    def generate_audiobook_by_chapters(self, chapters: List[Dict[str, str]]) -> List[Path]:
        """Generate audio files for each chapter and return the list of chapter audio files."""
        chapter_paths = []
        
        for i, chapter in enumerate(chapters):
            logger.info(f"Processing chapter {i+1}/{len(chapters)}: {chapter.get('title', f'Chapter {i+1}')}")
            chapter_path = self.generate_chapter_audio(chapter, i+1)
            if chapter_path:
                chapter_paths.append(chapter_path)
        
        # Generate output filename based on input filename if available
        if self.input_file and chapter_paths:
            input_path = Path(self.input_file)
            output_filename = f"{input_path.stem}_full.mp3"
            
            # Optionally combine all chapters into a single audiobook file
            self.combine_chapters(chapter_paths, output_filename)
        
        return chapter_paths
    
    def combine_chapters(self, chapter_paths: List[Path], output_filename: str) -> Optional[Path]:
        """Combine multiple chapter audio files into a single audiobook file."""
        if not chapter_paths:
            logger.warning("No chapter paths provided to combine")
            return None
            
        # Create a temporary list file for FFmpeg concatenation
        list_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        try:
            for path in chapter_paths:
                abs_path = os.path.abspath(path)
                list_file.write(f"file '{abs_path}'\n")
            list_file.close()
            
            final_path = self.output_dir / output_filename
            logger.info(f"Combining {len(chapter_paths)} chapters into {final_path}")
            
            subprocess.run(
                ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file.name, '-c', 'copy', str(final_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return final_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg concatenation failed: {e.stderr}")
            return None
        finally:
            os.unlink(list_file.name)