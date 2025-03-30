# Audiobook Generator

A Python application that converts text documents (DOCX, EPUB, Markdown) into audiobooks using OpenAI's text-to-speech API.

## Features

- Supports multiple document formats (DOCX, EPUB, Markdown)
- Secure API key management using system credential store
- Automatic chunking of large texts
- Progress tracking during audio generation
- Combines audio chunks into a single audiobook file

## Requirements

- Python 3.11 or higher
- FFmpeg (for audio file concatenation)
- OpenAI API key

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/audiobook-generator.git
   cd audiobook-generator
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Set up your OpenAI API key:
   ```bash
   poetry run python scripts/setup_credentials.py
   ```

4. Install FFmpeg (if not already installed):
   ```bash
   poetry run python scripts/install_ffmpeg.py
   ```

## Usage

```bash
# Convert a DOCX file to audiobook
poetry run python -m src.main input/your-document.docx

# Convert an EPUB file to audiobook
poetry run python -m src.main input/your-book.epub

# Convert a Markdown file to audiobook
poetry run python -m src.main input/your-text.md
```

The generated audiobook will be saved in the `output` directory.

## Project Structure

```
├── src/                  # Source code
│   ├── audio_generator.py # Audio generation logic
│   ├── config.py         # Configuration and API key management
│   ├── main.py           # Main application entry point
│   └── text_processor.py # Document parsing and text extraction
├── scripts/              # Utility scripts
│   ├── check_credentials.py # Verify API key setup
│   ├── create_test_docx.py  # Create test document
│   ├── install_ffmpeg.py    # Install FFmpeg
│   └── setup_credentials.py # Set up secure API key storage
├── input/                # Input documents (not included in repo)
├── output/               # Generated audiobooks (not included in repo)
├── pyproject.toml       # Poetry configuration
└── poetry.lock          # Dependency lock file
```

## Security

This project supports storing your OpenAI API key in your system's secure credential store instead of in plain text in the `.env` file. This provides better security for your API key as it's protected by your system's security mechanisms.

For more information about secure credential storage, see [README_CREDENTIALS.md](README_CREDENTIALS.md).

## License

MIT