import io
import random
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from team_finder.constants import AVATAR_SIZE, AVATAR_FONT_SIZE, AVATAR_COLORS


def generate_avatar(letter: str) -> ContentFile:
    bg_color = random.choice(AVATAR_COLORS)
    img = Image.new("RGB", AVATAR_SIZE, bg_color)
    draw = ImageDraw.Draw(img)

    font = None
    font_paths = [
        # Windows
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        # Mac
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]

    for path in font_paths:
        try:
            font = ImageFont.truetype(path, AVATAR_FONT_SIZE)
            break
        except OSError:
            continue

    if font is None:
        font = ImageFont.load_default()

    bbox = font.getbbox(letter)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (AVATAR_SIZE[0] - text_w) / 2
    y = (AVATAR_SIZE[1] - text_h) / 2 - 5
    draw.text((x, y), letter, fill="white", font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name=f"avatar_{letter}.png")