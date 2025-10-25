"""Content updater for replacing image URLs in WordPress posts and pages."""

import re
from typing import List, Dict, Tuple


class ContentUpdater:
    """Handles updating image URLs in WordPress content."""

    @staticmethod
    def find_and_replace_urls(
        content: str,
        old_urls: List[str],
        new_url: str
    ) -> Tuple[str, int]:
        """
        Find and replace old image URLs with new URL in content.

        Args:
            content: HTML content string
            old_urls: List of old URLs to replace
            new_url: New URL to use

        Returns:
            Tuple of (updated_content, replacement_count)
        """
        updated_content = content
        total_replacements = 0

        for old_url in old_urls:
            # Escape special regex characters in URL
            escaped_url = re.escape(old_url)

            # Count occurrences
            count = len(re.findall(escaped_url, updated_content))

            if count > 0:
                # Replace all occurrences
                updated_content = re.sub(escaped_url, new_url, updated_content)
                total_replacements += count

        return updated_content, total_replacements

    @staticmethod
    def find_content_with_urls(
        posts_and_pages: List[Dict],
        urls: List[str]
    ) -> List[Dict]:
        """
        Find all posts/pages that contain any of the URLs.

        Args:
            posts_and_pages: List of post/page dictionaries
            urls: List of URLs to search for

        Returns:
            List of content items that contain the URLs
        """
        matching_content = []

        for item in posts_and_pages:
            content = item.get("content", {})

            # Content might be dict with 'rendered' key or string
            if isinstance(content, dict):
                content_html = content.get("rendered", "")
            else:
                content_html = str(content)

            # Check if any URL appears in content
            for url in urls:
                if url in content_html:
                    matching_content.append(item)
                    break  # No need to check other URLs for this item

        return matching_content

    @staticmethod
    def update_content_items(
        api,
        content_items: List[Dict],
        old_urls: List[str],
        new_url: str,
        content_type: str = "post"
    ) -> List[Dict]:
        """
        Update multiple content items with URL replacements.

        Args:
            api: WordPressAPI instance
            content_items: List of post/page dictionaries to update
            old_urls: List of old URLs to replace
            new_url: New URL to use
            content_type: "post" or "page"

        Returns:
            List of update results with keys: id, title, success, replacements
        """
        results = []

        for item in content_items:
            item_id = item.get("id")
            title = item.get("title", {})

            # Handle title (might be dict or string)
            if isinstance(title, dict):
                title_text = title.get("rendered", "Untitled")
            else:
                title_text = str(title)

            content = item.get("content", {})

            # Handle content (might be dict or string)
            if isinstance(content, dict):
                content_html = content.get("rendered", "")
            else:
                content_html = str(content)

            # Replace URLs
            updated_content, replacement_count = ContentUpdater.find_and_replace_urls(
                content_html,
                old_urls,
                new_url
            )

            # Update via API
            if content_type == "post":
                success = api.update_post(item_id, updated_content)
            else:
                success = api.update_page(item_id, updated_content)

            results.append({
                "id": item_id,
                "title": title_text,
                "success": success,
                "replacements": replacement_count
            })

        return results
