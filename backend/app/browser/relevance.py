class TaskRelevance:

    def calculate_score(self, element):
        """
        Calculate a simple structural relevance score.

        IMPORTANT:

        This is NOT an AI probability.

        It is a deterministic score based on facts
        we know about the webpage.

        Higher score = stronger evidence that the
        element belongs to a task/form.
        """

        score = 0


        # -------------------------------------------------
        # FORM MEMBERSHIP
        # -------------------------------------------------
        # Being inside a real HTML form is strong evidence
        # that the element is part of a form-related task.
        form_context = element.get(
            "form_context",
            {}
        )

        if form_context.get("inside_form"):
            score += 40


        # -------------------------------------------------
        # LABEL
        # -------------------------------------------------
        # A human-readable label is useful evidence.
        label = element.get("label")

        if label:
            score += 10


        # -------------------------------------------------
        # NAME
        # -------------------------------------------------
        # HTML names such as:
        #
        # fname
        # email
        # phone
        #
        # can provide semantic information.
        name = element.get("name")

        if name:
            score += 10


        # -------------------------------------------------
        # CONTEXT
        # -------------------------------------------------
        # Nearby text helps identify the purpose
        # of the element.
        context = element.get(
            "context",
            {}
        )

        if context.get("parent_text"):
            score += 10


        # -------------------------------------------------
        # PLACEHOLDER
        # -------------------------------------------------
        # A placeholder can also describe the field.
        placeholder = element.get(
            "placeholder"
        )

        if placeholder:
            score += 5


        # -------------------------------------------------
        # REQUIRED ATTRIBUTE
        # -------------------------------------------------
        # Required fields are more likely to be
        # actual form/task fields.
        if element.get("required"):
            score += 5


        return score


    def classify(self, score):
        """
        Convert the numerical score into a simple
        category.

        These categories make debugging easier.
        """

        if score >= 60:
            return "high"

        if score >= 30:
            return "medium"

        return "low"