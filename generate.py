"""
generate.py — Milestone 5: grounded generation.

Takes a user question, retrieves the most relevant student reviews, and asks
Groq (Llama 3.3 70B) to answer USING ONLY those reviews. The model is
instructed to refuse when the reviews don't cover the question, so it can't
fabricate elective advice that no student actually gave.

    from generate import answer
    result = answer("Which electives are the easiest?")
    print(result["text"])      # the grounded answer
    print(result["sources"])   # list of cited source URLs
"""

import os

from dotenv import load_dotenv
from groq import Groq

from embed_store import retrieve, TOP_K

load_dotenv()

MODEL = "llama-3.3-70b-versatile"  # planning.md Retrieval Approach

SYSTEM_PROMPT = """\
You are an advisor for Oregon State University's online post-bacc CS program.
You answer questions about CS electives using ONLY the student reviews provided
in the context below. These are real opinions from r/OSUOnlineCS.

Rules:
- Use ONLY information from the provided reviews. Do not use outside knowledge
  about these courses, and do not invent details.
- If the reviews do not contain enough information to answer, say so plainly:
  "The student reviews I have don't cover that." Do not guess.
- Reviews often disagree or are from different years. When they conflict, say so
  ("opinions are mixed") rather than presenting one view as fact.
- Cite the courses by their number/name as the students do (e.g. CS 372, Cloud).
- Keep answers concise and grounded in what students actually said.
"""


def build_context(hits):
    """Format retrieved chunks into a numbered context block for the prompt.

    Each block includes the thread question (original_post) so short replies
    like "Seconding Cloud" are interpretable, plus the source URL for citation.
    """
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(
            f"[Review {i}]\n"
            f"Thread question: {h['original_post']}\n"
            f"Student reply: {h['text']}\n"
            f"Source: {h['url']}"
        )
    return "\n\n".join(blocks)


def answer(query, k=TOP_K):
    """Retrieve reviews for the query and generate a grounded answer."""
    hits = retrieve(query, k=k)
    context = build_context(hits)

    user_prompt = (
        f"Student reviews:\n\n{context}\n\n"
        f"Question: {query}\n\n"
        f"Answer using only the reviews above."
    )

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,  # low — we want grounded, not creative
    )

    text = resp.choices[0].message.content
    sources = list(dict.fromkeys(h["url"] for h in hits))  # unique, ordered
    return {"text": text, "sources": sources, "hits": hits}


if __name__ == "__main__":
    for q in [
        "Which electives are the most useful for getting a software engineering job?",
        "What do students say about CS 493 Cloud?",
        "Is there an elective about underwater basket weaving?",  # grounding test
    ]:
        print("=" * 70)
        print("Q:", q)
        result = answer(q)
        print("\nA:", result["text"])
        print("\nSources:")
        for s in result["sources"]:
            print("  -", s)
        print()
