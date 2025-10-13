"""
Setup script for Scriptum Simplex
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="scriptum_simplex",
    version="100.00",
    author="Scriptum Simplex Project",
    author_email="scriptum.simplex@example.com",
    description="Markdown editor with CriticMarkup support and Typora theme editor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://sourceforge.net/projects/scriptum-simplex/",
    project_urls={
        "Bug Tracker": "https://sourceforge.net/p/scriptum-simplex/tickets/",
        "Documentation": "https://sourceforge.net/p/scriptum-simplex/wiki/",
        "Source Code": "https://sourceforge.net/p/scriptum-simplex/code/",
    },
    packages=find_packages(exclude=["tests", "tests.*", "build", "dist"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Topic :: Text Editors",
        "Topic :: Office/Business",
        "Topic :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    keywords=[
        "markdown",
        "editor",
        "criticmarkup",
        "change-tracking",
        "typora",
        "themes",
        "css-editor",
        "document-editing",
        "collaborative-editing",
        "gui",
        "tkinter",
    ],
    python_requires=">=3.11",
    install_requires=[
        "ttkbootstrap>=1.10.1",
        "markdown>=3.4.0",
        "mistune>=3.0.0",
        "tinycss2>=1.2.1",
        "cssselect2>=0.7.0",
        "webencodings>=0.5.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "mypy>=1.5.0",
            "flake8>=6.1.0",
            "black>=23.7.0",
        ],
        "build": [
            "pyinstaller>=5.13.0",
            "wheel>=0.41.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "criticmarkup-editor=criticmarkup:main",
            "typora-theme-editor=theme_editor:main",
        ],
        "gui_scripts": [
            "criticmarkup-editor-gui=criticmarkup:main",
            "typora-theme-editor-gui=theme_editor:main",
        ],
    },
    package_data={
        "editor.theme_editor": [
            "samples/*.md",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
)
