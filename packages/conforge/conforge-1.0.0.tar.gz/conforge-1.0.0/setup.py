# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['conforge']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=3.1.6,<4.0.0']

entry_points = \
{'console_scripts': ['conforge = conforge.cli:run_app']}

setup_kwargs = {
    'name': 'conforge',
    'version': '1.0.0',
    'description': 'A tool for generating config files from given templates and variables.',
    'long_description': '# Conforge\n\nA tool for generating config files from given templates and variables.\n\n## Installation\n\n```bash\npipx install conforge\n```\n\n## Usage\n\n```bash\nconforge config.json\n```\n\n## Configuration File\n\nCurrently only JSON format is supported. The syntax is:\n\n```json\n{\n    "variables": {\n        "app": {\n            "name": "Conforge",\n            "version": "1.0.0",\n            "description": "A tool for generating config files from given templates and variables."\n        }\n    },\n    "templates": [\n        {\n            "template": "README.tpl",\n            "outputs": [\n                "README.md"\n            ]\n        }\n    ]\n}\n```\n\nIn here, all the variables for generating the config files go under the `variables` key. The templates are specified in the `templates` key.\n\nEach template specification is a dictionary having keys `template` and `outputs`. The value of `template` key is the path to the template file that should be used for generating the files specified in the `outputs` array. Multiple files can be given in the `outputs` array.\n\nConforge currently supports [Jinja2](https://jinja.palletsprojects.com) as the templating engine.\n\n## License\n\nConforge is licensed under the terms of GPL version 3.0. See the [LICENSE](https://codeberg.org/scripthoodie/conforge/src/branch/main/LICENSE) file for details.',
    'author': 'ScriptHoodie',
    'author_email': 'dev@scripthoodie.dev',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
