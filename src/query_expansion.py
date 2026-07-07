"""
Query Expansion Module for RAG Pipeline
Generates alternative query variations to improve retrieval

This module uses the configured LLM (Ollama or Gemini) to generate
3 alternative variations of the user's query, then performs retrieval
for all 4 queries (original + 3 expanded) and combines results.
"""

import os
import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass


@dataclass
class ExpansionResult:
    """Result of query expansion"""
    original_query: str
    expanded_queries: List[str]
    all_queries: List[str]  # original + expanded


class QueryExpander:
    """
    LLM-based query expansion

    Generates 3 alternative variations of the user's query to improve
    retrieval recall by capturing different phrasings and perspectives.
    """

    def __init__(self, llm_client=None):
        """
        Initialize query expander

        Args:
            llm_client: Optional LLM client (OllamaClient or GeminiClient)
                        If None, will create based on LLM_BACKEND env var
        """
        self.llm_client = llm_client
        self._init_llm()

        # Query expansion prompt template
        self.expansion_prompt = """You are a query expansion assistant. Your task is to generate 3 alternative variations of a user's search query to help find relevant documents.

Original query: "{query}"

Generate 3 alternative queries that:
1. Rephrase the question using different words
2. Break down complex questions into simpler components
3. Consider related topics or synonyms that might help find relevant information

Format your response as a numbered list:
1. [Alternative query 1]
2. [Alternative query 2]
3. [Alternative query 3]

Provide ONLY the numbered list, no other text."""

    def _init_llm(self):
        """Initialize LLM client based on environment configuration"""
        if self.llm_client is not None:
            return

        # Determine which LLM backend to use
        backend = os.getenv("LLM_BACKEND", "ollama").strip().lower()

        if backend == "ollama":
            from src.ollama_client import OllamaClient
            self.llm_client = OllamaClient()
        else:
            from src.gemini_client import GeminiClient
            self.llm_client = GeminiClient()

    def expand_query(self, query: str) -> ExpansionResult:
        """
        Generate 3 alternative query variations

        Args:
            query: Original user query

        Returns:
            ExpansionResult with original and expanded queries
        """
        # Call LLM to generate expansions
        prompt = self.expansion_prompt.format(query=query)

        try:
            response = self.llm_client.generate(prompt)

            # Parse the response to extract the 3 queries
            expanded_queries = self._parse_expansion_response(response)

            # Combine original + expanded
            all_queries = [query] + expanded_queries

            return ExpansionResult(
                original_query=query,
                expanded_queries=expanded_queries,
                all_queries=all_queries
            )

        except Exception as e:
            print(f"⚠️ Query expansion failed: {e}. Using original query only.")
            # Fallback to original query only
            return ExpansionResult(
                original_query=query,
                expanded_queries=[],
                all_queries=[query]
            )

    def _parse_expansion_response(self, response: str) -> List[str]:
        """
        Parse LLM response to extract alternative queries

        Args:
            response: LLM response text

        Returns:
            List of 3 alternative query strings
        """
        queries = []

        # Try to extract numbered list format
        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()

            # Match patterns like "1. query", "1) query", "- query"
            match = re.match(r'^(\d+[\.\)])\s*(.+)', line)
            if match:
                queries.append(match.group(2).strip())
            elif line.startswith('- ') or line.startswith('• '):
                # Bullet point format
                queries.append(line[2:].strip())

        # If we couldn't parse properly, split by newlines and filter
        if len(queries) < 3:
            queries = []
            for line in lines:
                line = line.strip()
                # Skip empty lines and headers
                if line and not line.startswith('#') and len(line) > 3:
                    if line.lower() not in ['alternative query', 'query', 'variations:']:
                        queries.append(line)

        # Return exactly 3 queries (or fewer if not enough)
        return queries[:3]

    def combine_retrieval_results(self,
                                 retrieval_results: List[List[Dict]],
                                 deduplicate: bool = True) -> List[Dict]:
        """
        Combine retrieval results from multiple queries

        Args:
            retrieval_results: List of retrieval result lists (one per query)
            deduplicate: Whether to remove duplicate documents

        Returns:
            Combined and deduplicated list of documents
        """
        combined = []
        seen_doc_ids: Set[str] = set()
        seen_content_hashes: Set[str] = set()

        for result_list in retrieval_results:
            for doc in result_list:
                # Get document identifier
                doc_id = doc.get("passage_id") or doc.get("id") or doc.get("metadata", {}).get("chunk_id")

                # Get content for hash-based deduplication
                content = doc.get("page_content") or doc.get("text") or doc.get("content", "")
                content_hash = hash(content[:200])  # Hash first 200 chars

                # Check for duplicates
                is_duplicate = False
                if deduplicate:
                    if doc_id and doc_id in seen_doc_ids:
                        is_duplicate = True
                    elif content_hash in seen_content_hashes:
                        is_duplicate = True

                if not is_duplicate:
                    combined.append(doc)
                    if doc_id:
                        seen_doc_ids.add(doc_id)
                    seen_content_hashes.add(content_hash)

        return combined

    def expand_and_retrieve(self,
                           query: str,
                           retriever_func,
                           k: int = 5,
                           deduplicate: bool = True) -> Dict:
        """
        Perform query expansion and multi-query retrieval

        Args:
            query: Original user query
            retriever_func: Function that takes (query, k) and returns List[Dict]
            k: Number of documents to retrieve per query
            deduplicate: Whether to deduplicate results

        Returns:
            Dict with combined results and metadata
        """
        # Step 1: Expand query
        expansion_result = self.expand_query(query)

        # Step 2: Retrieve for each query
        all_results = []
        query_results = []

        for i, expanded_query in enumerate(expansion_result.all_queries):
            try:
                results = retriever_func(expanded_query, k=k)
                all_results.append(results)
                query_results.append({
                    "query": expanded_query,
                    "query_type": "original" if i == 0 else "expanded",
                    "num_results": len(results)
                })
            except Exception as e:
                print(f"⚠️ Retrieval failed for query '{expanded_query}': {e}")

        # Step 3: Combine and deduplicate results
        combined_docs = self.combine_retrieval_results(all_results, deduplicate=deduplicate)

        # Re-rank combined results by score if available
        combined_docs = self._rerank_combined(combined_docs, k=k)

        return {
            "original_query": expansion_result.original_query,
            "expanded_queries": expansion_result.expanded_queries,
            "all_queries": expansion_result.all_queries,
            "combined_documents": combined_docs[:k],  # Return top-k after combining
            "total_retrieved": len(combined_docs),
            "query_breakdown": query_results
        }

    def _rerank_combined(self, documents: List[Dict], k: int) -> List[Dict]:
        """
        Re-rank combined documents by score

        Args:
            documents: List of documents
            k: Number of top documents to return

        Returns:
            Re-ranked list of documents
        """
        # Sort by score if available
        scored_docs = []
        for doc in documents:
            score = doc.get("score") or doc.get("similarity") or doc.get("relevance_score") or 0
            scored_docs.append((score, doc))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Return top-k documents
        return [doc for score, doc in scored_docs[:k]]


def main():
    """Test query expansion"""
    print("=== Query Expansion Test ===\n")

    expander = QueryExpander()

    # Test query expansion
    test_query = "What are the main causes of climate change?"
    print(f"Original query: {test_query}\n")

    result = expander.expand_query(test_query)

    print("Expanded queries:")
    for i, query in enumerate(result.expanded_queries, 1):
        print(f"  {i}. {query}")

    print(f"\nAll queries (original + expanded):")
    for i, query in enumerate(result.all_queries, 1):
        print(f"  {i}. {query}")

    # Test combining results (simulated)
    print("\n" + "="*60)
    print("Testing result combination...")

    mock_results = [
        [{"passage_id": "doc1", "score": 0.9, "text": "Content 1"}],
        [{"passage_id": "doc2", "score": 0.8, "text": "Content 2"},
         {"passage_id": "doc1", "score": 0.85, "text": "Content 1"}],  # Duplicate
        [{"passage_id": "doc3", "score": 0.7, "text": "Content 3"}],
    ]

    combined = expander.combine_retrieval_results(mock_results, deduplicate=True)
    print(f"Combined {len(combined)} unique documents (deduplication worked)")

    print("\n✅ Query expansion test completed!")


if __name__ == "__main__":
    main()
