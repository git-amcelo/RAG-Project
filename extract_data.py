#!/usr/bin/env python3
"""
Data Extraction Script for Week 3
Extracts MS MARCO v2.1 dataset for RAG dense retrieval system

Usage:
    python extract_data.py                    # Extract with defaults
    python extract_data.py --max-queries 500  # Extract 500 queries
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import MSMarcoDataLoader


def main():
    parser = argparse.ArgumentParser(description="Extract MS MARCO data for RAG Week 3")
    parser.add_argument("--split", type=str, default="validation",
                       choices=["validation", "train", "test"],
                       help="Dataset split to extract")
    parser.add_argument("--max-queries", type=int, default=1000,
                       help="Maximum number of queries to extract")
    parser.add_argument("--max-passages", type=int, default=10,
                       help="Maximum passages per query")
    args = parser.parse_args()

    print("="*60)
    print("  MS MARCO v2.1 Data Extraction for Week 3")
    print("="*60)

    print(f"\nConfiguration:")
    print(f"  Split: {args.split}")
    print(f"  Max queries: {args.max_queries}")
    print(f"  Max passages per query: {args.max_passages}")

    # Initialize loader
    loader = MSMarcoDataLoader("data/raw")

    # Extract data
    print(f"\n{'='*60}")
    print("  Extracting data from MS MARCO v2.1...")
    print(f"{'='*60}\n")

    loader.extract_from_v21(
        split=args.split,
        max_queries=args.max_queries,
        max_passages_per_query=args.max_passages
    )

    # Show summary
    print(f"\n{'='*60}")
    print("  EXTRACTION COMPLETE!")
    print(f"{'='*60}")
    print(f"\n📊 Data Summary:")
    print(f"  ✅ Queries:   {len(loader.queries)}")
    print(f"  ✅ Passages:  {len(loader.passages)}")
    print(f"  ✅ Qrels:     {len(loader.qrels)} queries with relevance")

    print(f"\n📁 Files saved in data/processed/:")
    print(f"  - queries.json")
    print(f"  - passages.json")
    print(f"  - qrels.json")

    # Show sample
    print(f"\n📝 Sample Query:")
    qid, query = list(loader.queries.items())[0]
    print(f"  ID: {qid}")
    print(f"  Query: {query}")

    print(f"\n📝 Sample Passage:")
    pid, passage = list(loader.passages.items())[0]
    print(f"  ID: {pid}")
    print(f"  Text: {passage[:100]}...")

    print(f"\n{'='*60}\n")

    return 0


if __name__ == "__main__":
    exit(main())
