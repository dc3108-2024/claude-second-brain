"""
Semantic search over idea backlog items.

Uses sentence-transformers (all-MiniLM-L6-v2) to embed query + item text,
returns best match by cosine similarity.

CLI: python3 search.py "query text"
     → JSON: {"match": "Title", "score": 0.87, "ambiguous": false, "candidates": [...]}

Thresholds:
  score >= 0.40 → clear match
  score 0.25–0.39 → ambiguous, return top-3 for user to pick
  score < 0.25  → no match found
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from recommend import parse_ideas, IDEAS_PATH

_MODEL_NAME = "all-MiniLM-L6-v2"
_CLEAR_THRESHOLD = 0.40
_AMBIGUOUS_THRESHOLD = 0.25
_EXCLUDED_STATUSES = {"Done"}  # Parked items are searchable (user may want to un-park them)


def _cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def _item_text(entry: dict) -> str:
    return f"{entry.get('title', '')}. {entry.get('notes', '')}".strip()


def find_item(query: str, entries: list[dict] | None = None) -> dict:
    """
    Semantic search. Returns:
      {"match": title, "score": float, "ambiguous": bool, "candidates": [...]}
    match is None when score < _AMBIGUOUS_THRESHOLD.
    """
    from sentence_transformers import SentenceTransformer
    if entries is None:
        entries = parse_ideas(IDEAS_PATH.read_text())

    open_items = [e for e in entries if e.get("status", "") not in _EXCLUDED_STATUSES]
    if not open_items:
        return {"match": None, "score": 0.0, "ambiguous": False, "candidates": []}

    model = SentenceTransformer(_MODEL_NAME)
    texts = [_item_text(e) for e in open_items]
    embeddings = model.encode([query] + texts, normalize_embeddings=True)
    q_emb = embeddings[0]
    item_embs = embeddings[1:]

    scored = sorted(
        [(float(_cosine(q_emb, item_embs[i])), open_items[i]) for i in range(len(open_items))],
        key=lambda x: -x[0],
    )

    top_score, top_item = scored[0]
    candidates = [
        {"title": e["title"], "score": round(sc, 3)}
        for sc, e in scored[:3]
    ]

    if top_score >= _CLEAR_THRESHOLD:
        return {"match": top_item["title"], "score": round(top_score, 3),
                "ambiguous": False, "candidates": candidates}
    if top_score >= _AMBIGUOUS_THRESHOLD:
        return {"match": None, "score": round(top_score, 3),
                "ambiguous": True, "candidates": candidates}
    return {"match": None, "score": round(top_score, 3),
            "ambiguous": False, "candidates": []}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 search.py <query>", file=sys.stderr)
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    result = find_item(query)
    print(json.dumps(result, indent=2))
