# Bear Blog MCP Server

[![PyPI version](https://badge.fury.io/py/bearblog-mcp-server.svg)](https://pypi.org/project/bearblog-mcp-server/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for interacting with [Bear Blog](https://bearblog.dev) programmatically. This allows AI assistants like Claude to manage your Bear Blog posts directly.

## Features

### Post Management
- **List Posts**: Get all your blog posts with metadata
- **Read Posts**: Retrieve full post content including title, slug, and markdown body
- **Create Posts**: Write new blog posts (as drafts or published)
- **Update Posts**: Edit existing posts
- **Delete Posts**: Permanently remove posts
- **Publish/Unpublish**: Toggle post publication status

### Page Management
- **List Pages**: Get all your static pages with metadata
- **Read Pages**: Retrieve full page content
- **Create Pages**: Create new pages (About, Contact, etc.)
- **Update Pages**: Edit existing pages
- **Delete Pages**: Permanently remove pages
- **Publish/Unpublish Pages**: Toggle page publication status

### Blog Settings
- **Get Settings**: Retrieve all blog configuration
- **Update Settings**: Modify blog subdomain, language, analytics, and advanced options

### Home Page Content
- **Get Home Page**: Retrieve blog title, favicon, meta description, meta image, and landing page content
- **Update Home Page**: Customize blog title, favicon, meta description, meta image, and home page markdown

### Navigation Management
- **Get Navigation**: Retrieve navigation menu links in markdown format
- **Update Navigation**: Customize navigation menu with markdown-formatted links

### Theme and Style Management
- **List Themes**: Get all available pre-built themes (30+ community themes)
- **Get Styles**: Retrieve current custom CSS
- **Update Styles**: Modify custom CSS to customize appearance
- **Apply Theme**: Apply a pre-built theme (WARNING: overwrites custom CSS)

## Installation

### Quick Start (Recommended)

Install and run with `uvx` (zero-install, runs immediately):

```bash
uvx --from bearblog-mcp-server bearblog-mcp
```

Or install persistently with `pipx`:

```bash
pipx install bearblog-mcp-server
# Then run with:
bearblog-mcp
```

### For Development

Clone the repository and install in editable mode:

```bash
git clone https://github.com/rmunoz33/bearblog-mcp.git
cd bearblog-mcp
uv pip install -e .
```

## Configuration

### Environment Variables

The MCP server requires Bear Blog credentials to be provided as environment variables:

- `BEAR_BLOG_EMAIL` - Your Bear Blog account email
- `BEAR_BLOG_PASSWORD` - Your Bear Blog account password
- `BEAR_BLOG_SUBDOMAIN` - Your blog's subdomain (e.g., "myblog" for myblog.bearblog.dev)
- `BEAR_BLOG_BASE_URL` - Base URL (default: https://bearblog.dev)

**Note**: For passwords with special characters, use single quotes in `.env` files.

**Note**: Use double quotes around the password. If your password contains a dollar sign (`$`), it will be treated as a literal character (python-dotenv does not expand bare `$` variables).

## Usage

### With Claude Code

Add to your Claude Code MCP settings (`~/.claude.json`):

```json
{
  "mcpServers": {
    "bearblog": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "bearblog-mcp-server", "bearblog-mcp"],
      "env": {
        "BEAR_BLOG_EMAIL": "your_email@example.com",
        "BEAR_BLOG_PASSWORD": "your_password",
        "BEAR_BLOG_SUBDOMAIN": "your_subdomain"
      }
    }
  }
}
```

**Alternative with `pipx` (if installed persistently):**

```json
{
  "mcpServers": {
    "bearblog": {
      "type": "stdio",
      "command": "bearblog-mcp",
      "env": {
        "BEAR_BLOG_EMAIL": "your_email@example.com",
        "BEAR_BLOG_PASSWORD": "your_password",
        "BEAR_BLOG_SUBDOMAIN": "your_subdomain"
      }
    }
  }
}
```

After editing the config, restart Claude Code and verify with the `/mcp` command.

### Standalone

Run the server directly:

```bash
# With uvx (zero-install)
BEAR_BLOG_EMAIL=your@email.com BEAR_BLOG_PASSWORD=pass BEAR_BLOG_SUBDOMAIN=blog \
  uvx --from bearblog-mcp-server bearblog-mcp

# Or if installed with pipx
BEAR_BLOG_EMAIL=your@email.com BEAR_BLOG_PASSWORD=pass BEAR_BLOG_SUBDOMAIN=blog \
  bearblog-mcp
```

## Available Tools

### Post Tools
- `bear_list_posts` - List all blog posts
- `bear_get_post` - Get a specific post by ID
- `bear_create_post` - Create a new post
- `bear_update_post` - Update an existing post
- `bear_delete_post` - Delete a post permanently
- `bear_publish_post` - Toggle publish status

### Page Tools
- `bear_list_pages` - List all pages
- `bear_get_page` - Get a specific page by ID
- `bear_create_page` - Create a new page
- `bear_update_page` - Update an existing page
- `bear_delete_page` - Delete a page permanently
- `bear_publish_page` - Toggle page publish status

### Settings Tools
- `bear_get_blog_settings` - Get current blog configuration
- `bear_update_blog_settings` - Update blog settings

### Home Page Tools
- `bear_get_home_page` - Get blog title, favicon, meta description, meta image, and content
- `bear_update_home_page` - Update blog title, favicon, meta description, meta image, and content

### Navigation Tools
- `bear_get_navigation` - Get navigation menu links
- `bear_update_navigation` - Update navigation menu with markdown links

### Theme and Style Tools
- `bear_list_themes` - List all available pre-built themes
- `bear_get_styles` - Get current custom CSS
- `bear_update_styles` - Update custom CSS
- `bear_apply_theme` - Apply a pre-built theme (WARNING: overwrites custom CSS)

### Resources
- `bear://posts` - Formatted list of all posts
- `bear://post/{id}` - Individual post content
- `bear://pages` - Formatted list of all pages
- `bear://page/{id}` - Individual page content

## Premium Features

This MCP server was developed and tested using a **free Bear Blog account**. Some Bear Blog features require a [Bear Blog Pro subscription](https://bearblog.dev/dashboard/upgrade/) ($5/month or $49/year) and are not currently implemented:

- **Email List Management**: Subscriber capture and newsletter functionality
- **Media Upload**: Direct file and image uploading via MCP tools
- **Custom Domains**: Domain configuration tools
- **Advanced Analytics**: Detailed traffic and engagement metrics

If you have a Bear Blog Pro account and would like these features added, please [open an issue on GitHub](https://github.com/rmunoz33/bearblog-mcp/issues) or reach out to discuss implementation.

## Testing

Run the test scripts to verify functionality:

```bash
# Test post management
uv run python tests/test_tools.py

# Test page management
uv run python tests/test_pages.py
```

## Development

See `research/` directory for API exploration scripts and `API_FINDINGS.md` for endpoint documentation.

## License

MIT

## Credits

Built with [FastMCP](https://github.com/jlowin/fastmcp) - The fast, Pythonic way to build MCP servers.
