# Zotero Code Execution Library

A Python library wrapper for Zotero MCP that enables efficient code-based search orchestration, based on [Anthropic's code execution with MCP pattern](https://www.anthropic.com/engineering/code-execution-with-mcp).

## The Problem

The current Zotero MCP implementation has a critical limitation: large responses can cause Claude Desktop to crash and delete conversations. This requires:

- Manual `limit=10` workarounds on every search
- Multiple sequential searches to get comprehensive results
- Claude manually orchestrating complex search strategies
- All search results loading into LLM context

## The Solution

Code execution allows Claude to write Python code that:

1. **Fetches large datasets** (50-100+ items per search)
2. **Filters and ranks in code** (deduplication, scoring, filtering)
3. **Returns only top results** to LLM context
4. **Eliminates crash risk** (large data stays in execution environment)

### Token Savings

Following Anthropic's pattern, this approach can reduce token usage by ~98%:
- **Before:** Load all tool definitions + all search results into context
- **After:** Load only library imports + final filtered results

## Architecture

```
┌─────────────────────────────────────────────┐
│ Claude Code (LLM Context)                   │
│  - Writes Python code                       │
│  - Imports zotero_lib                       │
│  - Receives only filtered results           │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Code Execution Environment                  │
│  ┌─────────────────────────────────────┐   │
│  │ zotero_lib.py (This Library)        │   │
│  │  - ZoteroLibrary (search methods)   │   │
│  │  - SearchOrchestrator (multi-search)│   │
│  │  - Filtering & Ranking              │   │
│  └────────────────┬────────────────────┘   │
│                   │                         │
│                   ▼                         │
│  ┌─────────────────────────────────────┐   │
│  │ Zotero MCP (imported as library)    │   │
│  │  - client.py                         │   │
│  │  - semantic_search.py                │   │
│  │  - All other modules                 │   │
│  └────────────────┬────────────────────┘   │
└───────────────────┼─────────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ Zotero API / Local DB │
         └──────────────────────┘
```

## Installation

1. **Prerequisites:**
   - Zotero MCP already installed (via pipx)
   - Python 3.8+

2. **Install the library:**
   ```bash
   cd /Users/niyaro/Documents/Code/zotero-code-execution
   pip install -e .
   ```

   Or just copy `zotero_lib.py` to your project and import it.

## Usage Examples

### Example 1: Simple Comprehensive Search

Instead of this (old way with manual limits):
```python
# Old: Multiple small searches manually orchestrated by Claude
results1 = zotero_semantic_search("embodied cognition", limit=10)
results2 = zotero_semantic_search("embodiment theory", limit=10)
results3 = zotero_search_items("embodied cognition", limit=10)
# ... manually combine and deduplicate
```

Do this (new way):
```python
from zotero_lib import SearchOrchestrator

orchestrator = SearchOrchestrator()

# Automatically performs multiple search strategies,
# fetches 50+ items per strategy, deduplicates,
# ranks, and returns top 20
results = orchestrator.comprehensive_search(
    "embodied cognition",
    max_results=20,
    search_limit_per_strategy=50
)

# Only these 20 results go to Claude's context
for item in results:
    print(item.to_markdown())
```

**Benefits:**
- One function call instead of many
- Fetches 150+ items (50 × 3 strategies)
- Returns only top 20 to context
- No crash risk
- Automatic deduplication

### Example 2: Large-Scale Filtering

```python
from zotero_lib import ZoteroLibrary, SearchOrchestrator

library = ZoteroLibrary()
orchestrator = SearchOrchestrator(library)

# Fetch 100 items (safe because filtering happens in code)
items = library.search_items("machine learning", limit=100)

# Filter to recent journal articles with specific tags
filtered = orchestrator.filter_by_criteria(
    items,
    item_types=["journalArticle"],
    date_range=(2020, 2025),
    required_tags=["deep-learning"],
    excluded_tags=["draft"]
)

# Return only top 15 to Claude's context
top_results = filtered[:15]
```

**Benefits:**
- Process 100 items in code
- Complex filtering without context bloat
- Return only relevant subset

### Example 3: Custom Multi-Angle Search

```python
from zotero_lib import ZoteroLibrary, SearchOrchestrator, format_results

library = ZoteroLibrary()
orchestrator = SearchOrchestrator(library)

# Custom search strategy with many angles
all_results = set()

# Semantic variations
for query in [
    "skill transfer between contexts",
    "transfer of learning",
    "generalization of skills"
]:
    results = library.semantic_search(query, limit=30)
    all_results.update(results)

# Keyword variations
for keyword in ["transfer", "generalization", "skill acquisition"]:
    results = library.search_items(keyword, limit=30)
    all_results.update(results)

# Tag-based search
tag_results = library.search_by_tag(["learning", "cognition"], limit=30)
all_results.update(tag_results)

# Rank all results and return top 25
ranked = orchestrator._rank_items(list(all_results), "skill transfer")
top_25 = ranked[:25]

# Format for Claude's context
output = format_results(top_25, include_abstracts=True)
print(output)
```

**Benefits:**
- Fetches 200+ items across 6+ searches
- Deduplicates automatically (set)
- Ranks by relevance
- Returns only 25 most relevant
- All processing happens in code

### Example 4: Iterative Refinement

```python
from zotero_lib import SearchOrchestrator

orchestrator = SearchOrchestrator()

# First pass: broad search
initial_results = orchestrator.comprehensive_search(
    "neural networks",
    max_results=50,
    search_limit_per_strategy=100
)

# Analyze results in code to find common tags
tag_frequencies = {}
for item in initial_results:
    for tag in item.tags:
        tag_frequencies[tag] = tag_frequencies.get(tag, 0) + 1

# Get most common tags
top_tags = sorted(tag_frequencies.items(), key=lambda x: x[1], reverse=True)[:5]

# Second pass: search with refined tags
refined_results = orchestrator.filter_by_criteria(
    initial_results,
    required_tags=[tag for tag, count in top_tags]
)

# Return refined results to Claude
print(format_results(refined_results[:20]))
```

## API Reference

### `ZoteroLibrary`

Main interface to Zotero data.

#### Methods:

- **`search_items(query, qmode, item_type, limit, tag)`**
  - Basic keyword search
  - Returns `List[ZoteroItem]`
  - Can use large limits safely (filtering happens in code)

- **`semantic_search(query, limit, search_type)`**
  - Semantic/vector search
  - `search_type`: "hybrid", "vector", or "keyword"
  - Returns `List[ZoteroItem]`

- **`search_by_tag(tags, item_type, limit)`**
  - Tag-based search
  - Supports AND/OR/NOT logic
  - Returns `List[ZoteroItem]`

- **`get_tags()`**
  - Get all tags in library
  - Returns `List[str]`

- **`get_recent(limit)`**
  - Get recently added items
  - Returns `List[ZoteroItem]`

### `SearchOrchestrator`

High-level search orchestration with multi-strategy search and ranking.

#### Methods:

- **`comprehensive_search(query, max_results, use_semantic, use_keyword, use_tags, search_limit_per_strategy)`**
  - Performs multi-strategy search automatically
  - Deduplicates and ranks results
  - Returns top N most relevant items
  - **This is the main method you should use**

- **`filter_by_criteria(items, item_types, date_range, required_tags, excluded_tags)`**
  - Filter items by various criteria
  - Useful for post-search refinement

- **`_rank_items(items, query)`**
  - Rank items by relevance to query
  - Called automatically by `comprehensive_search`

### `ZoteroItem`

Simplified representation of a Zotero item.

#### Attributes:

- `key`: Item key
- `title`: Item title
- `item_type`: Type of item
- `date`: Publication date
- `authors`: Formatted author string
- `abstract`: Abstract text
- `tags`: List of tags
- `url`: URL (if available)
- `doi`: DOI (if available)
- `raw_data`: Original API response

#### Methods:

- **`to_markdown(include_abstract)`**
  - Convert to markdown format

### Helper Functions

- **`format_results(items, include_abstracts, max_abstract_length)`**
  - Format list of items as markdown
  - Truncates abstracts to avoid context bloat
  - Returns formatted string for LLM context

## Comparison: Old vs New Approach

### Old Approach (Direct MCP Calls)

```python
# Claude orchestrates manually
results1 = zotero_semantic_search("embodied cognition", limit=10)  # 10 items
results2 = zotero_semantic_search("embodiment", limit=10)          # 10 items
results3 = zotero_search_items("embodied cognition", limit=10)     # 10 items

# All 30+ items with full metadata in context
# Manual deduplication needed
# No ranking
# Risk of crashes if limit > 15
```

**Problems:**
- Limited to 10-15 items per call (crash risk)
- All results load into context
- Manual orchestration by Claude
- No automatic deduplication
- No ranking/filtering

### New Approach (Code Execution)

```python
from zotero_lib import SearchOrchestrator

orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search(
    "embodied cognition",
    max_results=20,
    search_limit_per_strategy=50
)

# Performs:
# - Semantic search: 50 items
# - Keyword search: 50 items
# - Tag search: 50 items
# - Deduplication: ~120 unique items
# - Ranking: by relevance
# - Filtering: top 20 most relevant
# Returns: Only top 20 to context
```

**Benefits:**
- Fetches 150+ items safely
- Only top 20 return to context
- Automatic deduplication
- Automatic ranking
- No crash risk
- One function call

## Integration with Claude Code

Claude Code can now write code like this:

```python
from zotero_lib import SearchOrchestrator, format_results

# User asks: "Find papers about embodied cognition"

orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search(
    "embodied cognition",
    max_results=20
)

# Format and display to user
output = format_results(results)
print(output)
```

Claude's instructions should be updated to:
1. Import `zotero_lib` for Zotero searches
2. Use `comprehensive_search()` as default
3. Use filtering functions for refinement
4. Only return formatted results to context

## Advanced Usage

### Custom Ranking Function

```python
from zotero_lib import SearchOrchestrator, ZoteroItem
from typing import List

orchestrator = SearchOrchestrator()

def custom_ranker(items: List[ZoteroItem], query: str) -> List[ZoteroItem]:
    """Custom ranking: prefer recent journal articles."""
    def score(item):
        score = 0
        if item.item_type == "journalArticle":
            score += 10
        try:
            year = int(item.date[:4])
            score += (year - 2000)  # Newer = higher score
        except:
            pass
        return score

    return sorted(items, key=score, reverse=True)

# Use custom ranker
items = orchestrator.library.search_items("cognition", limit=100)
ranked = custom_ranker(items, "cognition")
print(format_results(ranked[:20]))
```

### Saving Results for Later

```python
import json
from zotero_lib import SearchOrchestrator

orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search("memory", max_results=50)

# Save to file for later analysis
with open("search_results.json", "w") as f:
    json.dump([item.raw_data for item in results], f)

# Load later
with open("search_results.json", "r") as f:
    saved_data = json.load(f)
```

### Batch Processing

```python
from zotero_lib import SearchOrchestrator

orchestrator = SearchOrchestrator()

# Process multiple queries
queries = [
    "embodied cognition",
    "skill transfer",
    "reading comprehension",
    "memory consolidation"
]

all_results = {}
for query in queries:
    results = orchestrator.comprehensive_search(query, max_results=10)
    all_results[query] = results

# Analyze cross-query patterns
for query, items in all_results.items():
    print(f"\n{query}: {len(items)} results")
    common_tags = set()
    for item in items:
        common_tags.update(item.tags)
    print(f"Common tags: {common_tags}")
```

## Performance Considerations

### Token Usage

- **Direct MCP:** ~150,000 tokens (all tools + all results)
- **Code Execution:** ~2,000 tokens (imports + final results)
- **Savings:** ~98.7%

### Search Limits

Safe limits per strategy:
- **Direct MCP:** 10-15 (crash risk above this)
- **Code Execution:** 50-100 (safe, filtering happens in code)

### Deduplication

The `comprehensive_search()` method uses Python sets for deduplication:
- Automatic based on item key
- O(1) lookup time
- Handles overlapping search results efficiently

## Troubleshooting

### Issue: Semantic search not available

```python
# Check if semantic search is initialized
library = ZoteroLibrary()
if library.semantic_search is None:
    print("Semantic search not available")
    # Fall back to keyword search
    results = library.search_items("query", limit=50)
```

### Issue: No results returned

```python
orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search("query", max_results=20)

if not results:
    # Try broader search
    results = library.search_items("", limit=50)  # Get recent items
    # Then filter manually
```

### Issue: Results not relevant

```python
# Increase search limits to get more candidates
results = orchestrator.comprehensive_search(
    "query",
    max_results=20,
    search_limit_per_strategy=100  # Fetch more, filter more
)

# Or use custom filtering
filtered = orchestrator.filter_by_criteria(
    results,
    date_range=(2020, 2025),
    required_tags=["relevant-tag"]
)
```

## Future Enhancements

Potential improvements:

1. **Better Ranking:**
   - Use semantic similarity scoring
   - Incorporate citation counts
   - User feedback learning

2. **Caching:**
   - Cache search results
   - Invalidate on library updates
   - Faster repeated searches

3. **Parallel Processing:**
   - Execute multiple search strategies in parallel
   - Faster overall search time

4. **Export Formats:**
   - Generate BibTeX for multiple items
   - Export to CSV/JSON
   - Integration with citation managers

## License

Same as Zotero MCP (check upstream project)

## Credits

- Based on [Zotero MCP](https://github.com/your-repo/zotero-mcp)
- Inspired by [Anthropic's code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
