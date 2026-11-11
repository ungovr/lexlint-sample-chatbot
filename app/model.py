"""The language-model call that writes each reply to a customer."""

import os

import httpx

MODEL_API_URL = os.environ.get("MODEL_API_URL", "")
MODEL_API_KEY = os.environ.get("MODEL_API_KEY", "")

SYSTEM_PROMPT = (
    "You are the support assistant for {business}. Answer the customer's "
    "question about their order, account or our products in a friendly, "
    "concise way. If you cannot help, offer to pass them to a person."
)


def write_reply(business_id: str, customer_name: str, history: list[dict], message: str) -> str:
    """Ask the model for the next reply in the conversation and return its text."""
    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT.format(business=business_id)},
        *({"role": "user" if m["role"] == "customer" else "assistant", "content": m["text"]} for m in history),
        {"role": "user", "content": f"{customer_name}: {message}"},
    ]
    response = httpx.post(
        MODEL_API_URL,
        headers={"Authorization": f"Bearer {MODEL_API_KEY}"},
        json={"messages": prompt, "max_tokens": 400},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["text"].strip()
