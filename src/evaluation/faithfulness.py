"""
Faithfulness Evaluation Module for RAG Responses
Week 8: LLM-as-judge evaluation for answer faithfulness

Implements:
- Faithfulness Scoring: 0-1 scale measuring answer adherence to context
- Hallucination Detection: Identifies unsupported claims in answers
- Batch Evaluation: Efficient evaluation of multiple Q&A pairs
"""

import re
import time
from typing import Dict, List, Optional, Any
import numpy as np


class FaithfulnessEvaluator:
    """
    LLM-based faithfulness evaluator for RAG responses

    Uses Ollama LLM as a judge to evaluate:
    - Faithfulness: Does the answer stick to the provided context?
    - Hallucination: Does the answer introduce unsupported information?

    Usage:
        evaluator = FaithfulnessEvaluator()
        result = evaluator.evaluate(context, question, answer)
        # Returns: {"score": 0.85, "is_faithful": True, "hallucinations": []}
    """

    # Compact evaluation prompts (optimized for token efficiency)
    FAITHFULNESS_PROMPT = """Judge if the answer is faithful to the context.

Context:
{context}

Question:
{question}

Answer:
{answer}

Evaluate:
1. Does the answer use only info from the context?
2. Does it avoid adding facts not in context?
3. Does it accurately represent the context?

Respond with: "Score: X/10 - [one sentence reason]"
Only respond with the score format, nothing else."""

    HALLUCINATION_PROMPT = """Find claims in the answer NOT supported by the context.

Context:
{context}

Answer:
{answer}

List each unsupported claim on a new line starting with "- ".
If all claims are supported, respond: "None"

Respond:"""

    def __init__(self, model: str = "qwen2.5-coder:7b", temperature: float = 0.0):
        """
        Initialize faithfulness evaluator

        Args:
            model: Ollama model name for evaluation
            temperature: LLM temperature (0.0 for consistent evaluation)
        """
        from src.ollama_client import OllamaClient
        self.client = OllamaClient(model=model, temperature=temperature)
        self.client.temperature = temperature

        # Evaluation statistics
        self.results = {
            "faithfulness_scores": [],
            "hallucination_counts": [],
            "evaluation_times": []
        }
        self.query_count = 0

    def reset(self) -> None:
        """Reset all evaluation statistics"""
        self.results = {
            "faithfulness_scores": [],
            "hallucination_counts": [],
            "evaluation_times": []
        }
        self.query_count = 0

    def evaluate(
        self,
        context: str,
        question: str,
        answer: str,
        detect_hallucinations: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate faithfulness of a single answer

        Args:
            context: Retrieved document context
            question: User's question
            answer: Generated answer to evaluate
            detect_hallucinations: Whether to detect hallucinations

        Returns:
            Dictionary with faithfulness metrics:
            {
                "score": float (0-1),
                "is_faithful": bool,
                "hallucinations": List[str],
                "evaluation_time": float
            }
        """
        start_time = time.time()

        # Evaluate faithfulness
        faithfulness_result = self._evaluate_faithfulness(context, question, answer)
        score = faithfulness_result["score"]
        is_faithful = faithfulness_result["is_faithful"]
        reason = faithfulness_result.get("reason", "")

        # Detect hallucinations if requested
        hallucinations = []
        if detect_hallucinations:
            hallucinations = self._detect_hallucinations(context, answer)

        evaluation_time = time.time() - start_time

        # Store results
        self.results["faithfulness_scores"].append(score)
        self.results["hallucination_counts"].append(len(hallucinations))
        self.results["evaluation_times"].append(evaluation_time)
        self.query_count += 1

        return {
            "score": score,
            "is_faithful": is_faithful,
            "reason": reason,
            "hallucinations": hallucinations,
            "evaluation_time": evaluation_time
        }

    def _evaluate_faithfulness(self, context: str, question: str, answer: str) -> Dict[str, Any]:
        """
        Get LLM judgment of answer faithfulness

        Returns:
            {"score": float (0-1), "is_faithful": bool, "reason": str}
        """
        prompt = self.FAITHFULNESS_PROMPT.format(
            context=context[:2000],  # Limit context length for efficiency
            question=question,
            answer=answer
        )

        try:
            response = self.client.generate(prompt)

            # Parse score from response (format: "Score: X/10 - reason")
            match = re.search(r'Score:\s*(\d+(?:\.\d+)?)\s*/\s*10', response, re.IGNORECASE)
            if match:
                score_10 = float(match.group(1))
                score = min(score_10 / 10.0, 1.0)  # Normalize to 0-1

                # Extract reason
                reason_match = re.search(r'Score:[^-]*-\s*(.+)', response, re.IGNORECASE)
                reason = reason_match.group(1).strip() if reason_match else ""

                return {
                    "score": score,
                    "is_faithful": score >= 0.7,  # Threshold for faithful
                    "reason": reason
                }
            else:
                # Fallback: parse any number in response
                numbers = re.findall(r'\d+(?:\.\d+)?', response)
                if numbers:
                    score = min(float(numbers[0]) / 10.0, 1.0)
                    return {"score": score, "is_faithful": score >= 0.7, "reason": response[:100]}

                # Default to middle score if parsing fails
                return {"score": 0.5, "is_faithful": False, "reason": "Could not parse score"}

        except Exception as e:
            print(f"Faithfulness evaluation error: {e}")
            return {"score": 0.5, "is_faithful": False, "reason": f"Evaluation failed: {str(e)}"}

    def _detect_hallucinations(self, context: str, answer: str) -> List[str]:
        """
        Detect hallucinations (unsupported claims) in answer

        Returns:
            List of hallucinated claims (empty list if none)
        """
        prompt = self.HALLUCINATION_PROMPT.format(
            context=context[:2000],
            answer=answer
        )

        try:
            response = self.client.generate(prompt).strip()

            # Parse hallucinations from response
            if "none" in response.lower():
                return []

            # Extract lines starting with "-"
            hallucinations = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    claim = line[1:].strip()
                    if claim and len(claim) > 5:  # Filter out too-short claims
                        hallucinations.append(claim)

            return hallucinations

        except Exception as e:
            print(f"Hallucination detection error: {e}")
            return []

    def evaluate_batch(
        self,
        qa_pairs: List[Dict[str, str]],
        detect_hallucinations: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate multiple Q&A pairs

        Args:
            qa_pairs: List of dicts with "context", "question", "answer" keys
            detect_hallucinations: Whether to detect hallucinations

        Returns:
            Dictionary with aggregated metrics
        """
        individual_results = []

        for pair in qa_pairs:
            result = self.evaluate(
                context=pair["context"],
                question=pair["question"],
                answer=pair["answer"],
                detect_hallucinations=detect_hallucinations
            )
            individual_results.append(result)

        # Get mean metrics
        mean_metrics = self.get_mean_metrics()

        return {
            "individual_results": individual_results,
            "mean_metrics": mean_metrics,
            "total_evaluations": len(qa_pairs)
        }

    def get_mean_metrics(self) -> Dict[str, float]:
        """
        Get mean metrics across all evaluations

        Returns:
            Dictionary of mean metrics
        """
        if self.query_count == 0:
            return {
                "mean_faithfulness": 0.0,
                "faithful_rate": 0.0,
                "mean_hallucinations": 0.0,
                "mean_evaluation_time": 0.0
            }

        return {
            "mean_faithfulness": np.mean(self.results["faithfulness_scores"]),
            "faithful_rate": np.mean([s >= 0.7 for s in self.results["faithfulness_scores"]]),
            "mean_hallucinations": np.mean(self.results["hallucination_counts"]),
            "mean_evaluation_time": np.mean(self.results["evaluation_times"]),
            "total_evaluations": self.query_count
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive evaluation statistics

        Returns:
            Dictionary with evaluation stats and LLM usage stats
        """
        mean_metrics = self.get_mean_metrics()
        llm_stats = self.client.get_stats()

        return {
            **mean_metrics,
            "llm_requests": llm_stats["request_count"],
            "llm_tokens": llm_stats["total_tokens"],
            "llm_errors": llm_stats["error_count"]
        }

    def print_results(self) -> None:
        """Print evaluation results summary"""
        stats = self.get_stats()

        print(f"\n{'='*60}")
        print(f"  Faithfulness Evaluation Results ({stats['total_evaluations']} queries)")
        print(f"{'='*60}\n")

        print("Faithfulness Metrics:")
        print(f"  Mean Faithfulness Score: {stats['mean_faithfulness']:.4f} (0-1)")
        print(f"  Faithful Answer Rate: {stats['faithful_rate']:.2%}")

        print("\nHallucination Metrics:")
        print(f"  Mean Hallucinations per Answer: {stats['mean_hallucinations']:.2f}")

        print("\nPerformance:")
        print(f"  Mean Evaluation Time: {stats['mean_evaluation_time']*1000:.2f}ms")
        print(f"  Total LLM Requests: {stats['llm_requests']}")
        print(f"  Total LLM Tokens: {stats['llm_tokens']}")


def evaluate_rag_response(
    context: str,
    question: str,
    answer: str,
    model: str = "qwen2.5-coder:7b"
) -> Dict[str, Any]:
    """
    Convenience function for single evaluation

    Args:
        context: Retrieved document context
        question: User's question
        answer: Generated answer to evaluate
        model: Ollama model name

    Returns:
        Dictionary with faithfulness metrics
    """
    evaluator = FaithfulnessEvaluator(model=model)
    return evaluator.evaluate(context, question, answer)


def main():
    """Test the faithfulness evaluation module"""
    print("=== Faithfulness Evaluation Test ===\n")

    # Test case 1: Faithful answer
    print("Test 1: Faithful Answer")
    context1 = "Python is a high-level programming language created by Guido van Rossum. It was released in 1991."
    question1 = "Who created Python?"
    answer1 = "Python was created by Guido van Rossum."

    evaluator = FaithfulnessEvaluator()
    result1 = evaluator.evaluate(context1, question1, answer1, detect_hallucinations=False)
    print(f"  Score: {result1['score']:.2f}")
    print(f"  Faithful: {result1['is_faithful']}")
    print(f"  Reason: {result1.get('reason', '')}")

    # Test case 2: Hallucinating answer
    print("\nTest 2: Hallucinating Answer")
    answer2 = "Python was created by Guido van Rossum in 1995 at Google."
    result2 = evaluator.evaluate(context1, question1, answer2)
    print(f"  Score: {result2['score']:.2f}")
    print(f"  Faithful: {result2['is_faithful']}")
    print(f"  Hallucinations: {result2['hallucinations']}")

    # Test case 3: Batch evaluation
    print("\nTest 3: Batch Evaluation")
    qa_pairs = [
        {"context": "E = mc² is Einstein's mass-energy equivalence formula.", "question": "What is E=mc²?", "answer": "It's Einstein's formula."},
        {"context": "Water boils at 100°C at sea level.", "question": "When does water boil?", "answer": "Water boils at 100°C."},
        {"context": "The Earth orbits the Sun.", "question": "What orbits the Sun?", "answer": "The Moon orbits the Sun."}  # Unfaithful
    ]

    batch_result = evaluator.evaluate_batch(qa_pairs)
    print(f"  Mean Faithfulness: {batch_result['mean_metrics']['mean_faithfulness']:.2f}")
    print(f"  Faithful Rate: {batch_result['mean_metrics']['faithful_rate']:.2%}")

    # Print summary
    evaluator.print_results()
    print("\n✅ Faithfulness evaluation test completed!")


if __name__ == "__main__":
    main()
