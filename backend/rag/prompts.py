"""Prompt templates for the RAG pipeline.

These templates strictly instruct the LLM to answer ONLY from provided context
and to refuse to hallucinate. They also instruct the model to include citations
with timestamps and the origin chunk references.
"""
from typing import List, Dict


SYSTEM_PROMPT = (
    "You are an assistant that answers questions strictly using the provided "
    "context. Do NOT use any outside knowledge. If the answer is not present "
    "in the context, respond with: 'I couldn't find that information in the uploaded video.'"
)


RETRIEVAL_INSTRUCTIONS = (
    "You will be given a list of numbered context snippets extracted from a single "
    "or multiple uploaded YouTube videos. Each snippet includes a start and end "
    "timestamp and the original text. Use ONLY these snippets to answer the user's question. "
    "When you reference information, include the snippet number and timestamp as a citation.")


FINAL_PROMPT_TEMPLATE = (
    "{system}\n\n"
    "Context snippets:\n"
    "{context}\n\n"
    "Instructions:\n"
    "{instructions}\n\n"
    "User question: {question}\n\n"
    "Answer strictly from the context. If the answer is not available, reply:\n"
    "I couldn't find that information in the uploaded video.\n\n"
    "Response format requirements:\n"
    "1) Provide a concise answer paragraph.\n"
    "2) Provide a 'Citations' section listing snippet numbers and timestamps used.\n"
    "3) Provide a 'Referenced chunks' JSON array with items: {{chunk_id, video_id, start_timestamp, end_timestamp, text_excerpt}}.\n"
)


def build_prompt(snippets: List[Dict], question: str) -> str:
    """Assemble the final prompt.

    Args:
        snippets: list of dicts each containing `id`, `metadata` (with `start_timestamp`, `end_timestamp`, `video_id`) and `document`/`content`.
        question: the user's question string.
    """
    # Format snippets numbered for the model
    formatted = []
    for i, s in enumerate(snippets, start=1):
        meta = s.get("metadata", {})
        start = meta.get("start_timestamp")
        end = meta.get("end_timestamp")
        vid = meta.get("video_id")
        doc = s.get("document") or s.get("content") or meta.get("original_text") or ""
        formatted.append(f"[{i}] (video:{vid}) [{start}-{end}] {doc}")

    context_block = "\n\n".join(formatted)

    prompt = FINAL_PROMPT_TEMPLATE.format(system=SYSTEM_PROMPT, context=context_block, instructions=RETRIEVAL_INSTRUCTIONS, question=question)
    return prompt
