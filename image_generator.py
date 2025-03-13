# import os
# import vertexai
# from vertexai.preview.vision_models import ImageGenerationModel
# from config import GOOGLE_APPLICATION_CREDENTIALS, PROJECT_ID, LOCATION, IMAGES_DIR

# # Initialize Vertex AI
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
# vertexai.init(project=PROJECT_ID, location=LOCATION)
# image_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")


# def generate_image(img_prompt, filename=None):
#     """
#     Generate an image from the img_prompt using Vertex AI.

#     Args:
#         img_prompt (str): The text to generate an image from
#         filename (str, optional): Filename to save the image. If None, a timestamp will be used.

#     Returns:
#         dict: A dictionary containing image bytes and file path
#     """
#     results = {}
#     print(f"Generating image from: {img_prompt}")

#     try:
#         # Generate images from Vertex AI
#         response = image_model.generate_images(
#             prompt=img_prompt,
#             number_of_images=1,
#             language="en",
#             aspect_ratio="1:1",
#             safety_filter_level="block_some",
#             person_generation="allow_adult",
#         )

#         generated_image = response.images[0]
#         image_bytes = generated_image._image_bytes
#         results["image"] = image_bytes

#         # Save the generated image
#         os.makedirs(IMAGES_DIR, exist_ok=True)

#         # Use provided filename or a timestamp
#         if not filename:
#             import time
#             filename = str(int(time.time()))

#         image_filepath = os.path.join(IMAGES_DIR, f"{filename}.png")
#         with open(image_filepath, "wb") as f:
#             f.write(image_bytes)
#         results["image_path"] = image_filepath

#     except Exception as e:
#         results["error"] = str(e)
#         print(f"❌ Image generation failed: {e}")

#     return results


import os
import time
import logging
import ssl
import grpc
from google.api_core.exceptions import GoogleAPIError, RetryError, ServiceUnavailable
from vertexai.preview.vision_models import ImageGenerationModel
from config import GOOGLE_APPLICATION_CREDENTIALS, PROJECT_ID, LOCATION, IMAGES_DIR

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('image_generator')


def generate_image(img_prompt, filename=None, max_retries=1, retry_delay=2):
    """
    Generate an image from the img_prompt using Vertex AI with enhanced error handling.

    Args:
        img_prompt (str): The text to generate an image from
        filename (str, optional): Filename to save the image. If None, a timestamp will be used.
        max_retries (int): Maximum number of retry attempts for transient errors
        retry_delay (int): Seconds to wait between retry attempts

    Returns:
        dict: A dictionary containing image bytes and file path or error details
    """
    results = {}
    logger.info(f"Generating image from prompt: {img_prompt[:100]}...")

    # Use provided filename or a timestamp
    if not filename:
        filename = str(int(time.time()))

    # Ensure the images directory exists
    os.makedirs(IMAGES_DIR, exist_ok=True)
    image_filepath = os.path.join(IMAGES_DIR, f"{filename}.png")

    # Set environment variable for authentication
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    for attempt in range(max_retries):
        try:
            # Initialize Vertex AI for this attempt
            from vertexai import init
            init(project=PROJECT_ID, location=LOCATION)

            # Create a fresh model instance for each attempt
            image_model = ImageGenerationModel.from_pretrained(
                "imagen-3.0-generate-002")

            # Generate images from Vertex AI
            response = image_model.generate_images(
                prompt=img_prompt,
                number_of_images=1,
                language="en",
                aspect_ratio="1:1",
                safety_filter_level="block_some",
                person_generation="allow_adult",
            )

            if not response or not response.images:
                raise ValueError("Received empty response from Vertex AI")

            generated_image = response.images[0]
            image_bytes = generated_image._image_bytes

            if not image_bytes:
                raise ValueError("Received empty image bytes from Vertex AI")

            results["image"] = image_bytes

            # Save the generated image
            with open(image_filepath, "wb") as f:
                f.write(image_bytes)

            results["image_path"] = image_filepath
            logger.info(
                f"✅ Image successfully generated and saved to {image_filepath}")

            # Success, exit retry loop
            break

        except ssl.SSLError as e:
            error_msg = f"SSL error during image generation (attempt {attempt+1}/{max_retries}): {str(e)}"
            logger.error(error_msg)
            results["error"] = error_msg
            results["error_type"] = "ssl_error"

            # SSL errors might be temporary, worth retrying
            time.sleep(retry_delay)

        except (grpc.RpcError, ConnectionError, ServiceUnavailable) as e:
            error_msg = f"Network/connection error (attempt {attempt+1}/{max_retries}): {str(e)}"
            logger.error(error_msg)
            results["error"] = error_msg
            results["error_type"] = "network_error"

            # Network errors are good candidates for retry
            time.sleep(retry_delay)

        except GoogleAPIError as e:
            error_msg = f"Google API error (attempt {attempt+1}/{max_retries}): {str(e)}"
            logger.error(error_msg)
            results["error"] = error_msg
            results["error_type"] = "api_error"

            # Some API errors are transient and worth retrying
            time.sleep(retry_delay)

        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f"Unexpected error during image generation: {str(e)}"
            logger.error(error_msg)
            results["error"] = error_msg
            results["error_type"] = "unexpected_error"

            # For unexpected errors, we might not want to retry
            # but we'll give it one more chance with a longer delay
            if attempt < max_retries - 1:
                time.sleep(retry_delay * 2)
            else:
                break

    # Check if we succeeded after all retries
    if "image_path" not in results:
        logger.error(f"❌ Image generation failed after {max_retries} attempts")
        if "error" not in results:
            results["error"] = f"Failed to generate image after {max_retries} attempts with no specific error"

    return results
