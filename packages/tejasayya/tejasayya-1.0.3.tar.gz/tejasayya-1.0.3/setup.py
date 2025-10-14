from setuptools import setup, find_packages

setup(
    name="tejasayya",
    version="1.0.3",
    packages=find_packages(include=["tejasayya", "tejasayya.*"]),
    entry_points={
        "console_scripts": [
            "tejasayya=tejasayya.__main__:main",  # CLI command
        ],
    },
    description="CLI package that introduces Teja Swaroop Sayya 🚀",
    author="Teja Swaroop Sayya",
    author_email="tejasayya@gmail.com",
    license="MIT",
    python_requires=">=3.7",
)
