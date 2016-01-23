import os
import pypandoc
import tfatool._version
from setuptools import setup


version = tfatool._version.__version__
url = "https://github.com/TadLeonard/tfatool"
download = "{}/archive/{}.tar.gz".format(url, version)
long_description = pypandoc.convert('README.md', 'rst')


setup(name="tfatool",
      version=tfatool._version.__version__,
      scripts=["flashair-util", "flashair-config"],
      install_requires=["requests>=2.9.0", "tqdm>=3.7.1"],
      licence="MIT",
      packages=["tfatool"],
      description=("Tools for syncing files with the "
                   "Toshiba FlashAir wireless SD card"),
      long_description=long_description,
      include_package_data=True,
      package_data={"": ["README.md"]},
      author="Tad Leonard",
      author_email="tadfleonard@gmail.com",
      keywords="wireless sd card sync toshiba flashair", 
      url=url,
      download_url=download,
      zip_safe=True,
)

