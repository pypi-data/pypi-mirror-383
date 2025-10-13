from manim import Text
from .fonts import get_persian_font
from .translit import translit_to_fa
from .layout import fix_rtl_text

class FaText(Text):
    """Persian text support for Manim."""

    def __init__(
        self,
        content,
        font=None,
        font_size=48,
        color="WHITE",
        weight=None,
        slant=None,
        translit=False,
        rtl=True,
        auto_line_break=True,
        line_spacing=0.4,
        **kwargs,
    ):
        if translit:
            content = translit_to_fa(content)
        if rtl:
            content = fix_rtl_text(content, auto_line_break, line_spacing)
        font = get_persian_font(font)
        super().__init__(content, font=font, font_size=font_size, color=color, **kwargs)
        if weight:
            self.set_weight(weight)
        if slant:
            self.set_slant(slant)
