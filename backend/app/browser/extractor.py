# Import the QuestionField model.
# This is the structure we want to create
# for every discovered question.
from app.browser.question import QuestionField


class QuestionExtractor:

    def __init__(self, perception):

        # Store the PagePerception object.
        #
        # The extractor will ask perception
        # for all elements on the webpage.
        self.perception = perception

    async def extract(self):

        # Ask the perception layer to inspect the webpage.
        elements = await self.perception.get_elements()

        # This list will contain only actual
        # question/input fields.
        questions = []

        # Examine every element found by perception.
        for element in elements:

            # Get the semantic role.
            role = element.get("role")

            # Ignore elements that cannot represent
            # user input.
            if role not in [
                "textbox",
                "spinbutton",
                "radio",
                "checkbox",
                "combobox"
            ]:
                continue

            # Convert the webpage role into our
            # QuestionField type.
            field_type = self.get_field_type(
                element
            )

            # Get the label/question.
            question = element.get("label")

            # Get context information.
            context_data = element.get(
                "context",
                {}
            )

            # Get the surrounding text.
            context = context_data.get(
                "parent_text"
            )

            # Create a validated QuestionField.
            question_field = QuestionField(
                element_id=element["id"],
                field_type=field_type,
                question=question,
                required=element.get(
                    "required",
                    False
                ),
                context=context
            )

            # Add the question to our list.
            questions.append(
                question_field
            )

        # Return all discovered questions.
        return questions

    def get_field_type(self, element):

        # Get the semantic role.
        role = element.get("role")

        # Text/email/password fields.
        if role == "textbox":
            return "text"

        # Number field.
        if role == "spinbutton":
            return "number"

        # Radio button.
        if role == "radio":
            return "radio"

        # Checkbox.
        if role == "checkbox":
            return "checkbox"

        # Dropdown/combobox.
        if role == "combobox":
            return "select"

        # Unknown field.
        return "unknown"