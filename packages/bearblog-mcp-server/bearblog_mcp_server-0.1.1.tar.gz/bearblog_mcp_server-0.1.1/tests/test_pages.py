#!/usr/bin/env python3
"""Test page management functionality."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bearblog_mcp.client import BearBlogClient


def main():
    print("=" * 60)
    print("Bear Blog MCP Server - Page Management Tests")
    print("=" * 60)

    client = BearBlogClient()
    client.authenticate()

    # Test 1: List existing pages
    print("\n1. Testing list_pages...")
    try:
        pages = client.list_pages()
        print(f"✓ Found {len(pages)} pages")
        for page in pages:
            status = "✓" if page['published'] else "○"
            print(f"  {status} {page['title']} ({page['id']})")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return

    # Test 2: Get existing page (if any)
    if pages:
        print(f"\n2. Testing get_page with ID: {pages[0]['id']}...")
        try:
            page = client.get_page(pages[0]['id'])
            print(f"✓ Retrieved page: {page['title']}")
            print(f"  Slug: {page['slug']}")
            print(f"  Published: {page['published']}")
            print(f"  Content preview: {page['content'][:100]}...")
        except Exception as e:
            print(f"✗ Failed: {e}")
    else:
        print("\n2. Skipping get_page test (no pages exist)")

    # Test 3: Create a test page
    print("\n3. Testing create_page (draft)...")
    try:
        page_id = client.create_page(
            title="Test Page - MCP Testing",
            content="# Test Page\n\nThis is a test page created by the MCP server.\n\n**Should be deleted after testing.**",
            slug="test-page-mcp",
            publish=False
        )
        if page_id:
            print(f"✓ Created draft page with ID: {page_id}")
        else:
            print("✗ Failed to create page (no ID returned)")
            return
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 4: Update the page
    print(f"\n4. Testing update_page with ID: {page_id}...")
    try:
        success = client.update_page(
            page_id=page_id,
            content="# Test Page\n\n**UPDATED** content.\n\nThis page should be deleted after testing."
        )
        if success:
            print("✓ Successfully updated page")
        else:
            print("✗ Failed to update page")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 5: Publish and unpublish
    print(f"\n5. Testing publish/unpublish with ID: {page_id}...")
    try:
        # Publish
        success = client.update_page(page_id=page_id, publish=True)
        if success:
            print("✓ Successfully published page")
        else:
            print("✗ Failed to publish page")

        # Unpublish
        success = client.update_page(page_id=page_id, publish=False)
        if success:
            print("✓ Successfully unpublished page")
        else:
            print("✗ Failed to unpublish page")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 6: Verify page appears in list
    print(f"\n6. Verifying test page appears in list...")
    try:
        pages = client.list_pages()
        test_page = next((p for p in pages if p['id'] == page_id), None)
        if test_page:
            print(f"✓ Test page found in list: {test_page['title']}")
        else:
            print("✗ Test page not found in list")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 7: Delete the test page
    print(f"\n7. Testing delete_page with ID: {page_id}...")
    try:
        success = client.delete_page(page_id)
        if success:
            print("✓ Successfully deleted page")
        else:
            print("✗ Failed to delete page")
            print(f"⚠ Remember to manually delete test page with ID: {page_id}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        print(f"⚠ Remember to manually delete test page with ID: {page_id}")

    # Test 8: Verify deletion
    print(f"\n8. Verifying test page was deleted...")
    try:
        pages = client.list_pages()
        test_page = next((p for p in pages if p['id'] == page_id), None)
        if test_page is None:
            print("✓ Test page successfully removed from list")
        else:
            print("✗ Test page still in list")
    except Exception as e:
        print(f"✗ Failed: {e}")

    print("\n" + "=" * 60)
    print("Page management testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
