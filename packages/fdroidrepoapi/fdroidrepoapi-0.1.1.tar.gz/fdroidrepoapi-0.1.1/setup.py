# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fdroidrepoapi']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'fdroidrepoapi',
    'version': '0.1.1',
    'description': 'lib for querying F-Droid repositories',
    'long_description': "<!--\nSPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>\nSPDX-License-Identifier: AGPL-3.0-or-later\n-->\n\n# F-Droid Repo API\n\nA python module for querying F-Droid repositories as if they were a web API.\n\n## code checking\n\nThis project uses some tools for making sure code qauality doesn't degrade.\nHere's a helper script for running all checks:\n\n```\ntools/check\n```\n\nAlways make sure this script doesn't find any issues before commiting.\n",
    'author': 'Michael Pöhn',
    'author_email': 'michael@poehn.at',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://codeberg.org/uniqx/fdroidrepoapi',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
