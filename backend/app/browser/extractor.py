from app.browser.question import QuestionField


class QuestionExtractor:
    """
    Converts raw webpage elements into logical form questions.

    Perception gives us individual HTML elements.

    This class converts those elements into higher-level
    logical questions that AURA can reason about.
    """

    def __init__(self, perception):

        # Store the perception object.
        self.perception = perception

    async def extract(self):

        # Get all elements detected by perception.
        elements = await self.perception.get_elements()

        # First remove obvious duplicate elements.
        elements = self.remove_duplicates(elements)

        # Store the final logical questions.
        questions = []

        # Keep track of radio groups already processed.
        processed_radio_groups = set()

        # Keep track of checkbox groups already processed.
        processed_checkbox_groups = set()

        # Examine every perceived element.
        for element in elements:

            # Get the semantic role.
            role = element.get("role")

            # Ignore elements that are not form fields.
            if role not in [
                "textbox",
                "spinbutton",
                "radio",
                "checkbox",
                "combobox"
            ]:
                continue

            # -------------------------------------------------
            # RADIO GROUP
            # -------------------------------------------------

            if role == "radio":

                # Get the HTML name.
                name = element.get("name")

                # Use the name as the grouping key.
                group_key = name or element["id"]

                # If we already processed this radio group,
                # skip this individual radio button.
                if group_key in processed_radio_groups:
                    continue

                # Mark this group as processed.
                processed_radio_groups.add(group_key)

                # Find every radio button belonging to
                # the same HTML name.
                group = [
                    item
                    for item in elements
                    if item.get("role") == "radio"
                    and item.get("name") == name
                ]

                # Extract all option labels.
                options = []

                for item in group:

                    # Get the label of this radio option.
                    label = item.get("label")

                    # Add it if a label exists.
                    if label:
                        options.append(label)

                # Create one logical radio question.
                question = QuestionField(

                    # Use the first radio button as the
                    # representative browser element.
                    element_id=element["id"],

                    field_type="radio",

                    # The first option's label is not really
                    # the question, so we leave question empty
                    # for now. We will improve this using
                    # surrounding text later.
                    question=None,

                    # Store all radio options together.
                    options=options,

                    required=element.get(
                        "required",
                        False
                    ),

                    context=self.get_context(
                        element
                    ),

                    name=name,

                    placeholder=element.get(
                        "placeholder"
                    )
                )

                # Add the logical question.
                questions.append(question)

                continue

            # -------------------------------------------------
            # CHECKBOX
            # -------------------------------------------------

            if role == "checkbox":

                # For now, treat each checkbox as an
                # independently selectable field.
                question = QuestionField(

                    element_id=element["id"],

                    field_type="checkbox",

                    question=element.get("label"),

                    options=[],

                    required=element.get(
                        "required",
                        False
                    ),

                    context=self.get_context(
                        element
                    ),

                    name=element.get("name"),

                    placeholder=element.get(
                        "placeholder"
                    )
                )

                questions.append(question)

                continue

            # -------------------------------------------------
            # NORMAL INPUT
            # -------------------------------------------------

            question = QuestionField(

                element_id=element["id"],

                field_type=self.get_field_type(
                    element
                ),

                question=element.get(
                    "label"
                ),

                options=[],

                required=element.get(
                    "required",
                    False
                ),

                context=self.get_context(
                    element
                ),

                name=element.get("name"),

                placeholder=element.get(
                    "placeholder"
                )
            )

            questions.append(question)

        return questions

    def remove_duplicates(self, elements):
        """
        Remove duplicate representations of the same
        HTML input.

        We primarily use the combination of:
            tag/type + name + label

        as the temporary duplicate key.
        """

        unique_elements = []

        # Store keys that we have already seen.
        seen = set()

        for element in elements:

            # Get important identifying information.
            role = element.get("role")
            name = element.get("name")
            label = element.get("label")

            # Create a duplicate-detection key.
            key = (
                role,
                name,
                label
            )

            # If this exact combination was already seen,
            # ignore this element.
            if key in seen:
                continue

            # Remember this element.
            seen.add(key)

            # Keep it.
            unique_elements.append(element)

        return unique_elements

    def get_context(self, element):
        """
        Safely retrieve surrounding context.
        """

        context = element.get(
            "context",
            {}
        )

        return context.get(
            "parent_text"
        )

    def get_field_type(self, element):
        """
        Convert the perceived role into an
        AURA field type.
        """

        role = element.get("role")

        if role == "textbox":
            return "text"

        if role == "spinbutton":
            return "number"

        if role == "radio":
            return "radio"

        if role == "checkbox":
            return "checkbox"

        if role == "combobox":
            return "select"

        return "unknown"