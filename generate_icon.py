#!/usr/bin/env python3
"""Generate Svara app icons from the user's actual स्वर icon."""
from PIL import Image
import os, io, base64

# Embedded 128x128 palette PNG of the user's स्वर icon
ICON_B64 = (
    "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"
)

# Decode and load source icon
source = Image.open(io.BytesIO(base64.b64decode(ICON_B64)))
# Convert palette back to RGBA for resizing
source = source.convert('RGBA')
print(f"Source icon loaded: {source.size}")

# Generate all Android density variants
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

# Generate launcher icons
for folder, size in densities.items():
    d = f'app/src/main/res/{folder}'
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, 'ic_launcher.png'))
    r.save(os.path.join(d, 'ic_launcher_round.png'))
    print(f"Generated {folder}/ic_launcher.png ({size}x{size})")

# Generate foreground icons (adaptive)
for folder, size in adaptive.items():
    d = f'app/src/main/res/{folder}'
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, 'ic_launcher_foreground.png'))
    print(f"Generated {folder}/ic_launcher_foreground.png ({size}x{size})")

# Generate debug variant icons
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

print("All icon densities generated from user's स्वर icon")
