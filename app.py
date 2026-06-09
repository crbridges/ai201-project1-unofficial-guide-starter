"""
app.py — Milestone 5: query interface.

A Gradio chat interface over the grounded RAG pipeline. Ask about OSU online
post-bacc CS electives; answers come only from retrieved student reviews, with
sources and the raw retrieved reviews shown for transparency.

    python app.py   # then open the local URL it prints
"""

import gradio as gr

from generate import answer

EXAMPLES = [
    "Which electives are most useful for getting a software engineering job?",
    "Which electives do students say are the easiest?",
    "Which electives are considered the hardest?",
    "What do students say about CS 493 Cloud?",
    "Which electives are the most fun?",
]


def respond(query):
    if not query or not query.strip():
        return "Ask a question about OSU online CS electives.", "", ""

    result = answer(query)

    sources_md = "### Sources\n" + "\n".join(
        f"- [{u}]({u})" for u in result["sources"]
    )

    reviews_md = "\n\n---\n\n".join(
        f"**Review {i}** · `{h['source']}` · distance `{h['distance']:.3f}`\n\n"
        f"> {h['text']}"
        for i, h in enumerate(result["hits"], 1)
    )

    return result["text"], sources_md, reviews_md


with gr.Blocks(title="The Unofficial Guide — OSU Online CS Electives") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "### OSU online post-bacc CS electives, answered from real r/OSUOnlineCS student reviews\n"
        "Answers are grounded in retrieved reviews only — if students didn't discuss it, "
        "the guide will say so instead of guessing."
    )

    query = gr.Textbox(
        label="Your question",
        placeholder="e.g. Which electives are the easiest to take?",
        lines=2,
    )
    ask = gr.Button("Ask", variant="primary")

    answer_box = gr.Markdown(label="Answer")
    sources_box = gr.Markdown()

    with gr.Accordion("Retrieved reviews (what the answer is grounded in)", open=False):
        reviews_box = gr.Markdown()

    gr.Examples(examples=EXAMPLES, inputs=query)

    ask.click(respond, inputs=query, outputs=[answer_box, sources_box, reviews_box])
    query.submit(respond, inputs=query, outputs=[answer_box, sources_box, reviews_box])


if __name__ == "__main__":
    demo.launch()
