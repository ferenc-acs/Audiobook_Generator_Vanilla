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

import logging
import subprocess
import tempfile
import os
import json # Added for debug logging
from openai import OpenAI
from typing import Optional, List, Dict
from pathlib import Path
from tqdm import tqdm
from src.config import Config

logger = logging.getLogger(__name__)

# TTS synthesis instructions - used consistently across all synthesis and debug logging
TTS_INSTRUCTIONS = """
Voice Affect: Calm, Narrate in the style of a professional audiobook performer.

Tone: Keep the tone engaging and reflective of the text's mood

Pacing: Adopt a pace that is natural and conversational, but adaptable – slightly slower for emphasis or complex sentences, slightly faster for moments of excitement, always prioritizing intelligibility.

Emotions: Calm and subtly underscore the emotional context detected in the text.

Pronunciation: Accurate, crisp: Ensures clarity, especially with key details.

Pauses: Brief pauses at commas and natural clause breaks, with slightly longer pauses at sentence and paragraph endings to aid comprehension and flow.
"""

class AudioGenerator:
    def __init__(self, output_dir: str = "output", input_file: Optional[str] = None, voice: str = "ash", debug_log: bool = False):
        Config.validate_key()
        self.client = OpenAI(api_key=Config.get_openai_key())
        self.output_dir = Path(output_dir) # Use the provided output directory
        self.output_dir.mkdir(parents=True, exist_ok=True) # Ensure it exists, including parents
        self.input_file = input_file
        self.voice = voice # Store the selected voice
        self.debug_log = debug_log # Store the debug log flag
        
        # Determine debug log filename
        if self.debug_log:
            if self.input_file:
                input_path = Path(self.input_file)
                debug_filename = f"{input_path.stem}_synthesis_debug.txt"
            else:
                debug_filename = "synthesis_debug_log.txt" # Fallback if no input file
            self.debug_log_file = self.output_dir / debug_filename
        else:
            self.debug_log_file = None
        
        # Create chapters subdirectory within the specified output directory
        self.chapters_dir = self.output_dir / "chapters"
        self.chapters_dir.mkdir(exist_ok=True)

        # Clear the debug log file at the start if enabled
        if self.debug_log_file and self.debug_log_file.exists():
            self.debug_log_file.unlink()

    def _chunk_text(self, text: str, chunk_size: int = 4096) -> list[str]:
        # Use the sentence segmentation function from text_processor
        from src.text_processor import segment_text_by_sentences
        
        # First try to segment by sentences to maintain natural speech flow
        chunks = segment_text_by_sentences(text, chunk_size)
        
        # Fallback to simple chunking if sentence segmentation failed or returned nothing
        if not chunks:
            logger.warning("Sentence segmentation returned no chunks, falling back to simple chunking")
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            
        return chunks

    def _synthesize_chunk(self, text: str, index: int, chapter_dir: Optional[Path] = None, chapter_index: Optional[int] = None, is_indicator: bool = False) -> Optional[Path]:
        # Log debug information if enabled
        if self.debug_log:
            debug_info = {
                "chapter_index": chapter_index if chapter_index is not None else "N/A (Legacy/Indicator)",
                "chunk_index": index,
                "is_indicator": is_indicator,
                "voice": self.voice,
                "model": "gpt-4o-mini-tts",
                "input_text_length": len(text),
                "input_text": text,
                "instructions": TTS_INSTRUCTIONS
            }
            try:
                with open(self.debug_log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(debug_info, indent=2) + "\n---\n")
            except Exception as log_e:
                logger.error(f"Failed to write to debug log file {self.debug_log_file}: {log_e}")

        # --- Actual Synthesis ---
        try:
            # Use chapter directory if provided, otherwise use the specified output directory
            target_dir = chapter_dir if chapter_dir else self.output_dir
            output_path = target_dir / f"chunk_{index}.mp3"

            # Use streaming response to write audio directly to disk (memory-efficient)
            with self.client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice=self.voice,
                input=text,
                instructions=TTS_INSTRUCTIONS
            ) as response:
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
                # Pass chapter_index for debug logging
                chunk_path = self._synthesize_chunk(chunk, i, chapter_dir, chapter_index=chapter_index)
                if not chunk_path:
                    return None
                chunk_paths.append(chunk_path)
                pbar.update(1)
            
            # Process the chapter indicator
            # Pass chapter_index and is_indicator=True for debug logging
            indicator_path = self._synthesize_chunk(chapter_indicator, len(chunks), chapter_dir, chapter_index=chapter_index, is_indicator=True)
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
                # Pass chapter_index=None for legacy method
                chunk_path = self._synthesize_chunk(chunk, i, chapter_index=None)
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

    # New method to log debug info without synthesis (for --dry-run --debug-synthesis)
    def log_synthesis_debug_info(self, chapters: List[Dict[str, str]]):
        """Logs synthesis parameters for each chunk without calling the API."""
        if not self.debug_log:
            logger.warning("Debug logging is not enabled. Cannot log synthesis info.")
            return

        logger.info(f"Logging synthesis debug info to: {self.debug_log_file}")
        total_chunks_to_log = 0
        for i, chapter in enumerate(chapters):
            chapter_content = chapter.get("content", "")
            if chapter_content.strip():
                chunks = self._chunk_text(chapter_content)
                total_chunks_to_log += len(chunks) + 1 # +1 for indicator
        
        with tqdm(total=total_chunks_to_log, desc="Logging debug info") as pbar:
            for i, chapter in enumerate(chapters):
                chapter_index = i + 1
                chapter_title = chapter.get("title", f"Chapter {chapter_index}")
                chapter_content = chapter.get("content", "")

                if not chapter_content.strip():
                    logger.debug(f"Skipping debug log for empty Chapter {chapter_title}")
                    continue

                # Log chunks for the chapter content
                chunks = self._chunk_text(chapter_content)
                for j, chunk in enumerate(chunks):
                    self._log_chunk_debug_info(chunk, j, chapter_index=chapter_index, is_indicator=False)
                    pbar.update(1)

                # Log chunk for the chapter indicator
                chapter_indicator = self._create_chapter_indicator(chapter_title)
                self._log_chunk_debug_info(chapter_indicator, len(chunks), chapter_index=chapter_index, is_indicator=True)
                pbar.update(1)

    def _log_chunk_debug_info(self, text: str, index: int, chapter_index: int, is_indicator: bool):
        """Helper method to format and write debug info for a single chunk."""
        debug_info = {
            "chapter_index": chapter_index,
            "chunk_index": index,
            "is_indicator": is_indicator,
            "voice": self.voice,
            "model": "gpt-4o-mini-tts",
            "input_text_length": len(text),
            "input_text": text,
            "instructions": TTS_INSTRUCTIONS
        }
        try:
            with open(self.debug_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(debug_info, indent=2) + "\n---\n")
        except Exception as log_e:
            logger.error(f"Failed to write to debug log file {self.debug_log_file}: {log_e}")