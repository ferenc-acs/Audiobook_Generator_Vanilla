import logging
import subprocess
import tempfile
import os
from openai import OpenAI
from typing import Optional
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

    def _chunk_text(self, text: str, chunk_size: int = 4096) -> list[str]:
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def _synthesize_chunk(self, text: str, index: int) -> Optional[Path]:
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )
            output_path = self.output_dir / f"chunk_{index}.mp3"
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

    def generate_audiobook(self, text: str) -> Optional[Path]:
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