"""
load_documents.py — Milestone 3: ingestion + chunking.

Reads the cleaned thread files in documents/ (produced by clean_documents.py).
Each file is:
    URL: <thread url>
    ===
    <original post>
    ===
    <reply 1>
    ===
    <reply 2>
    ...

Returns a flat list of chunks, one per post/reply. Each chunk carries:
    text           -> the reply itself. THIS is what gets embedded.
    original_post  -> the thread's opening post (title + question), attached as
                      context so the LLM can interpret short replies like
                      "Seconding Cloud". This is NOT embedded (it would dilute
                      the vector and make every chunk in a thread look alike).
    url / source   -> citation + debugging metadata.

    [{"url": "...", "text": "...", "original_post": "...",
      "source": "post6.txt", "is_original_post": False}, ...]
"""

from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DELIM = "==="


def load_documents(docs_dir=DOCS_DIR):
    """Load cleaned thread files into a list of {url, text, source} chunks."""
    chunks = []
    files = sorted(
        docs_dir.glob("post*.txt"),
        key=lambda p: int("".join(c for c in p.stem if c.isdigit())),
    )

    for path in files:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            continue

        first_line, _, body = raw.partition("\n")
        if first_line.startswith("URL:"):
            url = first_line[len("URL:"):].strip()
        else:
            url = "UNKNOWN"
            body = raw  # no header — treat whole file as posts

        posts = [p.strip() for p in body.split(DELIM) if p.strip()]
        if not posts:
            continue

        original_post = posts[0]  # title + question — shared context for the thread
        for i, text in enumerate(posts):
            chunks.append({
                "url": url,
                "text": text,                   # embed ONLY this
                "original_post": original_post,  # LLM context, never embedded
                "source": path.name,
                "is_original_post": i == 0,
            })

    return chunks


if __name__ == "__main__":
    chunks = load_documents()

    print(f"Loaded {len(chunks)} chunks from {DOCS_DIR}\n")

    # Per-file breakdown
    by_file = {}
    for c in chunks:
        by_file[c["source"]] = by_file.get(c["source"], 0) + 1
    for name in sorted(by_file, key=lambda n: int("".join(filter(str.isdigit, n)))):
        print(f"  {name}: {by_file[name]} chunks")

    def preview(s, n=160):
        s = s.replace("\n", " ")
        return s[:n] + ("..." if len(s) > n else "")

    # Show a short reply so the attached context is obvious
    print("\n--- Sample: a short reply WITH its attached context ---")
    short = min((c for c in chunks if not c["is_original_post"]), key=lambda c: len(c["text"]))
    print(f"[source]        {short['source']}")
    print(f"[url]           {short['url']}")
    print(f"[text/EMBED]    {short['text']!r}")
    print(f"[original_post] {preview(short['original_post'])}")
    print("  ^ original_post gives the LLM context but is NOT part of the embedded text")

    # Quick sanity checks
    print("\n--- Sanity checks ---")
    print(f"  every chunk has a url:           {all(c['url'] != 'UNKNOWN' for c in chunks)}")
    print(f"  every chunk has text:            {all(c['text'] for c in chunks)}")
    print(f"  every chunk has original_post:   {all(c['original_post'] for c in chunks)}")
    print(f"  original_post NOT in embed text: {all('original_post' not in c['text'] for c in chunks)}")
    lengths = [len(c["text"]) for c in chunks]
    print(f"  embed-text length min/avg/max:   {min(lengths)} / {sum(lengths)//len(lengths)} / {max(lengths)}")
