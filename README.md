Here's a sample README file to help you understand and work with this code:

---

# Study Quiz: Audio and Video Transcription with Questions Generation

This application provides tools for extracting and transcribing audio from uploaded files, YouTube videos, or direct recording. The transcriptions are then processed to generate study questions and answers in German, alongside the transcript itself in markdown and downloadable PDF format.

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Configuration](#configuration)
6. [File Structure](#file-structure)

---

## Features

- **Audio Recording and Upload**: Directly record audio or upload audio files in WAV or MP3 format.
- **Upload PDF files**: Add PDF files, which contents will be included in the summary and questions.
- **YouTube Transcript Extraction**: Provide a YouTube URL to extract video transcripts (supports German and English).
- **Question Generation**: Generate a customizable set of questions based on the transcript to enhance study engagement.
- **Markdown Formatting**: Automatically format transcripts in readable markdown.
- **PDF Export**: Download formatted transcripts as a PDF file.
- **Interactive Interface**: Powered by Streamlit for a user-friendly interface.

## Requirements

Ensure you have the following libraries installed:
- `streamlit`
- `markdown_pdf`
- `audio_recorder_streamlit`
- `dotenv-python`
- `sounddevice`
- `scipy`
- `numpy`
- `pydub`
- `md2pdf`
- `spire.doc`
- `youtube_transcript_api`
- `re`
- `pandas`

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/your_username/study-quiz.git
    cd study-quiz
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your environment variables (see [Configuration](#configuration)).

## Usage

Run the application using Streamlit:
```bash
streamlit run main.py
```

This will open a web interface where you can:
- Record audio or upload a file.
- Provide a YouTube URL to extract a transcript.
- Generate questions and view the markdown-formatted transcript.
- Download the final transcript as a PDF.

### Key Functionalities

- **Audio Recording and Transcription**: Uses SoundDevice and Scipy to capture audio, save as WAV, and process it.
- **YouTube Transcription**: Extracts transcripts using `youtube_transcript_api`.
- **Question Generation**: Uses a custom prompt to generate questions and answers for study.
- **PDF Export**: Converts markdown to PDF for download.

## Configuration

The application requires a `.env` file to store your API key:

```plaintext
GROQ_API_KEY=your_groq_api_key
```

## File Structure

- `app.py`: Main application file with all code for audio recording, transcription, question generation, and PDF export.
- `requirements.txt`: Lists all dependencies.
- `README.md`: Documentation for the project.
- `.env`: Environment variables file (for API keys and sensitive information).

## Notes

- This app uses the Whisper model for transcription, YouTube Transcript API for video transcriptions, and Spire.Doc for handling PDFs.
- Make sure the audio files are under 25MB; larger files are converted to MP3 for processing efficiency.

---

This README provides an overview and setup instructions. For further development or questions, feel free to reach out to the contributors of this repository.
