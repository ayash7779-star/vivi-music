#!/usr/bin/env python3
"""Generate the Svara app icon: dark rounded square with waveform bars."""
from PIL import Image, ImageDraw, ImageFont
import os, math

SIZE = 512
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw rounded square background
RADIUS = 120
BG_TOP = (45, 35, 80)
BG_BOT = (20, 20, 40)

# Create gradient background
for y in range(SIZE):
    t = y / SIZE
    r = int(BG_TOP[0] * (1-t) + BG_BOT[0] * t)
    g = int(BG_TOP[1] * (1-t) + BG_BOT[1] * t)
    b = int(BG_TOP[2] * (1-t) + BG_BOT[2] * t)
    draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))

# Mask to rounded rectangle
mask = Image.new('L', (SIZE, SIZE), 0)
mdraw = ImageDraw.Draw(mask)
mdraw.rounded_rectangle([20, 20, SIZE-20, SIZE-20], radius=RADIUS, fill=255)
result = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
result.paste(img, (0, 0), mask)
img = result
draw = ImageDraw.Draw(img)

# Draw audio waveform bars
wave_y_base = SIZE - 130
num_bars = 22
bar_width = 7
gap = 9
total_width = num_bars * (bar_width + gap)
start_x = (SIZE - total_width) // 2

for i in range(num_bars):
    x = start_x + i * (bar_width + gap)
    center = num_bars / 2
    dist = abs(i - center) / center
    height = int(25 + 60 * abs(math.sin(i * 0.6 + 0.5)) * (1 - dist * 0.3))
    height = max(15, min(85, height))
    y_top = wave_y_base - height
    y_bottom = wave_y_base + 8
    t = i / num_bars
    r = int(120 + 100 * t)
    g = int(90 + 100 * (1 - t))
    b = int(200 + 55 * min(1, t * 1.5))
    draw.rounded_rectangle([x, y_top, x + bar_width, y_bottom], radius=3, fill=(r, g, b, 230))

# Try to find a Devanagari font for स्वर
font = None
font_paths = [
    '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf',
    '/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansDevanagari-Regular.otf',
    '/usr/share/fonts/noto/NotoSansDevanagari-Regular.ttf',
]
for fp in font_paths:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 160)
        break

if font is None:
    import subprocess
    result = subprocess.run(['fc-list', ':lang=hi'], capture_output=True, text=True)
    for line in result.stdout.strip().split('\n'):
        path = line.split(':')[0].strip()
        if os.path.exists(path):
            font = ImageFont.truetype(path, 160)
            break

if font is None:
    print("WARNING: No Devanagari font found")
    font = ImageFont.load_default()
else:
    print(f"Using font: {font.path}")

# Draw स्वर text centered in upper portion
text = "\u0938\u094d\u0935\u0930"
bbox = draw.textbbox((0, 0), text, font=font)
text_w = bbox[2] - bbox[0]
text_h = bbox[3] - bbox[1]
text_x = (SIZE - text_w) // 2 - bbox[0]
text_y = 90 - bbox[1]
draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

# Save 512x512 master
img.save('svara_icon_512.png')
print(f"Icon saved: {img.size}")

# Generate all Android density variants
densities = {'mipmap-mdpi': 48, 'mipmap-hdpi': 72, 'mipmap-xhdpi': 96, 'mipmap-xxhdpi': 144, 'mipmap-xxxhdpi': 192}
adaptive = {'mipmap-mdpi': 108, 'mipmap-hdpi': 162, 'mipmap-xhdpi': 216, 'mipmap-xxhdpi': 324, 'mipmap-xxxhdpi': 432}

for folder, size in densities.items():
    d = f'app/src/main/res/{folder}'
    os.makedirs(d, exist_ok=True)
    r = img.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, 'ic_launcher.png'))
    r.save(os.path.join(d, 'ic_launcher_round.png'))

for folder, size in adaptive.items():
    d = f'app/src/main/res/{folder}'
    os.makedirs(d, exist_ok=True)
    r = img.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, 'ic_launcher_foreground.png'))

for folder, size in densities.items():
    d = f'app/src/debug/res/{folder}'
    os.makedirs(d, exist_ok=True)
    r = img.resize((size, size), Image.LANCZOS)
    r.save(os.path.join(d, 'ic_launcher.png'))
    r.save(os.path.join(d, 'ic_launcher_round.png'))

print("All icon densities generated")
