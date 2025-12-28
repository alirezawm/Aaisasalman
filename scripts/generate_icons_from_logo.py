from PIL import Image, ImageOps
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_CANDIDATES = [
    os.path.join(PROJECT_ROOT, 'static', 'images', 'logo.png'),
    os.path.join(PROJECT_ROOT, 'static', 'images', 'photo_5460656944265162587_w.jpg'),
    os.path.join(PROJECT_ROOT, 'assets', 'images', 'splash_launch.jpg'),
]
RES_ROOT = os.path.join(PROJECT_ROOT, 'AsiaSalmanApp', 'android', 'app', 'src', 'main', 'res')
MIPMAP_DIRS = {
    'mdpi': (48, 48),
    'hdpi': (72, 72),
    'xhdpi': (96, 96),
    'xxhdpi': (144, 144),
    'xxxhdpi': (192, 192),
}

# choose source
src = None
for p in SRC_CANDIDATES:
    if os.path.isfile(p):
        src = p
        break
if src is None:
    raise FileNotFoundError('No logo source found; checked: ' + ','.join(SRC_CANDIDATES))

print('Using logo source:', src)
logo = Image.open(src).convert('RGBA')
# Use the logo image without cropping or recoloring. We only scale it down proportionally
# to fit the target sizes (contain), and keep a transparent background so the logo pixels
# remain unchanged in color and shape.

for density, size in MIPMAP_DIRS.items():
    out_dir = os.path.join(RES_ROOT, f'mipmap-{density}')
    os.makedirs(out_dir, exist_ok=True)
    # create foreground: transparent background with resized logo centered (no cropping)
    fg = Image.new('RGBA', size, (0,0,0,0))
    logo_resized = ImageOps.contain(logo, size, Image.LANCZOS)
    offset = ((size[0]-logo_resized.size[0])//2, (size[1]-logo_resized.size[1])//2)
    fg.paste(logo_resized, offset, logo_resized)
    fg_path = os.path.join(out_dir, 'ic_launcher_foreground.png')
    fg.save(fg_path)
    print('Saved foreground (unchanged logo)', fg_path)

    # create ic_launcher (legacy) using transparent background so no color is added
    root = Image.new('RGBA', size, (0,0,0,0))
    root.paste(logo_resized, offset, logo_resized)
    root_path = os.path.join(out_dir, 'ic_launcher.png')
    root.save(root_path)
    print('Saved launcher (transparent background)', root_path)

# also write mipmap-anydpi-v26 xml if missing
xml_dir = os.path.join(RES_ROOT, 'mipmap-anydpi-v26')
os.makedirs(xml_dir, exist_ok=True)
icon_xml = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
'''
with open(os.path.join(xml_dir, 'ic_launcher.xml'), 'w', encoding='utf-8') as f:
    f.write(icon_xml)
with open(os.path.join(xml_dir, 'ic_launcher_round.xml'), 'w', encoding='utf-8') as f:
    f.write(icon_xml)
print('Wrote adaptive xml files')

# update values/colors.xml background color
values_dir = os.path.join(RES_ROOT, 'values')
os.makedirs(values_dir, exist_ok=True)
colors_xml_path = os.path.join(values_dir, 'colors.xml')
# set ic_launcher_background to transparent so the logo is not altered
colors_xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">#00000000</color>
</resources>
'''
with open(colors_xml_path, 'w', encoding='utf-8') as f:
    f.write(colors_xml_content)
print('Set ic_launcher_background to transparent')

print('Icon generation complete')
