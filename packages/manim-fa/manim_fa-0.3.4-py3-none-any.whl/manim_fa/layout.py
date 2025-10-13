from manim import VGroup, RIGHT, LEFT, DOWN
import arabic_reshaper
from bidi.algorithm import get_display

def fix_rtl_text(text, auto_line_break=True, line_spacing=0.4):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)
def arrange_rtl(text_group: VGroup, spacing=0.3):
    text_group.submobjects = list(reversed(text_group.submobjects))
    text_group.arrange(RIGHT, buff=spacing)
    return text_group

def justify_rtl_lines(lines: list, line_spacing=0.4):
    group = VGroup(*lines)
    group.arrange(LEFT, buff=line_spacing)
    return group