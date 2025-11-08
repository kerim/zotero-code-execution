"""
Practical usage examples for Zotero Code Execution Library.

These examples demonstrate how to use the library in real-world scenarios.
Run these in a code execution environment within Claude Code.
"""

import setup_paths  # Add zotero_mcp to path
from zotero_lib import ZoteroLibrary, SearchOrchestrator, ZoteroItem, format_results
from typing import List


# ============================================================================
# Example 1: Basic Comprehensive Search
# ============================================================================

def example_1_basic_search():
    """
    Most common use case: comprehensive search for a topic.

    This replaces the old pattern of multiple manual searches with limits.
    """
    print("=" * 60)
    print("Example 1: Basic Comprehensive Search")
    print("=" * 60)

    orchestrator = SearchOrchestrator()

    # Single function call performs:
    # - Semantic search (2 variations)
    # - Keyword search (2 variations)
    # - Tag-based search
    # - Deduplication
    # - Ranking
    results = orchestrator.comprehensive_search(
        "embodied cognition",
        max_results=15,
        search_limit_per_strategy=50
    )

    print(f"\nFound {len(results)} most relevant papers:")
    print(format_results(results, include_abstracts=False))


# ============================================================================
# Example 2: Large-Scale Filtering
# ============================================================================

def example_2_filtering():
    """
    Fetch large dataset and filter in code before returning results.

    This is SAFE because filtering happens in code execution environment,
    not in LLM context.
    """
    print("=" * 60)
    print("Example 2: Large-Scale Filtering")
    print("=" * 60)

    library = ZoteroLibrary()
    orchestrator = SearchOrchestrator(library)

    # Fetch 100 items (safe!)
    print("\nFetching 100 items about machine learning...")
    all_items = library.search_items("machine learning", limit=100)
    print(f"Retrieved {len(all_items)} items")

    # Filter to recent journal articles
    print("\nFiltering to recent journal articles...")
    filtered = orchestrator.filter_by_criteria(
        all_items,
        item_types=["journalArticle"],
        date_range=(2022, 2025)
    )
    print(f"After filtering: {len(filtered)} items")

    # Return only top 10 to context
    print("\nTop 10 most relevant:")
    print(format_results(filtered[:10], include_abstracts=False))


# ============================================================================
# Example 3: Multi-Angle Search with Custom Logic
# ============================================================================

def example_3_multi_angle():
    """
    Perform complex multi-angle search with custom logic.

    This demonstrates the power of code execution: you can implement
    arbitrary search strategies that would be impossible with direct MCP.
    """
    print("=" * 60)
    print("Example 3: Multi-Angle Search")
    print("=" * 60)

    library = ZoteroLibrary()
    orchestrator = SearchOrchestrator(library)

    all_results = set()

    # Angle 1: Semantic variations
    print("\nSearching with semantic variations...")
    semantic_queries = [
        "skill transfer between contexts",
        "transfer of learning across domains",
        "generalization of cognitive skills"
    ]

    for query in semantic_queries:
        try:
            results = library.semantic_search(query, limit=30)
            all_results.update(results)
            print(f"  {query}: {len(results)} items")
        except Exception as e:
            print(f"  Semantic search failed: {e}")

    # Angle 2: Keyword variations
    print("\nSearching with keyword variations...")
    keywords = ["transfer", "generalization", "skill acquisition", "learning transfer"]

    for keyword in keywords:
        results = library.search_items(keyword, qmode="everything", limit=30)
        all_results.update(results)
        print(f"  {keyword}: {len(results)} items")

    # Angle 3: Tag-based
    print("\nSearching by tags...")
    try:
        tag_results = library.search_by_tag(["learning", "cognition"], limit=30)
        all_results.update(tag_results)
        print(f"  Tag search: {len(tag_results)} items")
    except Exception as e:
        print(f"  Tag search failed: {e}")

    print(f"\nTotal unique items found: {len(all_results)}")

    # Rank all results
    ranked = orchestrator._rank_items(list(all_results), "skill transfer")

    # Return top 20
    print("\nTop 20 most relevant:")
    print(format_results(ranked[:20], include_abstracts=True, max_abstract_length=150))


# ============================================================================
# Example 4: Iterative Refinement Based on Results
# ============================================================================

