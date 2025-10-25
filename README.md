# WordPress WebP Image Replacer

Automate replacing PNG images with compressed WebP versions in your WordPress media library and update all post/page references.

## Features

- 🔍 **Smart Matching**: Automatically matches local WebP files to WordPress PNG images by filename
- 📤 **Batch Upload**: Upload multiple WebP images to WordPress media library
- 🔄 **Content Update**: Automatically updates all post and page references to use new WebP images
- 📊 **Progress Tracking**: Real-time progress bar and detailed logging
- 💾 **Export Logs**: Save detailed logs of all replacements for review

## Requirements

- Python 3.11 or higher
- UV package manager
- WordPress site with REST API enabled
- Application Password for WordPress authentication

## Installation

### 1. Install UV Package Manager

If you don't have UV installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone/Download Project

```bash
cd /path/to/wordpress-image-replacer
```

### 3. Install Dependencies

```bash
uv sync
```

## Configuration

### WordPress Setup

1. **Enable Application Passwords** in WordPress:
   - Go to Users → Profile
   - Scroll to "Application Passwords"
   - Enter a name (e.g., "Image Replacer")
   - Click "Add New Application Password"
   - Copy the generated password (you won't see it again!)

2. **Edit config.json**:

```json
{
  "wordpress_url": "https://your-site.com",
  "username": "your-wordpress-username",
  "app_password": "your-application-password",
  "webp_folder": "/path/to/your/webp/files"
}
```

**Important**:
- Use your WordPress username, not email
- Use the Application Password, not your regular password
- WordPress URL should include `https://`
- WebP folder should be absolute path

## Usage

### Running the Application

```bash
uv run python main.py
```

### GUI Interface

1. **Enter WordPress Credentials**: Fill in site URL, username, and application password
2. **Select WebP Folder**: Browse to folder containing your WebP files
3. **Start Replacement**: Click "Start Replacement" button
4. **Monitor Progress**: Watch the log for detailed progress
5. **Export Log**: Save the log file for your records

### How It Works

1. Scans local folder for `.webp` files
2. Fetches all media items from WordPress library
3. For each WebP file:
   - Finds matching PNG file by filename (handles WordPress suffixes like `-scaled`, `-1024x768`)
   - Uploads WebP version to WordPress
   - Searches all posts and pages for old PNG URLs
   - Replaces old URLs with new WebP URLs
4. Generates detailed log of all changes

## File Matching

The tool handles WordPress naming conventions:

- `sunset.webp` matches `sunset.png`
- `sunset.webp` matches `sunset-scaled.png`
- `sunset.webp` matches `sunset-1024x768.png`
- Matching is case-insensitive

## Safety Features

- ✅ **Non-Destructive**: Original PNG files are NOT deleted (Phase 1)
- ✅ **Detailed Logging**: Every action is logged with timestamps
- ✅ **Connection Testing**: Validates WordPress connection before starting
- ✅ **Progress Tracking**: See exactly what's happening in real-time
- ✅ **Stop Button**: Cancel operation at any time

## Troubleshooting

### Connection Failed

- Verify WordPress URL is correct (include `https://`)
- Check Application Password is entered correctly
- Ensure WordPress REST API is accessible

### Upload Failed

- Check file permissions on WebP files
- Verify WordPress has upload permissions
- Check file size limits in WordPress

### No Matches Found

- Verify WebP filenames match PNG filenames (without extension)
- Check that PNG files exist in WordPress media library
- Try case-insensitive matching

## Development

### Project Structure

```
wordpress-image-replacer/
├── main.py               # GUI application
├── wordpress_api.py      # WordPress REST API client
├── image_matcher.py      # Filename matching logic
├── content_updater.py    # Content replacement logic
├── config.json           # Configuration (gitignored)
├── pyproject.toml        # UV project config
└── README.md             # This file
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
```

## Important Notes

⚠️ **Test on Staging First**: If possible, test on a staging site before production

⚠️ **Backup Recommended**: Always backup your WordPress database before bulk operations

⚠️ **Review Logs**: Check the exported log file to verify all replacements

## Roadmap (Phase 2)

- [ ] Delete old PNG files from media library
- [ ] Bulk cleanup of unused images
- [ ] Advanced filtering (date range, specific directories)
- [ ] Dry-run preview mode

## License

MIT

## Support

For issues or questions, please create an issue in the project repository.
