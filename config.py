import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Credentials
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "YOUR_ELEVENLABS_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/Users/nick/Desktop/insta-brainrot/corgi-news-c63371833ca9.json"
)
GEMINI_KEY = os.environ.get('GEMINI_KEY')
NVIDIA_KEY = os.environ.get('NVIDIA_KEY')

# Project Configuration
PROJECT_ID = 'corgi-news'
LOCATION = 'us-central1'

# Directories
TRANSCRIPTION_DIR = "process_transcription"
IMAGES_DIR = "images"
ALIGNMENT_OUTPUT_DIR = "alignment_output"

# Model Configuration
ELEVEN_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
ELEVEN_MODEL_ID = "eleven_multilingual_v2"

# MFA Configuration
MFA_CONDA_ENV = "aligner"
MFA_DICTIONARY = "english_us_arpa"
MFA_ACOUSTIC_MODEL = "english_us_arpa"
