from setuptools import setup, find_packages

setup(
    name="vedantsh",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "prompt_toolkit",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "vedantsh = vedantsh.terminal:main"
        ]
    },
    author="Vedant Mahajan",
    description="A custom Python-based terminal with colors, autocompletion, and basic shell commands.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="terminal shell python custom cli",  # replace with your GitHub later
    python_requires=">=3.8",
)
