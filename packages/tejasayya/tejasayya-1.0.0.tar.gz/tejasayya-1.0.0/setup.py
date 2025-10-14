from setuptools import setup, find_packages
from setuptools.command.install import install
import os

class PostInstallCommand(install):
    """Custom post-install command to print message right after pip install."""
    def run(self):
        install.run(self)
        os.system("python -m tejasayya")  # runs __main__.py after install

setup(
    name="tejasayya",
    version="1.0.0",
    packages=find_packages(include=["tejasayya", "tejasayya.*"]),
    entry_points={
        "console_scripts": [
            "tejasayya=tejasayya.__main__:main",  # ✅ creates the CLI command
        ],
    },
    cmdclass={
        "install": PostInstallCommand,
    },
    description="CLI package that introduces Teja Swaroop Sayya 🚀",
    author="Teja Swaroop Sayya",
    author_email="tejasayya@gmail.com",
    license="MIT",
    python_requires=">=3.7",
)
