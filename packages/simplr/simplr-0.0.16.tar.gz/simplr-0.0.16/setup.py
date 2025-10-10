from setuptools import find_packages, setup
import os

path: str = "requirements.txt"
install_requires = []
if os.path.isfile(path):
    with open(path, "r") as file:
        install_requires = file.read().splitlines()

setup(
    name="simplr",
    version="0.0.16",
    author="Noah Lisin",
    author_email="noah.g.lisin@vanderbilt.edu",
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "simplr = simplr.simplr:main",
        ],
    },
    description="Run OS independent commands using natural language.",
    long_description="""
        Run OS independent commands using natural language.
        See https://github.com/noahl25/simplr for more information.
    """,
    url="https://github.com/noahl25/simplr",
    install_requires=install_requires,
)