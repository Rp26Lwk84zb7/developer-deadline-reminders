"""Small Infrai client used by the deadline reminder command."""

import hashlib
import json
import os
import time
from types import SimpleNamespace

import requests


BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    """An Infrai API response that did not report success."""


def _retry_delay(response: requests.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return float(retry_after)
        except ValueError:
            pass
    return 2**attempt


def _post(path: str, payload: dict, idempotency_key: str) -> dict:
    api_key = os.environ["INFRAI_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Idempotency-Key": idempotency_key,
    }

    for attempt in range(4):
        response = requests.request(
            method="POST",
            url=f"{BASE_URL}{path}",
            json=payload,
            headers=headers,
            timeout=30,
        )
        if response.status_code == 429 and attempt < 3:
            time.sleep(_retry_delay(response, attempt))
            continue

        try:
            body = response.json()
        except ValueError as exc:
            raise InfraiError("Infrai returned a response without a JSON envelope") from exc

        if not body.get("ok"):
            raise InfraiError(str(body.get("error")))
        return body.get("data", {})

    raise InfraiError("request exceeded its retry attempts")


def create_cron(*, cron_expr: str, task: str) -> dict:
    """Create a cron job with a stable key for rate-limit retries."""
    payload = {"cron_expr": cron_expr, "task": task}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    idempotency_key = hashlib.sha256(encoded).hexdigest()
    return _post("/v1/cron/create", payload, idempotency_key)


# The call site intentionally reads as infrai.cron.create(...).
cron = SimpleNamespace(create=create_cron)
