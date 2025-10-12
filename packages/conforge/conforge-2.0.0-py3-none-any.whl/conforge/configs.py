import os
import json

import yaml

from .utils import Interpolate, deep_merge


class InvalidSyntaxException(Exception):
    def __init__(self, path, message):
        self.path = path
        self.message = message


class ConfigFileNotExistsException(Exception):
    def __init__(self, path):
        self.path = path


class VariableFileNotExistsException(Exception):
    def __init__(self, path):
        self.path = path


class DictConfig:
    def __init__(self, config, variable_file_parser_provider, base_dir=None):
        self.config = config
        self.variable_file_parser_provider = variable_file_parser_provider

        if not base_dir:
            self.base_dir = os.getcwd()
        else:
            self.base_dir = base_dir

    def get_variables_from_variable_files(self):
        variables = {}

        for variable_file_spec in self.config['variable_files']:
            try:
                variable_file_parser = self.variable_file_parser_provider.get_parser_for(
                    variable_file_spec['type'],
                    self.get_path_relative_to_base_dir(variable_file_spec['path'])
                )

                variable_file_variables = variable_file_parser.get_variables()

                if isinstance(variable_file_variables, dict):
                    variables = deep_merge(variables, variable_file_variables)
            except VariableFileNotExistsException as e:
                if variable_file_spec['required']:
                    raise e

        return variables

    def get_variables_expanded(self):
        variables_from_variable_files = self.get_variables_from_variable_files()

        interpolate = Interpolate(
            deep_merge(
                self.config['variables'],
                variables_from_variable_files
            )
        )

        return interpolate.get_interpolated()

    def get_path_relative_to_base_dir(self, path):
        return os.path.realpath(
            os.path.join(
                self.base_dir,
                path
            )
        )

    def get_template_specs(self):
        for template_spec in self.config['templates']:
            output_template_spec = {
                'template': self.get_path_relative_to_base_dir(template_spec['template']),
                'outputs': []
            }

            for output in template_spec['outputs']:
                output_template_spec['outputs'].append(self.get_path_relative_to_base_dir(output))

            yield output_template_spec

        return []

class JsonConfigFile:
    def __init__(self, json_config_file, variable_file_parser_provider):
        try:
            with open(json_config_file) as jfp:
                self.config = DictConfig(
                    json.load(jfp),
                    variable_file_parser_provider,
                    os.path.dirname(json_config_file)
                )
        except FileNotFoundError:
            raise ConfigFileNotExistsException(json_config_file)
        except json.decoder.JSONDecodeError as e:
            raise InvalidSyntaxException(json_config_file, str(e))

    @staticmethod
    def get_for_file(file, variable_file_parser_provider):
        return JsonConfigFile(file, variable_file_parser_provider)

    def get_variables_expanded(self):
        return self.config.get_variables_expanded()

    def get_template_specs(self):
        return self.config.get_template_specs()


class JsonVariableFile:
    def __init__(self, json_variable_file):
        try:
            with open(json_variable_file) as jfp:
                self.variables = json.load(jfp)
        except FileNotFoundError:
            raise VariableFileNotExistsException(json_variable_file)
        except json.decoder.JSONDecodeError as e:
            raise InvalidSyntaxException(json_variable_file, str(e))

    @staticmethod
    def get_for_file(file):
        return JsonVariableFile(file)

    def get_variables(self):
        return self.variables

class YamlConfigFile:
    def __init__(self, yaml_config_file, variable_file_parser_provider):
        try:
            with open(yaml_config_file) as yfp:
                self.config = DictConfig(
                    yaml.safe_load(yfp),
                    variable_file_parser_provider,
                    os.path.dirname(yaml_config_file)
                )
        except FileNotFoundError:
            raise ConfigFileNotExistsException(yaml_config_file)
        except yaml.YAMLError as e:
            raise InvalidSyntaxException(yaml_config_file, str(e))

    @staticmethod
    def get_for_file(file, variable_file_parser_provider):
        return YamlConfigFile(file, variable_file_parser_provider)

    def get_variables_expanded(self):
        return self.config.get_variables_expanded()

    def get_template_specs(self):
        return self.config.get_template_specs()


class YamlVariableFile:
    def __init__(self, yaml_variable_file):
        try:
            with open(yaml_variable_file) as yfp:
                self.variables = yaml.safe_load(yfp)
        except FileNotFoundError:
            raise VariableFileNotExistsException(yaml_variable_file)
        except yaml.YAMLError as e:
            raise InvalidSyntaxException(yaml_variable_file, str(e))

    @staticmethod
    def get_for_file(file):
        return YamlVariableFile(file)

    def get_variables(self):
        return self.variables