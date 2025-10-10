import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

import os
version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.txt")
with open(version_file, "r") as fh:
    version = fh.read().strip()


setuptools.setup(
    name="mypygui-ng",                     # This is the name of the package
    version=version,                        # The initial release version
    author="Martin Alejandro Oviedo",       # Full name of the author
    author_email="martin@oviedo.com.ar",
    description="Modern GUIs for Python using HTML+CSS - A lightweight alternative to Electron",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    url="https://github.com/Dragon-KK/mypygui",
    project_urls={
        "Documentation": "https://dragon-kk.github.io/mypygui/",
        "Source": "https://github.com/Dragon-KK/mypygui",
        "Tracker": "https://github.com/Dragon-KK/mypygui/issues",
    },
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.10',                # Minimum version requirement of the package
    license="MIT",
    keywords=["gui", "html", "css", "tkinter", "web", "interface", "browser", "rendering", "mypygui", "electron-alternative"],
    install_requires=[
        "pillow >= 9.1.0",
        "tinycss2 >= 1.1.1",
        "webcolors >= 1.12",
        "colorama >= 0.4.4",
        "requests >= 2.28.1"
    ],                    # Install other dependencies if any
    extras_require={
        "demo": ["Pillow>=9.1.0"],  # For image processing in demos
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "flake8>=6.0.0"],
    },
    entry_points={
        "console_scripts": [
            "mypygui-demo = mypygui_ng.demo:run_demo",
        ],
    },
    package_data={
        "mypygui_ng": [
            "themes/*.css",
            "../examples/html/*.html",
        ],
    },
    include_package_data=True,
)