from setuptools import setup, find_packages

setup(
    name="cybersightsh",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "prompt_toolkit",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "cybersightsh = cybersightsh.terminal:main"
        ]
    },
    author="Cybersight",
    description="A userguide custom terminal with colors, autocompletion, and basic shell commands.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="terminal shell custom cybersight cli",
    python_requires=">=3.8",
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
)