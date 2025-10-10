from setuptools import setup, find_packages

setup(
    name="gesture-blocks",
    version="0.6.0",
    description="Block-style gesture control for Arduino + Python (LEDs, Otto Robot, Wonders Explorer, Pose Finder, Sign Language Converter, and more)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    url="https://github.com/yourusername/gesture-blocks",
    packages=find_packages(),
    install_requires=[
        "opencv-python==4.8.1.78",
        "mediapipe==0.10.14",
        "pyserial==3.5"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7,<3.12',
)
