from typing import Literal

from pydantic import BaseModel, Field


class QuestionField(BaseModel):
    """
    Represents one logical question/field on a webpage.

    AURA uses this structure after perceiving the webpage
    and before asking Gemini to decide what to do.
    """

    # AURA's temporary ID for the actual browser element.
    # Example: "e9"
    element_id: str

    # Type of field.
    field_type: Literal[
        "text",
        "email",
        "number",
        "password",
        "date",
        "radio",
        "checkbox",
        "select",
        "textarea",
        "unknown"
    ]

    # Human-readable question or field label.
    # Example: "First name:"
    question: str | None = None

    # Options belonging to the field.
    #
    # For a radio question:
    # ["HTML", "CSS", "JavaScript"]
    #
    # For a checkbox group:
    # ["I have a bike", "I have a car", "I have a boat"]
    options: list[str] = Field(
        default_factory=list
    )

    # Whether the field is required.
    required: bool = False

    # Additional information surrounding the field.
    #
    # This is extremely important when two fields
    # have similar or identical labels.
    context: str | None = None

    # HTML name attribute.
    # Example: "fname"
    name: str | None = None

    # HTML placeholder.
    # Example: "Enter your first name"
    placeholder: str | None = None