# import threading
# import os
# import shutil
# import logging
# from text_generator import TextGenerator
# from audio_generator import generate_audio
# from image_generator import generate_image
# from text_aligner import align_text_mfa
# from utils import generate_timestamp_filename, encode_to_base64
# from config import TRANSCRIPTION_DIR

# # Set up logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger('article_processor')


# def process_article(article_text):
#     """
#     Process an article by generating a summary, audio, and image.
#     Then align the text with the audio and move processed files to archive.

#     Args:
#         article_text (str): The full article text to process

#     Returns:
#         dict: A dictionary containing the processing results
#     """
#     # Generate a unique filename for this processing run
#     filename = generate_timestamp_filename()

#     # Create transcribed directory if it doesn't exist
#     transcribed_dir = "transcribed"
#     os.makedirs(transcribed_dir, exist_ok=True)

#     logger.info(f"Starting article processing with filename: {filename}")

#     # Create text generator instance
#     text_generator = TextGenerator()

#     # Generate content (summary and picture ideas)
#     generation_result = text_generator.generate_content(article_text)
#     summary = generation_result.summary
#     picture_ideas = generation_result.picture_ideas

#     if not summary:
#         logger.error("Summary generation failed")
#         return {"error": "Summary generation failed"}

#     # Dictionary to store results from both threads
#     results = {
#         "summary": summary,
#         "picture_ideas": [idea.description for idea in picture_ideas]
#     }

#     # Process audio and image generation concurrently
#     threads = []

#     audio_thread = threading.Thread(
#         target=lambda: results.update(
#             {"audio_results": generate_audio(summary, filename)})
#     )

#     # Use the first picture idea for image generation if available
#     image_prompt = picture_ideas[0].description if picture_ideas else summary

#     image_thread = threading.Thread(
#         target=lambda: results.update(
#             {"image_results": generate_image(image_prompt, filename)})
#     )

#     threads.append(audio_thread)
#     threads.append(image_thread)

#     # Start all threads
#     for thread in threads:
#         thread.start()

#     # Wait for all threads to complete
#     for thread in threads:
#         thread.join()

#     # Check for errors
#     if "error" in results.get("audio_results", {}) or "error" in results.get("image_results", {}):
#         results["status"] = "partial_success"
#         logger.warning("Some components failed during processing")
#     else:
#         results["status"] = "success"
#         logger.info("All components processed successfully")

#     # Run MFA alignment
#     logger.info("Starting text-audio alignment with MFA")
#     alignment_success = align_text_mfa(input_path=TRANSCRIPTION_DIR)
#     results["alignment_success"] = alignment_success

#     # Move contents from transcription directory to transcribed directory
#     if os.path.exists(TRANSCRIPTION_DIR) and os.path.isdir(TRANSCRIPTION_DIR):
#         try:
#             # Create a subdirectory with the filename to keep files organized
#             destination_dir = os.path.join(transcribed_dir, filename)
#             os.makedirs(destination_dir, exist_ok=True)

#             # Get list of files in the transcription directory
#             files = os.listdir(TRANSCRIPTION_DIR)

#             if files:
#                 logger.info(
#                     f"Moving {len(files)} files from {TRANSCRIPTION_DIR} to {destination_dir}")

#                 for file in files:
#                     source_path = os.path.join(TRANSCRIPTION_DIR, file)
#                     destination_path = os.path.join(destination_dir, file)

#                     # Move the file (shutil.move handles both files and directories)
#                     shutil.move(source_path, destination_path)

#                 logger.info(
#                     f"Successfully moved all files to {destination_dir}")
#             else:
#                 logger.warning(
#                     f"No files found in {TRANSCRIPTION_DIR} to move")

#         except Exception as e:
#             logger.error(
#                 f"Error moving files from {TRANSCRIPTION_DIR} to {transcribed_dir}: {str(e)}")
#             results["file_movement_error"] = str(e)
#     else:
#         logger.warning(
#             f"{TRANSCRIPTION_DIR} directory does not exist or is not a directory")

#     # Add base64 encoded data if needed
#     if "wav_path" in results.get("audio_results", {}):
#         results["audio_base64"] = encode_to_base64(
#             results["audio_results"]["wav_path"])

#     if "image_path" in results.get("image_results", {}):
#         results["image_base64"] = encode_to_base64(
#             results["image_results"]["image_path"])

