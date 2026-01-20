# Zotero MCP Code Execution - Claude Code Skill

Claude Code skill for efficient Zotero searches using code execution.

## Installation

Copy this skill to your Claude skills directory:

```bash
cp -r claude-skill ~/.claude/skills/zotero-mcp-code
```

Or create a symlink:

```bash
ln -s /path/to/zotero-code-execution/claude-skill ~/.claude/skills/zotero-mcp-code
```

## Verification

Check that the skill is installed:

```bash
ls ~/.claude/skills/
```

You should see `zotero-mcp-code` in the list.

## Usage

Once installed, Claude Code will automatically use this skill for Zotero searches.

### Example Queries

Simply ask Claude:

- "Find papers about embodied cognition"
- "Show me recent journal articles about machine learning"
- "What papers do I have by Kahneman?"
- "Search for papers tagged with learning"
- "What did I recently add to my library?"

Claude will automatically write code using the efficient code execution pattern instead of direct MCP calls.

## What This Skill Does

### Automatic Code Execution

Instead of calling MCP tools directly (which can crash with large results), Claude writes Python code that:

1. Fetches large datasets (100+ items)
2. Filters and ranks in code
3. Returns only top results to context

### Example

**User asks:** "Find papers about neural networks"

**Claude writes:**
```python
import sys
sys.path.append('/Users/niyaro/Documents/Code/zotero-code-execution')
import setup_paths
from zotero_lib import SearchOrchestrator, format_results

orchestrator = SearchOrchestrator()
results = orchestrator.comprehensive_search("neural networks", max_results=20)
print(format_results(results))
```

**Result:** Top 20 most relevant papers, automatically deduplicated and ranked.

## Features

- ✅ **No crashes** - Large data stays in code execution environment
- ✅ **Multi-strategy search** - Semantic + keyword + tags automatically
- ✅ **Auto-deduplication** - Removes duplicate results
- ✅ **Auto-ranking** - Sorts by relevance
- ✅ **One function call** - Replaces 5-10 manual MCP calls

## Configuration

The skill expects the zotero-code-execution library at:

```
/Users/niyaro/Documents/Code/zotero-code-execution
```

If you install it elsewhere, update the path in SKILL.md:

```python
sys.path.append('/your/custom/path/zotero-code-execution')
```

## Comparison with zotero-mcp Skill

| Feature | zotero-mcp | zotero-mcp-code |
|---------|-----------|-----------------|
| Approach | Direct MCP calls | Code execution |
| Function calls | 5-10 | 1 |
| Search limit | 10-15 (crash risk) | 100+ (safe) |
| Deduplication | Manual | Automatic |
| Ranking | None | Automatic |
| Context size | Large | Small |

## Advanced Usage

See [SKILL.md](SKILL.md) for complete documentation including:

- Common search patterns
- Advanced filtering
- Custom search logic
- API reference
- Error handling

## Troubleshooting

### Skill Not Loading

1. Check installation:
   ```bash
   ls ~/.claude/skills/zotero-mcp-code/
   ```

2. Verify SKILL.md exists:
   ```bash
   cat ~/.claude/skills/zotero-mcp-code/SKILL.md | head -5
   ```

3. Check frontmatter:
   ```yaml
   ---
   name: zotero-mcp-code
   description: ...
   ---
   ```

### Import Errors

If you see `ModuleNotFoundError: No module named 'zotero_mcp'`:

1. Verify Zotero MCP is installed:
   ```bash
   pipx list | grep zotero
   ```

2. Check the path in the code:
   ```python
   sys.path.append('/Users/niyaro/Documents/Code/zotero-code-execution')
   import setup_paths  # This should add zotero_mcp to path
   ```

### Search Errors

If searches fail:

1. Check Zotero MCP configuration:
   ```bash
   cat ~/.config/zotero-mcp/config.json
   ```

2. Verify Zotero is running (if using local mode)

3. Check environment variables (if using remote mode):
   ```bash
   echo $ZOTERO_API_KEY
   echo $ZOTERO_LIBRARY_ID
   ```

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation
- **[../README.md](../README.md)** - Library documentation
- **[../examples.py](../examples.py)** - Usage examples
- **[../QUICK_START.md](../QUICK_START.md)** - Quick reference

## License

MIT License - see [../LICENSE](../LICENSE) for details.
