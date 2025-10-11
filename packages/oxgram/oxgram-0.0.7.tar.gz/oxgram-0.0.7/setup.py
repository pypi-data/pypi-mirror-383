from setuptools import find_packages
from setuptools import setup
from Oxgram import appname
from Oxgram import version
from Oxgram import install
from Oxgram import caption
from Oxgram import pythons
from Oxgram import clinton
from Oxgram import profile
from Oxgram import mention
from Oxgram import DATA01
from Oxgram import DATA02

with open("README.md", "r") as o:
    description = o.read()
    
setup(
    url=profile,
    name=appname,
    author=clinton,
    version=version,
    keywords=mention,
    classifiers=DATA02,
    author_email=DATA01,
    description=caption,
    python_requires=pythons,
    packages=find_packages(),
    install_requires=install,
    long_description=description,
    long_description_content_type="text/markdown")
