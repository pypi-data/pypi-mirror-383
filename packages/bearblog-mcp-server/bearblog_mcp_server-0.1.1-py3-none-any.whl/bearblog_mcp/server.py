"""Bear Blog MCP Server - FastMCP implementation."""

from typing import Optional

from fastmcp import FastMCP

from .client import BearBlogClient

# Initialize MCP server
mcp = FastMCP("Bear Blog")

# Initialize client (will be created on first use)
_client: Optional[BearBlogClient] = None


def get_client() -> BearBlogClient:
    """Get or create the Bear Blog client instance."""
    global _client
    if _client is None:
        _client = BearBlogClient()
        _client.authenticate()
    return _client


@mcp.tool()
def bear_list_posts() -> list[dict]:
    """List all blog posts with metadata.

    Returns a list of posts with their ID, title, publication date, and published status.
    This is useful for getting an overview of all posts or finding a specific post ID.

    Returns:
        List of dictionaries containing:
        - id: Unique post identifier
        - title: Post title
        - date: Publication date (ISO format)
        - published: Whether the post is published
    """
    client = get_client()
    return client.list_posts()


@mcp.tool()
def bear_get_post(post_id: str) -> dict:
    """Get full content of a specific blog post.

    Retrieves all details of a post including title, slug, content, and metadata.
    Use this to read a post's full content for editing or reference.

    Args:
        post_id: The unique identifier for the post (get from bear_list_posts)

    Returns:
        Dictionary containing:
        - id: Post identifier
        - title: Post title
        - slug: URL slug
        - published_date: When the post was/will be published
        - content: Full post content in markdown
        - published: Whether the post is currently published
    """
    client = get_client()
    return client.get_post(post_id)


@mcp.tool()
def bear_update_post(
    post_id: str,
    title: Optional[str] = None,
    slug: Optional[str] = None,
    content: Optional[str] = None,
    published_date: Optional[str] = None,
    publish: Optional[bool] = None,
) -> dict:
    """Update an existing blog post.

    Modify any aspect of a post. Only provide the fields you want to change;
    other fields will remain unchanged.

    Args:
        post_id: The unique identifier for the post
        title: New title for the post (optional)
        slug: New URL slug (optional)
        content: New markdown content (optional)
        published_date: New publication date in format 'YYYY-MM-DD HH:MM' (optional)
        publish: Set to true to publish, false to unpublish (optional)

    Returns:
        Dictionary with:
        - success: Whether the update succeeded
        - message: Status message
    """
    client = get_client()
    success = client.update_post(
        post_id=post_id,
        title=title,
        slug=slug,
        content=content,
        published_date=published_date,
        publish=publish,
    )

    return {
        "success": success,
        "message": "Post updated successfully" if success else "Failed to update post",
    }


@mcp.tool()
def bear_create_post(
    title: str, content: str, slug: Optional[str] = None, publish: bool = False
) -> dict:
    """Create a new blog post.

    Creates a new post with the provided content. By default, posts are created
    as drafts (unpublished). Set publish=true to publish immediately.

    Args:
        title: Title of the new post
        content: Post content in markdown format
        slug: URL slug (optional, auto-generated from title if not provided)
        publish: Whether to publish immediately (default: false, creates draft)

    Returns:
        Dictionary with:
        - success: Whether creation succeeded
        - post_id: ID of the newly created post (if successful)
        - message: Status message
    """
    client = get_client()
    post_id = client.create_post(title=title, content=content, slug=slug, publish=publish)

    if post_id:
        return {
            "success": True,
            "post_id": post_id,
            "message": f"Post created successfully with ID: {post_id}",
        }
    else:
        return {"success": False, "message": "Failed to create post"}


@mcp.tool()
def bear_delete_post(post_id: str) -> dict:
    """Delete a blog post permanently.

    **WARNING**: This action cannot be undone! The post will be permanently deleted.

    Args:
        post_id: The unique identifier for the post to delete

    Returns:
        Dictionary with:
        - success: Whether the deletion succeeded
        - message: Status message
    """
    client = get_client()
    success = client.delete_post(post_id)

    return {
        "success": success,
        "message": "Post deleted successfully" if success else "Failed to delete post",
    }


