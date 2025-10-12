from setuptools import setup, find_packages

setup(
    name="DIYA_Voice",
    version="0.15.0",
    author="DIYA Robotics",
    author_email="learn@diyaedulabs.com",
    description="Offline Voice-Controlled LED and Robotics GUI for ESP32 using Vosk.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/DIYA_Voice",
    packages=find_packages(),
    install_requires=[
        "vosk==0.3.45",
        "sounddevice>=0.5.2",
        "numpy>=1.20.0",
        "tqdm>=4.60.0",
        "requests>=2.25.0",
        "pyserial>=3.5"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)
