"""Tool registry with cached embeddings and semantic search."""

from __future__ import annotations

from typing import Dict, List


class ToolRegistry:
    """Embeds MCP registry descriptions and performs semantic search."""

    def __init__(
        self,
        embeddings,  # langchain Embeddings instance (e.g. OpenAIEmbeddings)
        registry: List[Dict],
        *,
        similarity_threshold: float = 0.25,
        relative_score_cutoff: float = 0.6,
        debug: bool = False,
    ):
        self._embeddings = embeddings
        self._registry = registry
        self._similarity_threshold = similarity_threshold
        self._relative_score_cutoff = relative_score_cutoff
        self._debug = debug
        self._cache: List[Dict] = []

    @staticmethod
    def _build_embed_text(entry: Dict) -> str:
        """Concatenate available metadata into a single embedding string.

        Format: ``name | category | description | kw1, kw2, ...``
        Missing fields are simply omitted.
        """
        parts: list[str] = []
        if entry.get("name"):
            parts.append(entry["name"])
        if entry.get("category"):
            parts.append(entry["category"])
        parts.append(entry["description"])
        if entry.get("keywords"):
            kw = entry["keywords"]
            parts.append(", ".join(kw) if isinstance(kw, list) else str(kw))
        return " | ".join(parts)
    
    def cache_embeddings(self) -> int:
        """Batch-embed all registry entries."""
        if not self._registry:
            return 0
        texts = [self._build_embed_text(t) for t in self._registry]
        
        vectors = self._embeddings.embed_documents(texts)
        
        self._cache = [
            {
                "url": self._registry[i]["url"],
                "description": self._registry[i]["description"],
                "embedding": vectors[i],
            }
            for i in range(len(self._registry))
        ]
        return len(self._cache)

    def search(self, queries: List[str]) -> List[Dict]:
        """Semantic search across the registry."""
        if not queries or not self._cache:
            return []

        query_vectors = [self._embeddings.embed_query(q) for q in queries]
        matched: Dict[str, Dict] = {}

        for query_text, q_vec in zip(queries, query_vectors):
            scored = []
            for tool in self._cache:
                score = _cosine_similarity(q_vec, tool["embedding"])
                if score >= self._similarity_threshold:
                    if self._debug:
                        print(f"  [🔍 Query '{query_text[:30]}...' matched {tool['url']} (score: {score:.3f})]")
                    scored.append((tool, score))

            if not scored:
                continue

            best = max(s for _, s in scored)
            cutoff = best * self._relative_score_cutoff
            if self._debug:
                print(f"  [🔍 Query '{query_text[:30]}...' - max: {best:.3f}, cutoff: {cutoff:.3f}]")

            for tool, score in scored:
                if score >= cutoff and tool["url"] not in matched:
                    matched[tool["url"]] = {
                        "url": tool["url"],
                        "description": tool["description"],
                        "score": round(score, 4),
                    }

        return list(matched.values())

    @property
    def tool_count(self) -> int:
        return len(self._cache)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(b * b for b in v2) ** 0.5
    if norm1 * norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)