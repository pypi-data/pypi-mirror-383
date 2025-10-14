
from setuptools import setup
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        subprocess.check_call([self.distribution.get_command_obj('build').executable,
                               "post_install.py"])

with open("README.md", "r") as f:
    description = f.read()

setup(
    name = "docin",
	version = "0.1.2",
	description = "A Python package for performing OCR and document indexing on legacy documents using the Mistral Ocr API.",
	author = ["Ime Inyang"],
	author_email = "alfiinyang@gmail.com",
	packages = ["ocr", "ocr.query"],
    install_requires = ["mistralai","datauri","langchain-core","spacy","IPython"],
    long_description=description,
    long_description_content_type="text/markdown",
    cmdclass={
        'install': PostInstallCommand,
    }
)