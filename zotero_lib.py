"""
Zotero Library Wrapper for Code Execution

This module wraps the Zotero MCP tools as a Python library that can be imported
and used in code execution environments. This enables:

1. Large-scale data filtering before returning results to LLM context
2. Complex search orchestration with loops and conditionals
3. Deduplication and ranking of results
4. Intermediate result persistence

Based on Anthropic's code execution with MCP pattern:
https://www.anthropic.com/engineering/code-execution-with-mcp
"""

from typing import List, Dict, Any, Optional, Literal, Set
from dataclasses import dataclass
from collections import defaultdict
import re
import json

# Import the actual Zotero MCP modules
from zotero_mcp.client import get_zotero_client, format_item_metadata
from zotero_mcp.semantic_search import create_semantic_search
from zotero_mcp.utils import format_creators
from pathlib import Path


@dataclass
class ZoteroItem:
    """Simplified representation of a Zotero item for easier manipulation."""
    key: str
    title: str
    item_type: str
    date: str
    authors: str
    abstract: str
    tags: List[str]
    url: Optional[str]
    doi: Optional[str]
    raw_data: Dict[str, Any]

    @classmethod
    def from_raw(cls, item: Dict[str, Any]) -> 'ZoteroItem':
        """Create a ZoteroItem from raw Zotero API response."""
        data = item.get("data", {})
        creators = data.get("creators", [])
        tags = [tag.get("tag", "") for tag in data.get("tags", [])]

        return cls(
            key=data.get("key", ""),
            title=data.get("title", "Untitled"),
            item_type=data.get("itemType", "unknown"),
            date=data.get("date", ""),
            authors=format_creators(creators),
            abstract=data.get("abstractNote", ""),
            tags=tags,
            url=data.get("url"),
            doi=data.get("DOI"),
            raw_data=item
        )

    def to_markdown(self, include_abstract: bool = True) -> str:
        """Convert to markdown format."""
        lines = [
            f"## {self.title}",
            f"**Key:** {self.key}",
            f"**Type:** {self.item_type}",
            f"**Date:** {self.date}",
            f"**Authors:** {self.authors}",
        ]

        if self.doi:
            lines.append(f"**DOI:** {self.doi}")
        if self.url:
            lines.append(f"**URL:** {self.url}")
        if self.tags:
            tag_str = " ".join([f"`{tag}`" for tag in self.tags])
            lines.append(f"**Tags:** {tag_str}")

        if include_abstract and self.abstract:
            lines.extend(["", "**Abstract:**", self.abstract])

        return "\n".join(lines)

    def __hash__(self):
        """Make items hashable by key for deduplication."""
        return hash(self.key)

    def __eq__(self, other):
        """Items are equal if they have the same key."""
        if isinstance(other, ZoteroItem):
            return self.key == other.key
        return False


class ZoteroLibrary:
    """
    High-level wrapper for Zotero operations optimized for code execution.

    This class provides methods that can filter, rank, and process large
    datasets before returning results to the LLM context.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Zotero library wrapper.

        Args:
            config_path: Path to Zotero MCP config file
        """
        self.zot = get_zotero_client()
        self.config_path = config_path or str(Path.home() / ".config" / "zotero-mcp" / "config.json")

        # Initialize semantic search if available
        try:
            self.semantic_search = create_semantic_search(self.config_path)
        except Exception as e:
            print(f"Warning: Semantic search not available: {e}")
            self.semantic_search = None

    def search_items(
        self,
        query: str,
        qmode: Literal["titleCreatorYear", "everything"] = "titleCreatorYear",
        item_type: str = "-attachment",
        limit: int = 100,
        tag: Optional[List[str]] = None
    ) -> List[ZoteroItem]:
        """
        Search Zotero library and return items as ZoteroItem objects.

        Args:
            query: Search query string
            qmode: Query mode
            item_type: Item type filter
            limit: Maximum results (can be large since filtering happens in code)
            tag: Tag conditions

        Returns:
            List of ZoteroItem objects
        """
        self.zot.add_parameters(
            q=query,
            qmode=qmode,
            itemType=item_type,
            limit=limit,
            tag=tag or []
        )
        results = self.zot.items()
        return [ZoteroItem.from_raw(item) for item in results]

    def semantic_search(
        self,
        query: str,
        limit: int = 100,
        search_type: Literal["hybrid", "vector", "keyword"] = "hybrid"
    ) -> List[ZoteroItem]:
        """
        Perform semantic search on Zotero library.

        Args:
            query: Natural language query
            limit: Maximum results
            search_type: Type of search to perform

        Returns:
            List of ZoteroItem objects
        """
        if not self.semantic_search:
            raise RuntimeError("Semantic search not initialized")

        results = self.semantic_search.search(
            query,
            n_results=limit,
            search_type=search_type
        )

        # Convert results to ZoteroItem objects
        items = []
        for result in results.get("items", []):
            item_key = result.get("key")
            if item_key:
                # Fetch full item data
                item = self.zot.item(item_key)
                items.append(ZoteroItem.from_raw(item))

        return items

    def search_by_tag(
        self,
        tags: List[str],
        item_type: str = "-attachment",
        limit: int = 100
    ) -> List[ZoteroItem]:
        """
        Search by tags.

        Args:
            tags: List of tag conditions
            item_type: Item type filter
            limit: Maximum results

        Returns:
            List of ZoteroItem objects
        """
        self.zot.add_parameters(
            q="",
            tag=tags,
            itemType=item_type,
            limit=limit
        )
        results = self.zot.items()
        return [ZoteroItem.from_raw(item) for item in results]

    def get_tags(self) -> List[str]:
        """
        Get all tags from the library.

        Returns:
            List of tag names
        """
        tags = self.zot.tags()
        return [tag.get("tag", "") for tag in tags]

    def get_recent(self, limit: int = 50) -> List[ZoteroItem]:
        """
        Get recently added items.

        Args:
            limit: Maximum number of items

        Returns:
            List of ZoteroItem objects
        """
        self.zot.add_parameters(limit=limit, sort="dateAdded", direction="desc")
        results = self.zot.items()
        return [ZoteroItem.from_raw(item) for item in results]


