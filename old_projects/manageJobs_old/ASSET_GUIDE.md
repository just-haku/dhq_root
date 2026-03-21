Required Static Assets

For the web server to look robust and professional, ensure the following files exist in your project/static folder.

1. Favicon (Browser Tab Icon)

Path: project/static/images/favicon.svg

Format: SVG (recommended) or ICO.

Note: We are currently using a base64 data URI in base.html as a fallback, but a physical file is better for caching.

2. Logo (Optional)

Path: project/static/images/logo.png

Usage: Replace the text "LUCKFOX://KURO" in the navbar with <img src="..."> if desired.

3. Default User Avatar

Path: project/static/images/default_avatar.png

Usage: Fallback if ui-avatars.com is unreachable (offline mode).

4. Standard Reaction Images (Optional - Offline Mode)

If the device will be used completely offline (no internet), the Twemoji CDN links in gallery.html will break. Download these icons and save them locally:

project/static/reactions/heart.png

project/static/reactions/like.png

project/static/reactions/haha.png

project/static/reactions/sad.png

project/static/reactions/angry.png

Then update the gallery.html src attributes to point to /static/reactions/....