@mcp.tool()
def bear_publish_post(post_id: str, publish: bool = True) -> dict:
    """Publish or unpublish a blog post.

    Toggle the publication status of a post without changing its content.

    Args:
        post_id: The unique identifier for the post
        publish: True to publish, False to unpublish (default: True)

    Returns:
        Dictionary with:
        - success: Whether the operation succeeded
        - message: Status message
    """
    client = get_client()
    success = client.update_post(post_id=post_id, publish=publish)

    action = "published" if publish else "unpublished"
    return {
        "success": success,
        "message": f"Post {action} successfully" if success else f"Failed to {action[:-2]} post",
    }


# Resources for listing posts
@mcp.resource("bear://posts")
def list_posts_resource() -> str:
    """Get a formatted list of all blog posts."""
    client = get_client()
    posts = client.list_posts()

    lines = ["# Bear Blog Posts\n"]
    for post in posts:
        status = "✓" if post["published"] else "○"
        lines.append(f"{status} [{post['title']}](bear://post/{post['id']}) - {post['date']}")

    return "\n".join(lines)


@mcp.resource("bear://post/{post_id}")
def get_post_resource(post_id: str) -> str:
    """Get full content of a specific post."""
    client = get_client()
    post = client.get_post(post_id)

    lines = [
        f"# {post['title']}\n",
        f"**Slug:** {post['slug']}",
        f"**Published:** {post['published']}",
        f"**Date:** {post['published_date']}\n",
        "---\n",
        post["content"],
    ]

    return "\n".join(lines)


# Page management tools
@mcp.tool()
def bear_list_pages() -> list[dict]:
    """List all pages with metadata.

    Pages are static content like About, Contact, etc. (as opposed to blog posts).

    Returns:
        List of dictionaries containing:
        - id: Unique page identifier
        - title: Page title
        - date: Last modified date (ISO format)
        - published: Whether the page is published
    """
    client = get_client()
    return client.list_pages()


@mcp.tool()
def bear_get_page(page_id: str) -> dict:
    """Get full content of a specific page.

    Args:
        page_id: The unique identifier for the page (get from bear_list_pages)

    Returns:
        Dictionary containing:
        - id: Page identifier
        - title: Page title
        - slug: URL slug
        - published_date: When the page was/will be published
        - content: Full page content in markdown
        - published: Whether the page is currently published
    """
    client = get_client()
    return client.get_page(page_id)


@mcp.tool()
def bear_create_page(
    title: str, content: str, slug: Optional[str] = None, publish: bool = False
) -> dict:
    """Create a new page.

    Pages are for static content like About, Contact, etc. By default created as drafts.

    Args:
        title: Title of the new page
        content: Page content in markdown format
        slug: URL slug (optional, auto-generated from title if not provided)
        publish: Whether to publish immediately (default: false, creates draft)

    Returns:
        Dictionary with:
        - success: Whether creation succeeded
        - page_id: ID of the newly created page (if successful)
        - message: Status message
    """
    client = get_client()
    page_id = client.create_page(title=title, content=content, slug=slug, publish=publish)

    if page_id:
        return {
            "success": True,
            "page_id": page_id,
            "message": f"Page created successfully with ID: {page_id}",
        }
    else:
        return {"success": False, "message": "Failed to create page"}


@mcp.tool()
def bear_update_page(
    page_id: str,
    title: Optional[str] = None,
    slug: Optional[str] = None,
    content: Optional[str] = None,
    published_date: Optional[str] = None,
    publish: Optional[bool] = None,
) -> dict:
    """Update an existing page.

    Modify any aspect of a page. Only provide the fields you want to change.

    Args:
        page_id: The unique identifier for the page
        title: New title for the page (optional)
        slug: New URL slug (optional)
        content: New markdown content (optional)
        published_date: New publication date in format 'YYYY-MM-DD HH:MM' (optional)
        publish: Set to true to publish, false to unpublish (optional)

    Returns:
        Dictionary with:
        - success: Whether the update succeeded
        - message: Status message
    """
    client = get_client()
    success = client.update_page(
        page_id=page_id,
        title=title,
        slug=slug,
        content=content,
        published_date=published_date,
        publish=publish,
    )

    return {
        "success": success,
        "message": "Page updated successfully" if success else "Failed to update page",
    }


@mcp.tool()
def bear_delete_page(page_id: str) -> dict:
    """Delete a page permanently.

    **WARNING**: This action cannot be undone! The page will be permanently deleted.

    Args:
        page_id: The unique identifier for the page to delete

    Returns:
        Dictionary with:
        - success: Whether the deletion succeeded
        - message: Status message
    """
    client = get_client()
    success = client.delete_page(page_id)

    return {
        "success": success,
        "message": "Page deleted successfully" if success else "Failed to delete page",
    }


