from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

from app.browser.schemas import BrowserAction


# Load variables from the .env file.
load_dotenv()


class GeminiClient:

    def __init__(self):
        # Read the Gemini API key from the .env file.
        api_key = os.getenv("GEMINI_API_KEY")

        # Stop the program if the API key is missing.
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        # Create the Gemini client.
        self.client = genai.Client(api_key=api_key)

        # Use the model that we confirmed is working.
        self.model = "gemini-3.8-flash"

    async def generate_action(self, task, elements):

        # Convert the detected browser elements into text
        # so Gemini can understand what is available on the page.
        elements_text = "\n".join(
            str(element)
            for element in elements
        )

        # Tell Gemini exactly what role it has in AURA.
        prompt = f"""
You are the browser planning brain of an autonomous
web automation agent called AURA.

USER TASK:
{task}

AVAILABLE PAGE ELEMENTS:
{elements_text}

RULES:

1. Return exactly ONE browser action.
2. Only use element IDs that exist in the available page elements.
3. Never invent an element ID.
4. For entering text, use "type".
5. For clicking a button or link, use "click".
6. For checking a checkbox, use "check".
7. For selecting an option, use "select".
8. For opening a URL, use "navigate".
9. Do NOT return Playwright code.
10. Return only the structured BrowserAction.
"""

        # Ask Gemini to generate a response matching
        # our BrowserAction Pydantic schema.
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BrowserAction
            )
        )

        # Gemini SDK parses the structured response
        # according to the BrowserAction schema.
        action = response.parsed

        # Make sure Gemini actually returned a valid action.
        if action is None:
            raise ValueError(
                "Gemini did not return a valid BrowserAction"
            )

        return action