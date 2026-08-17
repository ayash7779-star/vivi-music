#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Svara app icons from the user's actual Svara icon (lossless PNG)."""
from PIL import Image
import os

source = Image.open("svara_icon.png")
source = source.convert("RGBA")
print(f"Source icon loaded: {source.size}")

densities = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

adaptive = {
    "mipmap-mdpi": 108,
    "mipmap-hdpi": 162,
    "mipmap-xhdpi": 216,
    "mipmap-xxhdpi": 324,
    "mipmap-xxxhdpi": 432,
}

for folder, size in densities.items():
    d = f"app/src/main/res/{folder}"
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, "ic_launcher.png"))
    r.save(os.path.join(d, "ic_launcher_round.png"))
    print(f"Generated {folder}/ic_launcher.png ({size}x{size})")

for folder, size in adaptive.items():
    d = f"app/src/main/res/{folder}"
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, "ic_launcher_foreground.png"))
    print(f"Generated {folder}/ic_launcher_foreground.png ({size}x{size})")

for folder, size in densities.items():
    d = f"app/src/debug/res/{folder}"
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, "ic_launcher.png"))
    r.save(os.path.join(d, "ic_launcher_round.png"))

for folder, size in adaptive.items():
    d = f"app/src/debug/res/{folder}"
    os.makedirs(d, exist_ok=True)
    r = source.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, "ic_launcher_foreground.png"))

print("All icon densities generated from user Svara icon (lossless)")
