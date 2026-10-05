
from typing import Optional


class PagePerception:
    """
    PagePerception is responsible for OBSERVING the webpage.

    Important:
    This class should collect facts from the webpage.
    It should NOT decide whether an element is relevant to the
    user's task. That reasoning will be handled later by relevance.py.
    """

    def __init__(self, page):
        """
        Store the Playwright page object.

        element_map:
            AURA gives every discovered element an internal ID such as
            e1, e2, e3...

            Example:

                e1 -> search box
                e2 -> first name input
                e3 -> submit button

            The actual Playwright element is stored internally so
            BrowserActions can later use the AURA ID.
        """

        self.page = page

        # Maps AURA element IDs to actual Playwright elements.
        self.element_map = {}

    # ============================================================
    # 1. GET LABEL
    # ============================================================

    async def get_label(self, element):
        """
        Try to find the human-readable label of an element.

        We check several possible sources because websites can
        describe an input in different ways.

        Priority:

        1. aria-label
        2. <label for="...">
        3. aria-labelledby
        4. placeholder
        5. name
        """

        # --------------------------------------------------------
        # Check aria-label
        # --------------------------------------------------------

        aria_label = await element.get_attribute("aria-label")

        if aria_label:
            return aria_label.strip()

        # --------------------------------------------------------
        # Check <label for="element-id">
        # --------------------------------------------------------

        element_id = await element.get_attribute("id")

        if element_id:
            label = self.page.locator(
                f'label[for="{element_id}"]'
            )

            if await label.count() > 0:
                label_text = await label.first.inner_text()

                if label_text:
                    return label_text.strip()

        # --------------------------------------------------------
        # Check aria-labelledby
        # --------------------------------------------------------

        labelledby = await element.get_attribute("aria-labelledby")

        if labelledby:
            label_ids = labelledby.split()

            texts = []

            for label_id in label_ids:

                label = self.page.locator(
                    f"#{label_id}"
                )

                if await label.count() > 0:

                    text = await label.first.inner_text()

                    if text:
                        texts.append(text.strip())

            if texts:
                return " ".join(texts)

        # --------------------------------------------------------
        # Check placeholder
        # --------------------------------------------------------

        placeholder = await element.get_attribute("placeholder")

        if placeholder:
            return placeholder.strip()

        # --------------------------------------------------------
        # Check name
        # --------------------------------------------------------

        name = await element.get_attribute("name")

        if name:
            return name.strip()

        # --------------------------------------------------------
        # Nothing found
        # --------------------------------------------------------

        return None

    # ============================================================
    # 2. GET CONTEXT
    # ============================================================

    async def get_context(self, element):
        """
        Get surrounding text of an element.

        Example:

            <div>
                Student Information
                <input name="roll">
            </div>

        The context may help AURA understand that the input
        belongs to "Student Information".

        We collect text from the parent and grandparent.
        """

        context = await element.evaluate(
            """
            (element) => {

                const parent = element.parentElement;

                const grandparent =
                    parent ? parent.parentElement : null;

                return {
                    parent_text: parent ? parent.innerText : null,
                    grandparent_text:
                        grandparent ? grandparent.innerText : null
                };
            }
            """
        )

        parent_text = context.get("parent_text")
        grandparent_text = context.get("grandparent_text")

        # --------------------------------------------------------
        # Clean parent text
        # --------------------------------------------------------

        if parent_text:

            parent_text = " ".join(
                parent_text.split()
            )

            # Prevent extremely large context.
            parent_text = parent_text[:500]

        # --------------------------------------------------------
        # Clean grandparent text
        # --------------------------------------------------------

        if grandparent_text:

            grandparent_text = " ".join(
                grandparent_text.split()
            )

            grandparent_text = grandparent_text[:500]

        # --------------------------------------------------------
        # Prefer parent context
        # --------------------------------------------------------

        if parent_text:
            return parent_text

        if grandparent_text:
            return grandparent_text

        return None

    # ============================================================
    # 3. NEW: GET FORM CONTEXT
    # ============================================================

    async def get_form_context(self, element):
        """
        Find the form relationship of an element.

        IMPORTANT:
        An HTML element can be related to a form in TWO ways.

        CASE 1:
            The element is physically inside <form>.

            Example:

                <form id="studentForm">
                    <input name="name">
                </form>

        CASE 2:
            The element is outside the <form>, but uses
            the HTML 'form' attribute.

            Example:

                <form id="studentForm">
                </form>

                <input name="name" form="studentForm">

        We must support BOTH cases.

        This method ONLY COLLECTS FACTS.

        It does NOT decide whether the element is relevant.
        """

        # --------------------------------------------------------
        # Run JavaScript inside the browser.
        # --------------------------------------------------------

        form_info = await element.evaluate(
            """
            (element) => {

                // =================================================
                // CASE 1:
                // Check whether the element is physically inside
                // a <form> element.
                // =================================================

                let form = element.closest("form");

                let relationship = null;

                if (form) {

                    relationship = "ancestor";

                } else {

                    // =============================================
                    // CASE 2:
                    // Check HTML's 'form' attribute.
                    //
                    // Example:
                    //
                    // <input form="studentForm">
                    //
                    // Find:
                    //
                    // <form id="studentForm">
                    // =============================================

                    const formId =
                        element.getAttribute("form");

                    if (formId) {

                        form = document.getElementById(formId);

                        if (
                            form &&
                            form.tagName.toLowerCase() === "form"
                        ) {

                            relationship = "form_attribute";

                        } else {

                            // The element has a form attribute,
                            // but the referenced form does not exist
                            // or is not actually a <form>.
                            form = null;

                        }
                    }
                }

                // =================================================
                // No form relationship found
                // =================================================

                if (!form) {

                    return {
                        associated: false,

                        relationship: null,

                        form_id: null,

                        form_name: null,

                        form_action: null,

                        form_method: null,

                        form_text: null
                    };
                }

                // =================================================
                // Form was found.
                // Collect information about it.
                // =================================================

                return {

                    associated: true,

                    relationship: relationship,

                    form_id:
                        form.getAttribute("id"),

                    form_name:
                        form.getAttribute("name"),

                    form_action:
                        form.getAttribute("action"),

                    form_method:
                        form.getAttribute("method"),

                    form_text:
                        form.innerText
                };
            }
            """
        )

        # ========================================================
        # Clean form text
        # ========================================================

        form_text = form_info.get("form_text")

        if form_text:

            # Convert multiple spaces/newlines into
            # normal single spaces.

            form_text = " ".join(
                form_text.split()
            )

            # Do not allow huge amounts of text
            # to be sent to Gemini later.

            form_text = form_text[:500]

        # ========================================================
        # Return structured form information
        # ========================================================

        return {

            "associated":
                form_info.get("associated", False),

            "relationship":
                form_info.get("relationship"),

            "form_id":
                form_info.get("form_id"),

            "form_name":
                form_info.get("form_name"),

            "form_action":
                form_info.get("form_action"),

            "form_method":
                form_info.get("form_method"),

            "form_text":
                form_text
        }

    # ============================================================
    # 4. CHECK ACTIONABILITY
    # ============================================================

    async def is_actionable(self, element):
        """
        Check whether an element is currently usable.

        We require:

            visible == True
            enabled == True

        This prevents AURA from trying to interact with hidden
        or disabled elements.
        """

        try:

            visible = await element.is_visible()

            enabled = await element.is_enabled()

            return visible and enabled

        except Exception:

            # If Playwright cannot inspect the element,
            # treat it as non-actionable.

            return False

    # ============================================================
    # 5. GET INPUT ROLE
    # ============================================================

    async def get_input_role(self, element):
        """
        Determine what kind of interactive element this is.

        Examples:

            text input      -> textbox
            number input    -> spinbutton
            checkbox        -> checkbox
            radio           -> radio
            select          -> combobox
            textarea        -> textbox
            button          -> button
            link             -> link
        """

        tag_name = await element.evaluate(
            "(element) => element.tagName.toLowerCase()"
        )

        # --------------------------------------------------------
        # INPUT
        # --------------------------------------------------------

        if tag_name == "input":

            input_type = (
                await element.get_attribute("type")
            )

            input_type = (
                input_type.lower()
                if input_type
                else "text"
            )

            role_map = {

                "text": "textbox",

                "email": "textbox",

                "password": "textbox",

                "search": "textbox",

                "tel": "textbox",

                "url": "textbox",

                "number": "spinbutton",

                "radio": "radio",

                "checkbox": "checkbox",

                "date": "textbox",

                "datetime-local": "textbox",

                "month": "textbox",

                "week": "textbox",

                "time": "textbox",

                "file": "file"
            }

            return role_map.get(
                input_type,
                "textbox"
            )

        # --------------------------------------------------------
        # TEXTAREA
        # --------------------------------------------------------

        if tag_name == "textarea":

            return "textbox"

        # --------------------------------------------------------
        # SELECT
        # --------------------------------------------------------

        if tag_name == "select":

            return "combobox"

        # --------------------------------------------------------
        # BUTTON
        # --------------------------------------------------------

        if tag_name == "button":

            return "button"

        # --------------------------------------------------------
        # LINK
        # --------------------------------------------------------

        if tag_name == "a":

            return "link"

        # --------------------------------------------------------
        # ARIA ROLE
        # --------------------------------------------------------

        aria_role = await element.get_attribute("role")

        if aria_role:

            return aria_role

        return "unknown"

    # ============================================================
    # 6. GET ALL ELEMENTS
    # ============================================================

    async def get_elements(self):
        """
        Scan the webpage and return actionable interactive elements.

        AURA currently looks for:

            input
            textarea
            select
            button
            a

        It also checks ARIA interactive elements.

        Each element receives an AURA ID:

            e1
            e2
            e3
            ...

        IMPORTANT:
        We DO NOT remove elements merely because two elements
        have the same label or name.

        Two separate DOM elements may legitimately represent
        two separate fields.
        """

        # --------------------------------------------------------
        # Reset element map before every perception cycle.
        # --------------------------------------------------------

        self.element_map = {}

        elements = []

        element_counter = 1

        # ========================================================
        # PART 1:
        # Standard HTML interactive elements
        # ========================================================

        locator = self.page.locator(
            "input, textarea, select, button, a"
        )

        count = await locator.count()

        for index in range(count):

            element = locator.nth(index)

            # ----------------------------------------------------
            # Ignore hidden/disabled elements.
            # ----------------------------------------------------

            if not await self.is_actionable(element):
                continue

            # ----------------------------------------------------
            # Create AURA element ID.
            # ----------------------------------------------------

            element_id = f"e{element_counter}"

            element_counter += 1

            # ----------------------------------------------------
            # Get basic element information.
            # ----------------------------------------------------

            role = await self.get_input_role(element)

            input_type = await element.get_attribute(
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

            # ----------------------------------------------------
            # Get semantic information.
            # ----------------------------------------------------

            label = await self.get_label(element)

            context = await self.get_context(element)

            # ----------------------------------------------------
            # NEW:
            # Get form relationship.
            # ----------------------------------------------------

            form_context = await self.get_form_context(
                element
            )

            # ----------------------------------------------------
            # Store actual Playwright element internally.
            #
            # BrowserActions will later use this mapping.
            # ----------------------------------------------------

            self.element_map[element_id] = {
                "element": element,
                "id": element_id,
                "role": role,
                "type": input_type,
                "name": name,
                "label": label,
                "placeholder": placeholder,
                "required": bool(required),
                "context": {
                    "parent_text": context
                },
                "form_context": form_context
            }

            # ----------------------------------------------------
            # Return CLEAN information.
            #
            # We do not return the Playwright object because
            # Gemini cannot use it.
            # ----------------------------------------------------

            elements.append({

                "id": element_id,

                "role": role,

                "type": input_type,

                "name": name,

                "label": label,

                "placeholder": placeholder,

                "required": bool(required),

                "context": {
                    "parent_text": context
                },

                "form_context": form_context
            })

        # ========================================================
        # PART 2:
        # ARIA interactive elements
        # ========================================================

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

            # ----------------------------------------------------
            # Ignore hidden/disabled ARIA elements.
            # ----------------------------------------------------

            if not await self.is_actionable(element):
                continue

            # ----------------------------------------------------
            # Avoid adding the same physical element twice.
            #
            # Some native elements may also have an ARIA role.
            # ----------------------------------------------------

            already_exists = False

            for existing in self.element_map.values():

                existing_element = existing["element"]

                try:

                    same_element = await element.evaluate(
                        """
                        (element, other) => element === other
                        """,
                        existing_element
                    )

                    if same_element:

                        already_exists = True

                        break

                except Exception:

                    pass

            if already_exists:
                continue

            # ----------------------------------------------------
            # Create AURA ID.
            # ----------------------------------------------------

            element_id = f"e{element_counter}"

            element_counter += 1

            # ----------------------------------------------------
            # Collect information.
            # ----------------------------------------------------

            role = await self.get_input_role(element)

            input_type = await element.get_attribute(
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

            label = await self.get_label(element)

            context = await self.get_context(element)

            # ----------------------------------------------------
            # NEW:
            # Get form relationship for ARIA elements too.
            # ----------------------------------------------------

            form_context = await self.get_form_context(
                element
            )

            # ----------------------------------------------------
            # Store actual Playwright element.
            # ----------------------------------------------------

            self.element_map[element_id] = {

                "element": element,

                "id": element_id,

                "role": role,

                "type": input_type,

                "name": name,

                "label": label,

                "placeholder": placeholder,

                "required": bool(required),

                "context": {
                    "parent_text": context
                },

                "form_context": form_context
            }

            # ----------------------------------------------------
            # Add clean information to result.
            # ----------------------------------------------------

            elements.append({

                "id": element_id,

                "role": role,

                "type": input_type,

                "name": name,

                "label": label,

                "placeholder": placeholder,

                "required": bool(required),

                "context": {
                    "parent_text": context
                },

                "form_context": form_context
            })

        # ========================================================
        # Return all discovered elements.
        # ========================================================

        return elements

    # ============================================================
    # 7. GET ACTUAL PLAYWRIGHT ELEMENT
    # ============================================================

    def get_element(self, element_id):
        """
        Convert an AURA element ID such as 'e5'
        back into the actual Playwright element.

        Example:

            AURA:
                e5

            BrowserActions:
                get_element("e5")

            Result:
                actual Playwright locator/element
        """

        data = self.element_map.get(element_id)

        if not data:
            return None

        return data["element"]
