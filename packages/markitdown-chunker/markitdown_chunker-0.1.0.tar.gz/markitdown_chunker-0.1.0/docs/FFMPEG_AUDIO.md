# Audio/Video File Processing

## FFmpeg Warning

You may see this warning when using the package:

```
RuntimeWarning: Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work
```

**This warning is suppressed by default** and does not affect the core functionality of markitdown-chunker.

## Why This Warning Appears

The underlying `markitdown` library includes optional support for audio/video files via `pydub`, which requires `ffmpeg`. Since most document processing workflows don't need audio/video conversion, this warning is safely suppressed.

## If You Need Audio/Video Processing

If you want to process audio or video files (MP3, MP4, WAV, etc.) and convert them to markdown (e.g., transcription), you'll need to install ffmpeg:

### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install ffmpeg
```

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract and add to PATH
3. Or use chocolatey: `choco install ffmpeg`

### Verify Installation

```bash
ffmpeg -version
```

## Supported File Types Without FFmpeg

These formats work perfectly without ffmpeg:

- **Documents:** PDF, DOCX, DOC, TXT, MD, RTF, ODT
- **Spreadsheets:** XLSX, XLS, ODS  
- **Presentations:** PPTX, PPT, ODP
- **Web:** HTML, HTM

## Supported With FFmpeg

If you install ffmpeg, markitdown can also handle:

- **Audio:** MP3, WAV, FLAC, AAC, OGG
- **Video:** MP4, AVI, MOV, MKV, WebM

Note: Audio/video conversion typically requires transcription services (like OpenAI Whisper) which are not included by default.

## Disabling the Suppression

If you want to see the warning (e.g., for debugging), you can disable it:

```python
import warnings
warnings.filterwarnings("default", message=".*Couldn't find ffmpeg or avconv.*")

from markitdown_chunker import MarkitDownProcessor
```

## Questions?

If you have issues with audio/video processing:
1. Make sure ffmpeg is installed and in your PATH
2. Check markitdown documentation: https://github.com/microsoft/markitdown
3. Open an issue on our GitHub

