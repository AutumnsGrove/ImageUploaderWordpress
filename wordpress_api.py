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
        # First check if REST API is accessible at all
        try:
            rest_response = self.session.get(
                f"{self.site_url}/wp-json/",
                timeout=10,
                auth=None,  # No auth needed for discovery endpoint
            )
            if rest_response.status_code != 200:
                return (
                    False,
                    f"REST API not accessible (status {rest_response.status_code}). Check if REST API is enabled.",
                )
        except requests.exceptions.RequestException as e:
            return False, f"Cannot reach WordPress site: {str(e)}"

        # Now test authentication
        try:
            response = self.session.get(
                f"{self.site_url}/wp-json/wp/v2/users/me", timeout=10
            )
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("name", "Unknown")
                return True, f"Connection successful! Logged in as: {username}"
            elif response.status_code == 406:
                # Get more details about the 406 error
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = f" - {error_data.get('message', '')}"
                except:
                    pass
                return False, (
                    f"Authentication failed: 406 Not Acceptable{error_detail}\n\n"
                    "This usually means Application Passwords are not enabled.\n"
                    "WordPress requires version 5.6+ or the Application Passwords plugin."
                )
            else:
                return (
                    False,
                    f"Authentication failed: {response.status_code} - {response.reason}",
                )
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def run_diagnostics(self) -> Dict[str, any]:
        """
        Run comprehensive diagnostics on WordPress REST API connection.

        Returns:
            Dictionary with diagnostic results and recommendations
        """
        results = {"tests": [], "overall_status": "unknown", "recommendations": []}

        # Test 1: Basic REST API availability
        test1 = {"name": "REST API Availability", "status": "unknown", "message": ""}
        try:
            response = self.session.get(
                f"{self.site_url}/wp-json/", timeout=10, auth=None
            )
            if response.status_code == 200:
                test1["status"] = "pass"
                test1["message"] = "REST API is accessible"
            else:
                test1["status"] = "fail"
                test1["message"] = f"REST API returned status {response.status_code}"
                results["recommendations"].append(
                    "Contact your hosting provider - REST API may be disabled"
                )
        except requests.exceptions.RequestException as e:
            test1["status"] = "fail"
            test1["message"] = f"Cannot reach site: {str(e)}"
            results["recommendations"].append(
                "Check that the WordPress URL is correct and the site is online"
            )
        results["tests"].append(test1)

        # Test 2: Public posts endpoint
        test2 = {"name": "Public Posts Endpoint", "status": "unknown", "message": ""}
        try:
            response = self.session.get(
                f"{self.site_url}/wp-json/wp/v2/posts", timeout=10, auth=None
            )
            test2["status"] = "pass" if response.status_code == 200 else "warning"
            test2["message"] = f"Status {response.status_code}"
            if response.status_code != 200:
                results["recommendations"].append(
                    "Posts endpoint not accessible - may indicate REST API restrictions"
                )
        except requests.exceptions.RequestException as e:
            test2["status"] = "fail"
            test2["message"] = f"Error: {str(e)}"
        results["tests"].append(test2)

        # Test 3: HTTPS check
        test3 = {"name": "HTTPS Enabled", "status": "unknown", "message": ""}
        if self.site_url.startswith("https://"):
            test3["status"] = "pass"
            test3["message"] = "Site uses HTTPS (required for Application Passwords)"
        else:
            test3["status"] = "fail"
            test3["message"] = "Site uses HTTP - Application Passwords require HTTPS"
            results["recommendations"].append(
                "Enable SSL certificate on your hosting account. Most hosts offer free Let's Encrypt certificates."
            )
        results["tests"].append(test3)

        # Test 4: Authentication
        test4 = {"name": "Authentication", "status": "unknown", "message": ""}
        try:
            response = self.session.get(
                f"{self.site_url}/wp-json/wp/v2/users/me", timeout=10
            )
            if response.status_code == 200:
                test4["status"] = "pass"
                user_data = response.json()
                username = user_data.get("name", "Unknown")
                test4["message"] = f"Authenticated as: {username}"
            elif response.status_code == 401:
                test4["status"] = "fail"
                test4["message"] = "401 Unauthorized - Invalid credentials"
                results["recommendations"].extend(
                    [
                        "Verify your WordPress username is correct (not email address)",
                        "Regenerate your Application Password and try again",
                        "Make sure you copied the password without spaces",
                    ]
                )
            elif response.status_code == 406:
                test4["status"] = "fail"
                test4["message"] = "406 Not Acceptable - Server blocking request"
                results["recommendations"].extend(
                    [
                        "mod_security or hosting firewall is blocking the request",
                        "FIX #1: Go to WordPress Settings → Permalinks → Click 'Save Changes' (regenerates .htaccess)",
                        "FIX #2 (GoDaddy): In hosting panel, go to Website Security → Firewall → Access Control → Allow URL Paths → Add '/wp/v2/'",
                        "FIX #3: Contact hosting support and ask them to whitelist WordPress REST API endpoints",
                        "FIX #4: Temporarily disable security plugins like Wordfence to test",
                    ]
                )
            elif response.status_code == 403:
                test4["status"] = "fail"
                test4["message"] = (
                    "403 Forbidden - Valid credentials but insufficient permissions"
                )
                results["recommendations"].append(
                    "Your user account may not have sufficient permissions. Try with an Administrator account."
                )
            else:
                test4["status"] = "fail"
                test4["message"] = f"Status {response.status_code}: {response.reason}"
        except requests.exceptions.RequestException as e:
            test4["status"] = "fail"
            test4["message"] = f"Connection error: {str(e)}"
        results["tests"].append(test4)

        # Test 5: Check for authorization header support
        test5 = {"name": "Authorization Header", "status": "unknown", "message": ""}
        # This is indicated by 406 errors, so we can infer from test 4
        if test4["status"] == "fail" and "406" in test4["message"]:
            test5["status"] = "fail"
            test5["message"] = "Server not passing authorization headers"
            results["recommendations"].append(
                "Your server is stripping authorization headers. This is the most common cause of 406 errors."
            )
        elif test4["status"] == "pass":
            test5["status"] = "pass"
            test5["message"] = "Authorization headers working correctly"
        else:
            test5["status"] = "unknown"
            test5["message"] = "Cannot determine - authentication test needed"
        results["tests"].append(test5)

        # Determine overall status
        statuses = [test["status"] for test in results["tests"]]
        if all(s == "pass" for s in statuses):
            results["overall_status"] = "pass"
        elif any(s == "fail" for s in statuses):
            results["overall_status"] = "fail"
        else:
            results["overall_status"] = "warning"

        # Add general recommendations if there are issues
        if results["overall_status"] != "pass":
            if not any(
                "Settings → Permalinks" in r for r in results["recommendations"]
            ):
                results["recommendations"].append(
                    "QUICK FIX TO TRY: Go to WordPress Dashboard → Settings → Permalinks → Click 'Save Changes' (this often fixes authorization issues)"
                )

        return results

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
                    timeout=30,
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
                files = {"file": (file_path.name, f, "image/webp")}
                response = self.session.post(
                    f"{self.site_url}/wp-json/wp/v2/media", files=files, timeout=60
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
                    timeout=30,
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
                    timeout=30,
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
                timeout=30,
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
                timeout=30,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
