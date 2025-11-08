# Claude Instructions for Using Zotero Code Execution Library

This document provides instructions for Claude Code on how to use the Zotero Code Execution library when users request Zotero searches.

## When to Use This Library

Use this library instead of direct MCP tool calls when:

1. User asks to search Zotero library
2. User wants comprehensive search results
3. User needs to find papers on a topic
4. User wants to filter/rank results

## Basic Usage Pattern

For most Zotero searches, use this simple pattern:

```python
from zotero_lib import SearchOrchestrator, format_results

# Create orchestrator
orchestrator = SearchOrchestrator()

# Perform comprehensive search
results = orchestrator.comprehensive_search(
    "user's query here",
    max_results=20,
    search_limit_per_strategy=50
)

# Format and display
output = format_results(results, include_abstracts=True, max_abstract_length=200)
print(output)
```

**This single pattern replaces all the manual multi-search strategies from the old zotero-mcp skill.**

## Why This Works Better

### Old Way (Direct MCP - DON'T DO THIS)
```python
# ❌ DON'T DO THIS ANYMORE
results1 = zotero_semantic_search("query", limit=10)  # Risk of crash
results2 = zotero_semantic_search("variation", limit=10)  # Multiple calls
results3 = zotero_search_items("query", limit=10)  # Manual orchestration
# ... manually combine and deduplicate
```

**Problems:**
- Crash risk if limit > 15
- All results load into context
- Manual orchestration required
- No automatic deduplication

### New Way (Code Execution - DO THIS)
```python
# ✅ DO THIS INSTEAD
from zotero_lib import SearchOrchestrator

orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search("query", max_results=20)
# Automatically: fetches 150+ items, deduplicates, ranks, returns top 20
```

**Benefits:**
- No crash risk (filtering in code)
- Fetches 100+ items safely
- Automatic deduplication
- Automatic ranking
- One function call

## Common Patterns

### Pattern 1: Simple Search

**User asks:** "Find papers about embodied cognition"

```python
from zotero_lib import SearchOrchestrator, format_results

orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search(
    "embodied cognition",
    max_results=20
)

print(format_results(results))
```

### Pattern 2: Search with Filtering

**User asks:** "Find recent journal articles about machine learning"

```python
from zotero_lib import ZoteroLibrary, SearchOrchestrator, format_results

library = ZoteroLibrary()
orchestrator = SearchOrchestrator(library)

# Fetch broadly (safe to use limit=100)
items = library.search_items("machine learning", limit=100)

# Filter in code
filtered = orchestrator.filter_by_criteria(
    items,
    item_types=["journalArticle"],
    date_range=(2020, 2025)
)

print(format_results(filtered[:15]))
```

### Pattern 3: Multi-Topic Search

**User asks:** "Find papers about both cognition and learning"

```python
from zotero_lib import SearchOrchestrator, format_results

orchestrator = SearchOrchestrator()

# Search for first topic
results1 = orchestrator.comprehensive_search("cognition", max_results=30)

# Search for second topic
results2 = orchestrator.comprehensive_search("learning", max_results=30)

# Find intersection
keys1 = {item.key for item in results1}
keys2 = {item.key for item in results2}
common_keys = keys1 & keys2

# Get common items
common_items = [item for item in results1 if item.key in common_keys]

if common_items:
    print("Papers about both topics:")
    print(format_results(common_items))
else:
    print("No papers found on both topics. Showing results for each:")
    print("\nCognition:")
    print(format_results(results1[:10]))
    print("\nLearning:")
    print(format_results(results2[:10]))
```

### Pattern 4: Author Search

**User asks:** "What papers do I have by Kahneman?"

```python
from zotero_lib import ZoteroLibrary, format_results

library = ZoteroLibrary()

results = library.search_items(
    "Kahneman",
    qmode="titleCreatorYear",
    limit=50
)

# Sort by date
sorted_results = sorted(results, key=lambda x: x.date, reverse=True)

print(f"Found {len(sorted_results)} papers by Kahneman:")
print(format_results(sorted_results))
```

### Pattern 5: Tag-Based Search

**User asks:** "Show me papers tagged with 'learning' and 'cognition'"

```python
from zotero_lib import ZoteroLibrary, format_results

library = ZoteroLibrary()

results = library.search_by_tag(
    ["learning", "cognition"],
    limit=50
)

print(f"Found {len(results)} papers:")
print(format_results(results[:20]))
```

### Pattern 6: Recent Papers

**User asks:** "What did I recently add to my library?"

```python
from zotero_lib import ZoteroLibrary, format_results

library = ZoteroLibrary()

results = library.get_recent(limit=20)

print("Recently added papers:")
print(format_results(results))
```

## Advanced Patterns

### Custom Filtering Logic

```python
from zotero_lib import ZoteroLibrary, SearchOrchestrator, format_results

library = ZoteroLibrary()
orchestrator = SearchOrchestrator(library)

# Fetch large dataset
items = library.search_items("neural networks", limit=100)

# Custom filtering
recent_with_doi = [
    item for item in items
    if item.doi and item.date and int(item.date[:4]) >= 2020
]

print(format_results(recent_with_doi[:15]))
```

### Multi-Angle Search

```python
from zotero_lib import ZoteroLibrary, SearchOrchestrator, format_results

library = ZoteroLibrary()
orchestrator = SearchOrchestrator(library)

all_results = set()

# Try multiple related queries
queries = [
    "skill transfer",
    "transfer of learning",
    "generalization"
]

for query in queries:
    results = library.search_items(query, limit=30)
    all_results.update(results)

# Rank combined results
ranked = orchestrator._rank_items(list(all_results), "skill transfer")

print(format_results(ranked[:20]))
```

### Iterative Refinement

```python
from zotero_lib import ZoteroLibrary, SearchOrchestrator, format_results

library = ZoteroLibrary()
orchestrator = SearchOrchestrator(library)

# Initial search
initial = library.search_items("memory", limit=50)

# Analyze tags
tag_freq = {}
for item in initial:
    for tag in item.tags:
        tag_freq[tag] = tag_freq.get(tag, 0) + 1

# Find most common tag
if tag_freq:
    most_common_tag = max(tag_freq, key=tag_freq.get)

    # Refine search
    refined = orchestrator.filter_by_criteria(
        initial,
        required_tags=[most_common_tag]
    )

    print(f"Papers with most common tag '{most_common_tag}':")
    print(format_results(refined))
```

## Important Reminders

### Always Use Code Execution

- **DO NOT** call MCP tools directly (`zotero_semantic_search`, etc.)
- **DO** use the `zotero_lib` module
- **DO** perform filtering/ranking in code
- **DO** use large limits (50-100) safely

### Safe Limits

With code execution, you can safely use:
- `limit=50` or `limit=100` for searches
- Multiple searches in parallel
- Complex filtering logic

**Why?** Because large datasets stay in code execution environment and only filtered results return to context.

### Return Formatted Results

Always return results formatted with `format_results()`:

```python
# ✅ Good
print(format_results(results, include_abstracts=True, max_abstract_length=200))

# ❌ Bad - don't return raw objects
print(results)
```

### Default Parameters

Good defaults for most searches:

```python
orchestrator.comprehensive_search(
    query,
    max_results=20,  # Good default
    search_limit_per_strategy=50  # Fetches enough for good ranking
)
```

## Error Handling

Always handle potential errors gracefully:

```python
from zotero_lib import SearchOrchestrator, format_results

orchestrator = SearchOrchestrator()

try:
    results = orchestrator.comprehensive_search("query", max_results=20)

    if results:
        print(format_results(results))
    else:
        print("No results found. Try a broader search term.")

except Exception as e:
    print(f"Search failed: {e}")
    print("Please check your Zotero MCP configuration.")
```

## Migration from Old Skill

If you see old instructions telling you to:
- Use `limit=10` on searches
- Make multiple manual MCP calls
- Ask about search strategies

**Ignore those instructions.** Instead:
1. Import `zotero_lib`
2. Use `comprehensive_search()`
3. Let the code handle everything

## Quick Reference

| Task | Code |
|------|------|
| Basic search | `orchestrator.comprehensive_search(query, max_results=20)` |
| Filter by type | `orchestrator.filter_by_criteria(items, item_types=["journalArticle"])` |
| Filter by date | `orchestrator.filter_by_criteria(items, date_range=(2020, 2025))` |
| Search by author | `library.search_items(author, qmode="titleCreatorYear", limit=50)` |
| Search by tag | `library.search_by_tag([tags], limit=50)` |
| Recent items | `library.get_recent(limit=20)` |
| Format results | `format_results(items, include_abstracts=True)` |

## Complete Example

Here's a complete example showing the full pattern:

```python
#!/usr/bin/env python3
"""
Example: Comprehensive search for papers on a topic.
This is what Claude should write when user asks to search Zotero.
"""

from zotero_lib import SearchOrchestrator, format_results

def main():
    # User query
    query = "embodied cognition"

    # Create orchestrator
    orchestrator = SearchOrchestrator()

    # Comprehensive search
    # - Performs semantic + keyword + tag searches
    # - Fetches 50+ items per strategy
    # - Deduplicates and ranks
    # - Returns top 20
    results = orchestrator.comprehensive_search(
        query,
        max_results=20,
        search_limit_per_strategy=50
    )

    # Check if we found anything
    if not results:
        print(f"No papers found for '{query}'")
        print("Try a broader search term or check your library.")
        return

    # Format and display
    print(f"Found {len(results)} most relevant papers on '{query}':\n")
    output = format_results(
        results,
        include_abstracts=True,
        max_abstract_length=200
    )
    print(output)

if __name__ == "__main__":
    main()
```

That's it! This one pattern handles 90% of Zotero search requests.
