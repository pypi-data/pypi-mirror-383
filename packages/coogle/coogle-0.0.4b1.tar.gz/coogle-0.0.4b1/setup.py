from setuptools import find_packages
from setuptools import setup
from Coogle import appname
from Coogle import version
from Coogle import install
from Coogle import clinton
from Coogle import pythons
from Coogle import mention
from Coogle import licence
from Coogle import sources
from Coogle import DATA01
from Coogle import DATA02
from Coogle import DATA03

with open("README.md", "r") as o:
    description = o.read()
    
setup(
    url=sources,
    name=appname,
    author=clinton,
    version=version,
    license=licence,
    keywords=mention,
    description=DATA03,
    classifiers=DATA02,
    author_email=DATA01,
    python_requires=pythons,
    packages=find_packages(),
    install_requires=install,
    long_description=description,
    long_description_content_type="text/markdown")