class SearchOrchestrator:
    """
    High-level search orchestration with automatic deduplication and ranking.

    This class implements the multi-strategy search patterns described in the
    zotero-mcp skill, but performs all operations in code before returning
    filtered results.
    """

    def __init__(self, library: Optional[ZoteroLibrary] = None):
        """
        Initialize the search orchestrator.

        Args:
            library: ZoteroLibrary instance (creates new one if not provided)
        """
        self.library = library or ZoteroLibrary()

    def comprehensive_search(
        self,
        query: str,
        max_results: int = 20,
        use_semantic: bool = True,
        use_keyword: bool = True,
        use_tags: bool = True,
        search_limit_per_strategy: int = 50
    ) -> List[ZoteroItem]:
        """
        Perform comprehensive multi-strategy search with automatic deduplication.

        This is the core method that implements safe, comprehensive searching
        by combining multiple search strategies in code and filtering results
        before returning to LLM context.

        Args:
            query: Search query
            max_results: Maximum number of unique results to return
            use_semantic: Whether to use semantic search
            use_keyword: Whether to use keyword search
            use_tags: Whether to use tag-based search
            search_limit_per_strategy: Items to fetch per strategy (can be large)

        Returns:
            Deduplicated and ranked list of ZoteroItem objects
        """
        all_items: Set[ZoteroItem] = set()

        # Strategy 1: Semantic search with variations
        if use_semantic and self.library.semantic_search:
            try:
                # Original query
                items = self.library.semantic_search(
                    query,
                    limit=search_limit_per_strategy,
                    search_type="hybrid"
                )
                all_items.update(items)

                # Try vector-only for conceptual matches
                items = self.library.semantic_search(
                    query,
                    limit=search_limit_per_strategy,
                    search_type="vector"
                )
                all_items.update(items)
            except Exception as e:
                print(f"Semantic search failed: {e}")

        # Strategy 2: Keyword search
        if use_keyword:
            try:
                items = self.library.search_items(
                    query,
                    qmode="everything",
                    limit=search_limit_per_strategy
                )
                all_items.update(items)

                # Try title/author/year mode
                items = self.library.search_items(
                    query,
                    qmode="titleCreatorYear",
                    limit=search_limit_per_strategy
                )
                all_items.update(items)
            except Exception as e:
                print(f"Keyword search failed: {e}")

        # Strategy 3: Tag-based search
        if use_tags:
            try:
                # Extract potential tags from query
                query_words = query.lower().split()
                all_tags = [tag.lower() for tag in self.library.get_tags()]

                # Find tags that match query words
                matching_tags = [
                    tag for tag in all_tags
                    if any(word in tag for word in query_words)
                ]

                if matching_tags:
                    items = self.library.search_by_tag(
                        matching_tags[:5],  # Limit to top 5 matching tags
                        limit=search_limit_per_strategy
                    )
                    all_items.update(items)
            except Exception as e:
                print(f"Tag search failed: {e}")

        # Convert set back to list and rank
        ranked_items = self._rank_items(list(all_items), query)

        # Return top N results
        return ranked_items[:max_results]

    def _rank_items(self, items: List[ZoteroItem], query: str) -> List[ZoteroItem]:
        """
        Rank items by relevance to query.

        Simple ranking based on:
        1. Query term frequency in title/abstract
        2. Recency (more recent = higher)
        3. Tag matches

        Args:
            items: List of items to rank
            query: Original search query

        Returns:
            Sorted list of items (most relevant first)
        """
        query_terms = set(query.lower().split())

        def score_item(item: ZoteroItem) -> float:
            score = 0.0

            # Title matches (highest weight)
            title_lower = item.title.lower()
            title_matches = sum(1 for term in query_terms if term in title_lower)
            score += title_matches * 10

            # Abstract matches
            abstract_lower = item.abstract.lower()
            abstract_matches = sum(1 for term in query_terms if term in abstract_lower)
            score += abstract_matches * 2

            # Tag matches
            tag_lower = [tag.lower() for tag in item.tags]
            tag_matches = sum(1 for term in query_terms if any(term in tag for tag in tag_lower))
            score += tag_matches * 5

            # Recency bonus (very simple - just check if date exists and is recent)
            if item.date:
                try:
                    year = int(item.date[:4])
                    if year >= 2020:
                        score += 3
                    elif year >= 2015:
                        score += 1
                except (ValueError, IndexError):
                    pass

            return score

        # Sort by score (descending)
        items_with_scores = [(item, score_item(item)) for item in items]
        items_with_scores.sort(key=lambda x: x[1], reverse=True)

        return [item for item, score in items_with_scores]

    def filter_by_criteria(
        self,
        items: List[ZoteroItem],
        item_types: Optional[List[str]] = None,
        date_range: Optional[tuple[int, int]] = None,
        required_tags: Optional[List[str]] = None,
        excluded_tags: Optional[List[str]] = None
    ) -> List[ZoteroItem]:
        """
        Filter items by various criteria.

        This allows you to fetch a large set of results and then filter
        them in code before returning to LLM context.

        Args:
            items: Items to filter
            item_types: List of allowed item types
            date_range: (min_year, max_year) tuple
            required_tags: Tags that must be present
            excluded_tags: Tags that must not be present

        Returns:
            Filtered list of items
        """
        filtered = items

        if item_types:
            filtered = [item for item in filtered if item.item_type in item_types]

        if date_range:
            min_year, max_year = date_range
            filtered = [
                item for item in filtered
                if item.date and min_year <= int(item.date[:4]) <= max_year
            ]

        if required_tags:
            required_tags_lower = [tag.lower() for tag in required_tags]
            filtered = [
                item for item in filtered
                if any(
                    req_tag in [tag.lower() for tag in item.tags]
                    for req_tag in required_tags_lower
                )
            ]

        if excluded_tags:
            excluded_tags_lower = [tag.lower() for tag in excluded_tags]
            filtered = [
                item for item in filtered
                if not any(
                    exc_tag in [tag.lower() for tag in item.tags]
                    for exc_tag in excluded_tags_lower
                )
            ]

        return filtered


