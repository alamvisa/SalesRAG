"""
Integration tests for the SalesRAG pipeline.

Run with:
    pytest test_rag_pipeline.py -v
    pytest test_rag_pipeline.py -v --tb=short   # shorter tracebacks
    pytest test_rag_pipeline.py -v -s           # show print/log output
"""

import pytest
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


QUERIES = [
    "Which product category generates the most revenue?",
    "What sub-categories have the highest profit margins?",
    "Which products are frequently sold at a discount?",
    "Which region has the best sales performance?",
    "Compare sales performance across different states.",
    "Which cities are the top performers?"
]


def run_query(handler, query: str) -> dict:
    """
    Execute the full RAG pipeline for a single query and return a result dict.
    Calls filter() unconditionally to work around the broken process() return
    value (see: Handler.process() returns None, not 1).
    """
    handler.new_input(query)
    handler.filter()
    handler.retrieve()
    response = handler.generate()

    return {
        "query": query,
        "response": response,
        "context": handler.get_context(),
    }

@pytest.fixture(scope="session")
def loaded_db():
    """
    Loads the ChromaDB once per test session.
    If the DB already exists on disk it is reused; pass --reload on the CLI
    to force a fresh ingest (mirrors main.py behaviour).
    """
    from app.core.config.settings import config
    from app.pipeline.load import load
    from app.pipeline.process import process

    chroma_path = config.DATA_PROCESSED_DIR / "chroma"

    if not chroma_path.exists():
        # Re-process raw files then load embeddings
        raw_files = list(config.DATA_RAW_DIR.iterdir())
        assert raw_files, (
            f"No raw data files found in {config.DATA_RAW_DIR}. "
            "Place your CSV(s) there before running tests."
        )
        for f in raw_files:
            process(f.name)
        load()

    return True  # signal that DB is ready


@pytest.fixture(scope="session")
def handler(loaded_db):
    """
    A single Handler instance reused across all tests (embedding model is
    expensive to reload).
    """
    from app.core.request import Handler
    return Handler()

@pytest.mark.parametrize("query", QUERIES, ids=[
    "category_revenue",
    "subcategory_margins",
    "discounted_products",
])
class TestRAGPipelineSmoke:
    """Basic end-to-end checks: pipeline runs and returns non-empty output."""

    def test_returns_a_response(self, handler, query):
        result = run_query(handler, query)
        assert result["response"] is not None, \
            f"Generator returned None for: {query!r}"
        assert isinstance(result["response"], str), \
            f"Response should be a string, got {type(result['response'])}"
        assert len(result["response"].strip()) > 0, \
            f"Response is blank for: {query!r}"

    def test_context_is_populated(self, handler, query):
        result = run_query(handler, query)
        assert result["context"], \
            f"No context chunks retrieved for: {query!r}"

    def test_context_chunks_have_required_keys(self, handler, query):
        result = run_query(handler, query)
        required_keys = {"text", "metadata", "distance", "source"}
        for i, chunk in enumerate(result["context"]):
            missing = required_keys - chunk.keys()
            assert not missing, \
                f"Chunk {i} missing keys {missing} for query: {query!r}"

    def test_context_distances_are_within_threshold(self, handler, query):
        from app.core.config.settings import config
        result = run_query(handler, query)
        for chunk in result["context"]:
            assert chunk["distance"] < config.TRESHOLD, (
                f"Chunk from '{chunk['source']}' has distance "
                f"{chunk['distance']:.4f} >= threshold {config.TRESHOLD} "
                f"for query: {query!r}"
            )


class TestCategoryRevenueQuery:
    QUERY = QUERIES[0]  # "Which product category generates the most revenue?"

    def test_context_includes_category_source(self, handler):
        result = run_query(handler, self.QUERY)
        sources = {c["source"] for c in result["context"]}
        category_sources = {
            "agg_item_category",
            "agg_year_x_category",
            "agg_month_x_category",
            "agg_state_x_category",
        }
        assert sources & category_sources, (
            f"Expected at least one category-level source in context, got: {sources}"
        )

    def test_response_mentions_a_category(self, handler):
        result = run_query(handler, self.QUERY)
        known_categories = ["Furniture", "Technology", "Office Supplies"]
        response_lower = result["response"].lower()
        matched = [c for c in known_categories if c.lower() in response_lower]
        assert matched, (
            f"Response does not mention any known category {known_categories}.\n"
            f"Response was: {result['response']}"
        )


class TestSubcategoryMarginsQuery:
    QUERY = QUERIES[1]  # "What sub-categories have the highest profit margins?"

    def test_context_includes_subcategory_source(self, handler):
        result = run_query(handler, self.QUERY)
        sources = {c["source"] for c in result["context"]}
        assert "agg_item_sub_category" in sources, (
            f"Expected 'agg_item_sub_category' in context sources, got: {sources}"
        )

    def test_context_metadata_has_margin(self, handler):
        result = run_query(handler, self.QUERY)
        sub_cat_chunks = [
            c for c in result["context"]
            if c["source"] == "agg_item_sub_category"
        ]
        for chunk in sub_cat_chunks:
            assert "margin" in chunk["metadata"], (
                f"Sub-category chunk missing 'margin' in metadata: {chunk['metadata']}"
            )

    def test_response_mentions_margin_or_profit(self, handler):
        result = run_query(handler, self.QUERY)
        keywords = ["margin", "profit", "profitable"]
        response_lower = result["response"].lower()
        assert any(kw in response_lower for kw in keywords), (
            f"Response doesn't mention margin/profit.\nResponse: {result['response']}"
        )


class TestDiscountedProductsQuery:
    QUERY = QUERIES[2]  # "Which products are frequently sold at a discount?"

    def test_context_includes_product_or_transaction_source(self, handler):
        result = run_query(handler, self.QUERY)
        sources = {c["source"] for c in result["context"]}
        discount_relevant = {"agg_product", "agg_item_sub_category", "transactions"}
        assert sources & discount_relevant, (
            f"Expected a product/transaction source in context, got: {sources}"
        )

    def test_context_metadata_has_discount_field(self, handler):
        result = run_query(handler, self.QUERY)
        chunks_with_discount = [
            c for c in result["context"]
            if "discount_rate" in c["metadata"] or "discount" in c["metadata"]
        ]
        assert chunks_with_discount, (
            "No context chunks contain discount metadata. "
            "Check that discount fields are stored during ingestion."
        )

    def test_response_mentions_discount(self, handler):
        result = run_query(handler, self.QUERY)
        keywords = ["discount", "discounted", "markdown", "price reduction"]
        response_lower = result["response"].lower()
        assert any(kw in response_lower for kw in keywords), (
            f"Response doesn't mention discounting.\nResponse: {result['response']}"
        )


class TestContextQuality:

    @pytest.mark.parametrize("query", QUERIES, ids=[
        "category_revenue",
        "subcategory_margins",
        "discounted_products",
    ])
    def test_context_is_sorted_by_distance(self, handler, query):
        result = run_query(handler, query)
        distances = [c["distance"] for c in result["context"]]
        assert distances == sorted(distances), \
            "Context chunks are not sorted by ascending distance (closest first)."

    @pytest.mark.parametrize("query", QUERIES, ids=[
        "category_revenue",
        "subcategory_margins",
        "discounted_products",
    ])
    def test_no_duplicate_chunk_texts(self, handler, query):
        result = run_query(handler, query)
        texts = [c["text"] for c in result["context"]]
        assert len(texts) == len(set(texts)), \
            f"Duplicate chunks found in context for: {query!r}"