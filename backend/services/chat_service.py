"""Chat service that uses RAG retriever and LLM client to answer questions."""
from __future__ import annotations

import json
import logging
from typing import Optional

from ..rag.retriever import RAGRetriever
from ..rag.prompts import build_prompt
from ..services.llm_client import LLMClient
from ..database import repository as repo

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        self.retriever = RAGRetriever()
        self.llm = LLMClient()

    def _extract_final_answer(self, text: str) -> str:
        # Normalize model output by stripping out any leading reasoning and keeping
        # only the final answer section if present.
        if not text:
            return text

        normalized = text.strip()
        # If there is a 'Final Answer:' delimiter, keep the final answer and citations block
        if "Final Answer:" in normalized:
            normalized = normalized.split("Final Answer:", 1)[1].strip()

        # Remove trailing reasoning or tool instructions after the citations section
        if "Citations:" in normalized:
            parts = normalized.split("Citations:", 1)
            answer_part = parts[0].strip()
            citations_part = parts[1].strip()
            normalized = f"{answer_part}\n\nCitations: {citations_part}"

        return normalized

    def answer(self, db, question: str, video_id: Optional[str] = None, top_k: int | None = None, user_id: Optional[str] = None):
        # retrieve
        snippets = self.retriever.retrieve(question, top_k=top_k, video_id=video_id)

        if not snippets:
            answer = "I couldn't find that information in the uploaded video."
            repo.save_chat_history(
                db,
                question=question,
                answer=answer,
                retrieved_chunks=[],
                user_id=user_id,
                video_id=video_id,
            )
            return {"answer": answer, "citations": [], "retrieved_chunks": []}

        prompt = build_prompt(snippets, question)

        # call LLM
        try:
            raw = self.llm.generate(prompt=prompt, temperature=0.0)
        except Exception as exc:
            logger.exception("LLM call failed: %s", exc)
            raise

        # try to parse generated text from known keys
        text = None
        if isinstance(raw, dict):
            if "text" in raw and raw["text"] is not None:
                text = raw["text"]
            elif "generated_text" in raw and raw["generated_text"] is not None:
                text = raw["generated_text"]
            elif "output_text" in raw and raw["output_text"] is not None:
                text = raw["output_text"]
            elif "choices" in raw and isinstance(raw["choices"], list) and raw["choices"]:
                first = raw["choices"][0]
                text = first.get("text") or first.get("message", {}).get("content")
            elif "output" in raw and isinstance(raw["output"], list):
                parts = []
                for item in raw["output"]:
                    for content in item.get("content", []):
                        if content.get("type") in ("output_text", "text", "reasoning_text"):
                            t = content.get("text") or content.get("output_text")
                            if t:
                                parts.append(t)
                if parts:
                    text = "\n".join(parts)

        if text is None:
            text = "I couldn't find that information in the uploaded video."
        else:
            text = self._extract_final_answer(text)

        # save history
        repo.save_chat_history(
            db,
            question=question,
            answer=text,
            retrieved_chunks=snippets,
            user_id=user_id,
            video_id=video_id,
        )

        # extract simple citations from snippets
        citations = [{"id": s.get("id"), "metadata": s.get("metadata")} for s in snippets]

        return {"answer": text, "citations": citations, "retrieved_chunks": snippets}
