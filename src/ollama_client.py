"""
Ollama Local LLM Client
Drop-in replacement for GeminiClient using a locally-running Ollama model.

Supported models (must be pulled with `ollama pull <model>`):
  - qwen2.5-coder:7b  (default - already installed)
  - llama3, mistral, etc.

Ollama REST API: http://localhost:11434/api/generate
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional

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


class OllamaClient:
    """
    Ollama local LLM client.

    Drop-in replacement for GeminiClient:
      - generate(prompt)
      - generate_with_context(context, question, chat_history)
      - get_stats()
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ):
        self.model_name = os.getenv("OLLAMA_MODEL", model)
        self.base_url = os.getenv("OLLAMA_BASE_URL", base_url).rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Usage statistics
        self.request_count = 0
        self.total_tokens = 0
        self.error_count = 0

        # Verify Ollama is reachable
        self._check_connection()

        # Initialize prompt optimizer
        from src.optimization.prompt_optimizer import PromptOptimizer
        self.prompt_optimizer = PromptOptimizer()

        print("✓ Ollama client initialized")
        print(f"  Model : {self.model_name}")
        print(f"  URL   : {self.base_url}")

    # ------------------------------------------------------------------
    # Connection check
    # ------------------------------------------------------------------

    def _check_connection(self) -> None:
        """Ping Ollama to make sure it's running."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                available = [m["name"] for m in data.get("models", [])]

            if not available:
                raise ConnectionError(
                    "Ollama is running but no models are available. "
                    f"Run: ollama pull {self.model_name}"
                )

            # Check that the requested model is actually pulled
            model_ok = any(self.model_name.split(":")[0] in m for m in available)
            if not model_ok:
                raise ConnectionError(
                    f"Model '{self.model_name}' not found in Ollama. "
                    f"Available: {available}. "
                    f"Run: ollama pull {self.model_name}"
                )
        except urllib.error.URLError as exc:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: `ollama serve`"
            ) from exc

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------

    def _call_ollama(self, prompt: str) -> str:
        """Call the Ollama /api/generate endpoint."""
        payload = json.dumps({
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())

        text = data.get("response", "")
        # Track token usage if available
        self.total_tokens += data.get("eval_count", 0) + data.get("prompt_eval_count", 0)
        return text

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response for a plain-text prompt.

        Args:
            prompt:   Full prompt string
            **kwargs: Ignored (interface compatibility with GeminiClient)

        Returns:
            Response text
        """
        self.request_count += 1
        try:
            return self._call_ollama(prompt)
        except Exception as exc:
            self.error_count += 1
            raise Exception(f"Ollama API call failed: {exc}") from exc

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

        # Optimize prompt for token efficiency before sending to Ollama
        optimized_prompt, _ = self.prompt_optimizer.optimize_prompt(prompt, aggressive=True)
        return self.generate(optimized_prompt)

    # ------------------------------------------------------------------
    # Statistics (matches GeminiClient interface)
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
# Quick test - run directly: python src/ollama_client.py
# ------------------------------------------------------------------

def main():
    print("=== Ollama Client Test ===\n")

    client = OllamaClient()

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
    print("\n✅ Ollama client test complete!")


if __name__ == "__main__":
    main()
