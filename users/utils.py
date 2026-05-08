import io
import random
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from team_finder.constants import AVATAR_SIZE, AVATAR_FONT_SIZE, AVATAR_COLORS


def generate_avatar(letter: str) -> ContentFile:
    bg_color = random.choice(AVATAR_COLORS)

    img = Image.new("RGB", AVATAR_SIZE, bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", AVATAR_FONT_SIZE)
    except OSError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", AVATAR_FONT_SIZE)
        except OSError:
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