"""
app/llm/openai.py

Step 8 — OpenAI LLM provider.

Sends the system + user prompt to OpenAI's chat completion API and
returns the model's answer. Includes basic retry logic for transient
OpenAI server errors (5xx), since these happen occasionally even
when your code and account are fine.

Step 11 — added generate_answer_stream() for streaming responses.
"""

import time

from openai import OpenAI, InternalServerError, APIConnectionError

from app.config.llm import OPENAI_API_KEY, OPENAI_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

_client = OpenAI(api_key=OPENAI_API_KEY)


def generate_answer(system_prompt: str, user_prompt: str, max_retries: int = 3) -> str:
    """
    Send a system + user prompt to OpenAI and return the generated answer text.
    Retries automatically on transient server errors (not on bad requests
    or auth errors, which won't fix themselves by retrying).
    """
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = _client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=DEFAULT_MAX_TOKENS,
                temperature=DEFAULT_TEMPERATURE,
            )
            return response.choices[0].message.content

        except (InternalServerError, APIConnectionError) as e:
            last_error = e
            if attempt < max_retries:
                wait_time = 2 ** attempt  # 2s, 4s, 8s
                time.sleep(wait_time)
            continue

    raise last_error


def generate_answer_stream(system_prompt: str, user_prompt: str):
    """
    Same as generate_answer, but yields text chunks as they arrive
    from OpenAI, instead of waiting for the full response.
    """
    stream = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta