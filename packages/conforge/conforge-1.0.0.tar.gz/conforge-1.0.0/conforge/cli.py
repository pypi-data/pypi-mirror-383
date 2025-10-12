#!/usr/bin/env python3

import argparse

from . import main


def run_app():
    parser = argparse.ArgumentParser(description='Conforge: Generate config files from given templates and variables')

    parser.add_argument(
        'config',
        type=argparse.FileType('r'),
        help='The path to the configuration file.')

    args = parser.parse_args()

    config_file_parser_provider = main.ConfigFileParserProvider()
    config_file_parser_provider.add_parser(main.JsonConfigFileParser.CONFIG_FILE_TYPE, main.JsonConfigFileParser())

    config_file = main.ConfigFile('json', args.config.read())

    conforge = main.Conforge(config_file_parser_provider)
    conforge.make_config_files(config_file)

if __name__ == "__main__":
    run_app()