# CLAUDE.md

This file provides guidance to Claude Code when working with this WordPress Image Replacer project.

## Project Overview

This is a Python GUI application that automates replacing PNG images with WebP versions in WordPress media libraries. It handles:
- Uploading WebP files to WordPress
- Matching WebP files to existing PNG files
- Updating all post/page content references

## Running Commands

### UV Package Manager

**ALWAYS use `uv run` for Python commands:**

```bash
# Run the application
uv run python main.py

# Run tests
uv run pytest

# Format code
uv run black .
```

**DO NOT use bare `python` commands** - the environment is managed by UV.

## Project Structure

```
├── main.py              # GUI application (tkinter)
├── wordpress_api.py     # WordPress REST API client
├── image_matcher.py     # Filename matching logic
├── content_updater.py   # Post/page content updater
├── config.json          # User credentials (gitignored)
├── pyproject.toml       # UV dependencies
└── README.md            # User documentation
```

## Key Implementation Details

### WordPress API

The `WordPressAPI` class handles:
- Authentication via Application Passwords (Basic Auth)
- Media library operations (list, upload)
- Post/page operations (list, update)
- Pagination for large datasets (100 items per page)

### Image Matching

The `ImageMatcher` class:
- Normalizes filenames (removes WordPress suffixes: `-scaled`, `-1024x768`, etc.)
- Case-insensitive matching
- Handles multiple image sizes from WordPress

### Content Updates

The `ContentUpdater` class:
- Finds all posts/pages containing old image URLs
- Replaces URLs using regex (handles special characters)
- Counts replacements for logging

### GUI Application

The `WordPressImageReplacer` class:
- Tkinter-based interface
- Threaded operation (prevents UI freezing)
- Real-time progress tracking
- Detailed logging with timestamps

## Development Guidelines

### Code Style

- Use Black formatter for all Python code
- Add docstrings to all functions and classes
- Handle errors gracefully with try/except
- Log all important operations

### Error Handling

Key areas requiring error handling:
- Network requests (timeouts, connection errors)
- File operations (permissions, missing files)
- WordPress API responses (authentication, rate limiting)
- Content parsing and updating

### Testing

When adding features:
1. Test connection to WordPress API
2. Test file matching with various filename patterns
3. Test content replacement with edge cases
4. Test UI responsiveness during long operations

## Safety Considerations

⚠️ **This tool modifies live WordPress content**

- Always test on staging sites first
- Log all operations with detailed before/after info
- Provide stop button for user control
- Never delete files without explicit user action
- Save logs for user review

## Common Tasks

### Adding New Features

1. Update appropriate module (wordpress_api.py, image_matcher.py, etc.)
2. Add logging to new operations
3. Update UI if needed (main.py)
4. Update README with new functionality
5. Format code with Black
6. Test thoroughly

### Debugging Issues

1. Check log output in GUI
2. Verify WordPress API responses
3. Test filename matching separately
4. Check network connectivity
5. Validate credentials in config.json

## Configuration

Users configure via `config.json`:
- `wordpress_url`: WordPress site URL (with https://)
- `username`: WordPress username
- `app_password`: Application Password (not regular password!)
- `webp_folder`: Path to local WebP files

## Git Workflow

- Always format with Black before committing
- Write descriptive commit messages
- Follow commit message style from CLAUDE.md root instructions
- Don't commit config.json (contains credentials)
