import setuptools
from pathlib import Path

long_desc = Path("Readme.md").read_text()
setuptools.setup(
    name="holamundoplayer-moki01",
    version="0.0.1",
    long_description=long_desc,
    long_description_content_type="text/markdown",  # 🔹 agrega esto
    packages=setuptools.find_packages(
        exclude=["mocks", "tests"]
    )
)