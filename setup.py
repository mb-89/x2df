import setuptools
import shutil
import configparser

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    import pipreqs  # noqa: F401 #if we can import pipreqs, then the cmd utility exists
    import subprocess

    subprocess.call(["pipreqs", ".", "--force"])
except ModuleNotFoundError:
    pass

cfg = configparser.ConfigParser()
cfg.read("setup.cfg")

dct = {}
for s in cfg.sections():
    if s not in ["metadata", "options"]:
        continue
    for k, v in cfg[s].items():
        dct[k] = v

dct["long_description"] = long_description
dct["long_description_content_type"] = "text/markdown"
dct["package_dir"] = {"": "src"}
dct["packages"] = setuptools.find_packages(where="src")
dct["install_requires"] = open("requirements.txt", "r").readlines()

setuptools.setup(**dct)
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree(f"src/{dct['name']}.egg-info", ignore_errors=True)
