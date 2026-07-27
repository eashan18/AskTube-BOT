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

    def answer(self, db, question: str, video_id: Optional[str] = None, top_k: int | None = None):
        # retrieve
        snippets = self.retriever.retrieve(question, top_k=top_k, video_id=video_id)

        if not snippets:
            answer = "I couldn't find that information in the uploaded video."
            repo.save_chat_history(db, question=question, answer=answer, retrieved_chunks=[], video_id=video_id)
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
            # common providers include `text`, `generated_text`, or `choices` list
            if "generated_text" in raw:
                text = raw["generated_text"]
            elif "text" in raw:
                text = raw["text"]
            elif "choices" in raw and isinstance(raw["choices"], list) and raw["choices"]:
                first = raw["choices"][0]
                text = first.get("text") or first.get("message", {}).get("content")
        if text is None:
            # fallback to raw string
            text = str(raw)

        # save history
        repo.save_chat_history(db, question=question, answer=text, retrieved_chunks=snippets, video_id=video_id)

        # extract simple citations from snippets
        citations = [{"id": s.get("id"), "metadata": s.get("metadata")} for s in snippets]

        return {"answer": text, "citations": citations, "retrieved_chunks": snippets}
