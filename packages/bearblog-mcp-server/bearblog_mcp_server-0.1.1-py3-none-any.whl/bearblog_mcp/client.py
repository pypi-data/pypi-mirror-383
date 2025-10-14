"""Bear Blog API client for session-based authentication and requests."""

import html
import os
import re
from typing import Optional
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

load_dotenv(override=True)


class BearBlogClient:
    """Client for interacting with Bear Blog's web interface."""

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        subdomain: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize the Bear Blog client.

        Args:
            email: Bear Blog account email (defaults to BEAR_BLOG_EMAIL env var)
            password: Bear Blog account password (defaults to BEAR_BLOG_PASSWORD env var)
            subdomain: Blog subdomain (defaults to BEAR_BLOG_SUBDOMAIN env var)
            base_url: Base URL for Bear Blog (defaults to BEAR_BLOG_BASE_URL env var)
        """
        self.email = email or os.getenv("BEAR_BLOG_EMAIL")
        self.password = password or os.getenv("BEAR_BLOG_PASSWORD")
        self.subdomain = subdomain or os.getenv("BEAR_BLOG_SUBDOMAIN")
        self.base_url = base_url or os.getenv("BEAR_BLOG_BASE_URL", "https://bearblog.dev")

        if not all([self.email, self.password, self.subdomain]):
            raise ValueError(
                "Email, password, and subdomain must be provided or set in environment variables"
            )

        self.session = requests.Session()
        self._authenticated = False

    def _get_csrf_token(self) -> str:
        """Extract CSRF token from session cookies."""
        return self.session.cookies.get("csrftoken", "")

    def authenticate(self) -> bool:
        """Authenticate with Bear Blog and establish session.

        Returns:
            True if authentication successful, False otherwise
        """
        # Get login page to initialize CSRF token
        login_url = urljoin(self.base_url, "/accounts/login/")
        self.session.get(login_url)

        # Attempt login
        csrf_token = self._get_csrf_token()
        login_data = {
            "csrfmiddlewaretoken": csrf_token,
            "login": self.email,
            "password": self.password,
        }

        response = self.session.post(
            login_url,
            data=login_data,
            headers={"Referer": login_url},
            allow_redirects=True,
        )

        # Check if login was successful by looking for actual error messages
        # Note: "errorlist" appears in CSS, so we need to check for actual error elements
        has_error = '<ul class="errorlist">' in response.text
        self._authenticated = not has_error and response.status_code == 200
        return self._authenticated

    def _ensure_authenticated(self):
        """Ensure the client is authenticated, authenticate if not."""
        if not self._authenticated:
            if not self.authenticate():
                raise RuntimeError("Failed to authenticate with Bear Blog")

    def list_posts(self) -> list[dict]:
        """List all blog posts.

        Returns:
            List of post dictionaries with id, title, date, and published status
        """
        self._ensure_authenticated()

        posts_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/posts/")
        response = self.session.get(posts_url)
        response.raise_for_status()

        # Parse post list from HTML
        posts = []
        # Extract posts using regex that handles multiline content
        # Pattern: link tag followed by title (possibly on next line)
        post_pattern = r'<a href="/[^/]+/dashboard/posts/([^/]+)/">\s*([^<]+)</a>'
        date_pattern = r'<time datetime="([^"]+)">'
        unpublished_pattern = r'<small>\(not published\)</small>'

        # Find all matches with re.DOTALL to handle newlines
        post_matches = list(re.finditer(post_pattern, response.text, re.DOTALL))
        date_matches = list(re.finditer(date_pattern, response.text))

        # Build posts list
        for i, post_match in enumerate(post_matches):
            post_id = post_match.group(1)
            # Extract title (first line only, in case there's extra content)
            title_raw = post_match.group(2).strip()
            title = title_raw.split('\n')[0].strip()

            # Skip navigation links (like "Posts", "new")
            if not post_id or post_id in ['new', '']:
                continue

            # Find the nearest date before this post
            post_start = post_match.start()
            date = None
            for date_match in reversed(date_matches):
                if date_match.start() < post_start:
                    date = date_match.group(1)
                    break

            # Check if post is published
            # Look for "(not published)" after the post link
            next_200_chars = response.text[post_match.end():post_match.end() + 200]
            published = unpublished_pattern not in next_200_chars

            posts.append({
                "id": post_id,
                "title": title,
                "date": date or "",
                "published": published
            })

        return posts

    def get_post(self, post_id: str) -> dict:
        """Get a specific post by ID.

        Args:
            post_id: The post ID

        Returns:
            Dictionary with title, slug, published_date, content, and published status
        """
        self._ensure_authenticated()

        post_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/posts/{post_id}/")
        response = self.session.get(post_url)
        response.raise_for_status()

        response_html = response.text

        # Extract header content (title, slug, published_date)
        header_match = re.search(
            r'<div[^>]*id="header_content"[^>]*>(.*?)</div>', response_html, re.DOTALL
        )
        if not header_match:
            raise ValueError("Could not find header content in post")

        header_html = header_match.group(1)

        # Parse header fields (unescape HTML entities)
        title_match = re.search(r"<b>title:</b>\s*([^<\n]+)", header_html)
        slug_match = re.search(r"<b>link:</b>\s*([^<\n]+)", header_html)
        date_match = re.search(r'<span id="published-date">([^<]+)</span>', header_html)

        # Extract body content (unescape HTML entities)
        body_match = re.search(
            r'<textarea[^>]*name="body_content"[^>]*>(.*?)</textarea>', response_html, re.DOTALL
        )
        if not body_match:
            raise ValueError("Could not find body content in post")

        # Extract publish status
        publish_match = re.search(r'name="publish"[^>]*value="([^"]+)"', response_html)

        return {
            "id": post_id,
            "title": html.unescape(title_match.group(1).strip()) if title_match else "",
            "slug": slug_match.group(1).strip() if slug_match else "",
            "published_date": date_match.group(1).strip() if date_match else "",
            "content": html.unescape(body_match.group(1).strip()),
            "published": publish_match.group(1) == "true" if publish_match else False,
        }

    def update_post(
        self,
        post_id: str,
        title: Optional[str] = None,
        slug: Optional[str] = None,
        content: Optional[str] = None,
        published_date: Optional[str] = None,
        publish: Optional[bool] = None,
    ) -> bool:
        """Update an existing post.

        Args:
            post_id: The post ID
            title: New title (optional)
            slug: New slug (optional)
            content: New content (optional)
            published_date: New published date (optional)
            publish: Whether to publish the post (optional)

        Returns:
            True if update successful
        """
        self._ensure_authenticated()

        # Get current post data
        current = self.get_post(post_id)

        # Use provided values or fall back to current
        title = title if title is not None else current["title"]
        slug = slug if slug is not None else current["slug"]
        content = content if content is not None else current["content"]
        published_date = (
            published_date if published_date is not None else current["published_date"]
        )
        publish = publish if publish is not None else current["published"]

        # Build header content (use \r\n for proper line breaks in Bear Blog's contenteditable div)
        header_content = f"title: {title}\r\nlink: {slug}\r\npublished_date: {published_date}"

        # Submit update
        post_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/posts/{post_id}/")
        csrf_token = self._get_csrf_token()

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "header_content": header_content,
            "body_content": content,
            "publish": "true" if publish else "false",
        }

        response = self.session.post(
            post_url,
            data=data,
            headers={"Referer": post_url},
        )

        return response.status_code == 200

    def create_post(
        self, title: str, content: str, slug: Optional[str] = None, publish: bool = False
    ) -> Optional[str]:
        """Create a new post.

        Args:
            title: Post title
            content: Post content (markdown)
            slug: URL slug (optional, will be auto-generated if not provided)
            publish: Whether to publish immediately (default: False)

        Returns:
            Post ID if successful, None otherwise
        """
        self._ensure_authenticated()

        new_post_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/posts/new/")
        csrf_token = self._get_csrf_token()

        # If no slug provided, generate from title
        if not slug:
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

        # Use \r\n for proper line breaks in Bear Blog's contenteditable div
        header_content = f"title: {title}\r\nlink: {slug}"

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "header_content": header_content,
            "body_content": content,
            "publish": "true" if publish else "false",
        }

        response = self.session.post(
            new_post_url,
            data=data,
            headers={"Referer": new_post_url},
            allow_redirects=False,
        )

        # Extract post ID from redirect location
        if response.status_code in (301, 302):
            location = response.headers.get("Location", "")
            match = re.search(r"/posts/([^/]+)/", location)
            if match:
                return match.group(1)

        return None

    def delete_post(self, post_id: str) -> bool:
        """Delete a post.

        Args:
            post_id: The post ID

        Returns:
            True if deletion successful
        """
        self._ensure_authenticated()

        delete_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/posts/{post_id}/delete/")
        csrf_token = self._get_csrf_token()

        # POST to delete endpoint
        response = self.session.post(
            delete_url,
            data={"csrfmiddlewaretoken": csrf_token},
            headers={"Referer": delete_url},
            allow_redirects=False,
        )

        # Successful deletion should redirect
        return response.status_code in (301, 302, 303)

    # Page management methods
    # Pages use the same endpoints as posts but accessed via /dashboard/pages/

    def list_pages(self) -> list[dict]:
        """List all pages.

        Returns:
            List of page dictionaries with id, title, date, and published status
        """
        self._ensure_authenticated()

        pages_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/pages/")
        response = self.session.get(pages_url)
        response.raise_for_status()

        # Use same parsing logic as posts
        pages = []
        post_pattern = r'<a href="/[^/]+/dashboard/posts/([^/]+)/">\s*([^<]+)</a>'
        date_pattern = r'<time datetime="([^"]+)">'
        unpublished_pattern = r'<small>\(not published\)</small>'

        post_matches = list(re.finditer(post_pattern, response.text, re.DOTALL))
        date_matches = list(re.finditer(date_pattern, response.text))

        for i, post_match in enumerate(post_matches):
            post_id = post_match.group(1)
            title_raw = post_match.group(2).strip()
            title = title_raw.split('\n')[0].strip()

            if not post_id or post_id in ['new', '']:
                continue

            post_start = post_match.start()
            date = None
            for date_match in reversed(date_matches):
                if date_match.start() < post_start:
                    date = date_match.group(1)
                    break

            next_200_chars = response.text[post_match.end():post_match.end() + 200]
            published = unpublished_pattern not in next_200_chars

            pages.append({
                "id": post_id,
                "title": title,
                "date": date or "",
                "published": published
            })

        return pages

    def get_page(self, page_id: str) -> dict:
        """Get a specific page by ID.

        Args:
            page_id: The page ID

        Returns:
            Dictionary with title, slug, published_date, content, and published status
        """
        # Pages use the same endpoint structure as posts
        return self.get_post(page_id)

    def create_page(
        self, title: str, content: str, slug: Optional[str] = None, publish: bool = False
    ) -> Optional[str]:
        """Create a new page.

        Args:
            title: Page title
            content: Page content (markdown)
            slug: URL slug (optional, will be auto-generated if not provided)
            publish: Whether to publish immediately (default: False)

        Returns:
            Page ID if successful, None otherwise
        """
        self._ensure_authenticated()

        # Pages are created via the posts endpoint with is_page=True
        new_page_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/posts/new/?is_page=True")
        csrf_token = self._get_csrf_token()

        if not slug:
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

        # Use \r\n for proper line breaks in Bear Blog's contenteditable div
        header_content = f"title: {title}\r\nlink: {slug}"

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "header_content": header_content,
            "body_content": content,
            "publish": "true" if publish else "false",
        }

        response = self.session.post(
            new_page_url,
            data=data,
            headers={"Referer": new_page_url},
            allow_redirects=False,
        )

        if response.status_code in (301, 302):
            location = response.headers.get("Location", "")
            match = re.search(r"/posts/([^/]+)/", location)
            if match:
                return match.group(1)

        return None

    def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        slug: Optional[str] = None,
        content: Optional[str] = None,
        published_date: Optional[str] = None,
        publish: Optional[bool] = None,
    ) -> bool:
        """Update an existing page.

        Args:
            page_id: The page ID
            title: New title (optional)
            slug: New slug (optional)
            content: New content (optional)
            published_date: New published date (optional)
            publish: Whether to publish the page (optional)

        Returns:
            True if update successful
        """
        # Pages use the same update endpoint as posts
        return self.update_post(
            post_id=page_id,
            title=title,
            slug=slug,
            content=content,
            published_date=published_date,
            publish=publish,
        )

    def delete_page(self, page_id: str) -> bool:
        """Delete a page.

        Args:
            page_id: The page ID

        Returns:
            True if deletion successful
        """
        # Pages use the same delete endpoint as posts
        return self.delete_post(page_id)

    # Blog settings management

    def get_blog_settings(self) -> dict:
        """Get blog settings.

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
        self._ensure_authenticated()

        # Get basic settings
        settings_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/settings/")
        response = self.session.get(settings_url)
        response.raise_for_status()

        settings = {}

        # Extract subdomain
        subdomain_match = re.search(r'name="subdomain"\s+value="([^"]+)"', response.text)
        if subdomain_match:
            settings['subdomain'] = subdomain_match.group(1)

        # Extract language
        lang_match = re.search(r'name="lang"[^>]+value="([^"]+)"', response.text)
        if lang_match:
            settings['lang'] = lang_match.group(1)

        # Get advanced settings
        advanced_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/settings/advanced/")
        response = self.session.get(advanced_url)
        response.raise_for_status()

        # Extract analytics checkbox
        analytics_match = re.search(r'name="analytics_active"[^>]+(checked)', response.text)
        settings['analytics_active'] = bool(analytics_match)

        # Extract date format
        date_format_match = re.search(r'name="date_format"[^>]+value="([^"]*)"', response.text)
        settings['date_format'] = date_format_match.group(1) if date_format_match else ""

        # Extract fathom site ID
        fathom_match = re.search(r'name="fathom_site_id"[^>]+value="([^"]*)"', response.text)
        settings['fathom_site_id'] = fathom_match.group(1) if fathom_match else ""

        # Extract blog path
        blog_path_match = re.search(r'name="blog_path"\s+value="([^"]+)"', response.text)
        settings['blog_path'] = blog_path_match.group(1) if blog_path_match else ""

        # Extract RSS alias
        rss_alias_match = re.search(r'name="rss_alias"[^>]+value="([^"]*)"', response.text)
        settings['rss_alias'] = rss_alias_match.group(1) if rss_alias_match else ""

        # Extract meta tag
        meta_tag_match = re.search(r'name="meta_tag"[^>]+value="([^"]*)"', response.text)
        settings['meta_tag'] = meta_tag_match.group(1) if meta_tag_match else ""

        # Extract robots.txt
        robots_match = re.search(r'<textarea name="robots_txt"[^>]*>(.*?)</textarea>', response.text, re.DOTALL)
        settings['robots_txt'] = robots_match.group(1).strip() if robots_match else ""

        return settings

    def update_blog_settings(
        self,
        subdomain: Optional[str] = None,
        lang: Optional[str] = None,
        analytics_active: Optional[bool] = None,
        date_format: Optional[str] = None,
        fathom_site_id: Optional[str] = None,
        blog_path: Optional[str] = None,
        rss_alias: Optional[str] = None,
        meta_tag: Optional[str] = None,
        robots_txt: Optional[str] = None,
    ) -> bool:
        """Update blog settings.

        Args:
            subdomain: Blog subdomain (optional)
            lang: Language code (optional)
            analytics_active: Enable/disable analytics (optional)
            date_format: Custom date format (optional)
            fathom_site_id: Fathom analytics site ID (optional)
            blog_path: Path prefix for blog posts (optional)
            rss_alias: Custom RSS feed path (optional)
            meta_tag: Custom meta tag (optional)
            robots_txt: robots.txt content (optional)

        Returns:
            True if update successful
        """
        self._ensure_authenticated()

        # Get current settings
        current = self.get_blog_settings()

        # Update basic settings (subdomain, lang) if provided
        if subdomain is not None or lang is not None:
            settings_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/settings/")
            csrf_token = self._get_csrf_token()

            data = {
                "csrfmiddlewaretoken": csrf_token,
                "subdomain": subdomain if subdomain is not None else current['subdomain'],
                "lang": lang if lang is not None else current['lang'],
            }

            response = self.session.post(
                settings_url,
                data=data,
                headers={"Referer": settings_url},
            )

            if response.status_code != 200:
                return False

        # Update advanced settings if any advanced options provided
        advanced_fields = {
            'analytics_active': analytics_active,
            'date_format': date_format,
            'fathom_site_id': fathom_site_id,
            'blog_path': blog_path,
            'rss_alias': rss_alias,
            'meta_tag': meta_tag,
            'robots_txt': robots_txt,
        }

        if any(v is not None for v in advanced_fields.values()):
            advanced_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/settings/advanced/")
            csrf_token = self._get_csrf_token()

            data = {
                "csrfmiddlewaretoken": csrf_token,
                "blog_path": blog_path if blog_path is not None else current['blog_path'],
                "rss_alias": rss_alias if rss_alias is not None else current['rss_alias'],
                "date_format": date_format if date_format is not None else current['date_format'],
                "fathom_site_id": fathom_site_id if fathom_site_id is not None else current['fathom_site_id'],
                "meta_tag": meta_tag if meta_tag is not None else current['meta_tag'],
                "robots_txt": robots_txt if robots_txt is not None else current['robots_txt'],
            }

            # Handle checkbox: only include if True
            if analytics_active is not None:
                if analytics_active:
                    data["analytics_active"] = "on"
            elif current['analytics_active']:
                data["analytics_active"] = "on"

            response = self.session.post(
                advanced_url,
                data=data,
                headers={"Referer": advanced_url},
            )

            if response.status_code != 200:
                return False

        return True

    # Home page content management

    def get_home_page(self) -> dict:
        """Get home page content.

        Returns:
            Dictionary containing:
            - title: Blog title
            - favicon: Favicon emoji or URL
            - meta_image: Meta image URL for social sharing
            - content: Home page body content (markdown)
        """
        self._ensure_authenticated()

        home_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/")
        response = self.session.get(home_url)
        response.raise_for_status()

        # Extract header content
        header_match = re.search(
            r'<div[^>]*id="header_content"[^>]*>(.*?)</div>', response.text, re.DOTALL
        )

        home_page = {}

        if header_match:
            header_html = header_match.group(1)

            # Extract title (double unescape for HTML entities)
            # Format: <b>title:</b> value<br>
            title_match = re.search(r'<b>title:</b>\s*([^<]+?)(?:<br>|</div>|\n)', header_html, re.IGNORECASE)
            if title_match:
                title_text = title_match.group(1).strip()
                # Unescape twice due to double-encoding
                home_page['title'] = html.unescape(html.unescape(title_text))
            else:
                home_page['title'] = ""

            # Extract favicon (optional field)
            # Format can be: <b>favicon:</b> value OR just: favicon: value
            favicon_match = re.search(r'(?:<b>)?favicon:(?:</b>)?\s*([^<\n]+)', header_html, re.IGNORECASE)
            if favicon_match:
                favicon_text = favicon_match.group(1).strip()
                home_page['favicon'] = html.unescape(html.unescape(favicon_text))
            else:
                home_page['favicon'] = ""

            # Extract meta_image (optional field)
            # Format can be: <b>meta_image:</b> value OR just: meta_image: value
            meta_image_match = re.search(r'(?:<b>)?meta_image:(?:</b>)?\s*([^<\n]+)', header_html, re.IGNORECASE)
            if meta_image_match:
                meta_image_text = meta_image_match.group(1).strip()
                home_page['meta_image'] = html.unescape(html.unescape(meta_image_text))
            else:
                home_page['meta_image'] = ""

            # Extract meta_description (optional field)
            # Format can be: <b>meta_description:</b> value OR just: meta_description: value
            meta_desc_match = re.search(r'(?:<b>)?meta_description:(?:</b>)?\s*([^<\n]+)', header_html, re.IGNORECASE)
            if meta_desc_match:
                meta_desc_text = meta_desc_match.group(1).strip()
                # Remove any trailing separator that might have been manually added
                meta_desc_text = re.sub(r'\s*___\s*$', '', meta_desc_text)
                home_page['meta_description'] = html.unescape(html.unescape(meta_desc_text))
            else:
                home_page['meta_description'] = ""

        # Extract body content (unescape HTML entities)
        body_match = re.search(
            r'<textarea[^>]*name="body_content"[^>]*>(.*?)</textarea>', response.text, re.DOTALL
        )
        if body_match:
            # Unescape HTML entities in content (e.g., &quot; -> ")
            home_page['content'] = html.unescape(body_match.group(1).strip())
        else:
            home_page['content'] = ""

        return home_page

    def update_home_page(
        self,
        title: Optional[str] = None,
        favicon: Optional[str] = None,
        meta_description: Optional[str] = None,
        meta_image: Optional[str] = None,
        content: Optional[str] = None,
    ) -> bool:
        """Update home page content.

        Args:
            title: Blog title (optional)
            favicon: Favicon emoji or URL (optional)
            meta_description: Meta description for SEO (optional)
            meta_image: Meta image URL for social sharing (optional)
            content: Home page body content in markdown (optional)

        Returns:
            True if update successful
        """
        self._ensure_authenticated()

        # Get current content
        current = self.get_home_page()

        # Build header content (Bear Blog's contenteditable div will format with <b> and <br> tags)
        header_lines = []
        header_lines.append(f"title: {title if title is not None else current['title']}")

        favicon_val = favicon if favicon is not None else current['favicon']
        if favicon_val:
            header_lines.append(f"favicon: {favicon_val}")

        meta_desc_val = meta_description if meta_description is not None else current['meta_description']
        if meta_desc_val:
            header_lines.append(f"meta_description: {meta_desc_val}")

        meta_image_val = meta_image if meta_image is not None else current['meta_image']
        if meta_image_val:
            header_lines.append(f"meta_image: {meta_image_val}")

        # Join with \r\n - Bear Blog requires CRLF line endings for contenteditable div
        header_content = "\r\n".join(header_lines)

        # Submit update
        home_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/")
        csrf_token = self._get_csrf_token()

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "header_content": header_content,
            "body_content": content if content is not None else current['content'],
        }

        response = self.session.post(
            home_url,
            data=data,
            headers={"Referer": home_url},
        )

        return response.status_code == 200

    def get_navigation(self) -> str:
        """Get navigation links.

        Returns:
            Navigation content as markdown-formatted string
        """
        self._ensure_authenticated()

        nav_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/nav/")
        response = self.session.get(nav_url)
        response.raise_for_status()

        # Extract navigation content from textarea
        nav_match = re.search(
            r'<textarea[^>]*name="nav"[^>]*>(.*?)</textarea>', response.text, re.DOTALL
        )

        if nav_match:
            # Unescape HTML entities
            return html.unescape(nav_match.group(1).strip())

        return ""

    def update_navigation(self, nav_content: str) -> bool:
        """Update navigation links.

        Args:
            nav_content: Navigation content in markdown format
                        Example: "[Home](/) [Blog](/blog/) [About](/about/)"

        Returns:
            True if update successful
        """
        self._ensure_authenticated()

        nav_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/nav/")
        csrf_token = self._get_csrf_token()

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "nav": nav_content,
        }

        response = self.session.post(
            nav_url,
            data=data,
            headers={"Referer": nav_url},
        )

        return response.status_code == 200

    def get_styles(self) -> str:
        """Get custom CSS styles.

        Returns:
            Custom CSS content as string
        """
        self._ensure_authenticated()

        styles_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/styles/")
        response = self.session.get(styles_url)
        response.raise_for_status()

        # Extract custom styles from textarea
        styles_match = re.search(
            r'<textarea[^>]*name="custom_styles"[^>]*>(.*?)</textarea>',
            response.text,
            re.DOTALL,
        )

        if styles_match:
            # Unescape HTML entities
            return html.unescape(styles_match.group(1).strip())

        return ""

    def update_styles(self, css_content: str) -> bool:
        """Update custom CSS styles.

        Args:
            css_content: Custom CSS content

        Returns:
            True if update successful
        """
        self._ensure_authenticated()

        styles_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/styles/")
        csrf_token = self._get_csrf_token()

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "custom_styles": css_content,
            "codemirror_enabled": "on",  # Keep CodeMirror enabled
        }

        response = self.session.post(
            styles_url,
            data=data,
            headers={"Referer": styles_url},
        )

        return response.status_code == 200

    def apply_theme(self, theme_name: str) -> bool:
        """Apply a pre-built theme.

        WARNING: This will overwrite your current custom CSS!

        Args:
            theme_name: Theme name (e.g., 'default', 'writer', 'sakura', 'water')

        Returns:
            True if theme applied successfully
        """
        self._ensure_authenticated()

        styles_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/styles/")
        csrf_token = self._get_csrf_token()

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "stylesheet": theme_name,
        }

        response = self.session.post(
            styles_url,
            data=data,
            headers={"Referer": styles_url},
        )

        return response.status_code == 200

    def list_themes(self) -> list[str]:
        """Get list of available themes.

        Returns:
            List of theme names
        """
        self._ensure_authenticated()

        styles_url = urljoin(self.base_url, f"/{self.subdomain}/dashboard/styles/")
        response = self.session.get(styles_url)
        response.raise_for_status()

        # Extract all theme names from hidden inputs
        theme_matches = re.findall(
            r'<input type="hidden" name="stylesheet" value="([^"]+)">', response.text
        )

        # Remove duplicates and sort
        themes = sorted(set(theme_matches))

        return themes
