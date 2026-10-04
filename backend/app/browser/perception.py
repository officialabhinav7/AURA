from typing import Optional


class PagePerception:

    def __init__(self, page):
        # Store the Playwright page.
        # We use this page to inspect the current webpage.
        self.page = page

        # Store all detected elements using our own IDs
        # such as e1, e2, e3...
        self.element_map = {}


    async def get_label(self, element):
        """
        Find the most useful label for an element.

        We check several sources because webpages can describe
        form fields in different ways:
        - aria-label
        - <label for="...">
        - aria-labelledby
        - placeholder
        - name
        """

        # 1. Try aria-label.
        aria_label = await element.get_attribute("aria-label")

        if aria_label:
            return aria_label.strip()


        # 2. Try a <label> connected using the element's ID.
        element_id = await element.get_attribute("id")

        if element_id:

            label = self.page.locator(
                f'label[for="{element_id}"]'
            )

            if await label.count() > 0:

                label_text = await label.first.inner_text()

                if label_text.strip():
                    return label_text.strip()


        # 3. Try aria-labelledby.
        labelled_by = await element.get_attribute(
            "aria-labelledby"
        )

        if labelled_by:

            texts = []

            for label_id in labelled_by.split():

                label_element = self.page.locator(
                    f"#{label_id}"
                )

                if await label_element.count() > 0:

                    text = await label_element.inner_text()

                    if text.strip():
                        texts.append(text.strip())

            if texts:
                return " ".join(texts)


        # 4. Try placeholder.
        placeholder = await element.get_attribute(
            "placeholder"
        )

        if placeholder:
            return placeholder.strip()


        # 5. Try name.
        name = await element.get_attribute("name")

        if name:
            return name.strip()


        # Nothing useful was found.
        return None


    async def get_context(self, element):
        """
        Get nearby text around an element.

        Context helps Gemini understand what a field means.

        Example:

        First name: [________]
        Last name:  [________]

        The input itself may only have name="fname",
        but its surrounding text gives useful meaning.
        """

        context = await element.evaluate(
            """
            (element) => {

                // Get the immediate parent.
                const parent = element.parentElement;

                // Get the parent's parent.
                const grandparent =
                    parent ? parent.parentElement : null;

                return {
                    parent_text:
                        parent ? parent.innerText : "",

                    grandparent_text:
                        grandparent ? grandparent.innerText : ""
                };
            }
            """
        )


        # Get immediate parent text.
        parent_text = context.get("parent_text", "")

        # Get grandparent text.
        grandparent_text = context.get(
            "grandparent_text",
            ""
        )


        # Normalize whitespace.
        parent_text = " ".join(
            parent_text.split()
        )

        grandparent_text = " ".join(
            grandparent_text.split()
        )


        # Keep context reasonably small.
        parent_text = parent_text[:250]

        grandparent_text = grandparent_text[:300]


        # Prefer immediate parent context.
        if parent_text:
            return parent_text

        if grandparent_text:
            return grandparent_text

        return None


    async def is_actionable(self, element):
        """
        Determine whether an element is currently usable.

        This is the important improvement.

        An element can exist in the DOM but still be:
        - hidden
        - disabled
        - not currently usable

        We don't want such elements to be sent to Gemini
        as possible actions.
        """

        # -------------------------------------------------
        # CHECK VISIBILITY
        # -------------------------------------------------
        # Playwright checks whether the element is currently
        # visible to the user.
        if not await element.is_visible():
            return False


        # -------------------------------------------------
        # CHECK ENABLED STATE
        # -------------------------------------------------
        # Disabled form controls should not be considered
        # actionable.
        try:

            if not await element.is_enabled():
                return False

        except Exception:

            # Some non-form elements may not support the
            # enabled-state check in the same way.
            pass


        # If the element is visible and usable,
        # consider it actionable.
        return True


    async def get_input_role(self, element):
        """
        Determine the semantic role of an input element.

        We first check an explicit ARIA role.

        If no role exists, we infer it from the HTML input type.
        """

        # Check explicit ARIA role.
        role = await element.get_attribute("role")

        if role:
            return role


        # Get native input type.
        input_type = await element.get_attribute("type")

        if input_type in ["text", "email", "password", "search"]:
            return "textbox"

        if input_type == "number":
            return "spinbutton"

        if input_type == "radio":
            return "radio"

        if input_type == "checkbox":
            return "checkbox"

        if input_type == "date":
            return "textbox"

        return "textbox"


    async def get_elements(self):
        """
        Detect currently actionable interactive elements.

        Important:
        We DO NOT remove duplicate-looking elements here.

        If two different DOM elements exist, both can remain.

        Example:

        e9  -> fname
        e12 -> fname

        They are preserved because they may represent
        different physical fields.
        """

        # Reset the element map for the current perception.
        self.element_map = {}

        # Generate our own IDs.
        element_counter = 1


        # -------------------------------------------------
        # FIND NATIVE INTERACTIVE ELEMENTS
        # -------------------------------------------------
        locator = self.page.locator(
            "input, textarea, select, button, a"
        )

        count = await locator.count()


        for index in range(count):

            element = locator.nth(index)


            # -------------------------------------------------
            # IMPORTANT:
            # IGNORE HIDDEN/NON-ACTIONABLE ELEMENTS
            # -------------------------------------------------
            if not await self.is_actionable(element):
                continue


            # Get HTML tag.
            tag = await element.evaluate(
                "(element) => element.tagName"
            )

            tag = tag.upper()


            # -------------------------------------------------
            # DETERMINE ROLE
            # -------------------------------------------------
            if tag == "INPUT":

                role = await self.get_input_role(
                    element
                )

            elif tag == "TEXTAREA":

                role = "textbox"

            elif tag == "SELECT":

                role = "combobox"

            elif tag == "BUTTON":

                role = "button"

            elif tag == "A":

                role = "link"

            else:

                continue


            # Create our internal element ID.
            element_id = f"e{element_counter}"

            element_counter += 1


            # Get useful information.
            label = await self.get_label(
                element
            )

            context = await self.get_context(
                element
            )

            name = await element.get_attribute(
                "name"
            )

            placeholder = await element.get_attribute(
                "placeholder"
            )

            required = await element.get_attribute(
                "required"
            )


            # Store element information.
            self.element_map[element_id] = {
                "element": element,
                "id": element_id,
                "role": role,
                "type": await element.get_attribute(
                    "type"
                ),
                "name": name,
                "label": label,
                "placeholder": placeholder,
                "required": bool(required),
                "context": {
                    "parent_text": context
                }
            }


        # -------------------------------------------------
        # FIND ARIA INTERACTIVE ELEMENTS
        # -------------------------------------------------
        #
        # Some modern websites don't use native HTML
        # elements. They use things like:
        #
        # <div role="button">
        # <div role="textbox">
        # <div role="checkbox">
        #
        # So we inspect those as well.
        #
        aria_locator = self.page.locator(
            '[role="button"], '
            '[role="textbox"], '
            '[role="checkbox"], '
            '[role="radio"], '
            '[role="combobox"]'
        )

        aria_count = await aria_locator.count()


        for index in range(aria_count):

            element = aria_locator.nth(index)


            # Ignore hidden ARIA elements too.
            if not await self.is_actionable(element):
                continue


            role = await element.get_attribute(
                "role"
            )

            element_id = f"e{element_counter}"

            element_counter += 1


            label = await self.get_label(
                element
            )

            context = await self.get_context(
                element
            )

            name = await element.get_attribute(
                "name"
            )

            placeholder = await element.get_attribute(
                "placeholder"
            )

            required = await element.get_attribute(
                "required"
            )


            self.element_map[element_id] = {
                "element": element,
                "id": element_id,
                "role": role,
                "type": await element.get_attribute(
                    "type"
                ),
                "name": name,
                "label": label,
                "placeholder": placeholder,
                "required": bool(required),
                "context": {
                    "parent_text": context
                }
            }


        # -------------------------------------------------
        # RETURN CLEAN ELEMENT INFORMATION
        # -------------------------------------------------
        #
        # Don't expose the actual Playwright objects to
        # Gemini.
        #
        # Gemini only needs descriptive information.
        #
        elements = []

        for element_id, data in self.element_map.items():

            elements.append({
                "id": data["id"],
                "role": data["role"],
                "type": data["type"],
                "name": data["name"],
                "label": data["label"],
                "placeholder": data["placeholder"],
                "required": data["required"],
                "context": data["context"]
            })


        return elements


    def get_element(self, element_id):
        """
        Return the actual Playwright element associated
        with an AURA element ID.

        Example:

        e9
        ↓
        actual Playwright input element
        """

        data = self.element_map.get(
            element_id
        )

        if data is None:
            return None

        return data["element"]