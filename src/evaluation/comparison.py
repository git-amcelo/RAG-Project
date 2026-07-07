"""
Performance Comparison Module for RAG Evaluation
Week 8: Compare baseline vs optimized configurations

Implements:
- Before/after performance comparison
- Formatted table generation (Markdown, CSV, JSON)
- Metric comparison with improvement percentages
"""

import json
import csv
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    # Retrieval metrics
    recall_at_1: float
    recall_at_5: float
    recall_at_10: float
    precision_at_5: float
    mrr: float
    map_score: float

    # Performance metrics
    avg_retrieval_time: float
    avg_generation_time: float
    avg_total_time: float

    # Token metrics
    avg_input_tokens: int = 0
    avg_output_tokens: int = 0
    avg_total_tokens: int = 0

    # Faithfulness metrics (Week 8)
    faithfulness_score: float = 0.0
    faithful_rate: float = 0.0

    # Cache metrics (Week 8)
    cache_hit_rate: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class PerformanceComparer:
    """
    Compare performance between baseline and optimized configurations

    Usage:
        comparer = PerformanceComparer()
        result = comparer.compare(baseline_metrics, optimized_metrics)
        table = comparer.generate_comparison_table(result)
    """

    def __init__(self):
        """Initialize performance comparer"""
        self.comparisons = []

    def compare(
        self,
        baseline: PerformanceMetrics,
        optimized: PerformanceMetrics,
        baseline_name: str = "Baseline",
        optimized_name: str = "Optimized"
    ) -> Dict[str, Any]:
        """
        Compare baseline vs optimized metrics

        Args:
            baseline: Baseline performance metrics
            optimized: Optimized performance metrics
            baseline_name: Name for baseline configuration
            optimized_name: Name for optimized configuration

        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "baseline_name": baseline_name,
            "optimized_name": optimized_name,
            "baseline": baseline.to_dict(),
            "optimized": optimized.to_dict(),
            "improvements": {},
            "summary": {}
        }

        # Calculate improvements for each metric
        metrics_to_compare = [
            "recall_at_1", "recall_at_5", "recall_at_10",
            "precision_at_5", "mrr", "map_score",
            "avg_retrieval_time", "avg_generation_time", "avg_total_time",
            "avg_total_tokens", "faithfulness_score", "faithful_rate", "cache_hit_rate"
        ]

        for metric in metrics_to_compare:
            baseline_val = getattr(baseline, metric, 0)
            optimized_val = getattr(optimized, metric, 0)

            if baseline_val > 0:
                improvement = self._calculate_improvement(baseline_val, optimized_val, metric)
                comparison["improvements"][metric] = improvement

        # Calculate summary
        comparison["summary"] = self._generate_summary(comparison)

        self.comparisons.append(comparison)
        return comparison

    def _calculate_improvement(
        self,
        baseline: float,
        optimized: float,
        metric: str
    ) -> Dict[str, Any]:
        """
        Calculate improvement between baseline and optimized

        Returns:
            Dict with absolute and relative improvement
        """
        # For time metrics, lower is better (improvement = reduction)
        # For quality metrics, higher is better (improvement = increase)
        is_time_metric = "time" in metric or "token" in metric

        if is_time_metric:
            # Time reduction: positive improvement means faster
            absolute = baseline - optimized
            relative = (absolute / max(baseline, 0.001)) * 100
            direction = "faster" if absolute > 0 else "slower"
        else:
            # Quality improvement: positive improvement means better
            absolute = optimized - baseline
            relative = (absolute / max(abs(baseline), 0.001)) * 100
            direction = "better" if absolute > 0 else "worse"

        return {
            "baseline": baseline,
            "optimized": optimized,
            "absolute_change": absolute,
            "relative_change": relative,
            "direction": direction
        }

    def _generate_summary(self, comparison: Dict) -> Dict[str, Any]:
        """Generate summary of key improvements"""
        improvements = comparison["improvements"]

        summary = {
            "quality_improvements": [],
            "performance_improvements": [],
            "overall_assessment": ""
        }

        # Quality improvements
        for metric in ["recall_at_5", "mrr", "faithfulness_score"]:
            if metric in improvements:
                imp = improvements[metric]
                if imp["relative_change"] > 5:  # At least 5% improvement
                    summary["quality_improvements"].append({
                        "metric": metric,
                        "improvement": f"{imp['relative_change']:.1f}% {imp['direction']}"
                    })

        # Performance improvements
        for metric in ["avg_total_time", "avg_total_tokens"]:
            if metric in improvements:
                imp = improvements[metric]
                if imp["relative_change"] > 10:  # At least 10% improvement
                    summary["performance_improvements"].append({
                        "metric": metric,
                        "improvement": f"{imp['relative_change']:.1f}% {imp['direction']}"
                    })

        # Overall assessment
        total_improvements = len(summary["quality_improvements"]) + len(summary["performance_improvements"])
        if total_improvements >= 3:
            summary["overall_assessment"] = "Significant improvement across multiple metrics"
        elif total_improvements >= 1:
            summary["overall_assessment"] = "Moderate improvement in key areas"
        else:
            summary["overall_assessment"] = "Minimal or no improvement detected"

        return summary

    def generate_comparison_table(
        self,
        comparison: Dict[str, Any],
        format: str = "markdown"
    ) -> str:
        """
        Generate formatted comparison table

        Args:
            comparison: Comparison result from compare()
            format: Output format (markdown, csv, json)

        Returns:
            Formatted table string
        """
        if format == "json":
            return json.dumps(comparison, indent=2)

        if format == "csv":
            return self._generate_csv_table(comparison)

        if format == "markdown":
            return self._generate_markdown_table(comparison)

        raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_table(self, comparison: Dict) -> str:
        """Generate Markdown formatted table"""
        lines = []

        # Header
        lines.append(f"# Performance Comparison Report")
        lines.append(f"")
        lines.append(f"**Generated:** {comparison['timestamp']}")
        lines.append(f"")
        lines.append(f"## Configuration Comparison")
        lines.append(f"")
        lines.append(f"| Metric | {comparison['baseline_name']} | {comparison['optimized_name']} | Improvement |")
        lines.append(f"|--------|---------------------|----------------------|-------------|")

        # Metrics table
        improvements = comparison["improvements"]

        # Quality metrics
        lines.append(f"")
        lines.append(f"### Retrieval Quality")
        lines.append(f"")

        for metric in ["recall_at_1", "recall_at_5", "recall_at_10", "precision_at_5", "mrr", "map_score"]:
            if metric in improvements:
                imp = improvements[metric]
                baseline_str = f"{imp['baseline']:.4f}"
                optimized_str = f"{imp['optimized']:.4f}"
                improvement_str = f"{imp['relative_change']:+.1f}%"

                lines.append(f"| {metric} | {baseline_str} | {optimized_str} | {improvement_str} |")

        # Performance metrics
        lines.append(f"")
        lines.append(f"### Performance")
        lines.append(f"")

        for metric in ["avg_total_time", "avg_total_tokens"]:
            if metric in improvements:
                imp = improvements[metric]
                baseline_str = f"{imp['baseline']:.4f}"
                optimized_str = f"{imp['optimized']:.4f}"
                improvement_str = f"{imp['relative_change']:+.1f}%"

                lines.append(f"| {metric} | {baseline_str} | {optimized_str} | {improvement_str} |")

        # Faithfulness (Week 8)
        if "faithfulness_score" in improvements:
            lines.append(f"")
            lines.append(f"### Answer Quality (Week 8)")
            lines.append(f"")

            for metric in ["faithfulness_score", "faithful_rate"]:
                if metric in improvements:
                    imp = improvements[metric]
                    baseline_str = f"{imp['baseline']:.4f}"
                    optimized_str = f"{imp['optimized']:.4f}"
                    improvement_str = f"{imp['relative_change']:+.1f}%"

                    lines.append(f"| {metric} | {baseline_str} | {optimized_str} | {improvement_str} |")

        # Summary
        lines.append(f"")
        lines.append(f"## Summary")
        lines.append(f"")
        lines.append(f"**Overall Assessment:** {comparison['summary']['overall_assessment']}")
        lines.append(f"")

        if comparison['summary']['quality_improvements']:
            lines.append(f"**Quality Improvements:**")
            for imp in comparison['summary']['quality_improvements']:
                lines.append(f"  - {imp['metric']}: {imp['improvement']}")
            lines.append(f"")

        if comparison['summary']['performance_improvements']:
            lines.append(f"**Performance Improvements:**")
            for imp in comparison['summary']['performance_improvements']:
                lines.append(f"  - {imp['metric']}: {imp['improvement']}")
            lines.append(f"")

        return "\n".join(lines)

    def _generate_csv_table(self, comparison: Dict) -> str:
        """Generate CSV formatted table"""
        lines = []
        lines.append("metric,baseline,optimized,absolute_change,relative_change,direction")

        improvements = comparison["improvements"]
        for metric, imp in improvements.items():
            lines.append(
                f"{metric},{imp['baseline']},{imp['optimized']},"
                f"{imp['absolute_change']},{imp['relative_change']},{imp['direction']}"
            )

        return "\n".join(lines)

    def export_results(
        self,
        comparison: Dict[str, Any],
        filepath: str,
        format: str = "json"
    ) -> None:
        """
        Export comparison results to file

        Args:
            comparison: Comparison result
            filepath: Output file path
            format: Export format (json, csv, md)
        """
        content = self.generate_comparison_table(comparison, format)

        with open(filepath, 'w') as f:
            f.write(content)

        print(f"✓ Comparison results exported to {filepath}")

    def get_all_comparisons(self) -> List[Dict]:
        """Get all stored comparisons"""
        return self.comparisons


def create_sample_comparison() -> Dict:
    """Create a sample comparison for testing"""
    baseline = PerformanceMetrics(
        recall_at_1=0.65,
        recall_at_5=0.82,
        recall_at_10=0.91,
        precision_at_5=0.72,
        mrr=0.74,
        map_score=0.68,
        avg_retrieval_time=0.15,
        avg_generation_time=1.2,
        avg_total_time=1.35,
        avg_total_tokens=1200,
        faithfulness_score=0.75,
        faithful_rate=0.70,
        cache_hit_rate=0.0
    )

    optimized = PerformanceMetrics(
        recall_at_1=0.71,
        recall_at_5=0.88,
        recall_at_10=0.94,
        precision_at_5=0.79,
        mrr=0.81,
        map_score=0.75,
        avg_retrieval_time=0.08,
        avg_generation_time=0.9,
        avg_total_time=0.98,
        avg_total_tokens=950,
        faithfulness_score=0.82,
        faithful_rate=0.78,
        cache_hit_rate=0.35
    )

    comparer = PerformanceComparer()
    return comparer.compare(baseline, optimized)


def main():
    """Test the comparison module"""
    print("=== Performance Comparison Test ===\n")

    comparison = create_sample_comparison()
    comparer = PerformanceComparer()

    print("Markdown Table:")
    print("-" * 60)
    markdown = comparer.generate_comparison_table(comparison, "markdown")
    print(markdown)

    print("\n" + "=" * 60)
    print("CSV Export:")
    print("-" * 60)
    csv = comparer.generate_comparison_table(comparison, "csv")
    print(csv)

    print("\n✅ Performance comparison test completed!")


if __name__ == "__main__":
    main()
