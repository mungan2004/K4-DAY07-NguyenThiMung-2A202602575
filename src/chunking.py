from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        # Split on ". ", "! ", "? " or ".\n"
        sentences = re.split(r'(?<=[.!?])\s+(?=\S)|(?<=\.)\n(?=\S)', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i:i + self.max_sentences_per_chunk])
            chunks.append(chunk)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [current_text]
        
        sep = remaining_separators[0]
        if sep:
            parts = current_text.split(sep)
        else:
            parts = list(current_text)
            
        results = []
        for p in parts:
            if len(p) > self.chunk_size:
                results.extend(self._split(p, remaining_separators[1:]))
            else:
                results.append(p)
                
        merged = []
        current_chunk = ""
        for r in results:
            if not current_chunk:
                current_chunk = r
            elif len(current_chunk) + len(sep) + len(r) <= self.chunk_size:
                current_chunk += sep + r
            else:
                merged.append(current_chunk)
                current_chunk = r
        if current_chunk:
            merged.append(current_chunk)
        return merged


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_prod = _dot(vec_a, vec_b)
    mag_a = math.sqrt(_dot(vec_a, vec_a))
    mag_b = math.sqrt(_dot(vec_b, vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_prod / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fc = FixedSizeChunker(chunk_size=chunk_size)
        sc = SentenceChunker()
        rc = RecursiveChunker(chunk_size=chunk_size)
        
        res_fc = fc.chunk(text)
        res_sc = sc.chunk(text)
        res_rc = rc.chunk(text)
        
        return {
            'fixed_size': {
                'count': len(res_fc),
                'avg_length': sum(len(c) for c in res_fc) / len(res_fc) if res_fc else 0,
                'chunks': res_fc
            },
            'by_sentences': {
                'count': len(res_sc),
                'avg_length': sum(len(c) for c in res_sc) / len(res_sc) if res_sc else 0,
                'chunks': res_sc
            },
            'recursive': {
                'count': len(res_rc),
                'avg_length': sum(len(c) for c in res_rc) / len(res_rc) if res_rc else 0,
                'chunks': res_rc
            }
        }
