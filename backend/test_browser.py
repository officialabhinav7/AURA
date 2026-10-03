import asyncio

from app.browser.browser import BrowserController
from app.browser.perception import PagePerception
from app.browser.extractor import QuestionExtractor


async def main():

    # Create the browser controller.
    browser = BrowserController()

    # Start Playwright and open the browser.
    await browser.start()

    # Open our test webpage.
    await browser.open(
        "https://www.w3schools.com/html/html_forms.asp"
    )

    # Create the perception layer.
    # This layer understands what elements exist on the page.
    perception = PagePerception(
        browser.page
    )

    # Create the question extractor.
    # This converts perceived elements into QuestionField objects.
    extractor = QuestionExtractor(
        perception
    )

    # Extract all possible question/input fields.
    questions = await extractor.extract()

    # Print the number of fields discovered.
    print("\nTotal questions found:", len(questions))

    # Print every extracted question.
    print("\n========== EXTRACTED QUESTIONS ==========\n")

    for question in questions:

        # Pydantic model is printed here.
        print(question)

    print("\n=========================================\n")

    # Keep the browser open for a few seconds
    # so we can visually inspect the webpage.
    await asyncio.sleep(5)

    # Close the browser.
    await browser.close()


# Start the program.
asyncio.run(main())