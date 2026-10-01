# This class is responsible for understanding what is currently
# visible and interactive on the webpage.
class PagePerception:

    def __init__(self, page):

        # Store the Playwright Page object.
        # We use this object to inspect and interact with the webpage.
        self.page = page

        # Maps AURA IDs such as "e1" to actual Playwright elements.
        self.element_map = {}

    async def get_page_info(self):

        # Return basic information about the current webpage.
        return {
            "url": self.page.url,
            "title": await self.page.title()
        }

    async def get_label(self, element):

        # First try aria-label because it directly describes
        # the accessible name of an element.
        label = await element.get_attribute("aria-label")

        if label:
            return label.strip()

        # Get the HTML id of the element.
        element_id = await element.get_attribute("id")

        # If the element has an id, search for:
        # <label for="that-id">...</label>
        if element_id:

            label_locator = self.page.locator(
                f'label[for="{element_id}"]'
            )

            if await label_locator.count() > 0:

                return (
                    await label_locator.first.inner_text()
                ).strip()

        # Try the placeholder as another source of meaning.
        placeholder = await element.get_attribute(
            "placeholder"
        )

        if placeholder:
            return placeholder.strip()

        # Try the name attribute.
        name = await element.get_attribute("name")

        if name:
            return name.strip()

        # No useful label was found.
        return None

    async def get_context(self, element):

        # First try to find the label associated with the element.
        label = await self.get_label(element)

        # Find the nearest parent element.
        parent = element.locator("..")

        # Get text from that parent.
        parent_text = (
            await parent.inner_text()
        ).strip()

        # Limit the amount of context we collect.
        # Very large parent containers can contain unrelated text.
        if len(parent_text) > 500:
            parent_text = parent_text[:500]

        # Return all useful contextual information.
        return {
            "label": label,
            "parent_text": parent_text
        }

    async def get_elements(self):

        # Store all perceived elements here.
        elements = []

        # Reset the element map every time we perceive
        # the webpage because the page may have changed.
        self.element_map = {}

        # AURA element counter.
        counter = 1

        # Find all native input elements.
        inputs = await self.page.locator("input").all()

        for element in inputs:

            # Give the element an AURA ID.
            element_id = f"e{counter}"

            counter += 1

            # Read the input attributes.
            element_type = await element.get_attribute(
                "type"
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

            # Find the semantic label.
            label = await self.get_label(element)

            # Find surrounding context.
            context = await self.get_context(element)

            # Build the semantic representation of this element.
            element_data = {
                "id": element_id,
                "role": self.get_input_role(
                    element_type
                ),
                "type": element_type,
                "name": name,
                "label": label,
                "placeholder": placeholder,
                "required": required is not None,
                "context": context
            }

            # Add the semantic information to our list.
            elements.append(element_data)

            # Save the actual Playwright element.
            self.element_map[element_id] = element

        # Find all native buttons.
        buttons = await self.page.locator(
            "button"
        ).all()

        for element in buttons:

            # Give the button an AURA ID.
            element_id = f"e{counter}"

            counter += 1

            # Get the visible button text.
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

            elements.append(element_data)

            # Store the real Playwright element.
            self.element_map[element_id] = element

        # Find all links.
        links = await self.page.locator(
            "a"
        ).all()

        for element in links:

            # Give the link an AURA ID.
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

            elements.append(element_data)

            # Store the real Playwright element.
            self.element_map[element_id] = element

        return elements

    def get_input_role(self, input_type):

        # Convert HTML input types into semantic roles.
        roles = {
            "text": "textbox",
            "email": "textbox",
            "password": "textbox",
            "number": "spinbutton",
            "radio": "radio",
            "checkbox": "checkbox",
            "date": "date"
        }

        # Return the matching role.
        # If the type isn't known, return "input".
        return roles.get(
            input_type,
            "input"
        )

    def get_element(self, element_id):

        # Find the actual Playwright element associated
        # with an AURA element ID.
        return self.element_map.get(
            element_id
        )