from manim import Text, VGroup
from .fonts import get_persian_font
from .translit import translit_to_fa
from .layout import arrange_rtl
import re

# ===== FaText با RichText =====
def _parse_rich_text(content: str):
    pattern = re.compile(
        r"<(?P<tag>b|i|color|font|size)(?:=(?P<value>[^>]+))?>(?P<inner>.*?)</\1>", re.IGNORECASE
    )
    segments = []
    pos = 0
    for match in pattern.finditer(content):
        start, end = match.span()
        if start > pos:
            segments.append({"text": content[pos:start], "attrs": {}})
        tag = match.group("tag").lower()
        value = match.group("value")
        inner = match.group("inner")
        attrs = {}
        if tag == "b":
            attrs["weight"] = "BOLD"
        elif tag == "i":
            attrs["slant"] = "ITALIC"
        elif tag == "color":
            attrs["color"] = value
        elif tag == "font":
            attrs["font"] = value
        elif tag == "size":
            try:
                attrs["font_size"] = float(value)
            except ValueError:
                pass
        segments.append({"text": inner, "attrs": attrs})
        pos = end
    if pos < len(content):
        segments.append({"text": content[pos:], "attrs": {}})
    return segments

def FaText(
    content,
    font=None,
    font_size=48,
    color="WHITE",
    weight=None,
    slant=None,
    translit=False,
    rtl=True,
    rich=False,
    **kwargs,
):
    if translit:
        content = translit_to_fa(content)
    font = get_persian_font(font)
    if not rich:
        text = Text(content, font=font, font_size=font_size, color=color, **kwargs)
        if weight:
            text.set_weight(weight)
        if slant:
            text.set_slant(slant)
        if rtl:
            text.submobjects.reverse()
        return text

    segments = _parse_rich_text(content)
    group = VGroup()
    for seg in segments:
        seg_text = seg["text"].strip()
        if not seg_text:
            continue
        attrs = seg["attrs"]
        seg_font = get_persian_font(attrs.get("font", font))
        seg_obj = Text(
            seg_text,
            font=seg_font,
            font_size=attrs.get("font_size", font_size),
            color=attrs.get("color", color),
            **kwargs,
        )
        if "weight" in attrs:
            seg_obj.set_weight(attrs["weight"])
        if "slant" in attrs:
            seg_obj.set_slant(attrs["slant"])
        group.add(seg_obj)
    group.arrange(direction="RIGHT", buff=0.15)
    if rtl:
        group.submobjects.reverse()
    return group

# ===== FaParagraph =====
class FaParagraph(VGroup):
    def __init__(
        self,
        text: str,
        max_width: float = 10,
        font=None,
        font_size=48,
        color="WHITE",
        translit=False,
        rtl=True,
        rich=False,
        line_spacing=0.5,
        **kwargs,
    ):
        super().__init__()
        self.lines = []

        if translit:
            text = translit_to_fa(text)

        font = get_persian_font(font)
        words = text.split()
        current_line = ""
        for word in words:
            test_line = (current_line + " " + word).strip() if current_line else word
            test_obj = FaText(test_line, font=font, font_size=font_size, color=color, rtl=rtl, rich=rich, **kwargs)
            if test_obj.width > max_width:
                if current_line:
                    line_obj = FaText(current_line, font=font, font_size=font_size, color=color, rtl=rtl, rich=rich, **kwargs)
                    self.add(line_obj)
                    self.lines.append(line_obj)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            line_obj = FaText(current_line, font=font, font_size=font_size, color=color, rtl=rtl, rich=rich, **kwargs)
            self.add(line_obj)
            self.lines.append(line_obj)

        self.arrange(direction="DOWN", buff=line_spacing)
