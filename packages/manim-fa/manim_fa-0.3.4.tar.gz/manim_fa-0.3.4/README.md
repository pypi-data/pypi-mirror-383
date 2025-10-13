# manim-fa (v0.3.0)

افزونه‌ی مانیم برای نمایش دادن متن فارسی (از راست به چپ) با قابلیت خودکار آوانگاری از فنگلش به فارسی.


## نحوه نصب پلاگین

```bash
pip install manim-fa
```

## نحوه استفاده از این پلاگین
```python
from manim import Scene
from manim_fa import FaText

class Test(Scene):
    def construct(self):
        # ایجاد متن مستقیم فارسی
        t1 = FaText("سلام برشما کاربر گرامی!", color="BLUE", font_size=70)
        
        # قابلیت آوا نگاری از فنگلش به فارسی
        t2 = FaText("Salam bar shoma karbre manim farsi", translit=True, color="GREEN", font_size=70)
        
        self.play(Write(t1))
        self.play(Transform(t1, t2))
        self.wait(2)
```

## تراز بندی متن از راست به چپ
برای ایجاد متن‌های بلند :

```python
from manim_fa.layout import arrange_rtl
text_group = VGroup(line1, line2, line3)
arrange_rtl(text_group)
```