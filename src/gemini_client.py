"""
Gemini API Client - Google Gen AI Integration
Uses the new `google-genai` SDK (replaces deprecated `google-generativeai`).

Documentation: https://googleapis.github.io/python-genai/
Free-tier model: gemini-2.0-flash-lite  (fastest / cheapest)
"""

import os
from pathlib import Path
from typing import Optional, Dict, List, Any

# ---------------------------------------------------------------------------
# Load .env from project root before anything else
# ---------------------------------------------------------------------------
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _val = _line.split("=", 1)
                _val = _val.split("#")[0].strip()
                os.environ.setdefault(_key.strip(), _val.strip())


class GeminiClient:
    """
    Google Gemini API client (new `google-genai` SDK).

    Drop-in replacement for ZAIClient:
      - generate(prompt)
      - generate_with_context(context, question, chat_history)
      - get_stats()
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-lite",
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ):
        # pyrefly: ignore [missing-import]
        from google import genai
        # pyrefly: ignore [missing-import]
        from google.genai import types

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. "
                "Set GEMINI_API_KEY in your .env file or environment."
            )

        self.model_name = os.getenv("GEMINI_MODEL", model)
        self.temperature = temperature
        self.max_output_tokens = max_tokens

        self._client = genai.Client(api_key=self.api_key)
        self._types = types
        self._generate_config = types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
        )

        # Usage statistics
        self.request_count = 0
        self.total_tokens = 0
        self.error_count = 0

        print("✓ Gemini client initialized")
        print(f"  Model : {self.model_name}")
        print(f"  SDK   : google-genai (new)")

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response for a plain-text prompt.

        Args:
            prompt:   Full prompt string
            **kwargs: Ignored (interface compatibility)

        Returns:
            Response text
        """
        self.request_count += 1
        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self._generate_config,
            )
            text = response.text
            # Track tokens when metadata is available
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                self.total_tokens += getattr(
                    response.usage_metadata, "total_token_count", 0
                )
            return text
        except Exception as e:
            self.error_count += 1
            raise Exception(f"Gemini API call failed: {e}") from e

    def generate_with_context(
        self,
        context: str,
        question: str,
        chat_history: Optional[List] = None,
        **kwargs,
    ) -> str:
        """
        Generate a RAG-aware answer given retrieved context.

        Args:
            context:      Retrieved document text
            question:     User question
            chat_history: Optional list of (role, message) tuples or dicts
            **kwargs:     Ignored

        Returns:
            Answer text
        """
        # Format previous conversation turns (last 3 Q/A pairs = 6 entries)
        history_block = ""
        if chat_history:
            lines = []
            for entry in chat_history[-6:]:
                if isinstance(entry, (list, tuple)) and len(entry) == 2:
                    role, msg = entry
                else:
                    role = entry.get("role", "user")
                    msg = entry.get("content", str(entry))
                lines.append(f"{role.capitalize()}: {msg}")
            history_block = "\n".join(lines)

        prompt = (
            "You are a knowledgeable assistant helping a user understand their uploaded documents. "
            "The user uploaded documents and is asking questions about them. "
            "The following context was retrieved from their documents.\n\n"
            "=== DOCUMENT CONTEXT (retrieved from user's uploaded files) ===\n"
            f"{context}\n"
            "=== END CONTEXT ===\n\n"
        )
        if history_block:
            prompt += f"Previous conversation:\n{history_block}\n\n"
        prompt += (
            f"User's question: {question}\n\n"
            "Instructions:\n"
            "1. Answer the question based on the document context above.\n"
            "2. The context comes from the user's own documents — treat it as authoritative.\n"
            "3. When the user says 'my' or 'I', they are referring to the person or subject described in their documents.\n"
            "4. Be helpful, direct, and concise.\n"
            "5. If the context genuinely contains no relevant information for the question, "
            "say so and suggest what kind of document might help.\n"
            "6. Cite specific details from the context when possible.\n\n"
            "Answer:"
        )

        return self.generate(prompt)

    # ------------------------------------------------------------------
    # Statistics (matches ZAIClient interface used in get_stats())
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict:
        """Return usage statistics."""
        return {
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "success_rate": (self.request_count - self.error_count)
            / max(self.request_count, 1),
        }


# ------------------------------------------------------------------
# Quick test – run directly: python src/gemini_client.py
# ------------------------------------------------------------------

def main():
    print("=== Gemini API Client Test ===\n")

    client = GeminiClient()

    print("Test 1: Simple generation")
    resp = client.generate(
        "What is Retrieval-Augmented Generation? Answer in one sentence."
    )
    print(f"  Response: {resp.strip()}\n")

    print("Test 2: Context-aware (RAG) generation")
    ctx = (
        "RAG stands for Retrieval-Augmented Generation. "
        "It combines a retriever that fetches relevant document chunks "
        "from a vector database with a large language model that generates "
        "an answer conditioned on those chunks."
    )
    resp2 = client.generate_with_context(
        context=ctx,
        question="What does the RAG retriever do?",
    )
    print(f"  Response: {resp2.strip()}\n")

    stats = client.get_stats()
    print(f"Stats: {stats}")
    print("\n✅ Gemini client test complete!")


if __name__ == "__main__":
    main()
