# rag/embeddings.py
import math
import hashlib
import numpy as np
from typing import List, Optional
from app.core.config import settings

_model = None

def _get_sentence_transformer():
    global _model
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return _model
    except Exception as e:
        print(f"Notice: SentenceTransformer initialization note ({e}). Using robust feature-vector embedder.")
        return None

def _deterministic_fallback_embed(text: str, dim: int = 384) -> List[float]:
    """
    Fallback deterministic text embedder using n-gram frequency & hashing.
    Generates a unit-normalized vector with meaningful semantic overlap.
    """
    vec = np.zeros(dim, dtype=np.float32)
    clean = text.lower().strip()
    if not clean:
        return [0.0] * dim

    words = clean.split()
    # Word unigrams and bigrams
    tokens = words + [f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)]

    for token in tokens:
        # Generate multiple hash indices for distributed representation
        h = hashlib.md5(token.encode("utf-8")).hexdigest()
        idx1 = int(h[:8], 16) % dim
        idx2 = int(h[8:16], 16) % dim
        idx3 = int(h[16:24], 16) % dim
        sign = 1.0 if int(h[24:26], 16) % 2 == 0 else -1.0
        
        vec[idx1] += 1.0 * sign
        vec[idx2] += 0.5 * sign
        vec[idx3] += 0.25 * sign

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()

def get_embedding(text: str) -> List[float]:
    """
    Generate 384-dimensional normalized embedding for text.
    """
    if not text or not text.strip():
        return [0.0] * settings.EMBEDDING_DIMENSION

    # Try Gemini API embedding if configured
    if settings.GEMINI_API_KEY and "text-embedding" in settings.EMBEDDING_MODEL.lower():
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            resp = client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=text
            )
            raw = resp.embedding.values
            if len(raw) == settings.EMBEDDING_DIMENSION:
                norm = np.linalg.norm(raw)
                return (np.array(raw) / norm).tolist() if norm > 0 else raw
            elif len(raw) > settings.EMBEDDING_DIMENSION:
                # Truncate and normalize
                truncated = np.array(raw[:settings.EMBEDDING_DIMENSION], dtype=np.float32)
                norm = np.linalg.norm(truncated)
                return (truncated / norm).tolist() if norm > 0 else truncated.tolist()
        except Exception as e:
            print(f"Notice: Gemini embedding API failed ({e}), falling back to local embedder.")

    # Try local SentenceTransformer
    st_model = _get_sentence_transformer()
    if st_model is not None:
        try:
            emb = st_model.encode(text, normalize_embeddings=True)
            return emb.tolist()
        except Exception as e:
            print(f"Notice: SentenceTransformer inference error ({e}), using fallback.")

    return _deterministic_fallback_embed(text, settings.EMBEDDING_DIMENSION)

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Batch embedding generator.
    """
    return [get_embedding(t) for t in texts]
