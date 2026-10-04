from app.browser.schemas import BrowserAction


class BrowserActions:

    # Constructor
    # Receives the perception object and stores it.
    # Perception is responsible for finding/getting elements
    # from the webpage.
    def __init__(self, perception):
        self.perception = perception


    # ---------------------------------------------------------
    # EXECUTE ACTION
    # ---------------------------------------------------------
    # This is the main entry point for BrowserActions.
    #
    # Gemini gives us a BrowserAction such as:
    #
    # action="type"
    # element_id="e9"
    # value="Abhinav"
    #
    # This function looks at the action type and calls
    # the correct function below.
    async def execute(self, action: BrowserAction):

        # If Gemini decided to click something,
        # call the click() function.
        if action.action == "click":

            await self.click(
                action.element_id
            )

        # If Gemini decided to type something,
        # call the type() function.
        elif action.action == "type":

            await self.type(
                action.element_id,
                action.value
            )

        # If Gemini decided to check a checkbox,
        # call the check() function.
        elif action.action == "check":

            await self.check(
                action.element_id
            )

        # If Gemini decided to select an option,
        # call the select() function.
        elif action.action == "select":

            await self.select(
                action.element_id,
                action.value
            )

        # If Gemini decided to navigate to another URL.
        elif action.action == "navigate":

            await self.navigate(
                action.url
            )

        # If Gemini somehow returns an action that
        # we don't support, reject it.
        else:

            raise ValueError(
                f"Unsupported action: {action.action}"
            )


    # ---------------------------------------------------------
    # CLICK ACTION
    # ---------------------------------------------------------
    # This function clicks an element using its element_id.
    async def click(self, element_id):

        # Ask the perception layer to find the element
        # corresponding to the given element_id.
        element = self.perception.get_element(
            element_id
        )

        # If the element does not exist, stop the operation
        # and raise an error.
        if element is None:
            raise ValueError(
                f"Element {element_id} not found"
            )

        # Get the ARIA role of the element.
        role = await element.get_attribute("role")

        # Get the actual HTML tag name.
        tag = await element.evaluate(
            "(element) => element.tagName"
        )

        # Check whether the element is actually clickable.
        if role not in ["button", "link"] and tag not in [
            "BUTTON",
            "A"
        ]:
            raise ValueError(
                f"Element {element_id} cannot be clicked"
            )

        # If validation passes, click the element.
        await element.click()


    # ---------------------------------------------------------
    # TYPE ACTION
    # ---------------------------------------------------------
    # This function enters text into an input field.
    async def type(self, element_id, value):

        # Ask the perception layer to find the element.
        element = self.perception.get_element(
            element_id
        )

        # If the element cannot be found, raise an error.
        if element is None:
            raise ValueError(
                f"Element {element_id} not found"
            )

        # Get the ARIA role of the element.
        role = await element.get_attribute("role")

        # Get the HTML tag name.
        tag = await element.evaluate(
            "(element) => element.tagName"
        )

        # Get the input type.
        #
        # This is important because INPUT can also mean
        # checkbox, radio, password, number, etc.
        input_type = await element.get_attribute(
            "type"
        )

        # Prevent trying to type into a checkbox or radio.
        if input_type in ["checkbox", "radio"]:
            raise ValueError(
                f"Element {element_id} cannot receive text"
            )

        # Check whether the element can receive text.
        if role not in ["textbox"] and tag not in [
            "INPUT",
            "TEXTAREA"
        ]:
            raise ValueError(
                f"Element {element_id} cannot receive text"
            )

        # Make sure Gemini actually provided a value.
        if value is None:
            raise ValueError(
                "Type action requires a value"
            )

        # Fill the element with the provided value.
        await element.fill(value)


    # ---------------------------------------------------------
    # CHECK ACTION
    # ---------------------------------------------------------
    # This function checks a checkbox.
    async def check(self, element_id):

        # Find the element using the perception layer.
        element = self.perception.get_element(
            element_id
        )

        # If the element does not exist, raise an error.
        if element is None:
            raise ValueError(
                f"Element {element_id} not found"
            )

        # Get the ARIA role.
        role = await element.get_attribute("role")

        # Get the HTML input type.
        input_type = await element.get_attribute(
            "type"
        )

        # Check whether the element is actually a checkbox.
        if role != "checkbox" and input_type != "checkbox":
            raise ValueError(
                f"Element {element_id} is not a checkbox"
            )

        # If validation passes, check the checkbox.
        await element.check()


    # ---------------------------------------------------------
    # SELECT ACTION
    # ---------------------------------------------------------
    # This function selects an option from a dropdown.
    async def select(self, element_id, value):

        # Find the element using the perception layer.
        element = self.perception.get_element(
            element_id
        )

        # If the element does not exist, raise an error.
        if element is None:
            raise ValueError(
                f"Element {element_id} not found"
            )

        # Get the HTML tag name.
        tag = await element.evaluate(
            "(element) => element.tagName"
        )

        # Get the ARIA role.
        role = await element.get_attribute("role")

        # Native HTML SELECT.
        if tag == "SELECT":

            if value is None:
                raise ValueError(
                    "Select action requires a value"
                )

            await element.select_option(
                value
            )

        # Custom ARIA combobox.
        elif role == "combobox":

            # We don't yet have generic handling for
            # custom JavaScript dropdowns.
            raise NotImplementedError(
                "Custom ARIA combobox is not implemented yet"
            )

        else:

            raise ValueError(
                f"Element {element_id} is not a select element"
            )


    # ---------------------------------------------------------
    # NAVIGATE ACTION
    # ---------------------------------------------------------
    # This function opens a new URL.
    async def navigate(self, url):

        # A navigation action must contain a URL.
        if url is None:
            raise ValueError(
                "Navigate action requires a URL"
            )

        # Open the URL using Playwright.
        await self.perception.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )