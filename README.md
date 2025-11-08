# Zotero Code Execution

> Efficient multi-strategy Zotero search using code execution pattern

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for [Zotero MCP](https://github.com/zotero/zotero-mcp) that implements [Anthropic's code execution pattern](https://www.anthropic.com/engineering/code-execution-with-mcp) to enable safe, comprehensive searches without context overflow or crashes.

## Quick Start

```python
import sys
sys.path.append('/path/to/zotero-code-execution')
import setup_paths
from zotero_lib import SearchOrchestrator, format_results

# Single comprehensive search - fetches 100+ items, returns top 20
orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search("embodied cognition", max_results=20)
print(format_results(results))
```

**That's it!** This automatically:
- ✅ Performs semantic + keyword + tag searches
- ✅ Deduplicates results
- ✅ Ranks by relevance
- ✅ Keeps large datasets in code (no crashes)

## Why This Exists

### The Problem

Direct MCP tool calls have limitations:
- 🚫 **Crash risk** with large result sets (>15-20 items)
- 🚫 **Token bloat** - all results load into LLM context
- 🚫 **Manual orchestration** - multiple searches, manual deduplication
- 🚫 **No ranking** - results not sorted by relevance

### The Solution

Code execution keeps large datasets in the execution environment:
- ✅ **No crashes** - only filtered results return to context
- ✅ **Token efficient** - process 100+ items, return top 20
- ✅ **Auto-orchestration** - multi-strategy search in one call
- ✅ **Auto-ranking** - results sorted by relevance

## Features

### Multi-Strategy Search

One function call performs:
- Semantic search (multiple variations)
- Keyword search (multiple modes)
- Tag-based search
- Automatic deduplication
- Relevance ranking

### Safe Large Searches

```python
# ❌ Old way: Crash risk
results1 = zotero_semantic_search("query", limit=10)  # Limited to 10
results2 = zotero_search_items("query", limit=10)     # Another 10
# Manual deduplication, manual ranking...

# ✅ New way: Safe and comprehensive
orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search("query", max_results=20)
# Fetches 100+, processes in code, returns top 20
```

### Advanced Filtering

```python
# Fetch broadly, filter in code
library = ZoteroLibrary()
items = library.search_items("machine learning", limit=100)  # Safe!

# Filter to recent journal articles
filtered = orchestrator.filter_by_criteria(
    items,
    item_types=["journalArticle"],
    date_range=(2020, 2025)
)
```

## Installation

### Requirements

- Python 3.8+
- [Zotero MCP](https://github.com/zotero/zotero-mcp) installed via pipx
- Claude Code or similar code execution environment

### Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/zotero-code-execution.git
cd zotero-code-execution
```

2. Install dependencies (optional - usually already installed with Zotero MCP):
```bash
pip install -r requirements.txt
```

3. Use in your code:
```python
import sys
sys.path.append('/path/to/zotero-code-execution')
import setup_paths  # Adds zotero_mcp to path
from zotero_lib import SearchOrchestrator, format_results
```

## Usage Examples

### Basic Search

```python
orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search("neural networks", max_results=20)
print(format_results(results))
```

### Filter by Author

```python
library = ZoteroLibrary()
results = library.search_items("Kahneman", qmode="titleCreatorYear", limit=50)
sorted_results = sorted(results, key=lambda x: x.date, reverse=True)
print(format_results(sorted_results))
```

### Tag-Based Search

```python
library = ZoteroLibrary()
results = library.search_by_tag(["learning", "cognition"], limit=50)
print(format_results(results[:20]))
```

### Recent Papers

```python
library = ZoteroLibrary()
results = library.get_recent(limit=20)
print(format_results(results))
```

### Custom Filtering

```python
library = ZoteroLibrary()
orchestrator = SearchOrchestrator(library)

items = library.search_items("AI", limit=100)

# Only recent papers with DOI
recent_with_doi = [
    item for item in items
    if item.doi and item.date and int(item.date[:4]) >= 2020
]
print(format_results(recent_with_doi))
```

See [examples.py](examples.py) for 8 complete working examples.

## Claude Code Skill

This repository includes a Claude Code skill for easy integration.

### Installation

Copy the skill to your Claude skills directory:

```bash
cp -r claude-skill ~/.claude/skills/zotero-mcp-code
```

### Usage

In Claude Code, searches will automatically use the code execution pattern:

> "Find papers about embodied cognition"

Claude will write code using this library instead of direct MCP calls.

See [claude-skill/SKILL.md](claude-skill/SKILL.md) for complete skill documentation.

## API Reference

### `SearchOrchestrator`

Main class for automated multi-strategy searching.

#### `comprehensive_search(query, max_results=20, use_semantic=True, use_keyword=True, use_tags=True, search_limit_per_strategy=50)`

Performs comprehensive search with automatic deduplication and ranking.

**Returns:** List of `ZoteroItem` objects

#### `filter_by_criteria(items, item_types=None, date_range=None, required_tags=None, excluded_tags=None)`

Filter items by various criteria.

**Returns:** Filtered list of `ZoteroItem` objects

### `ZoteroLibrary`

Low-level interface to Zotero.

- `search_items(query, ...)` - Keyword search
- `semantic_search(query, ...)` - Semantic/vector search
- `search_by_tag(tags, ...)` - Tag-based search
- `get_recent(limit)` - Recently added items
- `get_tags()` - All library tags

### Helper Functions

- `format_results(items, include_abstracts=True, max_abstract_length=300)` - Format as markdown

See [README_LIBRARY.md](README_LIBRARY.md) for complete API documentation.

## Architecture

Based on [Anthropic's code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp):

1. **Claude writes Python code** (not direct MCP calls)
2. **Code fetches large datasets** (100+ items) from Zotero
3. **Code processes in execution environment** (dedup, rank, filter)
4. **Only filtered results** return to LLM context (20 items)

**Result:** Large datasets stay out of context, preventing crashes and saving tokens.

## Performance

### Expected Benefits

Based on Anthropic's pattern and implementation design:

- **Token reduction:** 50-90% (exact amount depends on search size)
- **Function calls:** 5-10x → 1x (confirmed by design)
- **Search limits:** 10-15 → 100+ items (safe in code)
- **Crash prevention:** Likely effective (untested)

### Status

⚠️ **Proof of concept** - Performance claims are theoretical projections, not measured results.

See [HONEST_STATUS.md](HONEST_STATUS.md) for detailed status and validation needs.

## Documentation

- **[README_LIBRARY.md](README_LIBRARY.md)** - Complete library documentation
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide
- **[CLAUDE_INSTRUCTIONS.md](CLAUDE_INSTRUCTIONS.md)** - Instructions for Claude Code
- **[examples.py](examples.py)** - 8 working examples
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[HONEST_STATUS.md](HONEST_STATUS.md)** - Implementation status
- **[claude-skill/SKILL.md](claude-skill/SKILL.md)** - Claude Code skill docs

## Contributing

Contributions welcome! Areas for improvement:

1. **Performance validation** - Measure actual token savings
2. **Better ranking** - Incorporate semantic similarity scores
3. **Caching** - Cache search results with invalidation
4. **Parallel processing** - Execute search strategies concurrently
5. **Export functions** - Batch BibTeX generation, CSV export

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

- Based on [Zotero MCP](https://github.com/zotero/zotero-mcp)
- Inspired by [Anthropic's code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)

## Related Projects

- [Zotero MCP](https://github.com/zotero/zotero-mcp) - The underlying MCP server
- [Claude Code](https://claude.com/claude-code) - Code execution environment
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework

## Citation

If you use this in research, please cite:

```bibtex
@software{zotero_code_execution,
  title = {Zotero Code Execution: Efficient Multi-Strategy Search},
  year = {2025},
  url = {https://github.com/kerim/zotero-code-execution}
}
```
