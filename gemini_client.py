"""
Zero-dependency Google Gemini Interactions API client (Python stdlib only).

Uses the stable Gemini Interactions API (`POST /v1/interactions`) with the
`x-goog-api-key` header, plus `POST /v1beta/decisions` for calibrated
classification via `gemini-decision-1`.
"""

import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from config import (
    GEMINI_API_KEY,
    GEMINI_API_VERSION,
    GEMINI_MODEL,
    GEMINI_TIMEOUT_SECONDS,
)

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com"
DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_DECISION_MODEL = "gemini-decision-1"
RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)


class GeminiAPIError(RuntimeError):
    """Raised when the Gemini REST API returns an error or network failure."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.response_body = response_body


class GeminiInteraction:
    """Wrapper around a Gemini Interactions API JSON response."""

    def __init__(self, raw: Dict[str, Any]):
        self.raw = raw
        self.id: Optional[str] = raw.get("id")
        self.status: Optional[str] = raw.get("status")
        self.model: Optional[str] = raw.get("model")
        self.steps: List[Dict[str, Any]] = raw.get("steps") or []
        self.usage: Dict[str, Any] = raw.get("usage") or {}

    @property
    def output_text(self) -> Optional[str]:
        """
        Matches the official SDK `interaction.output_text` semantics:
        the last consecutive run of text parts from trailing `model_output` steps.
        """
        trailing_text_parts: List[str] = []
        found_model_output = False

        for step in reversed(self.steps):
            if step.get("type") != "model_output":
                if found_model_output:
                    break
                continue

            found_model_output = True
            step_texts: List[str] = []
            for part in step.get("content") or []:
                if part.get("type") == "text" and isinstance(part.get("text"), str):
                    step_texts.append(part["text"])

            if step_texts:
                trailing_text_parts = step_texts + trailing_text_parts

        if not trailing_text_parts:
            return None
        return "".join(trailing_text_parts)

    def parse_json(self) -> Any:
        """Parses `output_text` as JSON, stripping optional code fences if present."""
        text = self.output_text
        if not text:
            raise ValueError("Interaction response contains no text output.")

        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if len(lines) >= 2 and lines[-1].strip() == "```":
                cleaned = "\n".join(lines[1:-1]).strip()
        return json.loads(cleaned)


class GeminiClient:
    """Zero-dependency HTTP client for the Gemini Interactions & Decisions APIs."""

    def __init__(
        self,
        api_key: str = GEMINI_API_KEY,
        default_model: str = GEMINI_MODEL,
        api_version: str = GEMINI_API_VERSION,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = GEMINI_TIMEOUT_SECONDS,
        max_retries: int = 2,
    ):
        self.api_key = (api_key or "").strip()
        self.default_model = (default_model or DEFAULT_MODEL).strip()
        self.api_version = (api_version or "v1").strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def create_interaction(
        self,
        input_data: Any,
        model: Optional[str] = None,
        system_instruction: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        previous_interaction_id: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        store: Optional[bool] = None,
        api_version: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> GeminiInteraction:
        """Calls `POST /{api_version}/interactions` and returns a GeminiInteraction."""
        payload: Dict[str, Any] = {
            "model": model or self.default_model,
            "input": input_data,
        }
        if system_instruction:
            payload["system_instruction"] = system_instruction
        if generation_config:
            payload["generation_config"] = generation_config
        if response_format:
            payload["response_format"] = response_format
        if previous_interaction_id:
            payload["previous_interaction_id"] = previous_interaction_id
        if tools:
            payload["tools"] = tools
        if store is not None:
            payload["store"] = store

        version = api_version or self.api_version
        raw = self._post_json(
            path=f"/{version}/interactions",
            payload=payload,
            timeout=timeout or self.timeout,
        )
        return GeminiInteraction(raw)

    def create_structured_json(
        self,
        input_data: Any,
        schema: Dict[str, Any],
        model: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        previous_interaction_id: Optional[str] = None,
        store: Optional[bool] = False,
        timeout: Optional[int] = None,
    ) -> Tuple[Any, GeminiInteraction]:
        """Requests schema-constrained JSON output via Interactions API."""
        generation_config: Dict[str, Any] = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_output_tokens is not None:
            generation_config["max_output_tokens"] = max_output_tokens

        interaction = self.create_interaction(
            input_data=input_data,
            model=model,
            system_instruction=system_instruction,
            generation_config=generation_config or None,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": schema,
            },
            previous_interaction_id=previous_interaction_id,
            store=store,
            timeout=timeout,
        )
        return interaction.parse_json(), interaction

    def create_decision(
        self,
        input_data: Any,
        questions: Dict[str, Dict[str, Any]],
        model: str = DEFAULT_DECISION_MODEL,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Calls `POST /v1beta/decisions` for calibrated yes/no, choice, or rubric scoring."""
        payload: Dict[str, Any] = {
            "model": model,
            "input": input_data,
            "questions": questions,
        }
        return self._post_json(
            path="/v1beta/decisions",
            payload=payload,
            timeout=timeout or self.timeout,
        )

    def health_check(self, model: Optional[str] = None) -> GeminiInteraction:
        """Runs a minimal, unstored Interactions API call to verify API key and connectivity."""
        return self.create_interaction(
            input_data="Reply with exactly: OK",
            model=model or self.default_model,
            generation_config={"max_output_tokens": 16},
            store=False,
            timeout=min(self.timeout, 20),
        )

    def _post_json(
        self,
        path: str,
        payload: Dict[str, Any],
        timeout: int,
    ) -> Dict[str, Any]:
        if not self.is_configured():
            raise GeminiAPIError(
                "GEMINI_API_KEY is not configured. Set it in .env or GitHub Secrets."
            )

        url = f"{self.base_url}{path}"
        body_bytes = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        last_error: Optional[Exception] = None
        attempts = self.max_retries + 1

        for attempt in range(attempts):
            req = urllib.request.Request(
                url,
                data=body_bytes,
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    raw_body = resp.read().decode("utf-8")
                    return json.loads(raw_body)
            except urllib.error.HTTPError as exc:
                raw_err = ""
                try:
                    raw_err = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    pass

                err_msg, err_code = self._parse_error_payload(raw_err, exc.reason)
                api_error = GeminiAPIError(
                    message=f"Gemini API HTTP {exc.code}: {err_msg}",
                    status_code=exc.code,
                    error_code=err_code,
                    response_body=raw_err,
                )
                last_error = api_error

                if exc.code in RETRYABLE_STATUS_CODES and attempt < attempts - 1:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                raise api_error from exc
            except urllib.error.URLError as exc:
                last_error = GeminiAPIError(
                    message=f"Gemini API network error: {exc.reason}"
                )
                if attempt < attempts - 1:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                raise last_error from exc
            except json.JSONDecodeError as exc:
                raise GeminiAPIError(
                    message=f"Gemini API returned invalid JSON: {exc}"
                ) from exc

        raise last_error or GeminiAPIError("Gemini API request failed.")

    @staticmethod
    def _parse_error_payload(raw_err: str, fallback: Any) -> Tuple[str, Optional[str]]:
        if not raw_err:
            return str(fallback), None
        try:
            parsed = json.loads(raw_err)
            if isinstance(parsed, list) and parsed:
                parsed = parsed[0]
            error_obj = parsed.get("error") if isinstance(parsed, dict) else None
            if isinstance(error_obj, dict):
                return (
                    str(error_obj.get("message") or fallback),
                    error_obj.get("status") or error_obj.get("code"),
                )
        except Exception:
            pass
        return raw_err[:300], None
