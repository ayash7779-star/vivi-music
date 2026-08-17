#!/usr/bin/env python3
"""Generate Svara app icons from the user's actual ‡§∏‡•ç‡§µ‡§∞ icon."""
from PIL import Image
import os, io, base64

ICON_B64 = (
    "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"
    "xR4qWokk8zhz49j2IP/Z"
)

source = Image.open(io.BytesIO(base64.b64decode(ICON_B64)))
source = source.convert('RGBA')
print(f"Source icon loaded: {source.size}")

densities = {
    'mipmap-mdpi': 48,
    'mipmap-hdpi': 72,
    'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144,
    'mipmap-xxxhdpi': 192,
}

adaptive = {
    'mipmap-mdpi': 108,
    'mipmap-hdpi': 162,
    'mipmap-xhdpi': 216,
    'mipmap-xxhdpi': 324,
    'mipmap-xxxhdpi': 432,
}

for folder, size in densities.items():
    d = f'app/src/main/res/{folder}'
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, 'ic_launcher.png'))
    r.save(os.path.join(d, 'ic_launcher_round.png'))
    print(f"Generated {folder}/ic_launcher.png ({size}x{size})")

for folder, size in adaptive.items():
    d = f'app/src/main/res/{folder}'
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, 'ic_launcher_foreground.png'))
    print(f"Generated {folder}/ic_launcher_foreground.png ({size}x{size})")

for folder, size in densities.items():
    d = f'app/src/debug/res/{folder}'
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, 'ic_launcher.png'))
    r.save(os.path.join(d, 'ic_launcher_round.png'))

for folder, size in adaptive.items():
    d = f'app/src/debug/res/{folder}'
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, 'ic_launcher_foreground.png'))

print("All icon densities generated from user's ‡§∏‡•ç‡§µ‡§∞Å•çΩ∏à§(