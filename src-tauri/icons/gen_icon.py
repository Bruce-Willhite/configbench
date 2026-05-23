from PIL import Image, ImageDraw, ImageFont
import math, os

SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# ── Colors ──
BG          = (28, 28, 36, 255)
STEEL_DARK  = (50, 53, 63, 255)
STEEL_MID   = (72, 76, 90, 255)
STEEL_LIGHT = (105, 110, 128, 255)
BLUE_FACE   = (45, 108, 210, 255)
BLUE_HI     = (75, 145, 245, 255)
WOOD        = (145, 88, 35, 255)
WOOD_DARK   = (100, 60, 20, 255)
WHITE       = (240, 245, 255, 255)

# ── Background circle ──
draw.ellipse([16, 16, SIZE-16, SIZE-16], fill=BG)

# ── Anvil geometry ──
# Base
BX1, BX2   = 78,  420
BY1, BY2   = 358, 415
draw.rectangle([BX1, BY1, BX2, BY2], fill=STEEL_DARK)
draw.rectangle([BX1, BY1, BX2, BY1+6], fill=STEEL_LIGHT)  # top edge

# Body (trapezoid connecting base to face)
body_pts = [(110, BY1), (390, BY1), (360, 260), (152, 260)]
draw.polygon(body_pts, fill=STEEL_MID)

# Side shading on body
draw.polygon([(390, BY1), (360, 260), (390, 260)], fill=STEEL_DARK)

# Horn (left, tapered)
horn_pts = [(152, 205), (152, 258), (38, 235)]
draw.polygon(horn_pts, fill=STEEL_MID)
draw.line([(152, 205), (38, 235)], fill=STEEL_LIGHT, width=3)

# Face / working surface (blue)
FX1, FX2 = 130, 390
FY1, FY2 = 200, 262
draw.rectangle([FX1, FY1, FX2, FY2], fill=BLUE_FACE)
# Highlight top edge
draw.rectangle([FX1, FY1, FX2, FY1+5], fill=BLUE_HI)
# Shadow bottom edge
draw.rectangle([FX1, FY2-4, FX2, FY2], fill=(30, 70, 140, 255))

# ── Text on face ──
face_cx = (FX1 + FX2) // 2
face_cy = (FY1 + FY2) // 2

font = None
for path in [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
]:
    if os.path.exists(path):
        font = ImageFont.truetype(path, 46)
        break
if font is None:
    font = ImageFont.load_default()

text = "CB"
bb = draw.textbbox((0, 0), text, font=font)
tw, th = bb[2] - bb[0], bb[3] - bb[1]
draw.text((face_cx - tw//2 - bb[0], face_cy - th//2 - bb[1]), text, fill=WHITE, font=font)

# ── Hammer (top-right, rotated ~-40°) ──
hammer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
hd = ImageDraw.Draw(hammer)

# Pivot point (where hammer rotates around)
px, py = 380, 80

# Handle
HX1, HX2 = px - 10, px + 10
HY1, HY2 = py + 10, py + 160
hd.rectangle([HX1, HY1, HX2, HY2], fill=WOOD)
hd.rectangle([HX1, HY1, HX2, HY1+12], fill=WOOD_DARK)   # shadow under head
# Wood grain lines
for g in range(HY1+16, HY2-10, 12):
    hd.line([(HX1+2, g), (HX2-2, g+4)], fill=WOOD_DARK, width=1)

# Head
HHW, HHH = 76, 50
HHX1 = px - HHW // 2
HHY1 = py - HHH + 12
HHX2 = HHX1 + HHW
HHY2 = HHY1 + HHH
hd.rectangle([HHX1, HHY1, HHX2, HHY2], fill=STEEL_MID)
# Faces / edges
hd.rectangle([HHX1, HHY1, HHX2, HHY1+6], fill=STEEL_LIGHT)   # top highlight
hd.rectangle([HHX1, HHY2-5, HHX2, HHY2], fill=STEEL_DARK)    # bottom shadow
hd.rectangle([HHX1, HHY1, HHX1+5, HHY2], fill=STEEL_LIGHT)   # left face
hd.rectangle([HHX2-5, HHY1, HHX2, HHY2], fill=STEEL_DARK)    # right shadow

# Rotate around pivot
hammer = hammer.rotate(40, center=(px, py), expand=False, resample=Image.BICUBIC)

img = Image.alpha_composite(img, hammer)

out = r"C:\Users\Bruce\Desktop\Projects\ConfigBench\src-tauri\icons\icon_source.png"
img.save(out)
print("Saved", out)
img.save(r"C:\Users\Bruce\Desktop\Projects\ConfigBench\src-tauri\icons\preview.png")
