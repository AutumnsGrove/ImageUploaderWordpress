"""Image matching logic for pairing local WebP files with WordPress PNG files."""

import re
from pathlib import Path
from typing import List, Dict, Optional


class ImageMatcher:
    """Handles matching local WebP files to WordPress PNG media items."""

    @staticmethod
    def get_webp_files(folder_path: Path) -> List[Path]:
        """
        Get all WebP files from folder.

        Args:
            folder_path: Path to folder containing WebP files

        Returns:
            List of Path objects for WebP files
        """
        if not folder_path.exists() or not folder_path.is_dir():
            return []

        return list(folder_path.glob("*.webp"))

    @staticmethod
    def normalize_filename(filename: str) -> str:
        """
        Normalize filename by removing WordPress suffixes and extensions.

        Removes patterns like:
        - -scaled
        - -1024x768
        - -300x200
        - Extension (.png, .webp, etc.)

        Args:
            filename: Original filename

        Returns:
            Normalized filename (lowercase, no extension or suffixes)
        """
        # Remove extension
        name = Path(filename).stem

        # Remove WordPress size suffixes (e.g., -1024x768, -300x200)
        name = re.sub(r"-\d+x\d+$", "", name)

        # Remove -scaled suffix
        name = re.sub(r"-scaled$", "", name)

        return name.lower()

    @staticmethod
    def find_matching_media(
        webp_file: Path,
        media_items: List[Dict]
    ) -> Optional[Dict]:
        """
        Find matching WordPress media item for a WebP file.

        Args:
            webp_file: Path to local WebP file
            media_items: List of WordPress media item dictionaries

        Returns:
            Matching media item dictionary or None
        """
        webp_normalized = ImageMatcher.normalize_filename(webp_file.name)

        for media in media_items:
            # Get source URL from media item
            source_url = media.get("source_url", "")

            # Extract filename from URL
            media_filename = Path(source_url).name

            # Only match PNG files
            if not media_filename.lower().endswith(".png"):
                continue

            media_normalized = ImageMatcher.normalize_filename(media_filename)

            if webp_normalized == media_normalized:
                return media

        return None

    @staticmethod
    def extract_url_patterns(media_item: Dict) -> List[str]:
        """
        Extract all possible URL patterns from media item.

        WordPress stores multiple sizes of images. This extracts all URLs
        that might be referenced in content.

        Args:
            media_item: WordPress media item dictionary

        Returns:
            List of URL patterns to search for
        """
        urls = []

        # Main source URL
        source_url = media_item.get("source_url")
        if source_url:
            urls.append(source_url)

        # Media details sizes
        media_details = media_item.get("media_details", {})
        sizes = media_details.get("sizes", {})

        for size_name, size_data in sizes.items():
            size_url = size_data.get("source_url")
            if size_url:
                urls.append(size_url)

        return urls
