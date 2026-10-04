# Import Google's Gemini SDK.
from google import genai

# Load variables from the .env file.
from dotenv import load_dotenv

# Used to read the API key from environment variables.
import os


# Load the .env file.
load_dotenv()


# ---------------------------------------------------------
# Get the Gemini API key.
# ---------------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")


# Make sure the API key exists.
if not api_key:

    raise ValueError(
        "GEMINI_API_KEY is not set"
    )


# ---------------------------------------------------------
# Create the Gemini client.
# ---------------------------------------------------------

client = genai.Client(
    api_key=api_key
)


# ---------------------------------------------------------
# Send a very simple request.
#
# IMPORTANT:
# We are NOT using:
# - Playwright
# - LangGraph
# - BrowserAction
# - tools
# - function calling
# - structured output
#
# We are testing Gemini alone.
# ---------------------------------------------------------

response = client.models.generate_content(

    # Current stable Flash model.
    model="gemini-3.8-flash",

    # Very simple test prompt.
    contents="Reply with exactly: AURA LLM OK"
)


# ---------------------------------------------------------
# Print Gemini's response.
# ---------------------------------------------------------

print("\nGemini response:")
print(response.text)