@mcp.tool()
def bear_publish_page(page_id: str, publish: bool = True) -> dict:
    """Publish or unpublish a page.

    Toggle the publication status of a page without changing its content.

    Args:
        page_id: The unique identifier for the page
        publish: True to publish, False to unpublish (default: True)

    Returns:
        Dictionary with:
        - success: Whether the operation succeeded
        - message: Status message
    """
    client = get_client()
    success = client.update_page(page_id=page_id, publish=publish)

    action = "published" if publish else "unpublished"
    return {
        "success": success,
        "message": f"Page {action} successfully" if success else f"Failed to {action[:-2]} page",
    }


# Resources for pages
@mcp.resource("bear://pages")
def list_pages_resource() -> str:
    """Get a formatted list of all pages."""
    client = get_client()
    pages = client.list_pages()

    lines = ["# Bear Blog Pages\n"]
    for page in pages:
        status = "✓" if page["published"] else "○"
        lines.append(f"{status} [{page['title']}](bear://page/{page['id']}) - {page['date']}")

    return "\n".join(lines)


@mcp.resource("bear://page/{page_id}")
def get_page_resource(page_id: str) -> str:
    """Get full content of a specific page."""
    client = get_client()
    page = client.get_page(page_id)

    lines = [
        f"# {page['title']}\n",
        f"**Slug:** {page['slug']}",
        f"**Published:** {page['published']}",
        f"**Date:** {page['published_date']}\n",
        "---\n",
        page["content"],
    ]

    return "\n".join(lines)


# Blog settings tools
@mcp.tool()
def bear_get_blog_settings() -> dict:
    """Get current blog settings.

    Retrieves all blog configuration including subdomain, language, analytics settings,
    and advanced options like blog path, RSS alias, and robots.txt.

    Returns:
        Dictionary containing:
        - subdomain: Blog subdomain
        - lang: Language code
        - analytics_active: Whether analytics are enabled
        - date_format: Custom date format
        - fathom_site_id: Fathom analytics site ID
        - blog_path: Path prefix for blog posts
        - rss_alias: Custom RSS feed path
        - meta_tag: Custom meta tag
        - robots_txt: robots.txt content
    """
    client = get_client()
    return client.get_blog_settings()


@mcp.tool()
def bear_update_blog_settings(
    subdomain: Optional[str] = None,
    lang: Optional[str] = None,
    analytics_active: Optional[bool] = None,
    date_format: Optional[str] = None,
    fathom_site_id: Optional[str] = None,
    blog_path: Optional[str] = None,
    rss_alias: Optional[str] = None,
    meta_tag: Optional[str] = None,
    robots_txt: Optional[str] = None,
) -> dict:
    """Update blog settings.

    Modify blog configuration. Only provide the fields you want to change.

    Args:
        subdomain: Blog subdomain (optional)
        lang: Language code, e.g. "en", "es", "fr" (optional)
        analytics_active: Enable/disable built-in analytics (optional)
        date_format: Custom date format string (optional)
        fathom_site_id: Fathom Analytics site ID for external analytics (optional)
        blog_path: Path prefix for blog posts, default "blog" (optional)
        rss_alias: Custom path for RSS feed (optional)
        meta_tag: Custom meta tag to inject in head (optional)
        robots_txt: Content for robots.txt file (optional)

    Returns:
        Dictionary with:
        - success: Whether the update succeeded
        - message: Status message
    """
    client = get_client()
    success = client.update_blog_settings(
        subdomain=subdomain,
        lang=lang,
        analytics_active=analytics_active,
        date_format=date_format,
        fathom_site_id=fathom_site_id,
        blog_path=blog_path,
        rss_alias=rss_alias,
        meta_tag=meta_tag,
        robots_txt=robots_txt,
    )

    return {
        "success": success,
        "message": "Blog settings updated successfully" if success else "Failed to update blog settings",
    }


# Home page content tools
@mcp.tool()
def bear_get_home_page() -> dict:
    """Get home page content and metadata.

    Retrieves the blog's home page configuration including title, favicon,
    meta description, meta image, and the main content displayed on the landing page.

    Returns:
        Dictionary containing:
        - title: Blog title
        - favicon: Favicon emoji or URL
        - meta_description: Meta description for SEO
        - meta_image: Meta image URL for social sharing
        - content: Home page body content (markdown)
    """
    client = get_client()
    return client.get_home_page()


