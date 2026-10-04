import asyncio

from app.browser.browser import BrowserController
from app.browser.perception import PagePerception
from app.browser.actions import BrowserActions
from app.browser.extractor import QuestionExtractor
from app.llm.gemini import GeminiClient


async def main():

    # =========================================================
    # 1. START BROWSER
    # =========================================================

    browser = BrowserController()

    await browser.start()

    # Open the webpage that contains the real questions.
    await browser.open(
        "https://www.w3schools.com/html/html_forms.asp"
    )

    # =========================================================
    # 2. CREATE PERCEPTION SYSTEM
    # =========================================================

    perception = PagePerception(
        browser.page
    )

    # =========================================================
    # 3. CREATE QUESTION EXTRACTOR
    # =========================================================

    extractor = QuestionExtractor(
        perception
    )

    # Extract the actual questions/fields
    # from the webpage.
    questions = await extractor.extract()

    print("\n========== REAL QUESTIONS ==========\n")

    for index, question in enumerate(questions):

        print(
            f"Question {index + 1}:"
        )

        print(question)

        print()

    print("=====================================\n")

    # =========================================================
    # 4. CREATE BROWSER ACTION SYSTEM
    # =========================================================

    actions = BrowserActions(
        perception
    )

    # =========================================================
    # 5. CREATE GEMINI CLIENT
    # =========================================================

    gemini = GeminiClient()

    # =========================================================
    # 6. USER PROFILE
    # =========================================================

    # This represents information AURA already knows
    # about the user.
    #
    # Later this can come from the FastAPI request.
    user_profile = {
        "first_name": "Abhinav",
        "last_name": "Mishra"
    }

    # =========================================================
    # 7. PROCESS QUESTIONS ONE BY ONE
    # =========================================================

    for index, question in enumerate(questions):

        print(
            f"\n========== PROCESSING QUESTION {index + 1} ==========\n"
        )

        print(
            "Question:",
            question
        )

        # -----------------------------------------------------
        # Ask Gemini to reason about THIS actual question.
        # -----------------------------------------------------

        action = await gemini.generate_action(
            question=question,
            elements=await perception.get_elements(),
            user_profile=user_profile
        )

        print("\nGemini decided:")

        print(action)

        # -----------------------------------------------------
        # Execute the action using Playwright.
        # -----------------------------------------------------

        try:

            await actions.execute(
                action
            )

            print(
                "Action executed successfully!"
            )

        except Exception as error:

            print(
                "Action failed:",
                error
            )

        # -----------------------------------------------------
        # Wait briefly so we can observe what happened.
        # -----------------------------------------------------

        await asyncio.sleep(1)

    # =========================================================
    # 8. KEEP BROWSER OPEN
    # =========================================================

    print(
        "\nAURA finished processing the extracted questions."
    )

    await asyncio.sleep(5)

    # =========================================================
    # 9. CLOSE BROWSER
    # =========================================================

    await browser.close()


# Start the asynchronous program.
asyncio.run(main())