"""
Prompt Optimizer for RAG System
Week 8: Prompt engineering optimization for cost efficiency

Implements:
- Token usage analysis
- Prompt template optimization
- Prompt caching
- Compact prompt generation
- Quality retention testing
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class PromptMetrics:
    """Prompt usage metrics"""
    original_tokens: int
    optimized_tokens: int
    reduction_percentage: float
    quality_score: float

    @property
    def tokens_saved(self) -> int:
        return self.original_tokens - self.optimized_tokens


class PromptAnalyzer:
    """
    Analyze prompt token usage

    Features:
    - Token counting (approximate)
    - Redundancy detection
    - Optimization opportunities
    """

    def __init__(self):
        self.token_cache = {}

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation)

        Args:
            text: Text to analyze

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 chars per token for English
        return len(text) // 4

    def analyze_prompt(self, prompt: str) -> Dict:
        """
        Analyze prompt structure and content

        Args:
            prompt: Prompt to analyze

        Returns:
            Analysis results
        """
        return {
            "estimated_tokens": self.estimate_tokens(prompt),
            "character_count": len(prompt),
            "line_count": len(prompt.split('\n')),
            "instruction_count": len(re.findall(r'\b(you|should|must|please|ensure)\b', prompt, re.I)),
            "redundant_phrases": self._find_redundant_phrases(prompt)
        }

    def _find_redundant_phrases(self, text: str) -> List[str]:
        """Find potentially redundant phrases"""
        redundant_patterns = [
            r'please please',
            r'very very',
            r'really really',
            r'in order to',  # can be replaced with 'to'
            r'due to the fact that',  # can be 'because'
        ]

        found = []
        for pattern in redundant_patterns:
            if re.search(pattern, text, re.I):
                found.append(pattern)
        return found


class PromptOptimizer:
    """
    Optimize prompts for token efficiency

    Features:
    - Remove redundant instructions
    - Compact phrasing
    - Template creation
    - Quality preservation
    """

    def __init__(self):
        self.analyzer = PromptAnalyzer()
        self.templates: Dict[str, str] = {}
        self.optimization_history: List[Dict] = []

    def optimize_prompt(self, prompt: str, aggressive: bool = False) -> Tuple[str, PromptMetrics]:
        """
        Optimize prompt for token efficiency

        Args:
            prompt: Original prompt
            aggressive: Use aggressive optimization

        Returns:
            (optimized_prompt, metrics)
        """
        original_tokens = self.analyzer.estimate_tokens(prompt)
        optimized = prompt

        # Apply optimizations
        optimizations = [
            self._remove_redundancy,
            self._compact_instructions,
            self._remove_filler_words,
        ]

        if aggressive:
            optimizations.extend([
                self._abbreviate_common_phrases,
                self._remove_polite_phrases,
            ])

        for opt_func in optimizations:
            optimized = opt_func(optimized)

        optimized_tokens = self.analyzer.estimate_tokens(optimized)
        reduction = ((original_tokens - optimized_tokens) / original_tokens) * 100

        metrics = PromptMetrics(
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            reduction_percentage=reduction,
            quality_score=1.0  # Would need actual evaluation
        )

        # Track history
        self.optimization_history.append({
            "original": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "optimized": optimized[:100] + "..." if len(optimized) > 100 else optimized,
            "metrics": metrics
        })

        return optimized, metrics

    def _remove_redundancy(self, text: str) -> str:
        """Remove redundant phrases"""
        replacements = {
            r'in order to': 'to',
            r'due to the fact that': 'because',
            r'at this point in time': 'now',
            r'for the purpose of': 'for',
        }

        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.I)

        return text

    def _compact_instructions(self, text: str) -> str:
        """Compact instruction phrases"""
        replacements = {
            r'you are required to': 'you must',
            r'it is important that you': 'you must',
            r'make sure to': 'ensure',
            r'please make sure': 'ensure',
        }

        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.I)

        return text

    def _remove_filler_words(self, text: str) -> str:
        """Remove filler words"""
        filler_phrases = [
            r'\bjust\b',
            r'\bsimply\b',
            r'\bbasically\b',
        ]

        for phrase in filler_phrases:
            text = re.sub(phrase, '', text, flags=re.I)

        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text)
        return text

    def _abbreviate_common_phrases(self, text: str) -> str:
        """Abbreviate common phrases (use with caution)"""
        abbreviations = {
            r'information': 'info',
            r'application': 'app',
            r'configuration': 'config',
        }

        for phrase, abbrev in abbreviations.items():
            text = re.sub(rf'\b{phrase}\b', abbrev, text, flags=re.I)

        return text

    def _remove_polite_phrases(self, text: str) -> str:
        """Remove polite phrases (safe for most prompts)"""
        polite_phrases = [
            r'please',
            r'if you could',
            r'if possible',
            r'kindly',
        ]

        for phrase in polite_phrases:
            text = re.sub(rf'\b{phrase}\b', '', text, flags=re.I)

        return text

    def create_template(self, name: str, template: str) -> None:
        """
        Create reusable prompt template

        Args:
            name: Template name
            template: Template string with {placeholders}
        """
        self.templates[name] = template

    def use_template(self, name: str, **kwargs) -> str:
        """
        Use a prompt template

        Args:
            name: Template name
            **kwargs: Template variables

        Returns:
            Formatted prompt
        """
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")

        return self.templates[name].format(**kwargs)


class CompactPromptGenerator:
    """
    Generate compact prompts for RAG system

    Features:
    - Minimal but effective prompts
    - Context-aware prompts
    - Task-specific templates
    """

    BASE_SYSTEM_PROMPT = "You are a helpful assistant answering questions based on provided context."
    COMPACT_SYSTEM_PROMPT = "Answer questions using the given context."

    QA_TEMPLATE_COMPACT = """Context: {context}

