import os
import requests

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REACTIONS_DIR = os.path.join(BASE_DIR, 'static', 'reactions')

if not os.path.exists(REACTIONS_DIR):
    os.makedirs(REACTIONS_DIR)
    print(f"Created {REACTIONS_DIR}")

# Twitter Emoji URLs (High quality PNGs)
EMOJIS = {
    'heart.png': 'https://abs-0.twimg.com/emoji/v2/72x72/2764.png',
    'like.png': 'https://abs-0.twimg.com/emoji/v2/72x72/1f44d.png',
    'haha.png': 'https://abs-0.twimg.com/emoji/v2/72x72/1f602.png',
    'sad.png': 'https://abs-0.twimg.com/emoji/v2/72x72/1f622.png',
    'angry.png': 'https://abs-0.twimg.com/emoji/v2/72x72/1f621.png'
}

print("Downloading default reaction assets...")
for name, url in EMOJIS.items():
    path = os.path.join(REACTIONS_DIR, name)
    if not os.path.exists(path):
        try:
            r = requests.get(url)
            with open(path, 'wb') as f:
                f.write(r.content)
            print(f" -> Downloaded {name}")
        except Exception as e:
            print(f" -> Failed {name}: {e}")
    else:
        print(f" -> {name} exists.")

print("Done.")