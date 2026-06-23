#!/usr/bin/env python3
# pylint: disable=invalid-name
"""Script to generate source of the libyal libraries."""

import argparse
import logging
import os
import sys

from yaldevtools import configuration
from yaldevtools import output_writers
from yaldevtools.source_generators import common
from yaldevtools.source_generators import config
from yaldevtools.source_generators import documents
from yaldevtools.source_generators import include
from yaldevtools.source_generators import library
from yaldevtools.source_generators import manpage
from yaldevtools.source_generators import python_module
from yaldevtools.source_generators import scripts
from yaldevtools.source_generators import tests
from yaldevtools.source_generators import tools


def Main():
    """Entry point of console script.

    Returns:
      int: exit code that is provided to sys.exit().
    """
    argument_parser = argparse.ArgumentParser(
        description=("Generates source files of the libyal libraries.")
    )
    argument_parser.add_argument(
        "-g",
        "--generators",
        dest="generators",
        action="store",
        default="all",
        help="names of the generators to run.",
    )
    argument_parser.add_argument(
        "-o",
        "--output",
        dest="output_directory",
        action="store",
        metavar="OUTPUT_DIRECTORY",
        default=None,
        help="path of the output files to write to.",
    )
    argument_parser.add_argument(
        "-p",
        "--projects",
        dest="projects_directory",
        action="store",
        metavar="PROJECTS_DIRECTORY",
        default=None,
        help="path of the projects.",
    )
    argument_parser.add_argument(
        "configuration_file",
        action="store",
        metavar="PATH",
        default="libyal.ini",
        help="path of the configuration file.",
    )
    options = argument_parser.parse_args()

    if not options.configuration_file:
        print("Configuration file missing.")
        print("")
        argument_parser.print_help()
        print("")
        return 1

    if not os.path.exists(options.configuration_file):
        print(f"No such configuration file: {options.configuration_file:s}")
        print("")
        return 1

    if options.output_directory and not os.path.exists(options.output_directory):
        print(f"No such output directory: {options.output_directory:s}")
        print("")
        return 1

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    project_configuration = configuration.ProjectConfiguration()
    project_configuration.ReadFromFile(options.configuration_file)

    libyal_directory = os.path.abspath(__file__)
    libyal_directory = os.path.dirname(libyal_directory)
    libyal_directory = os.path.dirname(libyal_directory)

    projects_directory = options.projects_directory
    if not projects_directory:
        projects_directory = os.path.dirname(libyal_directory)

    data_directory = os.path.join(libyal_directory, "data")

    # TODO: generate more source files.
    # include headers
    # yal.net files

    if options.generators == "all":
        generators = []
    else:
        generators = options.generators.split(",")

    SOURCE_GENERATORS = [
        ("common", common.CommonSourceFileGenerator),
        ("config", config.ConfigurationFileGenerator),
        ("documents", documents.DocumentFileGenerator),
        ("include", include.IncludeSourceFileGenerator),
        ("libyal", library.LibrarySourceFileGenerator),
        ("pyyal", python_module.PythonModuleSourceFileGenerator),
        ("scripts", scripts.ScriptFileGenerator),
        ("tests", tests.TestSourceFileGenerator),
        ("yaltools", tools.ToolSourceFileGenerator),
    ]
    sources_directory = os.path.join(data_directory, "source")
    for source_category, source_generator_class in SOURCE_GENERATORS:
        if generators and source_category not in generators:
            continue

        template_directory = os.path.join(sources_directory, source_category)
        source_generator_object = source_generator_class(
            projects_directory,
            data_directory,
            template_directory,
        )
        if options.output_directory:
            output_writer = output_writers.FileWriter(options.output_directory)
        else:
            output_writer = output_writers.StdoutWriter()

        source_generator_object.Generate(project_configuration, output_writer)

    # TODO: dpkg handle dependencies

    # TODO: generate manuals/Makefile.am

    SOURCE_GENERATORS = [
        ("libyal.3", manpage.LibraryManPageGenerator),
    ]
    if project_configuration.HasInfoTool():
        SOURCE_GENERATORS.append(("yalinfo.1", manpage.InfoToolManPageGenerator))

    manuals_directory = os.path.join(libyal_directory, "data", "source", "manuals")
    for source_category, source_generator_class in SOURCE_GENERATORS:
        if generators and source_category not in generators:
            continue

        template_directory = os.path.join(manuals_directory, source_category)
        source_generator_object = source_generator_class(
            projects_directory,
            data_directory,
            template_directory,
        )
        if options.output_directory:
            output_writer = output_writers.FileWriter(options.output_directory)
        else:
            output_writer = output_writers.StdoutWriter()

        source_generator_object.Generate(project_configuration, output_writer)

    return 0


if __name__ == "__main__":
    sys.exit(Main())
