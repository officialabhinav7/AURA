# Import Google's Gemini SDK.
from google import genai

# Import Pydantic configuration types used by Gemini.
from google.genai import types

# Load variables from the .env file.
from dotenv import load_dotenv

# Used to read GEMINI_API_KEY from environment variables.
import os

# Import our own Pydantic browser-action schema.
from app.browser.schemas import BrowserAction


# Load variables from .env.
load_dotenv()


class GeminiClient:

    def __init__(self):

        # Read the Gemini API key from the environment.
        api_key = os.getenv("GEMINI_API_KEY")

        # Stop immediately if the API key is missing.
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set"
            )

        # Create the Gemini client.
        self.client = genai.Client(
            api_key=api_key
        )

        # Keep the model name in one place.
        self.model = "gemini-3.8-flash"

    async def generate_action(
        self,
        task,
        elements
    ):

        # Convert the perceived webpage elements into
        # readable text that Gemini can understand.
        elements_text = "\n".join(
            str(element)
            for element in elements
        )

        # Give Gemini a clear role and explain exactly
        # what information it is allowed to use.
        prompt = f"""
You are the browser planning brain of an autonomous
web automation agent called AURA.

Your job is to select ONE browser action that moves
the current task forward.

USER TASK:
{task}

AVAILABLE PAGE ELEMENTS:
{elements_text}

IMPORTANT RULES:

1. Only use element IDs that exist in the available
   page elements.

2. Do not invent element IDs.

3. Select the most appropriate action for the task.

4. If the task requires entering text, use "type".

5. If the task requires clicking a button or link,
   use "click".

6. If the task requires checking a checkbox,
   use "check".

7. If the task requires selecting an option,
   use "select".

8. If the task requires opening a URL, use "navigate".

9. Return exactly ONE browser action.

10. Do not return Playwright code.

11. Do not return explanations outside the action.
"""

        # Ask Gemini to generate a response that follows
        # our BrowserAction Pydantic schema.
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                # Tell Gemini that the response must be JSON.
                response_mime_type="application/json",

                # Give Gemini our Pydantic schema.
                # This makes the output match BrowserAction.
                response_schema=BrowserAction
            )
        )

        # The Gemini SDK parses the structured response
        # into our BrowserAction Pydantic object.
        action = response.parsed

        # Make sure Gemini actually returned an action.
        if action is None:
            raise ValueError(
                "Gemini did not return a valid BrowserAction"
            )

        # Return the validated BrowserAction object.
        return action