# Copyright (c) 2018 Stephen Bunn (stephen@bunn.io)
# MIT License <https://choosealicense.com/licenses/mit/>

import os
import sys
import codecs
import shutil

import setuptools

VERSION = "0.0.8"

INSTALL_REQUIRES = ["attrs", "jsonschema"]
SETUP_REQUIRES = []
EXTRAS_REQUIRE = {
    "toml": ["toml"],
    "pytoml": ["pytoml"],
    "tomlkit": ["tomlkit"],
    "ujson": ["ujson"],
    "pyyaml": ["pyyaml"],
    "msgpack": ["msgpack"],
}

all_extras = list(set().union(*[packages for packages in EXTRAS_REQUIRE.values()]))
EXTRAS_REQUIRE["docs"] = all_extras + ["sphinx"]
EXTRAS_REQUIRE["test"] = all_extras + [
    "flake8",
    "pytest",
    "pytest-flake8",
    "pytest-sugar",
    "pytest-xdist",
    "hypothesis",
]
EXTRAS_REQUIRE["dev"] = (
    EXTRAS_REQUIRE["docs"] + EXTRAS_REQUIRE["test"] + ["black", "isort"]
)


class UploadCommand(setuptools.Command):

    description = "Build and publish package"
    user_options = []

    @staticmethod
    def status(status):
        print("... {0}".format(status))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("removing previous builds")
            shutil.rmtree(
                os.path.join(os.path.abspath(os.path.dirname(__file__)), "dist")
            )
        except FileNotFoundError:
            pass

        self.status("building distribution")
        os.system("{0} setup.py sdist".format(sys.executable))

        self.status("uploading distribution")
        os.system("twine upload dist/*")

        self.status("pushing git tags")
        os.system("git tag v{0}".format(VERSION))
        os.system("git push --tags")

        sys.exit()


long_description = ""
with codecs.open("README.rst", encoding="utf-8") as fp:
    long_description = "\n" + fp.read()

setuptools.setup(
    name="file-config",
    version=VERSION,
    description="An attr's based configuration file abstraction",
    long_description=long_description,
    url="https://github.com/stephen-bunn/file-config",
    license="MIT License",
    author="Stephen Bunn",
    author_email="stephen@bunn.io",
    install_requires=INSTALL_REQUIRES,
    setup_requires=SETUP_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    include_package_data=True,
    packages=setuptools.find_packages(exclude=["tests.*", "tests"]),
    keywords=["config", "file", "toml", "json", "yaml", "msgpack", "pickle"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={"upload": UploadCommand},
)
