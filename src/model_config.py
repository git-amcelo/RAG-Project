"""
Model Configuration and Selection Module
Weeks 4-5: Embedding model configuration and automatic selection

Implements:
- Model configuration for BGE-small and E5-base
- Automatic model selection based on use case
- Performance tracking and comparison
- Model recommendation engine
"""

import os
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ModelType(Enum):
    """Available embedding models"""
    BGE_SMALL = "BAAI/bge-small-en-v1.5"
    E5_BASE = "intfloat/e5-base-v2"


@dataclass
class ModelSpecs:
    """Specifications for an embedding model"""
    name: str
    path: str
    dimensions: int
    speed: str  # "fast", "medium", "slow"
    accuracy: str  # "good", "better", "best"
    storage_factor: float  # Relative to BGE-small
    use_case: str
    description: str


# Model specifications
MODEL_SPECS = {
    ModelType.BGE_SMALL: ModelSpecs(
        name="BGE-small",
        path=ModelType.BGE_SMALL.value,
        dimensions=384,
        speed="fast",
        accuracy="good",
        storage_factor=1.0,
        use_case="general",
        description="Fast and efficient for general queries and real-time applications"
    ),
    ModelType.E5_BASE: ModelSpecs(
        name="E5-base",
        path=ModelType.E5_BASE.value,
        dimensions=768,
        speed="medium",
        accuracy="better",
        storage_factor=2.0,
        use_case="complex",
        description="Higher accuracy for complex queries and document analysis"
    )
}


# Week 3 benchmark results (for comparison)
BENCHMARK_RESULTS = {
    ModelType.BGE_SMALL: {
        "recall_at_1": 0.50,
        "recall_at_5": 0.75,
        "recall_at_10": 0.85,
        "mrr": 0.68,
        "map": 0.72,
        "encoding_speed": 1.0,  # Relative speed
        "index_time": 1.0  # Relative time
    },
    ModelType.E5_BASE: {
        "recall_at_1": 0.55,
        "recall_at_5": 0.78,
        "recall_at_10": 0.88,
        "mrr": 0.72,
        "map": 0.75,
        "encoding_speed": 0.7,  # 30% slower
        "index_time": 1.3  # 30% slower
    }
}


