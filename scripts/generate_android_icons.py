from PIL import Image, ImageOps
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_CANDIDATES = [
    os.path.join(PROJECT_ROOT, 'static', 'images', 'photo_5460656944265162587_w.jpg'),
    os.path.join(PROJECT_ROOT, 'static', 'images', 'logo.png'),
    os.path.join(PROJECT_ROOT, 'assets', 'icons', 'store.svg')
]

# Android res directories
RES_ROOT = os.path.join(PROJECT_ROOT, 'AsiaSalmanApp', 'android', 'app', 'src', 'main', 'res')
MIPMAP_DIRS = {
    'mdpi': (48, 48),
    'hdpi': (72, 72),
    'xhdpi': (96, 96),
    'xxhdpi': (144, 144),
    'xxxhdpi': (192, 192),
}

# find source image
src = None
for p in SRC_CANDIDATES:
    if os.path.isfile(p):
        src = p
        break
if src is None:
    raise FileNotFoundError('No source image found for icon generation. Checked: ' + ','.join(SRC_CANDIDATES))

print('Using source image:', src)
img = Image.open(src).convert('RGBA')
# center-crop to square
w, h = img.size
min_edge = min(w, h)
img = ImageOps.fit(img, (min_edge, min_edge), method=Image.LANCZOS, centering=(0.5, 0.5))

# create mipmap ic_launcher and ic_launcher_foreground
for density, size in MIPMAP_DIRS.items():
    out_dir = os.path.join(RES_ROOT, f'mipmap-{density}')
    os.makedirs(out_dir, exist_ok=True)
    # ic_launcher (flatten on background color)
    out_icon = Image.new('RGBA', size, (237,228,217,255))  # earthySand #EDE4D9
    fg = img.resize(size, Image.LANCZOS)
    out_icon.paste(fg, (0, 0), fg)
    out_icon_path = os.path.join(out_dir, 'ic_launcher.png')
    out_icon.save(out_icon_path)
    print('Saved', out_icon_path)
    # ic_launcher_foreground (transparent background)
    fg_path = os.path.join(out_dir, 'ic_launcher_foreground.png')
    fg.save(fg_path)
    print('Saved', fg_path)

# create mipmap-anydpi-v26/ic_launcher.xml and ic_launcher_round.xml
xml_dir = os.path.join(RES_ROOT, 'mipmap-anydpi-v26')
os.makedirs(xml_dir, exist_ok=True)
icon_xml = '''<?xml version=\"1.0\" encoding=\"utf-8\"?>
<adaptive-icon xmlns:android=\"http://schemas.android.com/apk/res/android\"> 
    <background android:drawable=\"@color/ic_launcher_background\"/> 
    <foreground android:drawable=\"@mipmap/ic_launcher_foreground\"/> 
</adaptive-icon>
'''
with open(os.path.join(xml_dir, 'ic_launcher.xml'), 'w', encoding='utf-8') as f:
    f.write(icon_xml)
with open(os.path.join(xml_dir, 'ic_launcher_round.xml'), 'w', encoding='utf-8') as f:
    f.write(icon_xml)
print('Wrote adaptive icon xml files')

# create values/colors.xml with a background color
values_dir = os.path.join(RES_ROOT, 'values')
os.makedirs(values_dir, exist_ok=True)
colors_xml_path = os.path.join(values_dir, 'colors.xml')
colors_xml_content = '''<?xml version=\"1.0\" encoding=\"utf-8\"?>
<resources>
    <color name=\"ic_launcher_background\">#EDE4D9</color>
</resources>
'''
if not os.path.exists(colors_xml_path):
    with open(colors_xml_path, 'w', encoding='utf-8') as f:
        f.write(colors_xml_content)
    print('Created', colors_xml_path)
else:
    print('colors.xml already exists, skipping creation')

# create drawable-nodpi/launch_image.png (2048x2048 letterboxed)
drawable_dir = os.path.join(RES_ROOT, 'drawable-nodpi')
os.makedirs(drawable_dir, exist_ok=True)
max_size = (2048, 2048)
launch_img = Image.new('RGBA', max_size, (255,255,255,255))
# fit image inside max_size preserving aspect
img_fit = ImageOps.contain(Image.open(src).convert('RGBA'), max_size, Image.LANCZOS)
# center
offset = ((max_size[0] - img_fit.size[0]) // 2, (max_size[1] - img_fit.size[1]) // 2)
launch_img.paste(img_fit, offset, img_fit)
launch_path = os.path.join(drawable_dir, 'launch_image.png')
launch_img.save(launch_path)
print('Saved launch image', launch_path)

# modify launch_background.xml to reference @drawable/launch_image
launch_bg_path = os.path.join(RES_ROOT, 'drawable', 'launch_background.xml')
if os.path.exists(launch_bg_path):
    content = '''<?xml version=\"1.0\" encoding=\"utf-8\"?>
<layer-list xmlns:android=\"http://schemas.android.com/apk/res/android\"> 
    <item android:drawable=\"@android:color/white\" /> 
    <item>
        <bitmap
            android:gravity=\"center\"
            android:src=\"@drawable/launch_image\" />
    </item>
</layer-list>
'''
    with open(launch_bg_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated', launch_bg_path)
else:
    print('launch_background.xml not found -- expected at', launch_bg_path)

print('Icon & splash generation complete')
