"""WordPress WebP Image Replacer - Main GUI Application."""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path
import json
import threading
from datetime import datetime
from typing import Optional

from wordpress_api import WordPressAPI
from image_matcher import ImageMatcher
from content_updater import ContentUpdater


class WordPressImageReplacer:
    """Main GUI application for WordPress image replacement."""

    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("WordPress WebP Image Replacer")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # State variables
        self.running = False
        self.api: Optional[WordPressAPI] = None
        self.log_entries = []

        # Load config if exists
        self.config = self.load_config()

        # Create UI
        self.create_widgets()

        # Populate fields from config
        self.populate_from_config()

    def load_config(self) -> dict:
        """Load configuration from config.json."""
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def save_config(self):
        """Save current settings to config.json."""
        config = {
            "wordpress_url": self.url_var.get(),
            "username": self.username_var.get(),
            "app_password": self.password_var.get(),
            "webp_folder": self.folder_var.get()
        }
        try:
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass

    def populate_from_config(self):
        """Populate input fields from loaded config."""
        self.url_var.set(self.config.get("wordpress_url", ""))
        self.username_var.set(self.config.get("username", ""))
        self.password_var.set(self.config.get("app_password", ""))
        self.folder_var.set(self.config.get("webp_folder", ""))

        # Log loaded config (without password)
        if self.config:
            print("Loaded config from config.json:")
            print(f"  WordPress URL: {self.config.get('wordpress_url', 'NOT SET')}")
            print(f"  Username: {self.config.get('username', 'NOT SET')}")
            print(f"  Password: {'***' if self.config.get('app_password') else 'NOT SET'}")
            print(f"  WebP Folder: {self.config.get('webp_folder', 'NOT SET')}")

    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Input fields
        row = 0

        # WordPress URL
        ttk.Label(main_frame, text="WordPress URL:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.url_var, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)

        row += 1

        # Username
        ttk.Label(main_frame, text="Username:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.username_var, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)

        row += 1

        # App Password
        ttk.Label(main_frame, text="App Password:").grid(row=row, column=0, sticky=tk.W, pady=5)
        password_frame = ttk.Frame(main_frame)
        password_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        password_frame.columnconfigure(0, weight=1)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*", width=40)
        self.password_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        self.show_password_var = tk.BooleanVar()
        ttk.Checkbutton(
            password_frame,
            text="Show",
            variable=self.show_password_var,
            command=self.toggle_password
        ).grid(row=0, column=1)

        row += 1

        # WebP Folder
        ttk.Label(main_frame, text="WebP Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)

        self.folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.folder_var, width=40).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(folder_frame, text="Browse...", command=self.browse_folder).grid(row=0, column=1)

        row += 1

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Test Connection", command=self.test_connection).grid(row=0, column=0, padx=5)

        self.start_button = ttk.Button(button_frame, text="Start Replacement", command=self.start_replacement)
        self.start_button.grid(row=0, column=1, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_replacement, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5)

        row += 1

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_label = ttk.Label(main_frame, text="Ready")
        self.progress_label.grid(row=row, column=0, columnspan=2, pady=5)

        row += 1

        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        row += 1

        # Log area
        log_label = ttk.Label(main_frame, text="Log:")
        log_label.grid(row=row, column=0, sticky=tk.W, pady=(10, 5))

        row += 1

        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80, state=tk.DISABLED)
        self.log_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)

        row += 1

        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(bottom_frame, text="Export Log", command=self.export_log).grid(row=0, column=0, padx=5)
        ttk.Button(bottom_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=1, padx=5)

    def toggle_password(self):
        """Toggle password visibility."""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def browse_folder(self):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(title="Select WebP Folder")
        if folder:
            self.folder_var.set(folder)

    def test_connection(self):
        """Test WordPress connection without starting replacement."""
        if not all([self.url_var.get(), self.username_var.get(), self.password_var.get()]):
            messagebox.showerror("Error", "Please fill in WordPress URL, Username, and App Password")
            return

        self.log("Testing connection...")

        try:
            # Strip spaces from app password (common issue)
            app_password = self.password_var.get().replace(" ", "")

            api = WordPressAPI(
                self.url_var.get(),
                self.username_var.get(),
                app_password
            )

            success, message = api.test_connection()

            if success:
                self.log("✓ Connection successful!")
                messagebox.showinfo("Success", "Connected to WordPress successfully!")
            else:
                self.log(f"✗ Connection failed: {message}")

                # Provide specific help for common errors
                if "406" in message:
                    help_text = (
                        f"{message}\n\n"
                        "Common causes for 406 error:\n"
                        "• Application Passwords not enabled in WordPress\n"
                        "• REST API disabled by security plugin\n"
                        "• Application password has spaces (remove all spaces)\n"
                        "• Wrong username (use username, not email)\n\n"
                        "To enable Application Passwords:\n"
                        "WordPress Admin → Users → Profile → Application Passwords"
                    )
                    messagebox.showerror("Connection Failed", help_text)
                else:
                    messagebox.showerror("Connection Failed", message)

        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Connection test failed: {str(e)}")

    def log(self, message: str):
        """
        Add message to log.

        Args:
            message: Message to log
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_entries.append(log_entry)

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        """Clear the log display."""
        self.log_entries.clear()
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def export_log(self):
        """Export log to file."""
        if not self.log_entries:
            messagebox.showinfo("Export Log", "No log entries to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"replacement_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            try:
                with open(filename, "w") as f:
                    f.write("\n".join(self.log_entries))
                messagebox.showinfo("Export Log", f"Log exported to {filename}")
            except IOError as e:
                messagebox.showerror("Export Error", f"Failed to export log: {str(e)}")

    def update_progress(self, current: int, total: int):
        """
        Update progress bar.

        Args:
            current: Current progress value
            total: Total value
        """
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"Progress: {current}/{total}")
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="Ready")

    def start_replacement(self):
        """Start the replacement process in a separate thread."""
        # Validate inputs
        if not all([
            self.url_var.get(),
            self.username_var.get(),
            self.password_var.get(),
            self.folder_var.get()
        ]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        # Save config
        self.save_config()

        # Update UI state
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Run in thread to prevent UI freezing
        thread = threading.Thread(target=self.run_replacement, daemon=True)
        thread.start()

    def stop_replacement(self):
        """Stop the replacement process."""
        self.running = False
        self.log("Stopping process...")

    def run_replacement(self):
        """Main replacement logic (runs in separate thread)."""
        try:
            # Initialize API
            self.log("Initializing WordPress API...")

            # Strip spaces from app password (common issue)
            app_password = self.password_var.get().replace(" ", "")

            self.api = WordPressAPI(
                self.url_var.get(),
                self.username_var.get(),
                app_password
            )

            # Test connection
            self.log("Testing connection...")
            success, message = self.api.test_connection()
            if not success:
                self.log(f"ERROR: {message}")

                # Provide specific help for common errors
                if "406" in message:
                    self.log("Common causes for 406 error:")
                    self.log("  • Application Passwords not enabled in WordPress")
                    self.log("  • REST API disabled by security plugin")
                    self.log("  • Application password has spaces (remove all spaces)")
                    self.log("  • Wrong username (use username, not email)")

                self.finish_replacement()
                return

            self.log("Connection successful!")

            # Scan for WebP files
            self.log("Scanning for WebP files...")
            webp_folder = Path(self.folder_var.get())
            webp_files = ImageMatcher.get_webp_files(webp_folder)
            self.log(f"Found {len(webp_files)} WebP files")

            if not webp_files:
                self.log("No WebP files found in folder")
                self.finish_replacement()
                return

            # Fetch media library
            self.log("Fetching WordPress media library...")
            media_items = self.api.get_media_items()
            self.log(f"Found {len(media_items)} media items")

            # Process each WebP file
            successful_replacements = 0
            total_files = len(webp_files)

            for idx, webp_file in enumerate(webp_files):
                if not self.running:
                    self.log("Process stopped by user")
                    break

                self.update_progress(idx + 1, total_files)
                self.log(f"Processing: {webp_file.name}")

                # Find matching PNG
                matching_media = ImageMatcher.find_matching_media(webp_file, media_items)

                if not matching_media:
                    self.log(f"  No matching PNG found for {webp_file.name}")
                    continue

                old_filename = Path(matching_media["source_url"]).name
                self.log(f"  Matched: {webp_file.name} → {old_filename}")

                # Upload WebP
                self.log(f"  Uploading {webp_file.name}...")
                uploaded_media = self.api.upload_media(webp_file)

                if not uploaded_media:
                    self.log(f"  ERROR: Upload failed for {webp_file.name}")
                    continue

                new_url = uploaded_media["source_url"]
                self.log(f"  Uploaded successfully: {new_url}")

                # Get old URLs to replace
                old_urls = ImageMatcher.extract_url_patterns(matching_media)

                # Fetch posts and pages
                self.log("  Fetching posts and pages...")
                posts = self.api.get_posts()
                pages = self.api.get_pages()
                all_content = posts + pages

                # Find content with old URLs
                matching_content = ContentUpdater.find_content_with_urls(all_content, old_urls)
                self.log(f"  Found {len(matching_content)} items to update")

                # Update posts
                posts_to_update = [c for c in matching_content if c.get("type") == "post"]
                if posts_to_update:
                    results = ContentUpdater.update_content_items(
                        self.api, posts_to_update, old_urls, new_url, "post"
                    )
                    for result in results:
                        if result["success"]:
                            self.log(f"    Updated post: {result['title']} ({result['replacements']} replacements)")

                # Update pages
                pages_to_update = [c for c in matching_content if c.get("type") == "page"]
                if pages_to_update:
                    results = ContentUpdater.update_content_items(
                        self.api, pages_to_update, old_urls, new_url, "page"
                    )
                    for result in results:
                        if result["success"]:
                            self.log(f"    Updated page: {result['title']} ({result['replacements']} replacements)")

                successful_replacements += 1

            # Summary
            self.log("=" * 50)
            self.log(f"Replacement complete!")
            self.log(f"Processed: {successful_replacements}/{total_files} files")

        except Exception as e:
            self.log(f"ERROR: {str(e)}")

        finally:
            self.finish_replacement()

    def finish_replacement(self):
        """Clean up after replacement process."""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_progress(0, 0)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = WordPressImageReplacer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
