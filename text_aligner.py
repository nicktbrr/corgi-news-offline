import subprocess
import os
import logging
from config import MFA_DICTIONARY, MFA_ACOUSTIC_MODEL, ALIGNMENT_OUTPUT_DIR

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('text_aligner')


def align_text_mfa(input_path):
    """
    Aligns the transcript with the audio using Montreal Forced Aligner (MFA)
    directly calling the command without switching conda environments.

    Args:
        input_path (str): Path to the directory containing text and audio files

    Returns:
        bool: True if alignment succeeded, False otherwise
    """
    # Ensure output directory exists
    os.makedirs(ALIGNMENT_OUTPUT_DIR, exist_ok=True)

    try:
        # Direct MFA command without conda run
        command = [
            "mfa", "align",
            "--clean",
            "--verbose",
            input_path,
            MFA_DICTIONARY,
            MFA_ACOUSTIC_MODEL,
            ALIGNMENT_OUTPUT_DIR
        ]

        logger.info(
            f"Starting MFA alignment with command: {' '.join(command)}")

        # Run the command and capture output
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )

        # Log the output for debugging
        logger.info(f"MFA alignment stdout: {result.stdout}")

        if result.stderr:
            logger.warning(f"MFA alignment stderr: {result.stderr}")

        logger.info(
            f"✅ Alignment results successfully saved in {ALIGNMENT_OUTPUT_DIR}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during MFA alignment process: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error(
            "MFA command not found. Make sure MFA is installed and in your PATH")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during MFA alignment: {str(e)}")
        return False
