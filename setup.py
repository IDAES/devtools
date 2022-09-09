from setuptools import setup, find_packages


setup(
    name="idaes-devtools",
    author="IDAES SW/RelEng team",

    package_dir={"": "src"},
    packages=find_packages(where="src"),

    license="LICENSE.md",

    version="22.9.8",
    install_requires=[
        "pytest>=7",
        "oyaml",
        "pydantic",
        "rich",
        "typer",
        "astroid==2.12.9",
    ],
    entry_points={
        "console_scripts": [
            "idaes-devtools = idaes_devtools.cli:app",
            "deprector = deprector.cli:app",
        ],
        "pytest11": [
            "deprector.collect = deprector.pytest_.plugins:collect",
        ],
        "deprector.callsites": [
            "idaes = deprector.support:idaes"
        ],
    }
)
