from markdown_pdf import MarkdownPdf
import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
import json
import base64
from datetime import datetime
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import streamlit as st
import time
from pydub import AudioSegment
from spire.doc import *
from spire.doc.common import *
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import re
import pandas as pd
from io import StringIO
from upload import description
import tempfile

# Set parameters
sample_rate = 44100  # Sample rate in Hertz (CD quality)
channels = 1        # Stereo recording
output_filename = "audio.wav"
processing = False


load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

def extract_youtube_video_id(url: str) -> str:
    """
    Extract the video ID from the URL
    https://www.youtube.com/watch?v=XXX -> XXX
    https://youtu.be/XXX -> XXX
    """
    found = re.search(r"(?:youtu\.be\/|watch\?v=)([\w-]+)", url)
    if found:
        return found.group(1)
    return None

def get_video_transcript(video_id: str) -> str | None:
    """
    Fetch the transcript of the provided YouTube video
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['de', 'en'])
    except TranscriptsDisabled:
        # The video doesn't have a transcript
        return None

    text = " ".join([line["text"] for line in transcript])
    return text

def create_download_link(pdf_content):
    b64 = base64.b64encode(pdf_content).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="transcription.pdf">Download PDF</a>'

def generate_questions_answers(transcription):
    # Berechne die Anzahl der Wörter im Transkript
    num_words = len(transcription.split())
    
    # Bestimme die Anzahl der Fragen (z.B. 1 Frage pro 100 Wörter, mindestens 1 Frage)
    num_questions = max(1, num_words // 100)
    if num_questions < 3:
        num_questions = 3
    if num_questions > 10:
        num_questions = 10
    print(f"Anzahl der Wörter: {num_words}")
    
    prompt = f"""Du bist ein Professor welche inhaltliche fragen zu folgenden stellt. Hier erhältst du das Transcript einer Vorlesung, generiere {num_questions} Fragen, die testen, dass der Zuhörer aufgepasst hast auf Deutsch. Die Fragen sollen sich ausschließlich auf den Inhalt des Transscripts beziehen und sollten innerhalb des vortrags beantwortet werden können, die antworten ebenso: {transcription} Frage und Antwort sollten mindestens 10 Wörter lang sein

Antworte nur mit einem JSON-Objekt im folgenden Format:
{{
    "fragen": [
        {{"frage": "Frage 1", "antwort": "Antwort 1"}},
        ...
        {{"frage": "Frage {num_questions}", "antwort": "Antwort {num_questions}"}}
    ]
}}
"""
    answer_received = False
    #Since we're sending other requests as well, wait in case token limit per minute is reached
    while answer_received == False:
        try:
            chat_completion = client.chat.completions.create(
                model="llama3-groq-70b-8192-tool-use-preview",
                messages=[
                    {"role": "system", "content": "Du bist ein hilfreicher Assistent, der Fragen und Antworten zu einem gegebenen Transkript generiert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=500
            )
            answer_received = True
        except:
            print("Waiting for token limit to cool down")
            time.sleep(15)

    return chat_completion.choices[0].message.content

def format_transcription_markdown(transcription_text):
    prompt = f"""Format the following transcription in nicely formatted markdown, including appropriate headings. Keep the content in German:

