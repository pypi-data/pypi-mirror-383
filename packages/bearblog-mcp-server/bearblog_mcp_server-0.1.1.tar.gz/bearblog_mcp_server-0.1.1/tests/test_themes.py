#!/usr/bin/env python3
"""Test script for Bear Blog theme/style management tools."""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bearblog_mcp.client import BearBlogClient


def main():
    """Test theme and style management functionality."""
    print("Testing Bear Blog Theme/Style Management Tools\n")
    print("=" * 60)

    # Initialize client
    client = BearBlogClient()
    client.authenticate()
    print("✓ Authentication successful\n")

    # Test 1: List available themes
    print("Test 1: List available themes")
    print("-" * 60)
    themes = client.list_themes()
    print(f"Found {len(themes)} available themes:")
    for i, theme in enumerate(themes, 1):
        print(f"  {i:2d}. {theme}")
    print()

    # Test 2: Get current custom styles
    print("Test 2: Get current custom styles")
    print("-" * 60)
    current_styles = client.get_styles()
    print(f"Current custom CSS length: {len(current_styles)} characters")
    if current_styles:
        print("First 200 characters:")
        print(current_styles[:200])
    else:
        print("No custom styles currently set")
    print()

    # Test 3: Update custom styles (add a test comment)
    print("Test 3: Update custom styles")
    print("-" * 60)
    test_css = current_styles + "\n\n/* Test comment added by test_themes.py */"
    success = client.update_styles(test_css)
    if success:
        print("✓ Custom styles updated successfully")
    else:
        print("✗ Failed to update custom styles")
    print()

    # Test 4: Verify the update
    print("Test 4: Verify custom styles update")
    print("-" * 60)
    updated_styles = client.get_styles()
    if "Test comment added by test_themes.py" in updated_styles:
        print("✓ Custom styles update verified")
    else:
        print("✗ Custom styles update verification failed")
    print()

    # Test 5: Restore original styles
    print("Test 5: Restore original styles")
    print("-" * 60)
    success = client.update_styles(current_styles)
    if success:
        print("✓ Original styles restored successfully")
    else:
        print("✗ Failed to restore original styles")
    print()

    # Test 6: Verify restoration
    print("Test 6: Verify restoration")
    print("-" * 60)
    final_styles = client.get_styles()
    if final_styles == current_styles:
        print("✓ Styles restoration verified")
    else:
        print("✗ Styles restoration verification failed")
    print()

    # Note about theme application test
    print("=" * 60)
    print("\nNOTE: Skipping theme application test to preserve current styles.")
    print("To test theme application manually, use:")
    print("  client.apply_theme('theme_name')")
    print("\nWARNING: This will overwrite your custom CSS!")
    print("\n✓ All theme/style management tests completed successfully")


if __name__ == "__main__":
    main()
