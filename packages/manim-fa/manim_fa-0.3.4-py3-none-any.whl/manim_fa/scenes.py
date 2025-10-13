from manim import Scene, VGroup, DOWN, UP, FadeIn, Write, ScaleInPlace, PI
from .fa_text import FaText

class FaTextScene(Scene):
    def construct(self):
        line1 = FaText("افزونه مانیم برای نمایش دادن درست متن فارسی", color="BLUE", font_size=70)
        line2 = FaText("از راست به چپ و تبدیل فنگلش به فارسی", translit=True, color="GREEN", font_size=70)
        line3 = FaText("با قابلیت ویرایش کلاسیک متن :اتالیک، بولد...", color="RED", font_size=70, slant="ITALIC")

        text_group = VGroup(line1, line2, line3).arrange(DOWN).shift(UP)
        self.play(FadeIn(text_group))
        self.wait(2)