def example_4_iterative_refinement():
    """
    Perform initial search, analyze results, refine search based on findings.

    This pattern is only possible with code execution.
    """
    print("=" * 60)
    print("Example 4: Iterative Refinement")
    print("=" * 60)

    library = ZoteroLibrary()
    orchestrator = SearchOrchestrator(library)

    # Initial broad search
    print("\nInitial search for 'neural networks'...")
    initial_results = library.search_items("neural networks", limit=50)
    print(f"Found {len(initial_results)} items")

    # Analyze tags in results
    print("\nAnalyzing tags in results...")
    tag_frequencies = {}
    for item in initial_results:
        for tag in item.tags:
            tag_frequencies[tag] = tag_frequencies.get(tag, 0) + 1

    # Get top 5 most common tags
    top_tags = sorted(tag_frequencies.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nMost common tags:")
    for tag, count in top_tags:
        print(f"  {tag}: {count} papers")

    # Refined search using discovered tags
    print("\nRefining search with common tags...")
    tag_names = [tag for tag, count in top_tags]
    refined_results = orchestrator.filter_by_criteria(
        initial_results,
        required_tags=tag_names[:2]  # Use top 2 tags
    )

    print(f"\nRefined to {len(refined_results)} highly relevant papers:")
    print(format_results(refined_results[:15], include_abstracts=False))


# ============================================================================
# Example 5: Batch Processing Multiple Queries
# ============================================================================

def example_5_batch_processing():
    """
    Process multiple queries and find cross-cutting themes.
    """
    print("=" * 60)
    print("Example 5: Batch Processing")
    print("=" * 60)

    orchestrator = SearchOrchestrator()

    queries = [
        "embodied cognition",
        "skill transfer",
        "reading comprehension",
        "memory consolidation"
    ]

    results_by_query = {}

    print("\nProcessing multiple queries...")
    for query in queries:
        results = orchestrator.comprehensive_search(
            query,
            max_results=10,
            search_limit_per_strategy=30
        )
        results_by_query[query] = results
        print(f"  {query}: {len(results)} results")

    # Find papers that appear in multiple query results
    print("\nFinding cross-cutting papers...")
    all_keys = {}
    for query, items in results_by_query.items():
        for item in items:
            if item.key not in all_keys:
                all_keys[item.key] = {"item": item, "queries": []}
            all_keys[item.key]["queries"].append(query)

    # Papers appearing in 2+ searches
    cross_cutting = [
        (data["item"], data["queries"])
        for key, data in all_keys.items()
        if len(data["queries"]) >= 2
    ]

    if cross_cutting:
        print(f"\nFound {len(cross_cutting)} papers relevant to multiple topics:")
        for item, related_queries in cross_cutting:
            print(f"\n{item.title}")
            print(f"  Relevant to: {', '.join(related_queries)}")
    else:
        print("\nNo cross-cutting papers found")


# ============================================================================
# Example 6: Custom Ranking Strategy
# ============================================================================

def example_6_custom_ranking():
    """
    Implement custom ranking based on specific criteria.
    """
    print("=" * 60)
    print("Example 6: Custom Ranking")
    print("=" * 60)

    library = ZoteroLibrary()

    # Fetch items
    print("\nFetching items about 'cognitive psychology'...")
    items = library.search_items("cognitive psychology", limit=50)
    print(f"Found {len(items)} items")

    # Custom ranking: prefer recent journal articles with many tags
    def custom_score(item: ZoteroItem) -> float:
        score = 0.0

        # Item type bonus
        if item.item_type == "journalArticle":
            score += 20
        elif item.item_type == "book":
            score += 10

        # Recency bonus
        try:
            year = int(item.date[:4])
            if year >= 2023:
                score += 15
            elif year >= 2020:
                score += 10
            elif year >= 2015:
                score += 5
        except (ValueError, IndexError):
            pass

        # Tag richness (more tags = more categorized)
        score += len(item.tags) * 2

        # Has DOI (likely peer-reviewed)
        if item.doi:
            score += 5

        return score

    # Sort by custom score
    ranked = sorted(items, key=custom_score, reverse=True)

    print("\nTop 15 items by custom ranking:")
    print("(Recent journal articles with good metadata)")
    print(format_results(ranked[:15], include_abstracts=False))


# ============================================================================
# Example 7: Finding Papers by Multiple Authors
# ============================================================================

def example_7_author_search():
    """
    Find papers authored by specific researchers.
    """
    print("=" * 60)
    print("Example 7: Author Search")
    print("=" * 60)

    library = ZoteroLibrary()

    # Search for multiple authors
    authors = ["Kahneman", "Tversky", "Thaler"]

    all_papers = set()

    print("\nSearching for papers by specific authors...")
    for author in authors:
        results = library.search_items(
            author,
            qmode="titleCreatorYear",
            limit=20
        )
        all_papers.update(results)
        print(f"  {author}: {len(results)} papers")

    print(f"\nTotal unique papers: {len(all_papers)}")

    # Sort by date (most recent first)
    sorted_papers = sorted(
        all_papers,
        key=lambda x: x.date,
        reverse=True
    )

    print("\nMost recent papers:")
    print(format_results(sorted_papers[:10], include_abstracts=True))


# ============================================================================
# Example 8: Finding Papers by Tag Combinations
# ============================================================================

def example_8_tag_combinations():
    """
    Find papers with specific tag combinations.
    """
    print("=" * 60)
    print("Example 8: Tag Combination Search")
    print("=" * 60)

    library = ZoteroLibrary()
    orchestrator = SearchOrchestrator(library)

    # Get all tags first
    print("\nFetching all tags...")
    all_tags = library.get_tags()
    print(f"Total tags in library: {len(all_tags)}")

    # Find tags related to "learning"
    learning_tags = [tag for tag in all_tags if "learning" in tag.lower()]
    print(f"\nTags related to 'learning': {learning_tags[:10]}")

    # Search by tag combination
    if learning_tags:
        print("\nSearching for papers with learning-related tags...")
        results = library.search_by_tag(
            learning_tags[:3],  # Use top 3 learning tags
            limit=30
        )

        # Filter to recent papers
        filtered = orchestrator.filter_by_criteria(
            results,
            date_range=(2020, 2025)
        )

        print(f"\nFound {len(filtered)} recent papers:")
        print(format_results(filtered[:10], include_abstracts=False))


# ============================================================================
# Main Runner
# ============================================================================

if __name__ == "__main__":
    """
    Run all examples or specific ones.

    To run all: python examples.py
    To run specific: uncomment the examples you want
    """

    # Run all examples
    examples = [
        example_1_basic_search,
        example_2_filtering,
        example_3_multi_angle,
        example_4_iterative_refinement,
        example_5_batch_processing,
        example_6_custom_ranking,
        example_7_author_search,
        example_8_tag_combinations,
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            print("\n" * 3)
            example_func()
            print("\n" + "=" * 60)
            print(f"Example {i} completed successfully")
            print("=" * 60)
        except Exception as e:
            print(f"\nExample {i} failed with error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" * 2)
    print("All examples completed!")
