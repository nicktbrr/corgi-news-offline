import json
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai
from config import GEMINI_KEY


class PictureIdea(BaseModel):
    """A single picture idea for visualizing an article"""
    description: str = Field(...,
                             description="Visual description in 1-2 sentences")


class ArticleGeneration(BaseModel):
    """Article generation results including summary and picture ideas"""
    summary: str = Field(...,
                         description="A 20-30 second spoken summary of the article")
    picture_ideas: List[PictureIdea] = Field(
        ..., description="List of picture ideas to visualize the article")


class TextGenerator:
    """Handles generation of summaries and picture ideas from article text"""

    def __init__(self, api_key=None):
        """Initialize the text generator with API key"""
        self.api_key = api_key or GEMINI_KEY

    def generate_content(self, article_text):
        """
        Generate a summary and picture ideas for the article.

        Args:
            article_text (str): The full article text to process

        Returns:
            ArticleGeneration: Object containing summary and picture ideas
        """
        system_instruction = """
        Give me:
        1. A summary of the text that can be spoken in 20-30 seconds.
        2. Three distinct picture ideas that could visualize the article, each described in 1-2 sentences.
        3. Make sure that there are no special characters in the text, use the english spelling instead, EX '%' should be percent
        
        Format your response as valid JSON with the following structure:
        {
            "summary": "the 20-30 second summary goes here",
            "picture_ideas": [
                {"description": "first picture idea in 1-2 sentences"},
                {"description": "second picture idea in 1-2 sentences"},
                {"description": "third picture idea in 1-2 sentences"}
            ]
        }
        """

        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction=system_instruction
            )

            response = model.generate_content(
                article_text,
                generation_config=genai.types.GenerationConfig(
                    temperature=1.0,
                    response_mime_type="application/json"
                )
            )

            # Parse the JSON response
            json_response = json.loads(
                response.text
            )

            # Create and return ArticleGeneration model
            result = ArticleGeneration(
                summary=json_response.get("summary", ""),
                picture_ideas=[
                    PictureIdea(description=idea.get("description", ""))
                    for idea in json_response.get("picture_ideas", [])
                ]
            )
            return result

        except Exception as e:
            print(f"Error generating content: {e}")
            # Fallback to empty results with error message
            return ArticleGeneration(
                summary=f"Error generating summary: {str(e)}",
                picture_ideas=[
                    PictureIdea(description="Error generating picture idea"),
                    PictureIdea(description="Error generating picture idea"),
                    PictureIdea(description="Error generating picture idea")
                ]
            )

    # Legacy method for backward compatibility
    def generate_summary(self, article_text):
        """
        Legacy method that returns just the summary in the old format.

        Args:
            article_text (str): The full article text to summarize

        Returns:
            dict: A dictionary containing the summary
        """
        result = self.generate_content(article_text)
        return {"summary": result.summary}
