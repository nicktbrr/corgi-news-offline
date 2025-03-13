import base64
import time


def generate_timestamp_filename():
    """
    Generate a filename based on the current timestamp.

    Returns:
        str: A string representation of the current timestamp
    """
    return str(int(time.time()))


def encode_to_base64(file_path):
    """
    Read a file and encode its contents to base64.

    Args:
        file_path (str): Path to the file to encode

    Returns:
        str: Base64-encoded string of the file contents
    """
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        return base64.b64encode(file_bytes).decode('utf-8')
    except Exception as e:
        print(f"Error encoding file to base64: {e}")
        return None
