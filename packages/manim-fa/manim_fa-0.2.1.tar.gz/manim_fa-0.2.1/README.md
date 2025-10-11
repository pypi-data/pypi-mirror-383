# manim-fa

افزونه‌ی مانیم برای نمایش متن فارسی (راست به چپ) با قابلیت تبدیل خودکار از حروف لاتین به فارسی.

## نحوه نصب پلاگین

```bash
pip install manim-fa
```

## نحوه استفاده از این پلاگین

```python
from manim import *
from manim_fa import create_fa_text

class Demo(Scene):
    def construct(self):
        # ایجاد متن مستقیم فارسی
        t1 = create_fa_text(".سلام بر کاربر گرامی، این یک افزونه فارسی ساز در مانیم هست", color="BLUE", font_size=70)
        
        # قابلیت آوا نگاری از فنگلش به فارسی
        t2 = create_fa_text("Salam bar shoma karbare manim fa", translit=True, color="GREEN", font_size=70)
        
        self.play(Write(t1))
        self.play(Transform(t1, t2))
        self.wait(2)
```

## تراز بندی متن از راست به چپ
برای ایجاد متن بلند :

```python
from manim_fa.layout import arrange_rtl
text_group = VGroup(line1, line2, line3)
arrange_rtl(text_group)
```