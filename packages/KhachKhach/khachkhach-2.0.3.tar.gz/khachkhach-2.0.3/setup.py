from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="KhachKhach",             # package name on PyPI
    version="2.0.3",               # bump this every release
    packages=find_packages(),      # will auto-detect 'khachkhach' package
    include_package_data=True,
    install_requires=[
    "opencv-python>=4.5.0",
    "numpy>=1.20.0",
    "pillow>=8.0.0",
    "ultralytics>=8.0.0",
    "pathlib2>=2.3.0"
],
    author="pratapdevs11",
    author_email="divyapratap360@gmail.com",
    description="A package for processing video frames, annotating keypoints, and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pratapsdev11/Khach_Khach",
    project_urls={
        "Source": "https://github.com/pratapsdev11/Khach_Khach",
        "Tracker": "https://github.com/pratapsdev11/Khach_Khach/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.6",
)
