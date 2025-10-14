#!/usr/bin/env python3
"""Test script to verify Bear Blog MCP tools."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bearblog_mcp.client import BearBlogClient


def test_authentication():
    """Test that we can authenticate with Bear Blog."""
    print("Testing authentication...")
    client = BearBlogClient()
    try:
        client.authenticate()
        print("✓ Authentication successful")
        return True
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return False


def test_list_posts(client):
    """Test listing all posts."""
    print("\nTesting list_posts...")
    try:
        posts = client.list_posts()
        print(f"✓ Found {len(posts)} posts")
        if posts:
            print(f"  Sample post: {posts[0]['title']} (ID: {posts[0]['id']})")
        return posts
    except Exception as e:
        print(f"✗ Failed to list posts: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_get_post(client, post_id):
    """Test getting a specific post."""
    print(f"\nTesting get_post with ID: {post_id}...")
    try:
        post = client.get_post(post_id)
        print(f"✓ Retrieved post: {post['title']}")
        print(f"  Slug: {post['slug']}")
        print(f"  Published: {post['published']}")
        print(f"  Content length: {len(post['content'])} chars")
        return post
    except Exception as e:
        print(f"✗ Failed to get post: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_create_draft_post(client):
    """Test creating a draft post."""
    print("\nTesting create_post (draft)...")
    try:
        post_id = client.create_post(
            title="Test Draft Post - MCP Testing",
            content="This is a test draft post created by the MCP server testing suite.\n\n**Should be deleted after testing.**",
            slug="test-draft-mcp",
            publish=False
        )
        if post_id:
            print(f"✓ Created draft post with ID: {post_id}")
            return post_id
        else:
            print("✗ Failed to create post (no ID returned)")
            return None
    except Exception as e:
        print(f"✗ Failed to create post: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_update_post(client, post_id):
    """Test updating a post."""
    print(f"\nTesting update_post with ID: {post_id}...")
    try:
        success = client.update_post(
            post_id=post_id,
            content="This is UPDATED test content.\n\n**Still should be deleted after testing.**"
        )
        if success:
            print("✓ Successfully updated post")
            return True
        else:
            print("✗ Failed to update post")
            return False
    except Exception as e:
        print(f"✗ Failed to update post: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_publish_toggle(client, post_id):
    """Test publishing and unpublishing a post."""
    print(f"\nTesting publish toggle with ID: {post_id}...")
    try:
        # Publish
        success = client.update_post(post_id=post_id, publish=True)
        if success:
            print("✓ Successfully published post")
        else:
            print("✗ Failed to publish post")
            return False

        # Unpublish
        success = client.update_post(post_id=post_id, publish=False)
        if success:
            print("✓ Successfully unpublished post")
            return True
        else:
            print("✗ Failed to unpublish post")
            return False
    except Exception as e:
        print(f"✗ Failed to toggle publish: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Bear Blog MCP Server - Tool Testing")
    print("=" * 60)

    # Create client instance
    client = BearBlogClient()

    # Test authentication
    print("Testing authentication...")
    try:
        client.authenticate()
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print("\n⚠ Authentication failed, cannot continue with tests")
        return

    # Test list posts
    posts = test_list_posts(client)

    # Test get post (if we have any posts)
    if posts:
        test_get_post(client, posts[0]['id'])

    # Test create draft
    draft_id = test_create_draft_post(client)

    # Test update and publish if we created a draft
    if draft_id:
        test_update_post(client, draft_id)
        test_publish_toggle(client, draft_id)

        print(f"\n⚠ Remember to delete test post with ID: {draft_id}")

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
