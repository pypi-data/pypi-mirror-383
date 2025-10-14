"""
Tabs directive for Mistune.

Provides tabbed content sections with full markdown support including
nested directives, code blocks, and admonitions.

Supports both modern MyST syntax and legacy Bengal syntax:

Modern (MyST - Preferred):
    :::{tab-set}
    :::{tab-item} Python
    Content here
    :::
    :::{tab-item} JavaScript
    Content here
    :::
    ::::

Legacy (Bengal):
    ````{tabs}
    ### Tab: Python
    Content here
    ### Tab: JavaScript
    Content here
    ````
"""

import re
from re import Match
from typing import Any

from mistune.directives import DirectivePlugin

from bengal.utils.logger import get_logger

__all__ = [
    "TabItemDirective",  # Modern MyST syntax
    "TabSetDirective",  # Modern MyST syntax
    "TabsDirective",  # Legacy syntax (backward compat)
    "render_tab_item",
    "render_tab_set",
]

logger = get_logger(__name__)

# Pre-compiled regex patterns (compiled once, reused for all pages)
_TAB_SPLIT_PATTERN = re.compile(r"^### Tab: (.+)$", re.MULTILINE)


class TabSetDirective(DirectivePlugin):
    """
    Modern MyST-style tab container directive.

    Syntax:
        :::{tab-set}
        :sync: my-key  # Optional: sync tabs across multiple tab-sets

        :::{tab-item} Python
        Python content with **markdown** support.
        :::

        :::{tab-item} JavaScript
        JavaScript content here.
        :::
        ::::

    Each tab-item is a nested directive inside the tab-set.
    This is cleaner and more consistent with MyST Markdown.
    """

    def parse(self, block: Any, m: Match, state: Any) -> dict[str, Any]:
        """Parse tab-set directive."""
        options = dict(self.parse_options(m))

        # Parse nested tab-item directives
        content = self.parse_content(m)
        children = self.parse_tokens(block, content, state)

        return {
            "type": "tab_set",
            "attrs": options,
            "children": children,
        }

    def __call__(self, directive, md):
        """Register the directive with mistune."""
        directive.register("tab-set", self.parse)

        if md.renderer and md.renderer.NAME == "html":
            md.renderer.register("tab_set", render_tab_set)


class TabItemDirective(DirectivePlugin):
    """
    Individual tab directive (nested in tab-set).

    Syntax:
        :::{tab-item} Tab Title
        :selected:  # Optional: mark this tab as initially selected

        Tab content with full **markdown** support.
        :::

    Supports all markdown features including nested directives.
    """

    def parse(self, block: Any, m: Match, state: Any) -> dict[str, Any]:
        """Parse tab-item directive."""
        title = self.parse_title(m)
        options = dict(self.parse_options(m))

        # Parse tab content
        content = self.parse_content(m)
        children = self.parse_tokens(block, content, state)

        return {
            "type": "tab_item",
            "attrs": {
                "title": title,
                "selected": "selected" in options,
            },
            "children": children,
        }

    def __call__(self, directive, md):
        """Register the directive with mistune."""
        directive.register("tab-item", self.parse)

        if md.renderer and md.renderer.NAME == "html":
            md.renderer.register("tab_item", render_tab_item)


