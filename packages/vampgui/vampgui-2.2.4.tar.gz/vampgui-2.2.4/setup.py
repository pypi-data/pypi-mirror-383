import sys
from setuptools import setup, find_packages
from pathlib import Path
from vampgui.version import __version__


def check_tkinter():
    """Check if tkinter is available; show help if missing."""
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print("\n❌ tkinter is not installed. Please install it to use VAMPGUI.\n")
        print("For Debian-based systems:    sudo apt-get install python3-tk")
        print("For Red Hat-based systems:   sudo dnf install python3-tkinter")
        print("For Arch Linux:              sudo pacman -S tk\n")
        sys.exit(1)


# Run tkinter check
check_tkinter()

# Read README safely
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""


setup(
    name="vampgui",
    version=__version__,
    author="G. Benabdellah",
    author_email="ghlam.benabdellah@gmail.com",
    description="Graphical interface for VAMPIRE: Atomistic simulation of magnetic materials.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ghlam14/vampgui/tree/main",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "vampgui": ["background.png", "logo.png", "vam.ico"],
    },
    install_requires=[
        "matplotlib>=3.7.5",
        "numpy>=1.24.4",
        "Pillow>=10.0.0",
        "pymatgen>=2023.8.10",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "vampgui = vampgui.main:main",
        ],
    },
)
