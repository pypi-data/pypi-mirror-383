# manim-fa

افزونه‌ی مانیم برای نمایش دادن متن فارسی (راست به چپ) با قابلیت تبدیل خودکار آوانگاری از فنگلش به فارسی.

## نحوه نصب پلاگین

```bash
pip install manim-fa
```

## استفاده از FaText (متن فارسی ساده یا RichText)
متن فارسی ساده

```python
from manim import *
from manim_fa import FaText

class Test(Scene):
    def construct(self):
        # ایجاد متن مستقیم فارسی
        t1 = FaText("سلام برشما کاربر گرامی!", color="BLUE", font_size=70)
        
        # قابلیت آوا نگاری از فنگلش به فارسی
        t2 = FaText("Slam br shma karbre manim farsi", translit=True, color="GREEN", font_size=70)
        
        self.play(Write(t1))
        self.play(Transform(t1, t2))
        self.wait(2)
```
## ویرایش کلاسیک متن : RichText (Bold, Italic, Color, Font, Size)

```python
from manim import *
from manim_fa import FaText

class Test(Scene):
    def construct(self):
        # ایجاد تغییرات بر متن فارسی
        t3 = FaText(
        "این یک <b>نمونه</b> از <color=green>متن رنگی</color> و <i>ایتالیک</i> است.",
        rich=True,
        font_size=60
        )
        self.play(Write(t1))
        self.play(Transform(t1, t2))
        self.wait(2)

```
```python
🔹 تگ‌های پشتیبانی‌شده: <b>, <i>, <color=color_name_or_hex>, <font=font_name>, <size=number>
        
```

##    🔹 استفاده از FaParagraph (متن طولانی چندخطی)


```python
from manim import *
from manim_fa import FaParagraph

class ParagraphDemo(Scene):
    def construct(self):
        text = (
            "این یک متن طولانی است که باید به صورت خودکار "
            "به چند خط تقسیم شود و همه خطوط راست‌چین نمایش داده شوند. "
            "همچنین می‌توان از تگ‌های <b>ضخیم</b> و <color=green>رنگی</color> استفاده کرد."
        )

        paragraph = FaParagraph(text, max_width=12, font_size=45, rich=True)
        self.play(Write(paragraph))
        self.wait(2)

```
        - max_width : بر حسب واحد مانیم عرض خط را مشخص می‌کند
        - line_spacing : فاصله بین خطوط را کنترل می‌کند
        - پشتیبانی از RichText و RTL همزمان فعال است


## 🔹 تراز متن و چینش خطوط

```python
from manim_fa.layout import arrange_rtl, justify_rtl_lines
text_group = VGroup(line1, line2, line3)
arrange_rtl(text_group)

```
## 🔹 ابزار خط فرمان (CLI)
افزودن واژه به فرهنگ‌نامه

```python
manim-fa add-word salam سلام

```
حذف واژه از فرهنگ‌نامه

```python
manim-fa remove-word salam

```

## تراز بندی متن از راست به چپ
برای ایجاد متن بلند :

```python
from manim_fa.layout import arrange_rtl
text_group = VGroup(line1, line2, line3)
arrange_rtl(text_group)

```

## 🔹 ویژگی‌های اصلی
- نمایش متن فارسی در مانیم به صورت راست‌چین و حرفه‌ای
- تبدیل فینگلیش به فارسی خودکار
- پشتیبانی از RichText (Bold, Italic, Color, Font, Size)
- شکستن خودکار متن بلند به چند خط (FaParagraph)
- قابلیت تراز و چینش RTL
- ابزار خط فرمان برای مدیریت فرهنگ‌نامه



