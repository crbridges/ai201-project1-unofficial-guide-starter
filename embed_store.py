"""
embed_store.py — Milestone 4: embedding + vector store.

Embeds each chunk's reply text with all-MiniLM-L6-v2 and stores it in a
persistent ChromaDB collection. Only chunk["text"] (the reply) is embedded;
original_post / url / source ride along as metadata for context + citation.

Usage:
    python embed_store.py            # (re)build the index, then run a demo query
    from embed_store import retrieve # retrieve(query, k=5) -> list of chunks
"""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from load_documents import load_documents

DB_DIR = Path(__file__).parent / "chroma_db"
COLLECTION = "osu_electives"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5  # matches planning.md Retrieval Approach

_model = None
_client = None


def get_model():
    """Load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_client():
    """Persistent Chroma client (data saved under chroma_db/)."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(DB_DIR))
    return _client


def embed(texts):
    """Embed a list of strings. Normalized so cosine distance is meaningful."""
    return get_model().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    ).tolist()


def build_index():
    """Load chunks, embed the reply text, and (re)create the Chroma collection.

    Original posts are NOT embedded — they're questions that out-rank real
    answers at query time. Each reply still carries its OP as context metadata,
    so no information is lost.
    """
    chunks = [c for c in load_documents() if not c["is_original_post"]]
    client = get_client()

    # Rebuild fresh so re-running never duplicates rows.
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    coll = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    texts = [c["text"] for c in chunks]                # <-- the ONLY thing embedded
    print(f"Embedding {len(texts)} chunks with {MODEL_NAME} ...")
    embeddings = embed(texts)

    ids = [f"{c['source']}-{i}" for i, c in enumerate(chunks)]
    metadatas = [
        {
            "url": c["url"],
            "source": c["source"],
            "original_post": c["original_post"],   # context, not embedded
            "is_original_post": c["is_original_post"],
        }
        for c in chunks
    ]

    coll.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    print(f"Stored {coll.count()} vectors in collection '{COLLECTION}' at {DB_DIR}")
    return coll


def retrieve(query, k=TOP_K):
    """Return the top-k most similar chunks for a query."""
    coll = get_client().get_collection(COLLECTION)
    res = coll.query(query_embeddings=embed([query]), n_results=k)
    hits = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append(
            {
                "text": doc,
                "url": meta["url"],
                "source": meta["source"],
                "original_post": meta["original_post"],
                "distance": dist,  # lower = more similar (cosine)
            }
        )
    return hits


if __name__ == "__main__":
    build_index()

    demo = "Which elective is most useful for getting a software engineering job?"
    print(f"\n--- Demo query ---\n{demo!r}\n")
    for i, hit in enumerate(retrieve(demo), 1):
        text = hit["text"].replace("\n", " ")
        text = text[:180] + ("..." if len(text) > 180 else "")
        print(f"{i}. (dist={hit['distance']:.3f}) [{hit['source']}]")
        print(f"   {text}")
