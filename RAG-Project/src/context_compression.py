"""
Context Compression Module for RAG Pipeline
Filters and prunes retrieved chunks to reduce token count and improve relevance

This module implements:
1. Similarity-based filtering (remove low-relevance chunks)
2. Token budget pruning (limit total tokens to max budget)
3. Redundancy removal (remove overlapping/duplicate content)
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class CompressionConfig:
    """Configuration for context compression"""
    max_tokens: int = 2000  # Maximum tokens for context
    similarity_threshold: float = 0.5  # Minimum similarity score
    remove_redundancy: bool = True  # Remove redundant chunks
    token_estimate_ratio: float = 0.75  # chars / tokens (English avg)


@dataclass
class CompressionResult:
    """Result of context compression"""
    compressed_chunks: List[Dict]
    original_count: int
    compressed_count: int
    tokens_removed: int
    compression_ratio: float


class ContextCompressor:
    """
    Compress retrieved context before sending to LLM

    Features:
    - Similarity-based filtering
    - Token budget pruning
    - Redundancy removal
    """

    def __init__(self, config: CompressionConfig = None):
        """
        Initialize context compressor

        Args:
            config: Compression configuration
        """
        self.config = config or CompressionConfig()

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token for English
        return int(len(text) / self.config.token_estimate_ratio)

    def filter_by_similarity(self, chunks: List[Dict]) -> List[Dict]:
        """
        Filter chunks by similarity threshold

        Args:
            chunks: List of retrieved chunks with scores

        Returns:
            Filtered list of chunks
        """
        filtered = []
        for chunk in chunks:
            score = (
                chunk.get("score") or
                chunk.get("similarity") or
                chunk.get("relevance_score") or
                chunk.get("rank", 0)
            )

            # For rank-based results, convert to score-like value
            if "rank" in chunk and "score" not in chunk:
                # Assuming rank 1 = best, convert to descending score
                max_rank = max(c.get("rank", 1) for c in chunks)
                score = (max_rank - chunk.get("rank", 1) + 1) / max_rank

            # Keep chunks above threshold
            if score >= self.config.similarity_threshold:
                filtered.append(chunk)

        return filtered

    def prune_by_token_budget(self, chunks: List[Dict]) -> List[Dict]:
        """
        Prune chunks to fit within token budget

        Args:
            chunks: List of chunks to prune

        Returns:
            Pruned list of chunks
        """
        if not chunks:
            return chunks

        # Calculate total tokens
        total_tokens = 0
        pruned_chunks = []

        # Sort by score/relevance to keep most important first
        sorted_chunks = sorted(
            chunks,
            key=lambda c: (
                c.get("score") or
                c.get("similarity") or
                c.get("relevance_score") or
                1 - (c.get("rank", 1) / len(chunks))
            ),
            reverse=True
        )

        for chunk in sorted_chunks:
            content = (
                chunk.get("page_content") or
                chunk.get("text") or
                chunk.get("content", "")
            )

            chunk_tokens = self.estimate_tokens(content)

            # Check if adding this chunk would exceed budget
            if total_tokens + chunk_tokens <= self.config.max_tokens:
                pruned_chunks.append(chunk)
                total_tokens += chunk_tokens
            else:
                # Check if we can fit a truncated version
                remaining_budget = self.config.max_tokens - total_tokens
                if remaining_budget > 50:  # Only if meaningful space left
                    # Truncate content to fit
                    truncated_chars = int(remaining_budget * self.config.token_estimate_ratio)
                    chunk_copy = chunk.copy()
                    chunk_copy["page_content"] = content[:truncated_chars] + "... [truncated]"
                    if "text" in chunk_copy:
                        chunk_copy["text"] = chunk_copy["page_content"]
                    pruned_chunks.append(chunk_copy)
                    total_tokens += remaining_budget
                break

        return pruned_chunks

    def remove_redundancy(self, chunks: List[Dict]) -> List[Dict]:
        """
        Remove redundant/overlapping chunks

        Args:
            chunks: List of chunks

        Returns:
            List with redundant chunks removed
        """
        if not chunks or not self.config.remove_redundancy:
            return chunks

        unique_chunks = []
        seen_signatures = set()

        for chunk in chunks:
            # Get content
            content = (
                chunk.get("page_content") or
                chunk.get("text") or
                chunk.get("content", "")
            )

            # Create a signature for similarity detection
            # Use first and last sentences + length as signature
            sentences = re.split(r'[.!?]+', content)
            first_sentence = sentences[0].strip() if sentences else ""
            last_sentence = sentences[-1].strip() if len(sentences) > 1 else ""
            length = len(content)

            signature = (first_sentence[:50], last_sentence[:50], length)

            # Check if similar signature already seen
            is_redundant = False
            for seen_sig in seen_signatures:
                # Check similarity
                first_sim = self._text_similarity(signature[0], seen_sig[0])
                last_sim = self._text_similarity(signature[1], seen_sig[1])
                length_diff = abs(signature[2] - seen_sig[2]) / max(signature[2], seen_sig[2])

                if first_sim > 0.7 and last_sim > 0.7 and length_diff < 0.3:
                    is_redundant = True
                    break

            if not is_redundant:
                unique_chunks.append(chunk)
                seen_signatures.add(signature)

        return unique_chunks

    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity using word overlap

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score 0-1
        """
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def compress(self, chunks: List[Dict]) -> CompressionResult:
        """
        Compress retrieved chunks using all compression techniques

        Args:
            chunks: List of retrieved chunks

        Returns:
            CompressionResult with compressed chunks and metadata
        """
        original_count = len(chunks)

        # Calculate original token count
        original_tokens = sum(
            self.estimate_tokens(
                c.get("page_content") or c.get("text") or c.get("content", "")
            )
            for c in chunks
        )

        # Step 1: Filter by similarity
        filtered = self.filter_by_similarity(chunks)

        # Step 2: Remove redundancy
        deduplicated = self.remove_redundancy(filtered)

        # Step 3: Prune to token budget
        compressed = self.prune_by_token_budget(deduplicated)

        # Calculate final token count
        compressed_tokens = sum(
            self.estimate_tokens(
                c.get("page_content") or c.get("text") or c.get("content", "")
            )
            for c in compressed
        )

        tokens_removed = original_tokens - compressed_tokens
        compression_ratio = tokens_removed / original_tokens if original_tokens > 0 else 0

        return CompressionResult(
            compressed_chunks=compressed,
            original_count=original_count,
            compressed_count=len(compressed),
            tokens_removed=tokens_removed,
            compression_ratio=compression_ratio
        )

    def format_compressed_context(self, chunks: List[Dict]) -> str:
        """
        Format compressed chunks into context string

        Args:
            chunks: List of compressed chunks

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, chunk in enumerate(chunks):
            content = (
                chunk.get("page_content") or
                chunk.get("text") or
                chunk.get("content", "")
            )

            metadata = chunk.get("metadata", {})
            source = metadata.get("source") or metadata.get("filename") or f"Source {i+1}"

            context_parts.append(f"[Source: {source}]\n{content}")

        return "\n\n".join(context_parts)


def main():
    """Test context compression"""
    print("=== Context Compression Test ===\n")

    config = CompressionConfig(max_tokens=500, similarity_threshold=0.5)
    compressor = ContextCompressor(config)

    # Test chunks
    test_chunks = [
        {
            "page_content": "This is a very long piece of content that talks about climate change and its various effects on the environment including rising temperatures and melting ice caps. " * 5,
            "score": 0.9,
            "metadata": {"source": "doc1"}
        },
        {
            "page_content": "Climate change causes temperatures to rise and ice to melt.",
            "score": 0.7,
            "metadata": {"source": "doc2"}
        },
        {
            # Similar to doc2 - should be removed as redundant
            "page_content": "Temperatures are rising due to climate change and ice is melting.",
            "score": 0.6,
            "metadata": {"source": "doc3"}
        },
        {
            # Low score - should be filtered
            "page_content": "This is unrelated content about something else.",
            "score": 0.3,
            "metadata": {"source": "doc4"}
        }
    ]

    print(f"Original: {len(test_chunks)} chunks")

    # Test compression
    result = compressor.compress(test_chunks)

    print(f"\nCompressed: {result.compressed_count} chunks")
    print(f"Tokens removed: {result.tokens_removed}")
    print(f"Compression ratio: {result.compression_ratio:.1%}")

    print("\nCompressed chunks:")
    for i, chunk in enumerate(result.compressed_chunks):
        content = chunk.get("page_content", "")[:100] + "..."
        score = chunk.get("score", 0)
        print(f"  {i+1}. [Score: {score:.2f}] {content}")

    print("\n✅ Context compression test completed!")


if __name__ == "__main__":
    main()
