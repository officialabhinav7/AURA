class BrowserActions:

    # Constructor
    # Receives the perception object and stores it.
    # Perception is responsible for finding/getting elements from the webpage.
    def __init__(self, perception):
        self.perception = perception


    # ---------------------------------------------------------
    # CLICK ACTION
    # ---------------------------------------------------------
    # This function clicks an element using its element_id.
    async def click(self, element_id):

        # Ask the perception layer to find the element
        # corresponding to the given element_id.
        element = self.perception.get_element(element_id)

        # If the element does not exist, stop the operation
        # and raise an error.
        if element is None:
            raise ValueError(
                f"Element {element_id} not found"
            )

        # Get the ARIA role of the element.
        # Example: button, link, textbox, checkbox, etc.
        role = await element.get_attribute("role")

        # Get the actual HTML tag name.
        # Example:
        # <button> -> BUTTON
        # <a>      -> A
        # <input>  -> INPUT
        tag = await element.evaluate(
            "(element) => element.tagName"
        )

        # Check whether the element is actually clickable.
        #
        # It is allowed if:
        # 1. Its role is "button" or "link"
        # OR
        # 2. Its HTML tag is BUTTON or A
        #
        # If neither condition is true, clicking is rejected.
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

        # Find the element using the perception layer.
        element = self.perception.get_element(element_id)

        # If the element cannot be found, raise an error.
        if element is None:
            raise ValueError(
                f"Element {element_id} not found"
            )

        # Get the ARIA role of the element.
        # A text input can have role="textbox".
        role = await element.get_attribute("role")

        # Get the HTML tag name.
        # Common text input elements are:
        # INPUT and TEXTAREA.
        tag = await element.evaluate(
            "(element) => element.tagName"
        )

        # Check whether the element can receive text.
        #
        # It is allowed if:
        # 1. role == "textbox"
        # OR
        # 2. HTML tag is INPUT or TEXTAREA
        #
        # Otherwise, typing is rejected.
        if role not in ["textbox"] and tag not in [
            "INPUT",
            "TEXTAREA"
        ]:
            raise ValueError(
                f"Element {element_id} cannot receive text"
            )

        # If validation passes, fill the element with the
        # provided value.
        #
        # Example:
        # value = "Abhinav Mishra"
        #
        # This will put "Abhinav Mishra" inside the input.
        await element.fill(value)


    # ---------------------------------------------------------
    # CHECK ACTION
    # ---------------------------------------------------------
    # This function checks a checkbox.
    async def check(self, element_id):

        # Find the element using the perception layer.
        element = self.perception.get_element(element_id)

        # If the element does not exist, raise an error.
        if element is None:
            raise ValueError(
                f"Element {element_id} not found"
            )

        # Get the ARIA role.
        # Example:
        # role="checkbox"
        role = await element.get_attribute("role")

        # Get the HTML input type.
        # Example:
        # <input type="checkbox">
        #
        # Here input_type will be "checkbox".
        input_type = await element.get_attribute("type")

        # Check whether the element is actually a checkbox.
        #
        # It is valid if:
        # 1. role == "checkbox"
        # OR
        # 2. type == "checkbox"
        #
        # If neither is true, reject the action.
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
        element = self.perception.get_element(element_id)

        # If the element does not exist, raise an error.
        if element is None:
            raise ValueError(
                f"Element {element_id} not found"
            )

        # Get the HTML tag name.
        #
        # A normal HTML dropdown looks like:
        #
        # <select>
        #
        # In that case tag will be "SELECT".
        tag = await element.evaluate(
            "(element) => element.tagName"
        )

        # Get the ARIA role.
        #
        # Modern websites can create dropdown-like elements
        # using role="combobox".
        role = await element.get_attribute("role")

        # Check whether the element is a valid dropdown.
        #
        # It is allowed if:
        # 1. HTML tag is SELECT
        # OR
        # 2. role is combobox
        #
        # Otherwise, reject the action.
        if tag != "SELECT" and role != "combobox":
            raise ValueError(
                f"Element {element_id} is not a select element"
            )

        # Select the requested option.
        #
        # Example:
        #
        # <select>
        #     <option value="india">India</option>
        #     <option value="usa">USA</option>
        # </select>
        #
        # If value = "india", Playwright selects India.
        await element.select_option(value)