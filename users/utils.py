import io
import random

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import AVATAR_COLORS, AVATAR_FONT_SIZE, AVATAR_SIZE, FONT_PATHS


def generate_avatar(letter: str) -> ContentFile:
    bg_color = random.choice(AVATAR_COLORS)
    img = Image.new("RGB", AVATAR_SIZE, bg_color)
    draw = ImageDraw.Draw(img)

    font = None
    for path in FONT_PATHS:
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


def paginate(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