def format_results(
    items: List[ZoteroItem],
    include_abstracts: bool = True,
    max_abstract_length: int = 300
) -> str:
    """
    Format search results as markdown for LLM context.

    Args:
        items: Items to format
        include_abstracts: Whether to include abstracts
        max_abstract_length: Maximum abstract length

    Returns:
        Markdown-formatted string
    """
    if not items:
        return "No results found."

    output = [f"# Search Results ({len(items)} items)\n"]

    for i, item in enumerate(items, 1):
        output.append(f"## {i}. {item.title}")
        output.append(f"**Key:** {item.key}")
        output.append(f"**Type:** {item.item_type}")
        output.append(f"**Date:** {item.date}")
        output.append(f"**Authors:** {item.authors}")

        if item.doi:
            output.append(f"**DOI:** {item.doi}")
        if item.url:
            output.append(f"**URL:** {item.url}")
        if item.tags:
            tag_str = " ".join([f"`{tag}`" for tag in item.tags])
            output.append(f"**Tags:** {tag_str}")

        if include_abstracts and item.abstract:
            abstract = item.abstract
            if len(abstract) > max_abstract_length:
                abstract = abstract[:max_abstract_length] + "..."
            output.append(f"\n**Abstract:** {abstract}")

        output.append("")  # Blank line between items

    return "\n".join(output)


# Example usage patterns
if __name__ == "__main__":
    # Example 1: Simple comprehensive search
    orchestrator = SearchOrchestrator()
    results = orchestrator.comprehensive_search(
        "embodied cognition",
        max_results=20,
        search_limit_per_strategy=50  # Fetch 50 per strategy, return top 20
    )
    print(format_results(results))

    # Example 2: Search with filtering
    library = ZoteroLibrary()
    items = library.search_items("reading comprehension", limit=100)

    # Filter to recent journal articles
    filtered = orchestrator.filter_by_criteria(
        items,
        item_types=["journalArticle"],
        date_range=(2020, 2025)
    )

    print(format_results(filtered[:10]))

    # Example 3: Multi-angle search with custom ranking
    all_results = set()

    # Semantic variations
    for query_variation in [
        "theories of embodied cognition",
        "how body influences thought",
        "physical experience cognitive processes"
    ]:
        results = library.semantic_search(query_variation, limit=30)
        all_results.update(results)

    # Keyword variations
    for keyword in ["embodiment", "embodied cognition", "grounded cognition"]:
        results = library.search_items(keyword, limit=30)
        all_results.update(results)

    # Rank and return top 20
    ranked = orchestrator._rank_items(list(all_results), "embodied cognition")
    print(format_results(ranked[:20]))