#     results["filename"] = filename
#     results["transcribed_dir"] = os.path.join(transcribed_dir, filename)

#     logger.info(
#         f"Article processing complete with status: {results['status']}")
#     return results


# # Example usage
# if __name__ == "__main__":
#     sample_article = """
#     In a groundbreaking development, researchers have discovered a new method for sustainable energy production.
#     The technique, which combines solar power with advanced battery technology, could revolutionize how we power our homes and businesses.
#     Initial tests show a 40% increase in efficiency compared to traditional solar panels.
#     Dr. Jane Smith, lead researcher on the project, stated that this could be a game-changer for renewable energy.
#     The team plans to begin commercial testing next year.
#     """

#     results = process_article(sample_article)
#     print(f"Processing complete with status: {results['status']}")
#     print(f"Summary: {results['summary']}")

#     if "audio_results" in results:
#         print(f"Audio saved to: {results['audio_results'].get('wav_path')}")

#     if "image_results" in results:
#         print(f"Image saved to: {results['image_results'].get('image_path')}")

#     if "transcribed_dir" in results:
#         print(f"Processed files moved to: {results['transcribed_dir']}")

import threading
import os
import shutil
import logging
from text_generator import TextGenerator
from audio_generator import generate_audio
from image_generator import generate_image
from text_aligner import align_text_mfa
from utils import generate_timestamp_filename, encode_to_base64
from config import TRANSCRIPTION_DIR, ALIGNMENT_OUTPUT_DIR, IMAGES_DIR

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('article_processor')