class TabsDirective(DirectivePlugin):
    """
    LEGACY: Old Bengal tab syntax (backward compatibility).

    Syntax:
        ````{tabs}
        ### Tab: Python
        Content here
        ### Tab: JavaScript
        Content here
        ````

    NOTE: This is kept for backward compatibility only.
    New docs should use the MyST syntax (tab-set/tab-item).
    """

    def parse(self, block: Any, m: Match, state: Any) -> dict[str, Any]:
        """Parse legacy tabs directive with ### Tab: markers."""
        options = dict(self.parse_options(m))
        content = self.parse_content(m)

        # Split content by tab markers: ### Tab: Title
        parts = _TAB_SPLIT_PATTERN.split(content)

        tab_items = []
        if len(parts) > 1 and not parts[0].strip():
            # Parse each tab (skip empty first part)
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    title = parts[i].strip()
                    tab_content = parts[i + 1].strip()

                    tab_items.append(
                        {
                            "type": "tab_item",
                            "attrs": {
                                "title": title,
                                "selected": i == 1,  # First tab selected
                            },
                            "children": self.parse_tokens(block, tab_content, state),
                        }
                    )

        # If no valid tabs found, create single tab
        if not tab_items:
            tab_items.append(
                {
                    "type": "tab_item",
                    "attrs": {
                        "title": options.get("title", "Content"),
                        "selected": True,
                    },
                    "children": self.parse_tokens(block, content, state),
                }
            )

        return {
            "type": "tab_set",
            "attrs": options,
            "children": tab_items,
        }

    def __call__(self, directive, md):
        """Register the directive with mistune."""
        directive.register("tabs", self.parse)

        # Uses the same renderer as TabSetDirective
        if md.renderer and md.renderer.NAME == "html":
            md.renderer.register("tab_set", render_tab_set)
            md.renderer.register("tab_item", render_tab_item)


# Render functions


def render_tab_set(renderer, text: str, **attrs) -> str:
    """
    Render tab-set container to HTML.

    The text contains rendered tab-item children. We need to extract
    titles and contents to build the tab navigation and panels.

    Args:
        renderer: Mistune renderer
        text: Rendered children (tab items)
        attrs: Tab set attributes (id, sync, etc.)

    Returns:
        HTML string for tab set
    """
    tab_id = attrs.get("id", f"tabs-{id(text)}")
    sync_key = attrs.get("sync", "")

    # Extract tab items from rendered HTML
    # Pattern: <div class="tab-item" data-title="..." data-selected="...">content</div>
    import re

    tab_pattern = re.compile(
        r'<div class="tab-item" data-title="([^"]*)" data-selected="([^"]*)">(.*?)</div>', re.DOTALL
    )
    matches = tab_pattern.findall(text)

    if not matches:
        # Fallback: just wrap the content
        return f'<div class="tabs" id="{tab_id}">\n{text}</div>\n'

    # Build tab navigation
    nav_html = f'<div class="tabs" id="{tab_id}"'
    if sync_key:
        nav_html += f' data-sync="{_escape_html(sync_key)}"'
    nav_html += '>\n  <ul class="tab-nav">\n'

    for i, (title, selected, _) in enumerate(matches):
        active = (
            ' class="active"'
            if selected == "true" or (i == 0 and not any(s == "true" for _, s, _ in matches))
            else ""
        )
        nav_html += f'    <li{active}><a href="#" data-tab-target="{tab_id}-{i}">{_escape_html(title)}</a></li>\n'
    nav_html += "  </ul>\n"

    # Build content panes
    content_html = '  <div class="tab-content">\n'
    for i, (_, selected, content) in enumerate(matches):
        active = (
            " active"
            if selected == "true" or (i == 0 and not any(s == "true" for _, s, _ in matches))
            else ""
        )
        content_html += (
            f'    <div id="{tab_id}-{i}" class="tab-pane{active}">\n{content}    </div>\n'
        )
    content_html += "  </div>\n</div>\n"

    return nav_html + content_html


def render_tab_item(renderer, text: str, **attrs) -> str:
    """
    Render individual tab item to HTML.

    This creates a wrapper div with metadata that the parent tab-set
    will parse to build the navigation and panels.

    Args:
        renderer: Mistune renderer
        text: Rendered tab content
        attrs: Tab attributes (title, selected)

    Returns:
        HTML string for tab item (wrapper for tab-set to parse)
    """
    title = attrs.get("title", "Tab")
    selected = "true" if attrs.get("selected", False) else "false"

    # Return wrapper div that tab-set will parse
    # We escape the attributes but not the content (already rendered HTML)
    return (
        f'<div class="tab-item" '
        f'data-title="{_escape_html(title)}" '
        f'data-selected="{selected}">'
        f"{text}"
        f"</div>"
    )


def _escape_html(text: str) -> str:
    """
    Escape HTML special characters in attributes.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    if not text:
        return ""

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