{transcription_text}
"""

    chat_completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "Du formatierst Texte in schönem Markdown."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    return chat_completion.choices[0].message.content


st.set_page_config(page_title='Study Quiz', page_icon='logo.jpeg')

# Set page title
st.title('Study Quiz')

if not GROQ_API_KEY:
    with st.sidebar:
        groq_api_key = st.text_input("Enter your Groq API Key (gsk_yA...):", "", type="password")
        st.markdown("*Get your free API key at [console.groq.com/keys](https://console.groq.com/keys)*")
        # Initialize the Groq client
        client = Groq(api_key=groq_api_key)
else:
    # Initialize the Groq client
    client = Groq(api_key=GROQ_API_KEY)
    
# Create a toggle for recording
col1, col2 = st.columns([1, 3])

with col1:
    recording_state = st.toggle("Start/Stop Aufnahme")

with col2:
    youtube_url = st.text_input("YouTube Video URL")

uploaded_file = st.file_uploader("Choose a file")

# Rest of your existing recording logic
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = []
    
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False

if recording_state != st.session_state.is_recording:
    st.session_state.is_recording = recording_state
    
    if st.session_state.is_recording:
        st.session_state.audio_data = []
        
        # Start recording in the background
        recording = sd.InputStream(samplerate=sample_rate, channels=channels)
        with recording as stream:
            processing = False
            while st.session_state.is_recording:
                data, overflowed = stream.read(1024)
                st.session_state.audio_data.append(data)
                if overflowed:
                    st.warning("Buffer overflow occurred, some audio may be lost.")
                time.sleep(0.01)  # Small delay to prevent UI freeze
    else:
        if len(st.session_state.audio_data) > 0:
            # Combine the audio data into a single numpy array
            audio_data = np.concatenate(st.session_state.audio_data, axis=0)
            # Save as WAV file
            write(output_filename, sample_rate, audio_data)
if st.button("Fragen und Transkript generieren"):
    processing = True
    st.session_state.processing = True 
    text = ""
    if youtube_url == "":
        with st.spinner('Analysiere Audio...'):
            try:
                # Specify the path to the audio file
                filename = os.path.dirname(__file__) + "/audio.wav"
                print("Analysiere Audio...")

                # Check file size
                file_size_mb = os.path.getsize(filename) / (1024 * 1024)
                
                # If file is larger than 25MB, convert to MP3
                if file_size_mb > 25:
                    print("Konvertiere große WAV Datei zu MP3...")
                    audio = AudioSegment.from_wav(filename)
                    mp3_filename = filename.replace('.wav', '.mp3')
                    audio.export("audio.mp3", format="mp3", bitrate="128k")
                    process_filename = mp3_filename
                    print("Audio konvertiert")
                else:
                    process_filename = filename

                # Open the audio file
                with open(process_filename, "rb") as file:
                    # Create a transcription
                    transcription = client.audio.transcriptions.create(
                        file=(process_filename, file.read()),
                        model="whisper-large-v3-turbo",
                        language="de",
                        temperature=0.0
                    )
                    
                    # Print the transcription text
                    print(transcription.text)
                    text = transcription.text

                # Clean up temporary MP3 if it was created
                #if file_size_mb > 25:
                #    os.remove(mp3_filename)
            except Exception as e:
                print(e)
                st.error("Fehler beim Analysieren der Audio-Datei. Bitte versuchen Sie es erneut.")
    else:
        with st.spinner('Analysiere YouTube Video...'):
            video_id = extract_youtube_video_id(youtube_url)
            text = get_video_transcript(video_id)
    if uploaded_file is not None:
        with st.spinner('Analysiere Hochgeladene Datei...'):
            pdf_description = " \n **Folgende Zusammenfassung wurde aus der hochgeladenen Datei generiert:** \n "
            pdf_description += description.describe_file(uploaded_file)
            text = text + pdf_description

    if len(text) < 50:
        st.error("Transkript ist zu kurz, um Fragen generieren zu können.")    
    else:
        with st.spinner('Generiere Fragen...'):
            result = generate_questions_answers(text)
            
            try:
                # Parsen der JSON-Antwort
                qa_data = json.loads(result)
                
                st.subheader("Fragen")
                # Anzeigen der Fragen und Antworten
                for qa in qa_data["fragen"]:
                    st.write(qa["frage"])
                    with st.expander("Antwort anzeigen"):
                        st.write(qa["antwort"])
                    st.write("---")
            except json.JSONDecodeError:
                st.error("Fehler beim Parsen der Antwort. Bitte versuchen Sie es erneut.")
            print(result)
            
                    
    with st.spinner('Formatiere Transkript...'):
        formatted_transcription = format_transcription_markdown(text)
        st.header("Transcript")
        st.markdown(
            f"""
            <div style="height:300px; overflow: auto; border-radius:10px; border:1px solid #ccc; padding:10px; margin-bottom:10px;">
                {text}
            </div>
            """,
            unsafe_allow_html=True
        )

        if formatted_transcription:
                        # Create a temporary markdown file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp_md_file:
                temp_md_file.write(formatted_transcription.encode('utf-8'))
                markdown_file = temp_md_file.name
            
            # Convert markdown to PDF
            document = Document()
            document.LoadFromFile(markdown_file)
            
            output_pdf = 'ToPdf.pdf'
            document.SaveToFile(output_pdf, FileFormat.PDF)
            document.Dispose()
            
            # Read PDF file
            with open(output_pdf, 'rb') as f:
                pdf_data = f.read()
            os.remove(output_pdf)
            st.download_button(
                label='Download PDF',
                data=pdf_data,
                file_name='transcription.pdf',
                mime='application/pdf'
            )
