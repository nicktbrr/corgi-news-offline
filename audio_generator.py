import os
import subprocess
from elevenlabs import ElevenLabs
from config import ELEVENLABS_API_KEY, ELEVEN_VOICE_ID, ELEVEN_MODEL_ID, TRANSCRIPTION_DIR

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)


def generate_audio(summary, filename=None):
    """
    Generate audio from text using ElevenLabs.

    Args:
        summary (str): The text to convert to speech
        filename (str, optional): Filename to save the audio. If None, a timestamp will be used.

    Returns:
        dict: A dictionary containing audio bytes and file paths
    """
    results = {}

    try:
        # Generate audio using ElevenLabs
        response = elevenlabs_client.text_to_speech.convert(
            voice_id=ELEVEN_VOICE_ID,
            output_format="mp3_44100_128",
            text=summary,
            model_id=ELEVEN_MODEL_ID,
        )
        audio_bytes = b"".join(response)
        results["audio"] = audio_bytes

        # Save the summary text and audio file
        os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

        # Use provided filename or a timestamp
        if not filename:
            import time
            filename = str(int(time.time()))

        # Save text
        text_filepath = os.path.join(TRANSCRIPTION_DIR, f"{filename}.txt")
        with open(text_filepath, "w") as f:
            f.write(summary)
        results["text_path"] = text_filepath

        # Save MP3
        mp3_filepath = os.path.join(TRANSCRIPTION_DIR, f"{filename}.mp3")
        with open(mp3_filepath, "wb") as f:
            f.write(audio_bytes)
        results["mp3_path"] = mp3_filepath

        # Convert to WAV
        wav_filepath = os.path.join(TRANSCRIPTION_DIR, f"{filename}.wav")
        subprocess.run([
            "ffmpeg", "-y", "-i", mp3_filepath,
            "-ar", "16000",  # Set sample rate to 16 kHz
            "-ac", "1",      # Convert to mono
            "-acodec", "pcm_s16le",  # Ensure PCM 16-bit encoding
            wav_filepath
        ], check=True)
        results["wav_path"] = wav_filepath

        # Optionally remove the MP3 file
        # os.remove(mp3_filepath)

    except Exception as e:
        results["error"] = str(e)
        print(f"Error generating audio: {e}")

    return results
