from setuptools import setup
import tfatool._version


setup(name="tfatool",
      version=tfatool._version.__version__,
      scripts=["flashair-util"],
      install_requires=["requests>=2.9.0",],
      licence="MIT",
      packages=["tfatool"],
      description=("Tools for syncing files with the "
                   "Toshiba FlashAir wireless SD card"),
      author="Tad Leonard",
      author_email="tadfleonard@gmail.com",
      keywords="wireless sd card sync toshiba flashair", 
      url="https://github.com/TadLeonard/tfatool",
      download_url="https://github.com/TadLeonard/tfatool/archive/v1.0.0.tar.gz",
)

