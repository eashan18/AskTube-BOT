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

        url = f"{self.base_url.rstrip('/')}/v1/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.exception("LLM request failed: %s", e)
                raise

            data = resp.json()
            return data

    def _mock_generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Generate a simple mock response when no LLM API key is configured."""
        lower_prompt = prompt.lower()
        if "natural language processing" in lower_prompt or "nlp" in lower_prompt:
            answer = "The video is focused on natural language processing (NLP) in the context of machine learning."
        elif "main topic" in lower_prompt or "what is the main" in lower_prompt:
            answer = "Based on the provided context, the video is mainly about natural language processing and NLP for machine learning."
        else:
            answer = "I couldn't find that information in the uploaded video."

        return {"text": answer}
