class PagePerception:
    """
    Responsible for observing the current webpage.

    It does NOT decide what the user wants.

    Its job is only to collect useful information about
    interactive elements on the webpage.
    """

    def __init__(self, page):

        # Store the Playwright Page object.
        self.page = page

        # Map AURA IDs such as "e1" to actual
        # Playwright elements.
        self.element_map = {}

    async def get_page_info(self):

        # Return basic information about the webpage.
        return {
            "url": self.page.url,
            "title": await self.page.title()
        }

    async def get_label(self, element):

        # --------------------------------------------------
        # 1. Try aria-label.
        # --------------------------------------------------

        label = await element.get_attribute(
            "aria-label"
        )

        if label:
            return label.strip()

        # --------------------------------------------------
        # 2. Try an HTML <label>.
        # --------------------------------------------------

        element_id = await element.get_attribute(
            "id"
        )

        if element_id:

            label_locator = self.page.locator(
                f'label[for="{element_id}"]'
            )

            if await label_locator.count() > 0:

                return (
                    await label_locator.first.inner_text()
                ).strip()

        # --------------------------------------------------
        # 3. Try aria-labelledby.
        # --------------------------------------------------

        labelled_by = await element.get_attribute(
            "aria-labelledby"
        )

        if labelled_by:

            label_parts = []

            # aria-labelledby can contain multiple IDs.
            for label_id in labelled_by.split():

                label_element = self.page.locator(
                    f"#{label_id}"
                )

                if await label_element.count() > 0:

                    text = (
                        await label_element.first.inner_text()
                    ).strip()

                    if text:
                        label_parts.append(text)

            if label_parts:

                return " ".join(label_parts)

        # --------------------------------------------------
        # 4. Try placeholder.
        # --------------------------------------------------

        placeholder = await element.get_attribute(
            "placeholder"
        )

        if placeholder:
            return placeholder.strip()

        # --------------------------------------------------
        # 5. Try name.
        # --------------------------------------------------

        name = await element.get_attribute(
            "name"
        )

        if name:
            return name.strip()

        # No useful label found.
        return None

    async def get_context(self, element):
        """
        Collect useful text near an element.

        We prefer local context because a complete parent
        or webpage section can contain unrelated information.
        """

        # --------------------------------------------------
        # 1. Get the immediate parent.
        # --------------------------------------------------

        parent = element.locator("..")

        parent_text = (
            await parent.inner_text()
        ).strip()

        # --------------------------------------------------
        # 2. Get the grandparent.
        # --------------------------------------------------

        grandparent = parent.locator("..")

        grandparent_text = (
            await grandparent.inner_text()
        ).strip()

        # --------------------------------------------------
        # 3. Clean extra whitespace.
        # --------------------------------------------------

        parent_text = " ".join(
            parent_text.split()
        )

        grandparent_text = " ".join(
            grandparent_text.split()
        )

        # --------------------------------------------------
        # 4. Prefer immediate parent text.
        # --------------------------------------------------

        if parent_text:

            # Limit local context.
            if len(parent_text) > 250:
                parent_text = parent_text[:250]

            return {
                "parent_text": parent_text,
                "grandparent_text": (
                    grandparent_text[:300]
                    if grandparent_text
                    else ""
                )
            }

        # --------------------------------------------------
        # 5. If parent is empty, use grandparent.
        # --------------------------------------------------

        if grandparent_text:

            if len(grandparent_text) > 300:
                grandparent_text = (
                    grandparent_text[:300]
                )

            return {
                "parent_text": "",
                "grandparent_text": grandparent_text
            }

        # --------------------------------------------------
        # 6. Nothing useful found.
        # --------------------------------------------------

        return {
            "parent_text": "",
            "grandparent_text": ""
        }

    async def get_elements(self):

        # Store all perceived elements.
        elements = []

        # Reset the element map because the page
        # may have changed.
        self.element_map = {}

        # AURA element counter.
        counter = 1

        # ==================================================
        # NATIVE INPUT ELEMENTS
        # ==================================================

        inputs = await self.page.locator(
            "input"
        ).all()

        for element in inputs:

            # Create an AURA element ID.
            element_id = f"e{counter}"

            counter += 1

            # Get actual HTML input type.
            element_type = await element.get_attribute(
                "type"
            )

            # Get HTML name.
            name = await element.get_attribute(
                "name"
            )

            # Get placeholder.
            placeholder = await element.get_attribute(
                "placeholder"
            )

            # Check whether the input is required.
            required = await element.get_attribute(
                "required"
            )

            # Find semantic label.
            label = await self.get_label(
                element
            )

            # Get surrounding context.
            context = await self.get_context(
                element
            )

            # Build semantic element information.
            element_data = {
                "id": element_id,

                "role": self.get_input_role(
                    element_type
                ),

                # Keep the original HTML type.
                "type": element_type,

                "name": name,

                "label": label,

                "placeholder": placeholder,

                "required": required is not None,

                "context": context
            }

            # Add the element to our list.
            elements.append(
                element_data
            )

            # Map AURA ID to the real Playwright element.
            self.element_map[
                element_id
            ] = element

        # ==================================================
        # NATIVE BUTTONS
        # ==================================================

        buttons = await self.page.locator(
            "button"
        ).all()

        for element in buttons:

            element_id = f"e{counter}"

            counter += 1

            # Get visible button text.
            text = (
                await element.inner_text()
            ).strip()

            # Get surrounding context.
            context = await self.get_context(
                element
            )

            element_data = {
                "id": element_id,
                "role": "button",
                "text": text,
                "context": context
            }

            elements.append(
                element_data
            )

            self.element_map[
                element_id
            ] = element

        # ==================================================
        # NATIVE LINKS
        # ==================================================

        links = await self.page.locator(
            "a"
        ).all()

        for element in links:

            element_id = f"e{counter}"

            counter += 1

            # Get visible link text.
            text = (
                await element.inner_text()
            ).strip()

            # Get surrounding context.
            context = await self.get_context(
                element
            )

            element_data = {
                "id": element_id,
                "role": "link",
                "text": text,
                "context": context
            }

            elements.append(
                element_data
            )

            self.element_map[
                element_id
            ] = element

        # ==================================================
        # ARIA ELEMENTS
        # ==================================================

        aria_elements = await self.page.locator(
            '[role="button"], '
            '[role="textbox"], '
            '[role="radio"], '
            '[role="checkbox"], '
            '[role="combobox"], '
            '[role="link"]'
        ).all()

        for element in aria_elements:

            element_id = f"e{counter}"

            counter += 1

            # Get ARIA role.
            role = await element.get_attribute(
                "role"
            )

            # Get accessible label.
            aria_label = await element.get_attribute(
                "aria-label"
            )

            # Get visible text.
            text = (
                await element.inner_text()
            ).strip()

            # Get surrounding context.
            context = await self.get_context(
                element
            )

            element_data = {
                "id": element_id,
                "role": role,
                "label": aria_label,
                "text": text,
                "context": context
            }

            elements.append(
                element_data
            )

            self.element_map[
                element_id
            ] = element

        # Return all perceived elements.
        return elements

    def get_input_role(self, input_type):
        """
        Convert HTML input types into semantic roles.

        The original HTML type is still stored separately.
        """

        roles = {
            "text": "textbox",
            "email": "textbox",
            "password": "textbox",
            "number": "spinbutton",
            "radio": "radio",
            "checkbox": "checkbox",
            "date": "date"
        }

        return roles.get(
            input_type,
            "input"
        )

    def get_element(self, element_id):

        # Return the actual Playwright element
        # associated with an AURA element ID.
        return self.element_map.get(
            element_id
        )