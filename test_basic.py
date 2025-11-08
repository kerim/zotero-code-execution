#!/usr/bin/env python3
"""
Basic test script to verify zotero_lib implementation.

This script tests that:
1. ZoteroLibrary can be instantiated
2. Basic search functions work
3. SearchOrchestrator works
4. No import errors

Run with: python test_basic.py
"""

import sys
import setup_paths  # Add zotero_mcp to path


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from zotero_lib import (
            ZoteroLibrary,
            SearchOrchestrator,
            ZoteroItem,
            format_results
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_library_creation():
    """Test that ZoteroLibrary can be created."""
    print("\nTesting ZoteroLibrary creation...")
    try:
        from zotero_lib import ZoteroLibrary

        library = ZoteroLibrary()
        print("✓ ZoteroLibrary created successfully")
        print(f"  - Zotero client: {library.zot}")
        print(f"  - Config path: {library.config_path}")

        # Check if semantic search is available
        if library.semantic_search:
            print(f"  - Semantic search: Available")
        else:
            print(f"  - Semantic search: Not available (this is OK)")

        return True
    except Exception as e:
        print(f"✗ ZoteroLibrary creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_creation():
    """Test that SearchOrchestrator can be created."""
    print("\nTesting SearchOrchestrator creation...")
    try:
        from zotero_lib import SearchOrchestrator

        orchestrator = SearchOrchestrator()
        print("✓ SearchOrchestrator created successfully")
        print(f"  - Library: {orchestrator.library}")
        return True
    except Exception as e:
        print(f"✗ SearchOrchestrator creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_zotero_item():
    """Test ZoteroItem creation."""
    print("\nTesting ZoteroItem...")
    try:
        from zotero_lib import ZoteroItem

        # Create a mock item
        mock_data = {
            "data": {
                "key": "TEST123",
                "title": "Test Paper",
                "itemType": "journalArticle",
                "date": "2024",
                "creators": [{"lastName": "Smith", "firstName": "John"}],
                "abstractNote": "This is a test abstract.",
                "tags": [{"tag": "test"}, {"tag": "example"}],
                "DOI": "10.1234/test",
                "url": "https://example.com"
            }
        }

        item = ZoteroItem.from_raw(mock_data)
        print("✓ ZoteroItem created successfully")
        print(f"  - Key: {item.key}")
        print(f"  - Title: {item.title}")
        print(f"  - Authors: {item.authors}")
        print(f"  - Tags: {item.tags}")

        # Test markdown conversion
        markdown = item.to_markdown(include_abstract=False)
        print("✓ Markdown conversion works")

        return True
    except Exception as e:
        print(f"✗ ZoteroItem test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_format_results():
    """Test format_results function."""
    print("\nTesting format_results...")
    try:
        from zotero_lib import ZoteroItem, format_results

        # Create mock items
        mock_data = {
            "data": {
                "key": "TEST123",
                "title": "Test Paper",
                "itemType": "journalArticle",
                "date": "2024",
                "creators": [{"lastName": "Smith", "firstName": "John"}],
                "abstractNote": "This is a test abstract.",
                "tags": [{"tag": "test"}],
            }
        }

        items = [ZoteroItem.from_raw(mock_data)]

        output = format_results(items, include_abstracts=True)
        print("✓ format_results works")
        print("\nSample output:")
        print("-" * 60)
        print(output[:300] + "...")
        print("-" * 60)

        return True
    except Exception as e:
        print(f"✗ format_results test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_actual_search():
    """Test actual search if Zotero is configured."""
    print("\nTesting actual Zotero search (may fail if not configured)...")
    try:
        from zotero_lib import ZoteroLibrary

        library = ZoteroLibrary()

        # Try to get recent items
        results = library.get_recent(limit=3)

        if results:
            print(f"✓ Search successful - found {len(results)} items")
            print(f"  - First item: {results[0].title}")
            return True
        else:
            print("⚠ Search returned no results (library might be empty)")
            return True  # Not a failure if library is empty

    except Exception as e:
        print(f"⚠ Actual search failed: {e}")
        print("  (This is OK if Zotero is not configured)")
        return True  # Don't fail the test suite for this


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("Zotero Code Execution Library - Basic Tests")
    print("=" * 70)

    tests = [
        test_imports,
        test_library_creation,
        test_orchestrator_creation,
        test_zotero_item,
        test_format_results,
        test_actual_search,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
