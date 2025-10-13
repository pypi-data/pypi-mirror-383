from setuptools import setup, find_packages

setup(
    name="manim-fa",
    version="0.3.4",
    packages=find_packages(),
    install_requires=[
        "manim>=0.17.0",
        "arabic-reshaper",
        "python-bidi",
    ],
    author="علی تابش",
    author_email="tabesh_ali@yahoo.com",
    description="افزونه‌ی مانیم برای نمایش دادن متن فارسی (راست به چپ) با قابلیت خودکار آوانگاری از فنگلش به فارسی",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Tabesh2020/manim-fa",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
