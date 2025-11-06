# WordPress WebP Image Replacer

> **⚠️ ARCHIVED**: This project is no longer maintained. Development was discontinued due to difficulties with WordPress REST API authentication and hosting compatibility issues.

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

## Pre-Setup: Preparing Your WordPress Site

**IMPORTANT**: Before running this tool, complete these steps on your WordPress site to ensure everything works smoothly.

### Step 1: Verify HTTPS is Enabled ⚠️ REQUIRED

Application Passwords **require HTTPS**. Check your site URL starts with `https://` (not `http://`).

If you only have HTTP:
- Contact your hosting provider to enable SSL
- Most hosts offer free Let's Encrypt certificates
- This usually takes 5-10 minutes to set up

### Step 2: Check WordPress Version

You need **WordPress 5.6 or later**:
1. Log into WordPress Admin
2. Check version at bottom-right or go to Dashboard → Updates
3. Update if necessary

### Step 3: Fix Authorization Headers (CRITICAL)

This prevents 406 errors - **do this even if you're not having problems yet**:

**Quick Fix (Works 70% of the time):**
1. In WordPress Admin: Settings → Permalinks
2. Don't change anything, just click **"Save Changes"**
3. This regenerates `.htaccess` with correct authorization rules

**GoDaddy Users (Required):**
1. Log into GoDaddy hosting account
2. Website Security → Firewall → Settings → Access Control
3. Click "Allow URL Paths"
4. Add: `/wp-json/wp/v2/`
5. Click Allow

**If You Use Security Plugins:**
- **Wordfence**: Enable "Learning Mode" in WAF settings
- **"Disable REST API" plugins**: Deactivate temporarily
- **Other security plugins**: Check REST API isn't blocked

### Step 4: Test REST API Works

Open this URL in your browser (replace with your site):
```
https://your-site.com/wp-json/wp/v2/posts
```

✅ **Good**: You see JSON data (looks like code)
❌ **Bad**: Error page or "Forbidden" message

If blocked, contact hosting support: "Please enable WordPress REST API for Application Passwords"

## Configuration

### WordPress Setup

1. **Create Application Password** in WordPress:
   - Go to Users → Your Profile
   - Scroll to "Application Passwords" section
   - If section is missing: HTTPS is not enabled (see Pre-Setup above)
   - Enter a name (e.g., "Image Replacer")
   - Click "Add New Application Password"
   - **Copy the password immediately** (you won't see it again!)
   - Save it securely

2. **Edit config.json** (or enter in the GUI):

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

## Using the Application

### First Time Setup

1. Launch the application: `uv run python main.py`
2. Click **"Help: Setup App Password"** for step-by-step instructions
3. Enter your WordPress credentials:
   - WordPress URL (with https://)
   - Username (NOT email address)
   - Application Password (remove spaces)
4. Click **"Test Connection"** to verify it works
5. If you get errors, click **"Run Full Diagnostics"** for detailed help

### Running Image Replacement

1. Select the folder containing your WebP files
2. Click **"Start Replacement"**
3. Monitor progress in the log window
4. When complete, export the log for your records
5. Review changes on your WordPress site

## Troubleshooting

### Use the Built-in Diagnostics

The application includes powerful diagnostic tools:
1. Click **"Run Full Diagnostics"** button
2. Review the detailed test results in the log
3. Follow the numbered recommendations
4. Most issues are fixed by going to Settings → Permalinks → Save Changes

### Common Issues and Fixes

**Problem: 406 Not Acceptable Error**
- **Cause**: Server blocking authorization headers (mod_security or firewall)
- **Fix 1**: WordPress Settings → Permalinks → Save Changes
- **Fix 2**: GoDaddy users - whitelist `/wp-json/wp/v2/` in firewall
- **Fix 3**: Contact hosting support about REST API access
- **Fix 4**: Temporarily disable security plugins to test

**Problem: 401 Unauthorized Error**
- **Cause**: Invalid credentials
- **Fix 1**: Verify username is correct (not email)
- **Fix 2**: Regenerate Application Password and copy it carefully
- **Fix 3**: Remove all spaces from Application Password
- **Fix 4**: Verify you're using Application Password, not regular password

**Problem: Application Passwords Section Not Visible**
- **Cause**: HTTPS not enabled
- **Fix**: Enable SSL certificate in hosting panel (usually free)

**Problem: REST API Not Accessible**
- **Cause**: Hosting firewall or plugin blocking REST API
- **Fix 1**: Test by visiting: `https://your-site.com/wp-json/wp/v2/posts`
- **Fix 2**: Contact hosting support about enabling WordPress REST API
- **Fix 3**: Check for "Disable REST API" plugins and deactivate

**Problem: Connection Works But Upload Fails**
- **Cause**: File permissions or upload limits
- **Fix 1**: Check file permissions on WebP files
- **Fix 2**: Verify WordPress media upload permissions
- **Fix 3**: Check file size limits in WordPress settings

**Problem: No Matches Found**
- **Cause**: Filename mismatch between WebP and PNG files
- **Fix 1**: Verify WebP filenames match PNG filenames (without extension)
- **Fix 2**: Check that PNG files exist in WordPress media library
- **Fix 3**: Filenames are case-insensitive (sunset.webp matches Sunset.png)

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
