# Import Google's Gemini SDK.
from google import genai

# Load variables from .env.
from dotenv import load_dotenv

# Used to read the API key.
import os


# Load the .env file.
load_dotenv()


# Get the API key.
api_key = os.getenv(
    "GEMINI_API_KEY"
)


# Stop if the key is missing.
if not api_key:

    raise ValueError(
        "GEMINI_API_KEY is not set"
    )


# Create the Gemini client.
client = genai.Client(
    api_key=api_key
)


# Ask Google which models are available
# through this API key.
models = client.models.list()


# Print the available models.
print("\n========== AVAILABLE GEMINI MODELS ==========\n")

for model in models:

    # Print the model name.
    print(model.name)

print("\n=============================================\n")