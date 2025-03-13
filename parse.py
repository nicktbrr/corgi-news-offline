import re
import pandas as pd
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('textgrid_parser')


def parse_textgrid(textgrid_path):
    """
    Parse a TextGrid file to extract word alignments.

    Args:
        textgrid_path (str): Path to the TextGrid file

    Returns:
        list: List of caption tuples (start_time, end_time, text)
    """
    try:
        logger.info(f"Parsing TextGrid file: {textgrid_path}")

        # Check if file exists
        if not os.path.exists(textgrid_path):
            logger.error(f"TextGrid file not found at {textgrid_path}")
            return []

        # Read the TextGrid content from a file
        with open(textgrid_path, "r", encoding="utf-8") as file:
            textgrid_content = file.read()

        # Regular expression to extract only the "words" tier and stop reading at "phones" tier
        pattern_words = re.compile(
            r"item \[1\]:\s*class = \"IntervalTier\"\s*name = \"words\"(.*?)item \[2\]:",
            re.DOTALL
        )

        # Extract only the relevant section of the "words" tier
        match_words = pattern_words.search(textgrid_content)
        if match_words:
            words_section = match_words.group(1)
        else:
            logger.warning("Could not find 'words' tier in TextGrid file")
            return []

        # Regular expression pattern to extract xmin, xmax, and text from "words" tier
        pattern_intervals = re.compile(
            r"intervals \[\d+\]:\s*"
            r"xmin = ([\d\.]+)\s*"
            r"xmax = ([\d\.]+)\s*"
            r'text = "(.*?)"',
            re.DOTALL
        )

        # Extract matches from the words section
        matches = pattern_intervals.findall(words_section)

        # Convert to DataFrame
        df_parsed = pd.DataFrame(matches, columns=["start", "stop", "text"])

        # Convert start and stop to float
        df_parsed["start"] = df_parsed["start"].astype(float)
        df_parsed["stop"] = df_parsed["stop"].astype(float)

        # Remove empty text entries
        df_parsed = df_parsed[df_parsed["text"].str.strip() != ""]

        # Convert to list of tuples for captions format
        captions = list(df_parsed.itertuples(index=False, name=None))

        logger.info(f"Successfully parsed {len(captions)} captions")
        return captions

    except Exception as e:
        logger.error(f"Error parsing TextGrid file: {str(e)}")
        return []


# For direct testing
# if __name__ == "__main__":
#     # Example path for testing
#     test_path = "transcribed/1741894201/alignment/1741894201.TextGrid"
#     captions = parse_textgrid(test_path)
#     print(f"Found {len(captions)} captions:")
#     for start, end, text in captions[:5]:  # Display first 5 for sanity check
#         print(f"{start:.2f} - {end:.2f}: {text}")