class ModelSelector:
    """
    Automatic model selection based on use case and requirements

    Features:
    - Automatic model recommendation
    - Query complexity analysis
    - Resource consideration
    - Performance optimization
    """

    def __init__(self, default_model: ModelType = ModelType.BGE_SMALL):
        """
        Initialize model selector

        Args:
            default_model: Default model to use
        """
        self.default_model = default_model
        self.selection_history = []
        self.performance_tracker = {}

        print(f"✓ ModelSelector initialized")
        print(f"  Default model: {default_model.value}")

    def recommend_model(self,
                       query_complexity: float = 0.5,
                       num_documents: int = 1000,
                       priority: str = "balanced",
                       resource_constraints: Optional[Dict] = None) -> ModelType:
        """
        Recommend the best model for the given use case

        Args:
            query_complexity: Query complexity (0.0 to 1.0)
            num_documents: Number of documents to search
            priority: Priority type ("speed", "accuracy", "balanced")
            resource_constraints: Optional resource constraints

        Returns:
            Recommended model type
        """
        # Analyze requirements
        requirements = self._analyze_requirements(
            query_complexity, num_documents, priority, resource_constraints
        )

        # Select model based on requirements
        if requirements["needs_accuracy"]:
            recommended = ModelType.E5_BASE
            reason = "complex query requires higher accuracy"
        elif requirements["needs_speed"]:
            recommended = ModelType.BGE_SMALL
            reason = "speed priority with sufficient accuracy"
        elif requirements["resource_limited"]:
            recommended = ModelType.BGE_SMALL
            reason = "resource constraints favor efficient model"
        else:
            recommended = self.default_model
            reason = "default model suitable for this use case"

        # Track selection
        selection_record = {
            "model": recommended.value,
            "query_complexity": query_complexity,
            "num_documents": num_documents,
            "priority": priority,
            "reason": reason,
            "timestamp": time.time()
        }
        self.selection_history.append(selection_record)

        print(f"Model Recommendation: {recommended.value}")
        print(f"  Reason: {reason}")
        print(f"  Query complexity: {query_complexity:.2f}")
        print(f"  Documents: {num_documents}")

        return recommended

    def _analyze_requirements(self,
                            query_complexity: float,
                            num_documents: int,
                            priority: str,
                            resource_constraints: Optional[Dict]) -> Dict:
        """
        Analyze requirements to determine model needs

        Returns:
            Dictionary with requirement flags
        """
        requirements = {
            "needs_accuracy": False,
            "needs_speed": False,
            "resource_limited": False
        }

        # Check if high accuracy needed
        if query_complexity > 0.7:
            requirements["needs_accuracy"] = True

        # Check if speed is priority
        if priority == "speed":
            requirements["needs_speed"] = True
        elif priority == "accuracy":
            requirements["needs_accuracy"] = True

        # Check resource constraints
        if resource_constraints:
            if resource_constraints.get("memory_limit_mb", 0) < 2000:
                requirements["resource_limited"] = True
            if resource_constraints.get("max_storage_gb", 0) < 5:
                requirements["resource_limited"] = True

        # Large document collections favor speed
        if num_documents > 10000 and priority == "balanced":
            requirements["needs_speed"] = True

        return requirements

    def get_model_specs(self, model_type: ModelType) -> ModelSpecs:
        """Get specifications for a model"""
        return MODEL_SPECS[model_type]

    def compare_models(self, model1: ModelType, model2: ModelType) -> Dict:
        """
        Compare two models on various metrics

        Args:
            model1: First model to compare
            model2: Second model to compare

        Returns:
            Comparison dictionary
        """
        specs1 = self.get_model_specs(model1)
        specs2 = self.get_model_specs(model2)
        bench1 = BENCHMARK_RESULTS[model1]
        bench2 = BENCHMARK_RESULTS[model2]

        comparison = {
            "model1": {
                "name": specs1.name,
                "dimensions": specs1.dimensions,
                "speed": specs1.speed,
                "accuracy": specs1.accuracy
            },
            "model2": {
                "name": specs2.name,
                "dimensions": specs2.dimensions,
                "speed": specs2.speed,
                "accuracy": specs2.accuracy
            },
            "performance": {
                "recall_at_5_diff": bench2["recall_at_5"] - bench1["recall_at_5"],
                "mrr_diff": bench2["mrr"] - bench1["mrr"],
                "speed_diff": bench2["encoding_speed"] - bench1["encoding_speed"],
                "storage_diff": specs2.storage_factor - specs1.storage_factor
            },
            "recommendation": self._generate_comparison_recommendation(model1, model2)
        }

        return comparison

    def _generate_comparison_recommendation(self, model1: ModelType, model2: ModelType) -> Dict:
        """Generate usage recommendations for model comparison"""
        specs1 = self.get_model_specs(model1)
        specs2 = self.get_model_specs(model2)

        return {
            f"{specs1.name}_best_for": [
                "Real-time applications" if specs1.speed == "fast" else "",
                "Resource-constrained environments" if specs1.storage_factor <= 1.0 else "",
                "General queries" if specs1.use_case == "general" else ""
            ],
            f"{specs2.name}_best_for": [
                "Complex queries" if specs2.accuracy == "better" else "",
                "Document analysis" if specs2.dimensions > 500 else "",
                "Batch processing" if specs2.use_case == "complex" else ""
            ]
        }

    def get_selection_stats(self) -> Dict:
        """Get statistics about model selections"""
        if not self.selection_history:
            return {"total_selections": 0}

        model_counts = {}
        for record in self.selection_history:
            model = record["model"]
            model_counts[model] = model_counts.get(model, 0) + 1

        return {
            "total_selections": len(self.selection_history),
            "model_distribution": model_counts,
            "last_selection": self.selection_history[-1] if self.selection_history else None
        }

    def get_model_comparison_table(self) -> str:
        """Generate formatted comparison table"""
        table = "\n┌" + "─" * 80 + "┐"
        table += "\n│" + " " * 25 + "Embedding Model Comparison" + " " * 35 + "│"
        table += "\n├" + "─" * 80 + "┤"

        # Header
        table += "\n│ {:<20} │ {:<12} │ {:<10} │ {:<10} │ {:<12} │".format(
            "Model", "Dimensions", "Speed", "Accuracy", "Storage"
        )
        table += "\n├" + "─" * 80 + "┤"

        # BGE-small
        bge = MODEL_SPECS[ModelType.BGE_SMALL]
        table += "\n│ {:<20} │ {:<12} │ {:<10} │ {:<10} │ {:<12} │".format(
            bge.name,
            bge.dimensions,
            bge.speed,
            bge.accuracy,
            f"{bge.storage_factor}x"
        )

        # E5-base
        e5 = MODEL_SPECS[ModelType.E5_BASE]
        table += "\n│ {:<20} │ {:<12} │ {:<10} │ {:<10} │ {:<12} │".format(
            e5.name,
            e5.dimensions,
            e5.speed,
            e5.accuracy,
            f"{e5.storage_factor}x"
        )

        table += "\n└" + "─" * 80 + "┘"

        # Benchmark comparison
        table += "\n\nWeek 3 Benchmark Results:"
        table += "\n┌" + "─" * 80 + "┐"
        table += "\n│ {:<20} │ {:<12} │ {:<12} │ {:<12} │ {:<12} │".format(
            "Metric", "BGE-small", "E5-base", "Difference", "Improvement"
        )
        table += "\n├" + "─" * 80 + "┤"

        bge_bench = BENCHMARK_RESULTS[ModelType.BGE_SMALL]
        e5_bench = BENCHMARK_RESULTS[ModelType.E5_BASE]

        metrics = [
            ("Recall@5", "recall_at_5", "%"),
            ("MRR", "mrr", ""),
            ("MAP", "map", ""),
            ("Encoding Speed", "encoding_speed", "x"),
        ]

        for display_name, key, suffix in metrics:
            bge_val = bge_bench[key]
            e5_val = e5_bench[key]
            diff = e5_val - bge_val

            if key == "encoding_speed":
                diff_str = f"{diff:+.2f}x"
                improvement = "Slower" if diff < 0 else "Faster"
            else:
                diff_pct = (diff / bge_val) * 100 if bge_val > 0 else 0
                diff_str = f"{diff:+.4f} ({diff_pct:+.1f}%)" if suffix == "%" else f"{diff:+.4f}"
                improvement = "Better" if diff > 0 else "Lower"

            table += "\n│ {:<20} │ {:<12} │ {:<12} │ {:<12} │ {:<12} │".format(
                display_name,
                f"{bge_val:.4f}" if isinstance(bge_val, float) else str(bge_val),
                f"{e5_val:.4f}" if isinstance(e5_val, float) else str(e5_val),
                diff_str,
                improvement
            )

        table += "\n└" + "─" * 80 + "┘"

        return table


