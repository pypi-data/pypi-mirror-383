import setuptools

from ptlibs._version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ptlibs",
    description="Support library for penterepTools",
    author="Penterep",
    author_email="info@penterep.com",
    url="https://www.penterep.com/",
    version=__version__,
    license="GPLv3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    entry_points = {'console_scripts': ['ptlibs = ptlibs.cli:main']},
    include_package_data= True,
    python_requires = '>=3.9',
    install_requires=["requests", "requests-toolbelt", "filelock", "idna", "appdirs"], # filelock, idna, appdirs for cachefile
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls = {
    "homepage":   "https://www.penterep.com/",
    "repository": "https://github.com/penterep/ptlibs",
    }
)
