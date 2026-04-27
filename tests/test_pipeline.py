"""
RAG query recorder — runs each query through the full pipeline and
saves the input, response, and retrieved context to test_results.json.

Run with:
    uv run pytest tests/test_pipeline.py -v -s
"""

import pytest
import json
from pathlib import Path
import sys

QUERIES = [
    "Which product category generates the most revenue?",
    "What sub-categories have the highest profit margins?",
    "Which products are frequently sold at a discount?",
    "Which region has the best sales performance?",
    "Compare sales performance across different states.",
    "Which cities are the top performers?",
    "Compare Technology vs. Furniture sales trends.",
    "How does the West region compare to the East in terms of profit?"
]

RESULTS_FILE = Path(__file__).parent / "test_results.json"
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_query(handler, query: str) -> dict:
    handler.new_input(query)
    handler.retrieve()
    response = handler.generate()
    return {
        "query": query,
        "response": response,
        "context": handler.get_context(),
    }


@pytest.fixture(scope="session")
def handler():
    from app.core.request import Handler
    return Handler()


@pytest.mark.parametrize("query", QUERIES, ids=[
    "category_revenue",
    "subcategory_margins",
    "discounted_products",
    "region_sales",
    "comparing_states_sales",
    "best_cities",
    "tech_vs_furniture",
    "west_vs_east"
])
def test_query(handler, query):
    result = run_query(handler, query)

    print(f"\n{'='*60}")
    print(f"QUERY:    {result['query']}")
    print(f"RESPONSE: {result['response']}")
    print(f"CONTEXT SOURCES: {[c['source'] for c in result['context']]}")

    # Append to results file
    results = []
    if RESULTS_FILE.exists():
        results = json.loads(RESULTS_FILE.read_text())
    results.append({
        "query": result["query"],
        "response": result["response"],
        "context": [
            {"source": c["source"], "distance": c["distance"], "text": c["text"]}
            for c in result["context"]
        ]
    })
    RESULTS_FILE.write_text(json.dumps(results, indent=2))