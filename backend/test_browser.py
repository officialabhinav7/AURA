import asyncio

# Import the browser controller.
from app.browser.browser import BrowserController

# Import the perception layer.
from app.browser.perception import PagePerception

# Import our Gemini client.
from app.llm.gemini import GeminiClient


async def main():

    # Create the browser controller.
    browser = BrowserController()

    # Start Chromium.
    await browser.start()

    # Open the test webpage.
    await browser.open(
        "https://www.w3schools.com/html/html_forms.asp"
    )

    # Create the perception layer using
    # the current Playwright page.
    perception = PagePerception(
        browser.page
    )

    # Ask AURA to perceive the webpage.
    elements = await perception.get_elements()

    print("AVAILABLE ELEMENTS:")
    print()

    # Display the elements that Gemini will receive.
    for element in elements:
        print(element)

    # Create the Gemini client.
    gemini = GeminiClient()

    # Give Gemini a simple task.
    action = await gemini.generate_action(
        task="Enter Abhinav Mishra into the name field.",
        elements=elements
    )

    # Display Gemini's structured decision.
    print("\nGEMINI ACTION:")
    print(action)

    # Keep the browser open temporarily
    # so we can inspect the page.
    await asyncio.sleep(5)

    # Close the browser.
    await browser.close()


# Start the asynchronous program.
asyncio.run(main())