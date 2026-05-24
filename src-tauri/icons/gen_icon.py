from PIL import Image, ImageDraw

P = 8       # each pixel art "pixel" is 8x8 screen pixels
W = H = 512 # 64x64 art pixels

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# ── Palette ──
BG      = (20,  22,  30,  255)
SHADOW  = (28,  30,  40,  255)
DARK    = (46,  50,  62,  255)
MID     = (68,  73,  88,  255)
LIGHT   = (96,  104, 124, 255)
SHINE   = (138, 148, 170, 255)
WOOD    = (134, 84,  28,  255)
WOOD_D  = (88,  55,  16,  255)
STEEL   = (84,  90,  110, 255)
STEEL_L = (114, 122, 144, 255)

def R(ax, ay, aw, ah, c):
    d.rectangle([ax*P, ay*P, (ax+aw)*P, (ay+ah)*P], fill=c)

def T(pts, c):
    d.polygon([(x*P, y*P) for x,y in pts], fill=c)

# ── Background circle ──
d.ellipse([P, P, W-P, H-P], fill=BG)

# ════════════════════════════════
#  ANVIL  (side view, left-facing horn)
# ════════════════════════════════

# BASE  x=12..56  y=43..51
R(12, 43, 44, 8, MID)
R(12, 43, 44, 1, LIGHT)   # top highlight
R(12, 50, 44, 1, DARK)    # bottom shadow
R(12, 43,  1, 8, DARK)    # left edge
R(55, 43,  1, 8, SHADOW)  # right edge

# BODY  trapezoid connecting face-bottom to base-top
T([(18,28),(54,28),(56,43),(12,43)], MID)
T([(18,28),(12,43),(14,43),(20,28)], DARK)     # left slant
T([(54,28),(56,43),(54,43),(52,28)], SHADOW)   # right slant

# FACE (working surface)  x=18..54  y=20..28
R(18, 20, 36, 8, MID)
R(18, 20, 36, 1, SHINE)   # top shine row
R(18, 27, 36, 1, DARK)    # bottom shadow row
R(18, 20,  1, 8, DARK)    # left edge
R(53, 20,  1, 8, SHADOW)  # right edge

# STEP (raised block, right side of face)  x=47..56  y=14..28
R(47, 14,  9, 14, MID)
R(47, 14,  9,  1, SHINE)  # top
R(47, 14,  1, 14, LIGHT)  # left face (angled light)
R(55, 14,  1, 14, SHADOW) # right shadow
R(47, 26,  9,  2, DARK)   # bottom join shadow

# HORN  (left, triangle pointing left)
T([(5,28),(18,20),(18,35)], MID)
T([(5,28),(18,20),(18,22),(7,28)], LIGHT)   # top face brighter
T([(5,28),(18,33),(18,35)], DARK)            # bottom face darker

# ════════════════════════════════
#  HAMMER  (upper right, angled handle down-left)
# ════════════════════════════════

# Head — horizontal block at upper right, y=3..12  x=42..60
R(42,  3, 18, 9, STEEL)
R(42,  3, 18, 1, STEEL_L)  # top shine
R(42,  3,  1, 9, STEEL_L)  # left face
R(59,  3,  1, 9, SHADOW)   # right shadow
R(42, 11, 18, 1, DARK)     # bottom

# Handle — diagonal from under head (x≈51,y=12) going down-left to (x≈38,y=24)
T([(52,12),(54,12),(41,25),(39,25)], WOOD)
T([(53,12),(54,12),(41,25),(40,25)], WOOD_D)  # right-edge grain
# Grip end cap
R(38, 24, 4, 2, WOOD_D)

# ── "CB" label on working surface ──
# Hand-drawn pixel letters (3px wide, 5px tall each, total 8px wide for "CB")
# Each pixel = 1 art pixel = 8 screen pixels

def dot(ax, ay, c=SHINE):
    R(ax, ay, 1, 1, c)

# Letter "C"  (at art x=22, y=22 — 4 wide, 5 tall)
for dy in [0,1,2,3,4]:
    dot(22, 22+dy, SHINE)            # left column
for dx in [1,2,3]:
    dot(22+dx, 22,   SHINE)          # top
    dot(22+dx, 22+4, SHINE)          # bottom

# Letter "B"  (at art x=28, y=22 — 4 wide, 5 tall)
for dy in range(5):
    dot(28, 22+dy, SHINE)            # left column
for dx in [1,2]:
    dot(28+dx, 22,   SHINE)          # top
    dot(28+dx, 22+2, SHINE)          # mid
    dot(28+dx, 22+4, SHINE)          # bottom
dot(30, 22+1, SHINE)                 # top-right
dot(30, 22+3, SHINE)                 # bot-right

out = r"C:\Users\Bruce\Desktop\Projects\ConfigBench\src-tauri\icons\logo.png"
img.save(out)
print("Saved", out)
