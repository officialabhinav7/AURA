from google import genai
from dotenv import load_dotenv
import os
import json

from app.browser.schemas import BrowserAction
from app.browser.question import QuestionField


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------
# This loads variables from the .env file.
#
# Example:
# GEMINI_API_KEY=your_api_key
#
load_dotenv()


class GeminiClient:

    def __init__(self):

        # -------------------------------------------------
        # GET GEMINI API KEY
        # -------------------------------------------------
        # Read the Gemini API key from the .env file.
        api_key = os.getenv("GEMINI_API_KEY")

        # Stop the program if the API key is missing.
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        # -------------------------------------------------
        # CREATE GEMINI CLIENT
        # -------------------------------------------------
        self.client = genai.Client(
            api_key=api_key
        )

        # -------------------------------------------------
        # SELECT GEMINI MODEL
        # -------------------------------------------------
        # This model worked successfully in our previous test.
        self.model = "gemini-3.5-flash-lite"


    async def generate_action(
        self,
        question: QuestionField,
        elements,
        user_profile
    ):

        # -------------------------------------------------
        # CONVERT PAGE ELEMENTS TO TEXT
        # -------------------------------------------------
        # Gemini needs to understand which elements are
        # currently available on the webpage.
        #
        # Each element contains information such as:
        # element_id
        # field_type
        # label
        # context
        # name
        # placeholder
        #
        elements_text = "\n".join(
            str(element)
            for element in elements
        )


        # -------------------------------------------------
        # CONVERT CURRENT QUESTION TO TEXT
        # -------------------------------------------------
        # We process ONE question at a time.
        question_text = str(question)


        # -------------------------------------------------
        # CONVERT USER PROFILE TO TEXT
        # -------------------------------------------------
        # Example:
        #
        # {
        #     "first_name": "Abhinav",
        #     "last_name": "Mishra"
        # }
        #
        profile_text = str(user_profile)


        # -------------------------------------------------
        # CREATE GEMINI PROMPT
        # -------------------------------------------------
        prompt = f"""
You are the reasoning brain of an autonomous web
automation agent called AURA.

AURA is currently filling a webpage.

CURRENT QUESTION:
{question_text}

USER PROFILE:
{profile_text}

AVAILABLE PAGE ELEMENTS:
{elements_text}

Your job is to determine the correct browser action
for the CURRENT QUESTION.

RULES:

1. Work only on the CURRENT QUESTION.
2. Do not answer unrelated questions.
3. Use only element IDs that exist in AVAILABLE PAGE ELEMENTS.
4. Never invent an element ID.
5. For text input use "type".
6. For checkbox use "check".
7. For clicking use "click".
8. For selecting an option use "select".
9. For navigation use "navigate".
10. Do not return Playwright code.
11. Return ONLY valid JSON.
12. The JSON must contain:
    action
    element_id
    value
    url

Example:

{{
    "action": "type",
    "element_id": "e9",
    "value": "Abhinav",
    "url": null
}}
"""


        # -------------------------------------------------
        # SEND REQUEST TO GEMINI
        # -------------------------------------------------
        # Gemini analyzes the current question and decides
        # which browser action AURA should perform.
        #
        # Gemini does NOT directly control Playwright.
        #
        # It only returns a structured action.
        #
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt
        )


        # -------------------------------------------------
        # GET GEMINI RESPONSE AS TEXT
        # -------------------------------------------------
        raw_response = response.text.strip()


        # -------------------------------------------------
        # PRINT RAW GEMINI RESPONSE
        # -------------------------------------------------
        # This is useful while debugging AURA.
        print(
            "\n========== GEMINI RAW RESPONSE ==========\n"
        )

        print(raw_response)

        print(
            "\n=========================================\n"
        )


        # -------------------------------------------------
        # CLEAN GEMINI RESPONSE
        # -------------------------------------------------
        # Gemini sometimes returns JSON inside Markdown
        # code fences.
        #
        # Example:
        #
        # ```json
        # {
        #     "action": "check",
        #     "element_id": "e2",
        #     "value": null,
        #     "url": null
        # }
        # ```
        #
        # The ```json and ``` parts are NOT valid JSON.
        #
        # Therefore, we remove those lines before calling
        # json.loads().
        #
        if raw_response.startswith("```"):

            # Split the response into individual lines.
            lines = raw_response.splitlines()


            # -------------------------------------------------
            # REMOVE OPENING CODE FENCE
            # -------------------------------------------------
            # Removes:
            #
            # ```json
            #
            # or:
            #
            # ```
            #
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]


            # -------------------------------------------------
            # REMOVE CLOSING CODE FENCE
            # -------------------------------------------------
            # Removes:
            #
            # ```
            #
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]


            # -------------------------------------------------
            # REBUILD CLEAN JSON STRING
            # -------------------------------------------------
            raw_response = "\n".join(lines).strip()


        # -------------------------------------------------
        # CONVERT JSON TEXT INTO PYTHON DICTIONARY
        # -------------------------------------------------
        try:

            action_data = json.loads(
                raw_response
            )

        except json.JSONDecodeError as error:

            # If Gemini returned something that is still
            # not valid JSON, show the actual response.
            raise ValueError(
                f"Gemini returned invalid JSON: {error}\n"
                f"Raw response:\n{raw_response}"
            )


        # -------------------------------------------------
        # VALIDATE GEMINI ACTION USING PYDANTIC
        # -------------------------------------------------
        # BrowserAction checks that Gemini returned a valid
        # action such as:
        #
        # type
        # click
        # check
        # select
        # navigate
        #
        # It also checks required fields such as
        # element_id and value.
        #
        try:

            action = BrowserAction.model_validate(
                action_data
            )

        except Exception as error:

            raise ValueError(
                f"Invalid BrowserAction: {error}"
            )


        # -------------------------------------------------
        # RETURN VALIDATED ACTION
        # -------------------------------------------------
        # The returned action will then be passed to
        # BrowserActions.execute().
        #
        return action