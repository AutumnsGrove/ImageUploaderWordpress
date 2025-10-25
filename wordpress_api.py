"""WordPress REST API client for media and content management."""

import requests
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class WordPressAPI:
    """Client for interacting with WordPress REST API."""

    def __init__(self, site_url: str, username: str, app_password: str):
        """
        Initialize WordPress API client.

        Args:
            site_url: WordPress site URL (e.g., https://example.com)
            username: WordPress username
            app_password: Application password for authentication
        """
        self.site_url = site_url.rstrip("/")
        self.auth = (username, app_password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to WordPress API.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            response = self.session.get(
                f"{self.site_url}/wp-json/wp/v2/users/me",
                timeout=10
            )
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"Authentication failed: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def get_media_items(self, per_page: int = 100) -> List[Dict]:
        """
        Fetch all media library items with pagination.

        Args:
            per_page: Number of items per page (max 100)

        Returns:
            List of media item dictionaries
        """
        all_media = []
        page = 1

        while True:
            try:
                response = self.session.get(
                    f"{self.site_url}/wp-json/wp/v2/media",
                    params={"per_page": per_page, "page": page},
                    timeout=30
                )

                if response.status_code != 200:
                    break

                media_items = response.json()
                if not media_items:
                    break

                all_media.extend(media_items)

                # Check if there are more pages
                total_pages = int(response.headers.get("X-WP-TotalPages", 1))
                if page >= total_pages:
                    break

                page += 1

            except requests.exceptions.RequestException:
                break

        return all_media

    def upload_media(self, file_path: Path) -> Optional[Dict]:
        """
        Upload media file to WordPress.

        Args:
            file_path: Path to media file

        Returns:
            Media item dictionary if successful, None otherwise
        """
        try:
            with open(file_path, "rb") as f:
                files = {
                    "file": (file_path.name, f, "image/webp")
                }
                response = self.session.post(
                    f"{self.site_url}/wp-json/wp/v2/media",
                    files=files,
                    timeout=60
                )

                if response.status_code == 201:
                    return response.json()
                else:
                    return None

        except (requests.exceptions.RequestException, IOError):
            return None

    def get_posts(self, per_page: int = 100) -> List[Dict]:
        """
        Fetch all posts with pagination.

        Args:
            per_page: Number of posts per page

        Returns:
            List of post dictionaries
        """
        all_posts = []
        page = 1

        while True:
            try:
                response = self.session.get(
                    f"{self.site_url}/wp-json/wp/v2/posts",
                    params={"per_page": per_page, "page": page},
                    timeout=30
                )

                if response.status_code != 200:
                    break

                posts = response.json()
                if not posts:
                    break

                all_posts.extend(posts)

                total_pages = int(response.headers.get("X-WP-TotalPages", 1))
                if page >= total_pages:
                    break

                page += 1

            except requests.exceptions.RequestException:
                break

        return all_posts

    def get_pages(self, per_page: int = 100) -> List[Dict]:
        """
        Fetch all pages with pagination.

        Args:
            per_page: Number of pages per page

        Returns:
            List of page dictionaries
        """
        all_pages = []
        page = 1

        while True:
            try:
                response = self.session.get(
                    f"{self.site_url}/wp-json/wp/v2/pages",
                    params={"per_page": per_page, "page": page},
                    timeout=30
                )

                if response.status_code != 200:
                    break

                pages = response.json()
                if not pages:
                    break

                all_pages.extend(pages)

                total_pages = int(response.headers.get("X-WP-TotalPages", 1))
                if page >= total_pages:
                    break

                page += 1

            except requests.exceptions.RequestException:
                break

        return all_pages

    def update_post(self, post_id: int, content: str) -> bool:
        """
        Update post content.

        Args:
            post_id: WordPress post ID
            content: New post content (HTML)

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.post(
                f"{self.site_url}/wp-json/wp/v2/posts/{post_id}",
                json={"content": content},
                timeout=30
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def update_page(self, page_id: int, content: str) -> bool:
        """
        Update page content.

        Args:
            page_id: WordPress page ID
            content: New page content (HTML)

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.post(
                f"{self.site_url}/wp-json/wp/v2/pages/{page_id}",
                json={"content": content},
                timeout=30
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
