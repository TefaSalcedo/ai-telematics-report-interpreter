"""
AI Service - Handles communication with Groq API.

This module sends the telematics report data along with the appropriate
system prompt (based on user profile) to Groq's chat completion API.

Groq provides FREE access to powerful open-source models like Llama 3.3 70B.
Get your free API key at: https://console.groq.com/keys
"""

import os
import json
from groq import Groq
from .prompts import SYSTEM_PROMPTS, USER_PROMPT_TEMPLATE


def get_groq_client() -> Groq:
    """
    Creates and returns a Groq client.
    The API key is read from the GROQ_API_KEY environment variable.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "paste-your-groq-api-key-here":
        raise ValueError(
            "GROQ_API_KEY is not configured. "
            "Please set it in the backend/.env file. "
            "Get your FREE key at https://console.groq.com/keys"
        )
    return Groq(api_key=api_key)


def interpret_report(report_data: dict, profile: str) -> dict:
    """
    Sends the report data to Groq for interpretation.

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

    # Get the model name from environment (default: llama-3.3-70b-versatile)
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Create the Groq client and make the API call
    client = get_groq_client()
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
