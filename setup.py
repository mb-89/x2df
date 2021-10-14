import setuptools
import subprocess
import shutil

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

subprocess.call(["pipreqs", ".", "--force"])

setuptools.setup(

    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=open("requirements.txt", "r").readlines()
)

shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("src/dfana.egg-info", ignore_errors=True)