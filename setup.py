#!/usr/bin/python
#
# File: setup.py
#
# This file is part of the biblio-py project
#
# License:
#
# Copyright (C) 2009 Juan Fiol This is free software.
#
# You may redistribute copies of it under the terms of the GNU General Public License
# version 2 or later.  There is NO WARRANTY, to the extent permitted by law.
#
# Written by Juan Fiol <juanfiol@gmail.com>
import os
import glob
from distutils.core import setup
from yapbib.version import VERSION


def read(*rnames):
  return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.txt')
)

packages = ["yapbib", "query_ads"]
scripts = glob.glob('scripts/*.py')


def setup_package():
  # Rewrite the version file everytime
  if os.path.exists('yapbib/version.py'):
    os.remove('yapbib/version.py')
  fo = open('yapbib/version.py', 'w')
  try:
    fo.write('VERSION= "{0}"'.format(VERSION))
  finally:
    fo.close()

  # do the distutils setup
  setup(name="biblio-py",
        version=VERSION,
        description="Package to manage bibliography files",
        long_description=long_description,
        license="GPLv2",
        url="https://github.com/fiolj/biblio-py",
        keywords="bibliography, bibtex, converter, html, xml, latex, parser",
        author="Juan Fiol",
        author_email="juanfiol@gmail.com",
        packages=packages,
        scripts=scripts,
        )


if __name__ == '__main__':
  setup_package()
