"""Lightweight client for calling the Groq API (or other HTTP LLM endpoints).

This module provides a minimal, dependency-free wrapper that posts prompts
to a configured endpoint. The exact payload/response shape may vary between
providers; this client assumes a common POST /v1/generate-like interface.
"""
from __future__ import annotations

import os
import logging
from typing import Optional, Dict, Any

import httpx

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.base_url = base_url or settings.GROQ_BASE_URL
        self.mock_mode = not bool(self.api_key)
        if not self.api_key:
            logger.warning("No GROQ_API_KEY configured; using local mock LLM responses for testing.")

    def generate(self, prompt: str, model: str = "llama-3.3-70b", temperature: float = 0.0, max_tokens: int = 1024) -> Dict[str, Any]:
        """Send a prompt to the LLM and return the raw response dict.

        This method attempts to call `<base_url>/v1/generate` with a JSON payload.
        When no API key is configured, a local mock response is returned for testing.
        """
        if self.mock_mode:
            return self._mock_generate(prompt, model=model, temperature=temperature, max_tokens=max_tokens)

        openai_url = f"{self.base_url.rstrip('/')}/openai/v1/responses"
        candidate_models = [
            model if str(model).startswith("openai/") else "openai/gpt-oss-20b",
            "openai/gpt-oss-7b",
            "openai/gpt-3.5-mini",
        ]

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        last_exception = None

        for openai_model in candidate_models:
            payload = {
                "model": openai_model,
                "input": prompt,
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            with httpx.Client(timeout=60.0) as client:
                try:
                    resp = client.post(openai_url, json=payload, headers=headers)
                    resp.raise_for_status()
                except Exception as exc:
                    logger.warning("LLM request failed for model %s: %s", openai_model, exc)
                    last_exception = exc
                    continue

                data = resp.json()
                if isinstance(data, dict):
                    if "output_text" in data and data.get("output_text") is not None:
                        return {"text": data.get("output_text"), "raw": data}
                    if "output" in data and isinstance(data["output"], list):
                        parts = []
                        for item in data["output"]:
                            for content in item.get("content", []):
                                if content.get("type") in ("output_text", "text", "reasoning_text"):
                                    t = content.get("text") or content.get("output_text")
                                    if t:
                                        parts.append(t)
                        if parts:
                            return {"text": "\n".join(parts), "raw": data}
                return data

        logger.exception("LLM request failed for all models. Last error: %s", last_exception)
        return self._mock_generate(prompt, model=model, temperature=temperature, max_tokens=max_tokens)

    def _mock_generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Generate a simple mock response when no LLM API key is configured."""
        lower_prompt = prompt.lower()
        # Heuristic mock: prefer to echo the first context snippet if available,
        # otherwise give a conservative 'not found' reply.
        answer = None
        try:
            if "context snippets:" in lower_prompt:
                # extract the block after 'context snippets:' and take the first snippet
                tail = prompt.split("Context snippets:", 1)[1]
                # snippets are separated by blank lines; pick the first non-empty chunk
                parts = [p.strip() for p in tail.split("\n\n") if p.strip()]
                if parts:
                    first = parts[0]
                    # truncate to a short summary
                    summary = first[:400].replace('\n', ' ')
                    answer = f"Based on the provided context: {summary}"
        except Exception:
            answer = None

        if not answer:
            # fallback conservative response
            answer = "I couldn't find that information in the uploaded video."

        return {"text": answer}
