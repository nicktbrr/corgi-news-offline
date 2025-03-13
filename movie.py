from moviepy import *
import numpy as np
import os
import logging
import sys
from parse import parse_textgrid

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('movie_generator')

# YouTube Shorts resolution
SHORTS_WIDTH, SHORTS_HEIGHT = 1080, 1920
PADDING = 50  # Padding for summary image


def create_shorts_video(process_folder, output_path=None):
    """
    Create a YouTube Shorts style video using assets from a processed article.

    Args:
        process_folder (str): Path to the folder containing processed article assets
        output_path (str, optional): Path where the output video should be saved
                                     If None, saves to process_folder/output_shorts.mp4

    Returns:
        str: Path to the created video file or None if creation failed
    """
    try:
        # Ensure process folder exists
        if not os.path.exists(process_folder):
            logger.error(f"Process folder not found: {process_folder}")
            return None

        # Set up paths based on the structure
        alignment_folder = os.path.join(process_folder, "alignment")

        # Set output path if not provided
        if output_path is None:
            output_path = os.path.join(process_folder, "output_shorts.mp4")

        # Set FFmpeg path for the current environment
        if sys.platform == "darwin":  # macOS
            os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/anaconda3/envs/mana/bin/ffmpeg"
            os.environ["IMAGEMAGICK_BINARY"] = "/opt/homebrew/bin/magick"

        # Find TextGrid file in alignment folder
        textgrid_files = [f for f in os.listdir(
            alignment_folder) if f.endswith('.TextGrid')]
        if not textgrid_files:
            logger.error(f"No TextGrid files found in {alignment_folder}")
            return None

        textgrid_path = os.path.join(alignment_folder, textgrid_files[0])

        # Parse TextGrid to get captions
        captions = parse_textgrid(textgrid_path)
        if not captions:
            logger.error("Failed to extract captions from TextGrid")
            return None

        logger.info(f"Extracted {len(captions)} captions for video")

        # Find audio file in process folder
        audio_files = [f for f in os.listdir(
            process_folder) if f.endswith('.wav') or f.endswith('.mp3')]
        if not audio_files:
            logger.error(f"No audio files found in {process_folder}")
            return None

        audio_path = os.path.join(process_folder, audio_files[0])

        # Find image file in process folder
        image_files = [f for f in os.listdir(
            process_folder) if f.endswith('.png') or f.endswith('.jpg')]
        if not image_files:
            logger.error(f"No image files found in {process_folder}")
            return None

        image_path = os.path.join(process_folder, image_files[0])

        # Path to corgi GIF in assets folder
        corgi_path = "./assets/corgi.gif"
        if not os.path.exists(corgi_path):
            logger.error(f"Corgi GIF not found at {corgi_path}")
            return None

        # Maximum duration based on last caption end time
        # Default 10 seconds if no captions
        MAX_DURATION = captions[-1][1] if captions else 10

        logger.info(
            f"Creating video with duration: {MAX_DURATION:.2f} seconds")

        # Create a background with YouTube Shorts resolution
        background = ColorClip(size=(SHORTS_WIDTH, SHORTS_HEIGHT),
                               color=(10, 6, 47), duration=MAX_DURATION)

        # Load and prepare the corgi GIF
        video = VideoFileClip(corgi_path, has_mask=True)

        # Loop the gif for the full duration
        looped_video = video.with_effects([vfx.Loop(duration=MAX_DURATION)])

        # Animation parameters
        initial_height = 100  # Start small
        final_height = 700    # Target size

        # # Get original aspect ratio
        aspect_ratio = video.w / video.h

        # # Define scaling function for smooth animation
        def scale_func(t):
            if t > 0.3:
                # Exact target size
                return (final_height * aspect_ratio, final_height)
            else:
                scale_factor = (t / 0.3)  # Linear scaling
                height = int(initial_height + scale_factor *
                             (final_height - initial_height))
                return (int(height * aspect_ratio), height)

        # Apply scaling and position

        gif_resized = looped_video.with_position(
            ("center", "bottom")).resized(scale_func)

        # # Load and prepare the trend image
        trend_img = ImageClip(image_path, duration=MAX_DURATION).resized(
            width=SHORTS_WIDTH - 2 * PADDING, height=SHORTS_HEIGHT // 2)
        trend_img = trend_img.with_position(
            ("center", 350))

        # # Load audio
        audio = AudioFileClip(audio_path).with_duration(MAX_DURATION)

        # Choose a font
        font_path = None
        if sys.platform == "darwin":  # macOS
            font_path = "/System/Library/Fonts/Supplemental/Impact.ttf"
        # Add Windows and Linux paths if needed

        if not font_path or not os.path.exists(font_path):
            logger.warning("Impact font not found, using default")
            font_path = None

        # Position for captions (above the trend image)
        trend_img_height = SHORTS_HEIGHT // 3
        subtitle_y_position = (SHORTS_HEIGHT // 2) - \
            (trend_img_height // 2) - 500

        # Generate text clips for captions
        subtitle_clips = []
        for start, end, text in captions:
            try:
                clip = TextClip(text=text, font_size=100, color="white", font=font_path,
                                stroke_width=3, stroke_color="black")
                clip = clip.with_position(("center", subtitle_y_position))
                clip = clip.with_start(start).with_end(end)
                subtitle_clips.append(clip)
            except Exception as e:
                logger.warning(
                    f"Error creating subtitle for '{text}': {str(e)}")

        clips_to_compose = [background, trend_img, gif_resized]
        clips_to_compose.extend(subtitle_clips)

        # Create composite with explicit duration
        final_video = CompositeVideoClip(
            clips_to_compose, size=(SHORTS_WIDTH, SHORTS_HEIGHT))
        final_video.audio = CompositeAudioClip([audio])

        # # Save the final video
        logger.info(f"Writing video to {output_path}")
        # final_video.write_videofile(
        #     output_path, codec="libx264", fps=24, audio_codec="aac", bitrate="5000k", verbose=False,)

        final_video.preview()

        # Clean up resources
        video.close()
        final_video.close()
        audio.close()

        logger.info(f"Video creation complete: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error creating shorts video: {str(e)}")
        return None


def main():
    """
    Main function with hard-coded input directory and output path.
    """
    # Hard-coded input directory
    input_folder = "transcribed/1741894201"

    # Hard-coded output path
    output_path = "output_videos/shorts_video.mp4"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    result = create_shorts_video(input_folder, output_path)

    if result:
        print(f"✅ Video created successfully: {result}")
        return 0
    else:
        print("❌ Video creation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