def process_article(article_text):
    """
    Process an article by generating a summary, audio, and image.
    Then align the text with the audio and move all processed files to archive.

    Args:
        article_text (str): The full article text to process

    Returns:
        dict: A dictionary containing the processing results
    """
    # Generate a unique filename for this processing run
    filename = generate_timestamp_filename()

    # Create transcribed directory if it doesn't exist
    transcribed_dir = "transcribed"
    os.makedirs(transcribed_dir, exist_ok=True)

    logger.info(f"Starting article processing with filename: {filename}")

    # Create text generator instance
    text_generator = TextGenerator()

    # Generate content (summary and picture ideas)
    generation_result = text_generator.generate_content(article_text)
    summary = generation_result.summary
    picture_ideas = generation_result.picture_ideas

    if not summary:
        logger.error("Summary generation failed")
        return {"error": "Summary generation failed"}

    # Dictionary to store results from both threads
    results = {
        "summary": summary,
        "picture_ideas": [idea.description for idea in picture_ideas]
    }

    # Process audio and image generation concurrently
    threads = []

    audio_thread = threading.Thread(
        target=lambda: results.update(
            {"audio_results": generate_audio(summary, filename)})
    )

    # Use the first picture idea for image generation if available
    image_prompt = picture_ideas[0].description if picture_ideas else summary

    image_thread = threading.Thread(
        target=lambda: results.update(
            {"image_results": generate_image(image_prompt, filename)})
    )

    threads.append(audio_thread)
    threads.append(image_thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check for errors
    if "error" in results.get("audio_results", {}) or "error" in results.get("image_results", {}):
        results["status"] = "partial_success"
        logger.warning("Some components failed during processing")
    else:
        results["status"] = "success"
        logger.info("All components processed successfully")

    # Run MFA alignment
    logger.info("Starting text-audio alignment with MFA")
    alignment_success = align_text_mfa(input_path=TRANSCRIPTION_DIR)
    results["alignment_success"] = alignment_success

    # Create a subdirectory with the filename to keep files organized
    destination_dir = os.path.join(transcribed_dir, filename)
    os.makedirs(destination_dir, exist_ok=True)

    # Dictionary to track moved files
    moved_files = {
        "transcription": [],
        "alignment": [],
        "image": []
    }

    # 1. Move contents from transcription directory
    if os.path.exists(TRANSCRIPTION_DIR) and os.path.isdir(TRANSCRIPTION_DIR):
        try:
            # Get list of files in the transcription directory
            files = os.listdir(TRANSCRIPTION_DIR)

            if files:
                logger.info(
                    f"Moving {len(files)} files from {TRANSCRIPTION_DIR} to {destination_dir}")

                for file in files:
                    source_path = os.path.join(TRANSCRIPTION_DIR, file)
                    destination_path = os.path.join(destination_dir, file)

                    # Move the file (shutil.move handles both files and directories)
                    shutil.move(source_path, destination_path)
                    moved_files["transcription"].append(file)

                logger.info(
                    f"Successfully moved all transcription files to {destination_dir}")
            else:
                logger.warning(
                    f"No files found in {TRANSCRIPTION_DIR} to move")

        except Exception as e:
            logger.error(
                f"Error moving files from {TRANSCRIPTION_DIR} to {destination_dir}: {str(e)}")
            results["file_movement_error_transcription"] = str(e)

    # 2. Move alignment output
    if os.path.exists(ALIGNMENT_OUTPUT_DIR) and os.path.isdir(ALIGNMENT_OUTPUT_DIR):
        try:
            # Create an alignment subdirectory
            alignment_dest_dir = os.path.join(destination_dir, "alignment")
            os.makedirs(alignment_dest_dir, exist_ok=True)

            # Get list of files in the alignment directory
            files = os.listdir(ALIGNMENT_OUTPUT_DIR)

            if files:
                logger.info(
                    f"Moving {len(files)} files from {ALIGNMENT_OUTPUT_DIR} to {alignment_dest_dir}")

                for file in files:
                    source_path = os.path.join(ALIGNMENT_OUTPUT_DIR, file)
                    destination_path = os.path.join(alignment_dest_dir, file)

                    # Move the file
                    shutil.move(source_path, destination_path)
                    moved_files["alignment"].append(file)

                logger.info(
                    f"Successfully moved all alignment files to {alignment_dest_dir}")
            else:
                logger.warning(
                    f"No files found in {ALIGNMENT_OUTPUT_DIR} to move")

        except Exception as e:
            logger.error(
                f"Error moving files from {ALIGNMENT_OUTPUT_DIR} to {alignment_dest_dir}: {str(e)}")
            results["file_movement_error_alignment"] = str(e)

    # 3. Move the generated image if it exists
    if "image_path" in results.get("image_results", {}):
        try:
            image_path = results["image_results"]["image_path"]
            if os.path.exists(image_path):
                image_filename = os.path.basename(image_path)
                destination_path = os.path.join(
                    destination_dir, image_filename)

                # Move the image file
                # Using copy2 to preserve metadata
                shutil.copy2(image_path, destination_path)

                # Update the image path in results to point to the new location
                results["image_results"]["original_image_path"] = image_path
                results["image_results"]["image_path"] = destination_path
                moved_files["image"].append(image_filename)

                logger.info(f"Successfully copied image to {destination_path}")
            else:
                logger.warning(f"Image file not found at {image_path}")
        except Exception as e:
            logger.error(f"Error moving image file: {str(e)}")
            results["file_movement_error_image"] = str(e)

    # Add base64 encoded data if needed
    if "wav_path" in results.get("audio_results", {}):
        results["audio_base64"] = encode_to_base64(
            results["audio_results"]["wav_path"])

    if "image_path" in results.get("image_results", {}):
        results["image_base64"] = encode_to_base64(
            results["image_results"]["image_path"])

    results["filename"] = filename
    results["transcribed_dir"] = destination_dir
    results["moved_files"] = moved_files

    logger.info(
        f"Article processing complete with status: {results['status']}")
    return results


# Example usage
if __name__ == "__main__":
    sample_article = """
    In a groundbreaking development, researchers have discovered a new method for sustainable energy production.
    The technique, which combines solar power with advanced battery technology, could revolutionize how we power our homes and businesses.
    Initial tests show a 40% increase in efficiency compared to traditional solar panels.
    Dr. Jane Smith, lead researcher on the project, stated that this could be a game-changer for renewable energy.
    The team plans to begin commercial testing next year.
    """

    results = process_article(sample_article)
    print(f"Processing complete with status: {results['status']}")
    print(f"Summary: {results['summary']}")

    if "audio_results" in results:
        print(f"Audio saved to: {results['audio_results'].get('wav_path')}")

    if "image_results" in results:
        print(f"Image saved to: {results['image_results'].get('image_path')}")

    if "transcribed_dir" in results:
        print(f"Processed files moved to: {results['transcribed_dir']}")

    if "moved_files" in results:
        print(f"Files moved summary:")
        print(
            f"  - Transcription files: {len(results['moved_files']['transcription'])}")
        print(
            f"  - Alignment files: {len(results['moved_files']['alignment'])}")
        print(f"  - Image files: {len(results['moved_files']['image'])}")
