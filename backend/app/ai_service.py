"""
AI Service - Handles communication with OpenAI API.

This module sends the telematics report data along with the appropriate
system prompt (based on user profile) to OpenAI's chat completion API.
"""

import os
import json
from openai import OpenAI
from .prompts import SYSTEM_PROMPTS, USER_PROMPT_TEMPLATE


def get_openai_client() -> OpenAI:
    """
    Creates and returns an OpenAI client.
    The API key is read from the OPENAI_API_KEY environment variable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-api-key-here":
        raise ValueError(
            "OPENAI_API_KEY is not configured. "
            "Please set it in the .env file."
        )
    return OpenAI(api_key=api_key)


def interpret_report(report_data: dict, profile: str) -> dict:
    """
    Sends the report data to OpenAI for interpretation.

    Args:
        report_data: The telematics report as a dictionary.
        profile: The user profile ('gerente' or 'operaciones').

    Returns:
        A dictionary with the interpretation, model used, and tokens consumed.
    """
    # Get the system prompt for the selected profile
    system_prompt = SYSTEM_PROMPTS.get(profile)
    if not system_prompt:
        raise ValueError(f"Unknown profile: {profile}")

    # Format the report data as a readable JSON string
    report_json = json.dumps(report_data, indent=2, ensure_ascii=False)

    # Build the user message with the report data
    user_message = USER_PROMPT_TEMPLATE.format(report_json=report_json)

    # Get the model name from environment (default: gpt-4o-mini)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Create the OpenAI client and make the API call
    client = get_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    # Extract the response content and metadata
    interpretation = response.choices[0].message.content
    tokens_used = response.usage.total_tokens if response.usage else None

    return {
        "interpretation": interpretation,
        "model_used": model,
        "tokens_used": tokens_used,
    }
