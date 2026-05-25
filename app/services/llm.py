import os
import json
import urllib.request
import urllib.error
from typing import Tuple, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))


def _call_gemini(system: str, user_prompt: str) -> Tuple[str, Optional[int]]:

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment.")

    # Full prompt combining system + user
    full_prompt = f"{system}\n\n{user_prompt}"

    # Request body
    body = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": _TEMPERATURE,
            "maxOutputTokens": 1024
        }
    }

    body_bytes = json.dumps(body).encode("utf-8")

    # Try models in order until one works
    models_to_try = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-pro-latest",
        "gemini-pro"
    ]

    last_error = None

    for model_name in models_to_try:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={api_key}"
        )

        req = urllib.request.Request(
            url,
            data=body_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            logger.info(f"Trying model: {model_name}")
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            # Extract reply text
            reply = result["candidates"][0]["content"]["parts"][0]["text"].strip()

            # Extract token count if available
            tokens = None
            try:
                tokens = result["usageMetadata"]["totalTokenCount"]
                logger.info(f"Token usage - Total: {tokens} tokens")
            except Exception:
                pass

            logger.info(f"Success with model: {model_name}")
            return reply, tokens

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            logger.warning(f"Model {model_name} failed: {e.code} - {error_body}")
            last_error = f"{e.code}: {error_body}"
            continue

        except Exception as e:
            logger.warning(f"Model {model_name} error: {e}")
            last_error = str(e)
            continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


def call_llm(system_prompt: str, user_prompt: str) -> Tuple[str, Optional[int]]:
    """
    Calls Gemini via REST API.
    Returns: (reply: str, tokens_used: int | None)
    """
    logger.info("Calling Gemini LLM via REST API")

    try:
        reply, tokens = _call_gemini(system_prompt, user_prompt)
        return reply, tokens

    except ValueError as exc:
        logger.error(f"Config error: {exc}")
        raise RuntimeError(f"Invalid API key: {exc}") from exc

    except Exception as exc:
        err_str = str(exc).lower()
        if "429" in err_str or "rate" in err_str:
            raise RuntimeError("Rate limit exceeded. Try again later.") from exc
        if "401" in err_str or "403" in err_str or "api key" in err_str:
            raise RuntimeError("Invalid API key. Check your .env file.") from exc
        logger.error(f"Error: {exc}")
        raise RuntimeError(f"LLM service error: {exc}") from exc