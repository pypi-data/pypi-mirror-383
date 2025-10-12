# Conforge

A tool for generating config files from given templates and variables.

## Installation

```bash
pipx install conforge
```

## Usage

```bash
conforge config.json
```

## Configuration File

Currently only JSON format is supported. The syntax is:

```json
{
    "variables": {
        "app": {
            "name": "Conforge",
            "version": "1.0.0",
            "description": "A tool for generating config files from given templates and variables."
        }
    },
    "templates": [
        {
            "template": "README.tpl",
            "outputs": [
                "README.md"
            ]
        }
    ]
}
```

In here, all the variables for generating the config files go under the `variables` key. The templates are specified in the `templates` key.

Each template specification is a dictionary having keys `template` and `outputs`. The value of `template` key is the path to the template file that should be used for generating the files specified in the `outputs` array. Multiple files can be given in the `outputs` array.

Conforge currently supports [Jinja2](https://jinja.palletsprojects.com) as the templating engine.

## License

Conforge is licensed under the terms of GPL version 3.0. See the [LICENSE](https://codeberg.org/scripthoodie/conforge/src/branch/main/LICENSE) file for details.