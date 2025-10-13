from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="emberfall",
    version="0.1.0",
    author="Nullsec0x",
    author_email="contact@nullsec0x.dev",
    description="A magical roguelike game - Chronicles of Emberfall",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "textual>=0.1.18",
    ],
    entry_points={
        "console_scripts": [
            "emberfall=emberfall.main:main",
        ],
    },
    include_package_data=True,
    keywords="roguelike, game, terminal, textual, ascii",
    url="https://github.com/nullsec0x/terminus-veil-chronicles-of-emberfall",
    license="MIT",
)
