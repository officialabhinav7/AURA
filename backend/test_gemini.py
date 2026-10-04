import asyncio

from app.browser.browser import BrowserController
from app.browser.perception import PagePerception
from app.browser.actions import BrowserActions
from app.browser.schemas import BrowserAction


async def main():

    # ---------------------------------------------------------
    # 1. START THE BROWSER
    # ---------------------------------------------------------

    # Create the browser controller.
    browser = BrowserController()

    # Launch Chromium.
    await browser.start()

    # Open the test webpage.
    await browser.open(
        "https://www.w3schools.com/html/html_forms.asp"
    )

    # ---------------------------------------------------------
    # 2. CREATE THE PERCEPTION SYSTEM
    # ---------------------------------------------------------

    # PagePerception allows AURA to inspect the webpage.
    perception = PagePerception(
        browser.page
    )

    # ---------------------------------------------------------
    # 3. CREATE THE ACTION SYSTEM
    # ---------------------------------------------------------

    # BrowserActions executes validated actions
    # using Playwright.
    actions = BrowserActions(
        perception
    )

    # ---------------------------------------------------------
    # 4. PERCEIVE THE PAGE
    # ---------------------------------------------------------

    # Detect the elements currently available on the page.
    elements = await perception.get_elements()

    print("\n========== PAGE ELEMENTS ==========\n")

    for element in elements:
        print(element)

    print("\n===================================\n")

    # ---------------------------------------------------------
    # 5. CREATE A VALIDATED BROWSER ACTION
    # ---------------------------------------------------------

    # This is the same action Gemini successfully generated
    # in our previous test.
    #
    # We are manually creating it here first so that we can
    # verify that Playwright can execute it correctly.
    action = BrowserAction(
        action="type",
        element_id="e9",
        value="Abhinav"
    )

    print("\n========== ACTION ==========\n")
    print(action)
    print("\n============================\n")

    # ---------------------------------------------------------
    # 6. EXECUTE THE ACTION
    # ---------------------------------------------------------

    print("Executing action...")

    await actions.execute(
        action
    )

    print("Action executed successfully!")

    # Keep the browser open for 5 seconds
    # so we can see the result.
    await asyncio.sleep(5)

    # ---------------------------------------------------------
    # 7. CLOSE THE BROWSER
    # ---------------------------------------------------------

    await browser.close()


# Start the asynchronous program.
asyncio.run(main())