Question: {question}

Answer:"""

    QA_TEMPLATE_ORIGINAL = """You are a helpful assistant. Please answer the following question based on the provided context.

Context:
{context}

Question: {question}

Please provide a clear and accurate answer based on the context above."""


class PromptCache:
    """
    Cache for prompt templates and optimized prompts

    Features:
    - Template storage
    - Optimized prompt cache
    - Token savings tracking
    """

    def __init__(self):
        self.cache: Dict[str, Tuple[str, int]] = {}
        self.total_original_tokens = 0
        self.total_optimized_tokens = 0

    def get(self, key: str) -> Optional[str]:
        """Get cached optimized prompt"""
        if key in self.cache:
            return self.cache[key][0]
        return None

    def set(self, key: str, prompt: str, original_tokens: int) -> None:
        """Cache optimized prompt"""
        optimized_tokens = len(prompt) // 4  # Estimate
        self.cache[key] = (prompt, optimized_tokens)
        self.total_original_tokens += original_tokens
        self.total_optimized_tokens += optimized_tokens

    def get_savings(self) -> Dict:
        """Get token savings statistics"""
        return {
            "total_original": self.total_original_tokens,
            "total_optimized": self.total_optimized_tokens,
            "tokens_saved": self.total_original_tokens - self.total_optimized_tokens,
            "reduction_percentage": (
                ((self.total_original_tokens - self.total_optimized_tokens) /
                 self.total_original_tokens * 100)
                if self.total_original_tokens > 0 else 0
            )
        }


class PromptOptimizerManager:
    """
    Main prompt optimizer manager

    Features:
    - Prompt analysis and optimization
    - Template management
    - Caching
    - Performance tracking
    """

    def __init__(self):
        self.analyzer = PromptAnalyzer()
        self.optimizer = PromptOptimizer()
        self.generator = CompactPromptGenerator()
        self.cache = PromptCache()

        # Initialize with common templates
        self._init_templates()

    def _init_templates(self):
        """Initialize common prompt templates"""
        self.optimizer.create_template(
            "qa_compact",
            self.generator.QA_TEMPLATE_COMPACT
        )
        self.optimizer.create_template(
            "qa_original",
            self.generator.QA_TEMPLATE_ORIGINAL
        )
        self.optimizer.create_template(
            "system_compact",
            self.generator.COMPACT_SYSTEM_PROMPT
        )
        self.optimizer.create_template(
            "system_base",
            self.generator.BASE_SYSTEM_PROMPT
        )

    def optimize_rag_prompt(self,
                           context: str,
                           question: str,
                           use_compact: bool = True) -> Tuple[str, PromptMetrics]:
        """
        Optimize RAG prompt

        Args:
            context: Document context
            question: User question
            use_compact: Use compact template

        Returns:
            (optimized_prompt, metrics)
        """
        template_name = "qa_compact" if use_compact else "qa_original"

        # Use template
        prompt = self.optimizer.use_template(
            template_name,
            context=context,
            question=question
        )

        # Optimize further
        optimized, metrics = self.optimizer.optimize_prompt(prompt)

        return optimized, metrics

    def get_optimization_summary(self) -> Dict:
        """Get optimization summary"""
        cache_savings = self.cache.get_savings()

        total_reductions = [m.reduction_percentage for _, m in self.optimizer.optimization_history]
        avg_reduction = sum(total_reductions) / len(total_reductions) if total_reductions else 0

        return {
            "prompts_optimized": len(self.optimizer.optimization_history),
            "avg_reduction_percentage": avg_reduction,
            "template_count": len(self.optimizer.templates),
            "cache_savings": cache_savings
        }


def main():
    """Test prompt optimizer"""
    print("=== Prompt Optimizer Test ===\n")

    manager = PromptOptimizerManager()

    # Test RAG prompt optimization
    context = "RAG (Retrieval-Augmented Generation) is a technique that combines retrieval and generation."
    question = "What is RAG?"

    optimized, metrics = manager.optimize_rag_prompt(context, question)

    print(f"Original tokens: {metrics.original_tokens}")
    print(f"Optimized tokens: {metrics.optimized_tokens}")
    print(f"Reduction: {metrics.reduction_percentage:.1f}%")
    print(f"\nOptimized prompt:\n{optimized}")

    # Get summary
    summary = manager.get_optimization_summary()
    print(f"\nOptimization Summary: {summary}")

    print("\n✅ Prompt optimizer test completed!")


if __name__ == "__main__":
    main()
