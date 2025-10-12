import json

from jinja2 import Template

class InvalidConfigFileException(Exception):
    pass

class ConfigFileParserProvider:
    parsers = {}

    def add_parser(self, type, parser):
        self.parsers[type] = parser

    def get_parser_for(self, type):
        return self.parsers[type]

    def get_supported_config_file_types(self):
        return self.parsers.keys()


class JsonConfigFileParser:

    CONFIG_FILE_TYPE = 'json'

    @staticmethod
    def get_config(config_file):
        if config_file.type != JsonConfigFileParser.CONFIG_FILE_TYPE:
            raise InvalidConfigFileException()

        return Config(json.loads(config_file.contents))


class ConfigFile:
    def __init__(self, type, contents):
        self.type = type
        self.contents = contents


class Config:
    def __init__(self, config):
        self.config = config

    def get_variables_expanded(self):
        return self.config['variables']

    def get_template_specs(self):
        return self.config['templates']


class TemplateRenderer:
    def __init__(self, template_content, variables):
        template = Template(template_content)
        self.rendered_content = template.render(variables)

    def write_to(self, output):
        with open(output, 'w') as output_fp:
            output_fp.write(self.rendered_content)


class Conforge:
    def __init__(self, config_file_parser_provider):
        self.config_file_parser_provider = config_file_parser_provider

    def make_config_files(self, config_file):
        config_file_parser = self.config_file_parser_provider.get_parser_for(config_file.type)

        config = config_file_parser.get_config(config_file)

        variables = config.get_variables_expanded()

        template_specs = config.get_template_specs()

        for template_spec in template_specs:
            with open(template_spec['template'], 'r') as template_fp:
                template_renderer = TemplateRenderer(template_fp.read(), variables)

                for output in template_spec['outputs']:
                    template_renderer.write_to(output)
