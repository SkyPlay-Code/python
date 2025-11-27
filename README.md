# SkyPlay Python Utils  
**Your ultimate toolkit for AI automation, media processing, file conversions, and creative coding experiments**  
AI-Powered Tools • Computer Vision Magic • Universal Converters • Fun ASCII Art & More  

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)  
[![Stars](https://img.shields.io/github/stars/SkyPlay-Code/python?style=for-the-badge&color=yellow)](https://github.com/SkyPlay-Code/python/stargazers)  
[![Last Commit](https://img.shields.io/github/last-commit/SkyPlay-Code/python?style=for-the-badge&color=brightgreen)](https://github.com/SkyPlay-Code/python/commits/main)  

> “Code once, automate forever. From AI brains to file wizards—this repo has your back.” – SkyPlay-Code

## What’s Inside?

This repo is packed with practical Python scripts leveraging gems like Google Gemini AI, MediaPipe for CV, and FFmpeg/Pillow for conversions. Whether you're automating tasks, processing media, or just hacking fun stuff, dive in!

| Folder              | What It Does                                  | Highlights                              |
|---------------------|-----------------------------------------------|-----------------------------------|
| `ai/`               | AI-driven automation and code generation      | 🤖 Gemini-powered script executors & generators |
| `cv/`               | Computer vision tools for tracking & scanning | 👁️ Face/hand trackers, virtual drawing, 3D face models |
| `file_conversion/`  | Universal converters for audio/video/images/docs | 🪄 Audio, video, docs, archives, fonts, ebooks, presentations |
| `misc/`             | Random utilities: ASCII art, geometry calc, Windows automation | 🧠 Spinning donuts, shape calculators, random bots |

## 🚀 Quick Start

1. Clone the repo:
   ```bash
   git clone https://github.com/SkyPlay-Code/python.git
   cd python
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run a sample:
   - AI Automation: `python ai/ai_auto.py` (Enter commands like "Write a script to fetch weather")
   - Face Scanner: `python cv/face_scanner.py` (Scan your face for a 3D model)
   - Video Converter: `python file_conversion/video_conversion.py` (Follow prompts for conversion)

## ✨ Highlights (The Cool Stuff)

### AI / Automation (`ai/`)
- `ai_auto.py` & `coder.py`: Chat with Gemini AI to generate, save, and execute code in Python/JS/Shell. Handles actions like "execute" or "open".
  - Example: "Create a web scraper for news" → Generates & runs the script.
- `auto_command.py`: Dynamically generates and executes functions from natural language prompts.
- `indefinite.py`: Infinitely generates random Python scripts, saving each to a file.
- `gemini-text.py`, `gemini-image.py`, `gemini-thinking.py`: Text generation, image creation/modification, and advanced "thinking" configs with Gemini.

### Computer Vision (`cv/`)
- `face_scanner.py`: LiDAR-style face scanner using MediaPipe. Builds a 3D OBJ model by capturing landmarks from multiple angles.
- `drawing.py`: Two-handed virtual drawing app—use fingers to draw in air, change colors with pinches.
- `tracker.py`: Real-time hand and face tracking with landmarks, contours, and mesh.
- `neural_net-digits.py`: From-scratch neural network for MNIST digit recognition (training included).

### File Conversion Wizardry (`file_conversion/`)
- `main.py`: All-in-one converter—auto-detects file type (audio/video/image/doc/etc.) and launches the right tool.
- `audio_conversion.py`: Convert between 20+ audio formats (MP3, FLAC, WAV) with bitrate options and rich UI.
- `video_conversion.py`: Video to video/audio/GIF. Supports H.264, VP9, quality presets.
- `image_conversion.py`: Handles 20+ image formats (JPEG, PNG, RAW) with quality/resolution tweaks.
- `document_conversion.py`: DOCX/PDF/RTF conversions using Pandoc/PyMuPDF.
- `archive_conversion.py`: ZIP/TAR/7Z/RAR conversions with extraction.
- `font_conversion.py`: Font formats (TTF/OTF/WOFF) using FontForge.
- `ebook_conversion.py`: EPUB/AZW3/MOBI using Calibre.
- `powerpoint_conversion.py`: PPTX/ODP/PDF using LibreOffice.

### Misc (The “I Needed This Yesterday” Folder) (`misc/`)
- `donut.py`: Mesmerizing spinning ASCII donut—adapts to terminal size.
- `3d_shapes.py`: Calculator for 3D/2D shapes (volume, area, diagonals).
- `random_win_automation.py`: Fun Windows automation—opens apps, plays music, "hacks" CMD.
- `code_autotype.py`: Auto-types code into your editor with verification & repair.
- `audio_process.py`: Transcribes audio files using Gemini.

## 🛠️ Installation & Dependencies

1. Python 3.8+ required.
2. Install core deps:
   ```txt
   # requirements.txt (core + common; see individual scripts for extras)
   google-generativeai
   rich
   art
   opencv-python
   mediapipe
   pydub
   pillow
   pypandoc
   pymupdf
   fontforge  # For fonts (system install may be needed)
   ebooklib  # For ebooks (via Calibre CLI)
   numpy
   pyautogui
   pyperclip
   rawpy
   pillow-heif
   ffmpeg-python
   ```
   ```bash
   pip install -r requirements.txt
   ```
3. Extras:
   - Gemini API: Set `GEMINI_API_KEY` env var.
   - FFmpeg: Install system-wide for audio/video conversions.
   - LibreOffice/Calibre/FontForge: For docs/presentations/ebooks/fonts.
   - MediaPipe/OpenCV: For CV scripts.

Run tests: `pytest` (add `tests/` folder with basics).

## 🤝 Contributing

Found a bug or want to add a killer script? Let's collab!

1. Fork & clone.
2. Branch: `git checkout -b feat/new-converter`.
3. Code: Follow PEP 8, add docstrings.
4. Commit: `git commit -m "feat: add video stabilizer"`.
5. Push & PR.

Issues/PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Star History (Because Stars Are Cool)

[![Star History Chart](https://api.star-history.com/svg?repos=SkyPlay-Code/python&type=Date)](https://star-history.com/#SkyPlay-Code/python)

---

**Built with curiosity, caffeine, and a dash of AI magic.**  
If this repo sparked an idea or saved you time → drop a ⭐ and let's connect!

Got ideas? Open an issue or ping [@SkyPlay-Code on GitHub](https://github.com/SkyPlay-Code).  
Let’s turn this into the ultimate Python playground. 🚀

Made with ❤️ by [@SkyPlay-Code](https://github.com/SkyPlay-Code)  
Last updated: November 26, 2025