class ModelConfig:
    """
    Configuration management for embedding models

    Handles model loading, caching, and configuration
    """

    def __init__(self):
        """Initialize model configuration"""
        self.loaded_models = {}
        self.cache_dir = "models/embeddings"
        os.makedirs(self.cache_dir, exist_ok=True)

        # Default configuration
        self.config = {
            "default_model": ModelType.BGE_SMALL.value,
            "auto_select": True,
            "cache_models": True,
            "device": "auto",  # auto, cpu, cuda, mps
            "batch_size": 32
        }

    def get_config(self) -> Dict:
        """Get current configuration"""
        return self.config.copy()

    def update_config(self, **kwargs):
        """Update configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                print(f"✓ Updated {key}: {value}")

    def get_model_path(self, model_name: str) -> str:
        """Get full model path"""
        if model_name in MODEL_SPECS:
            return MODEL_SPECS[ModelType(model_name)].path
        return model_name

    def list_available_models(self) -> List[str]:
        """List all available models"""
        return [model.value for model in ModelType]


def main():
    """Test model configuration and selection"""
    print("=== Model Configuration Test ===\n")

    # Test model selector
    selector = ModelSelector()

    # Print comparison table
    print(selector.get_model_comparison_table())

    # Test recommendations
    print("\n" + "="*50)
    print("Testing Model Recommendations")
    print("="*50)

    test_cases = [
        {"query_complexity": 0.8, "num_documents": 100, "priority": "accuracy"},
        {"query_complexity": 0.3, "num_documents": 10000, "priority": "speed"},
        {"query_complexity": 0.5, "num_documents": 1000, "priority": "balanced"},
        {"query_complexity": 0.9, "num_documents": 50, "priority": "accuracy"},
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        recommended = selector.recommend_model(**test_case)

    # Show selection stats
    print("\n" + "="*50)
    print("Selection Statistics")
    print("="*50)
    stats = selector.get_selection_stats()
    print(f"Total selections: {stats['total_selections']}")
    print(f"Model distribution: {stats['model_distribution']}")

    print("\n✅ Model configuration test completed!")


if __name__ == "__main__":
    main()