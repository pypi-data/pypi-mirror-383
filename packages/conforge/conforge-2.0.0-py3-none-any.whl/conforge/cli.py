#!/usr/bin/env python3

import sys
import argparse

from . import main, configs


class ExitCodes:
    CONFIG_FILE_DOES_NOT_EXIST = 129
    VARIABLE_FILE_DOES_NOT_EXIST = 130
    INVALID_SYNTAX = 131


def run_app():
    config_file_parser_provider = main.ConfigFileParserProvider()
    config_file_parser_provider.add_parser('json', configs.JsonConfigFile)
    config_file_parser_provider.add_parser('yaml', configs.YamlConfigFile)

    variable_file_parser_provider = main.VariableFileParserProvider()
    variable_file_parser_provider.add_parser('json', configs.JsonVariableFile)
    variable_file_parser_provider.add_parser('yaml', configs.YamlVariableFile)

    parser = argparse.ArgumentParser(description='Conforge: Generate config files from given templates and variables')

    parser.add_argument(
        '-t',
        '--config-type',
        type=str,
        choices=config_file_parser_provider.get_supported_config_file_types(),
        required=True,
        help='Type of config file')
    parser.add_argument(
        'config',
        type=str,
        help='The path to the configuration file.')

    args = parser.parse_args()

    try:
        conforge = main.Conforge(config_file_parser_provider, variable_file_parser_provider)
        conforge.make_config_files(args.config_type, args.config)
    except configs.ConfigFileNotExistsException as e:
        print('Config file {} does not exist!'.format(e.path), file=sys.stderr)
        sys.exit(ExitCodes.CONFIG_FILE_DOES_NOT_EXIST)
    except configs.VariableFileNotExistsException as e:
        print('Variable file {} does not exist!'.format(e.path), file=sys.stderr)
        sys.exit(ExitCodes.VARIABLE_FILE_DOES_NOT_EXIST)
    except configs.InvalidSyntaxException as e:
        print('Invalid syntax error in {}:\n\n{}'.format(e.path, e.message))
        sys.exit(ExitCodes.INVALID_SYNTAX)

if __name__ == "__main__":
    run_app()