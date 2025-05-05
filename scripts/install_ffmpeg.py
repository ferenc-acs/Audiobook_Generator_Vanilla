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

import subprocess
import sys

def install_ffmpeg():
    # Check if FFmpeg is already installed
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("FFmpeg is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        result = subprocess.run(
            ['choco', 'install', 'ffmpeg', '-y'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("FFmpeg installed successfully:\n", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Installation failed:\n", e.stderr)
        return False

if __name__ == "__main__":
    success = install_ffmpeg()
    sys.exit(0 if success else 1)