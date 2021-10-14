import setuptools
import subprocess
import shutil
import configparser

with open("README.md", "r", encoding="utf-8") as fh: long_description = fh.read()
subprocess.call(["pipreqs", ".", "--force"])

cfg = configparser.ConfigParser()
cfg.read("setup.cfg")

dct = {}
for s in cfg.sections():
    for k,v in cfg[s].items():
        dct[k] = v

dct["long_description"] = long_description
dct["long_description_content_type"] = "text/markdown"
dct["package_dir"] = {"": "src"}
dct["packages"] = setuptools.find_packages(where="src")
dct["install_requires"] = open("requirements.txt", "r").readlines()

setuptools.setup(**dct)
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("src/dfana.egg-info", ignore_errors=True)