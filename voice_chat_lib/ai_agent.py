from __future__ import annotations

import json
import urllib.error
import urllib.request

from voice_chat_lib.config import AIConfig


def request_chat_reply(
    user_text: str,
    ai_config: AIConfig,
    history: list[dict[str, str]] | None = None,
) -> str:
    messages: list[dict[str, str]] = [{"role": "system", "content": ai_config.system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": ai_config.model_name,
        "temperature": ai_config.temperature,
        "messages": messages,
    }

    request = urllib.request.Request(
        ai_config.api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=ai_config.timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP error {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Connection error: {exc}") from exc

    data = json.loads(body)
    choices = data.get("choices")
    if not choices:
        raise RuntimeError(f"Invalid response: {data}")

    content = choices[0].get("message", {}).get("content")
    if not content:
        raise RuntimeError(f"No message content in response: {data}")

    return content.strip()
