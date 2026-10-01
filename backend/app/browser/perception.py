class PagePerception:

    def __init__(self, page):
        self.page = page
        self.element_map = {}

    async def get_page_info(self):

        return {
            "url": self.page.url,
            "title": await self.page.title()
        }

    async def get_label(self, element):

        label = await element.get_attribute("aria-label")

        if label:
            return label.strip()

        element_id = await element.get_attribute("id")

        if element_id:

            label_locator = self.page.locator(
                f'label[for="{element_id}"]'
            )

            if await label_locator.count() > 0:

                return (
                    await label_locator.first.inner_text()
                ).strip()

        placeholder = await element.get_attribute(
            "placeholder"
        )

        if placeholder:
            return placeholder.strip()

        name = await element.get_attribute("name")

        if name:
            return name.strip()

        return None

    async def get_elements(self):

        elements = []

        self.element_map = {}

        counter = 1

        inputs = await self.page.locator("input").all()

        for element in inputs:

            element_id = f"e{counter}"

            counter += 1

            element_type = await element.get_attribute("type")
            name = await element.get_attribute("name")
            placeholder = await element.get_attribute(
                "placeholder"
            )
            required = await element.get_attribute(
                "required"
            )

            label = await self.get_label(element)

            element_data = {
                "id": element_id,
                "role": self.get_input_role(element_type),
                "type": element_type,
                "name": name,
                "label": label,
                "placeholder": placeholder,
                "required": required is not None
            }

            elements.append(element_data)

            self.element_map[element_id] = element

        buttons = await self.page.locator("button").all()

        for element in buttons:

            element_id = f"e{counter}"

            counter += 1

            text = (
                await element.inner_text()
            ).strip()

            element_data = {
                "id": element_id,
                "role": "button",
                "text": text
            }

            elements.append(element_data)

            self.element_map[element_id] = element

        links = await self.page.locator("a").all()

        for element in links:

            element_id = f"e{counter}"

            counter += 1

            text = (
                await element.inner_text()
            ).strip()

            element_data = {
                "id": element_id,
                "role": "link",
                "text": text
            }

            elements.append(element_data)

            self.element_map[element_id] = element

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

            role = await element.get_attribute("role")

            aria_label = await element.get_attribute(
                "aria-label"
            )

            text = (
                await element.inner_text()
            ).strip()

            element_data = {
                "id": element_id,
                "role": role,
                "label": aria_label,
                "text": text
            }

            elements.append(element_data)

            self.element_map[element_id] = element

        return elements

    def get_input_role(self, input_type):

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

        return self.element_map.get(element_id)