@mcp.tool()
def bear_update_home_page(
    title: Optional[str] = None,
    favicon: Optional[str] = None,
    meta_description: Optional[str] = None,
    meta_image: Optional[str] = None,
    content: Optional[str] = None,
) -> dict:
    """Update home page content and metadata.

    Customize your blog's landing page. Only provide the fields you want to change.

    Args:
        title: Blog title shown in browser tab and header (optional)
        favicon: Favicon emoji (e.g., "🐻") or URL to favicon image (optional)
        meta_description: Meta description for SEO and social sharing (optional)
        meta_image: URL to image for social media previews (optional)
        content: Home page body content in markdown format (optional)

    Returns:
        Dictionary with:
        - success: Whether the update succeeded
        - message: Status message
    """
    client = get_client()
    success = client.update_home_page(
        title=title,
        favicon=favicon,
        meta_description=meta_description,
        meta_image=meta_image,
        content=content,
    )

    return {
        "success": success,
        "message": "Home page updated successfully" if success else "Failed to update home page",
    }


# Navigation management tools
@mcp.tool()
def bear_get_navigation() -> str:
    """Get navigation links.

    Retrieves the blog's navigation menu content in markdown format.
    Navigation links appear in the blog's header/menu area.

    Returns:
        Navigation content as markdown-formatted string.
        Example: "[Home](/) [Blog](/blog/) [About](/about/)"
    """
    client = get_client()
    return client.get_navigation()


@mcp.tool()
def bear_update_navigation(nav_content: str) -> dict:
    """Update navigation links.

    Customize the navigation menu that appears on your blog.
    Use markdown link syntax to define navigation items.

    Args:
        nav_content: Navigation links in markdown format.
                    Examples:
                    - "[Home](/) [Blog](/blog/)"
                    - "[Home](/) [About](/about/) [Projects](/projects/)"
                    - "[Home](/) [Twitter](https://twitter.com/username)"

    Returns:
        Dictionary with:
        - success: Whether the update succeeded
        - message: Status message
    """
    client = get_client()
    success = client.update_navigation(nav_content)

    return {
        "success": success,
        "message": "Navigation updated successfully" if success else "Failed to update navigation",
    }


# Theme and style management tools
@mcp.tool()
def bear_get_styles() -> str:
    """Get custom CSS styles.

    Retrieves the blog's custom CSS styles from the theme editor.
    This returns only the custom CSS, not pre-built theme styles.

    Returns:
        Custom CSS content as string
    """
    client = get_client()
    return client.get_styles()


@mcp.tool()
def bear_update_styles(css_content: str) -> dict:
    """Update custom CSS styles.

    Customize your blog's appearance with custom CSS.
    This updates only the custom CSS section, preserving any applied theme.

    Args:
        css_content: Custom CSS content to apply to the blog

    Returns:
        Dictionary with:
        - success: Whether the update succeeded
        - message: Status message
    """
    client = get_client()
    success = client.update_styles(css_content)

    return {
        "success": success,
        "message": "Custom styles updated successfully" if success else "Failed to update styles",
    }


@mcp.tool()
def bear_list_themes() -> list[str]:
    """List available pre-built themes.

    Returns a list of all available Bear Blog themes that can be applied.
    These are pre-designed styles created by the Bear Blog community.

    Returns:
        List of theme names (e.g., ['default', 'writer', 'sakura', 'water'])
    """
    client = get_client()
    return client.list_themes()


@mcp.tool()
def bear_apply_theme(theme_name: str) -> dict:
    """Apply a pre-built theme.

    **WARNING**: Applying a theme will OVERWRITE your current custom CSS!
    If you have custom styles you want to keep, save them first using bear_get_styles.

    Args:
        theme_name: Name of the theme to apply (use bear_list_themes to see available options)
                   Examples: 'default', 'writer', 'sakura', 'water', 'archie', 'retro'

    Returns:
        Dictionary with:
        - success: Whether the theme was applied successfully
        - message: Status message
    """
    client = get_client()
    success = client.apply_theme(theme_name)

    return {
        "success": success,
        "message": f"Theme '{theme_name}' applied successfully" if success else f"Failed to apply theme '{theme_name}'",
    }


def main():
    """Entry point for the bearblog-mcp console command."""
    mcp.run()


if __name__ == "__main__":
    main()
