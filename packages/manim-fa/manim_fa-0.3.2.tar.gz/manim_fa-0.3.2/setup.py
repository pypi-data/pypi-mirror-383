from setuptools import setup, find_packages

setup(
    name="manim-fa",
    version="0.3.2",
    packages=find_packages(),
    install_requires=[
        "manim>=0.17.0",
        "arabic-reshaper",
        "python-bidi",
    ],
    entry_points={
        "console_scripts": [
            "manim-fa = manim_fa.cli:main"
        ],
    },
    author="علی تابش",
    author_email="tabesh_ali@yahoo.com",
    description="افزونه‌ی مانیم برای نمایش متن فارسی (راست به چپ) با RichText و تبدیل فینگلیش",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/<username>/manim-fa",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
