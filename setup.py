import os
import tfatool._version
from setuptools import setup


version = tfatool._version.__version__
url = "https://github.com/TadLeonard/tfatool"
download = "{}/archive/{}.tar.gz".format(url, version)

# NOTE: pandoc doesn't convert Markdown's in-word-emphasis,
# so I have to upload a different hand-tuned README to PyPI
# PyPI might also just be terrible at rendering RST 

#try:
#    import pypandoc
#    long_description = pypandoc.convert('README.md', 'rst')
#except ImportError:
#    long_description = ("Tools for syncing files with the Toshiba FlashAir "
#                        "wireless SD card")

long_description("See {} for documentation".format(url))
description = ("Tools for synchronizing files to/from "
               "and configuring the Toshiba FlashAir "
               "wireless SD card")

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Environment :: Console',
  'Intended Audience :: End Users/Desktop',
  'Intended Audience :: Developers',
  'Operating System :: OS Independent',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python :: 3 :: Only',
  'Topic :: Home Automation',
  'Topic :: System :: Archiving',
  'Topic :: System :: Archiving :: Backup',
  'Topic :: System :: Archiving :: Mirroring',
]

setup(name="tfatool",
      version=tfatool._version.__version__,
      scripts=["flashair-util", "flashair-config"],
      install_requires=["requests>=2.9.0", "tqdm>=3.7.1", "arrow"],
      licence="MIT",
      packages=["tfatool"],
      description=description,
      long_description=long_description,
      classifiers=classifiers,
      include_package_data=True,
      package_data={"": ["README.md"]},
      author="Tad Leonard",
      author_email="tadfleonard@gmail.com",
      keywords="wireless sd card sdcard sync toshiba flashair", 
      url=url,
      download_url=download,
      zip_safe=True,
)

