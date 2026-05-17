#!/usr/bin/env python3
"""Script to convert github.com issues into CSV."""

import argparse
import configparser
import json
import logging
import os
import re
import sys
import time

from urllib import error as urllib_error
from urllib.request import urlopen


class Project:
    """Project definition.

    Attributes:
      appveyor_identifier (str): the AppVeyor identifier.
      category (str): the project category.
      description (str): the project description.
      display_name (str): the project display name.
      documentation_only (bool): True if the project only contains documentation.
      name (str): the name of the project.
    """

    def __init__(self, name):
        """Initializes a project definition.

        Args:
          name (str): name of the project.
        """
        super().__init__()
        self.appveyor_identifier = None
        self.category = None
        self.description = None
        self.display_name = name
        self.documentation_only = False
        self.name = name


class ProjectsReader:
    """Project definition reader."""

    def __init__(self):
        """Initializes a projects definition reader."""
        super().__init__()
        self._config_parser = configparser.ConfigParser(interpolation=None)

    def _GetConfigValue(self, section_name, value_name):
        """Retrieves a value from the config parser.

        Args:
          section_name (str): name of the section that contains the value.
          value_name (str): name of the value.

        Returns:
          object: the value.
        """
        return json.loads(self._config_parser.get(section_name, value_name))

    def ReadFromFile(self, filename):
        """Reads the projects from file.

        Args:
          filename (str): the filename.

        Returns:
          list[Project]: project definitions.
        """
        self._config_parser.read([filename])

        projects = []
        for project_name in self._config_parser.sections():
            project = Project(project_name)

            try:
                project.appveyor_identifier = self._GetConfigValue(
                    project_name, "appveyor_identifier"
                )
            except configparser.NoOptionError:
                pass

            project.category = self._GetConfigValue(project_name, "category")
            project.description = self._GetConfigValue(project_name, "description")

            try:
                project.display_name = self._GetConfigValue(
                    project_name, "display_name"
                )
            except configparser.NoOptionError:
                pass

            try:
                project.documentation_only = self._GetConfigValue(
                    project_name, "documentation_only"
                )
            except configparser.NoOptionError:
                pass

            projects.append(project)

        return projects


class GithubIssueHelper:
    """Github issue helper."""

    _KEYS = [
        "number",
        "state",
        "created_at",
        "assignee",
        "milestone",
        "labels",
        "title",
        "html_url",
    ]

    _LAST_PAGE_RE = re.compile(
        r"<(https://api.github.com/repositories/[0-9]+/issues\?"
        r'state=open&page=)([0-9]+)>; rel="last"'
    )

    def __init__(self, organization):
        """Initialize a Github issue helper.

        Args:
          organization (str): name of the organization on Github.
        """
        super().__init__()
        self._organization = organization

    def _DownloadPageContent(self, download_url):
        """Downloads the page content from the URL.

        Args:
          download_url (str): URL where to download the page content.

        Returns:
          tuple[bytes, HTTPMessage]: page content and HTTP response message
              containing the response headers if successful, None otherwise.
        """
        if not download_url:
            return None, None

        try:
            with urlopen(download_url) as url_object:
                if url_object.code == 200:
                    return url_object.read(), url_object.info()

                logging.warning(
                    f"Unable to download URL: {download_url:s} with status code: "
                    f"{url_object.code:d}"
                )
                return None, None

        except urllib_error.URLError as exception:
            logging.warning(
                f"Unable to download URL: {download_url:s} with error: {exception!s}"
            )
            return None, None

    def _ListIssuesForProject(self, project_name, output_writer):
        """Lists the issues of a specific project.

        Args:
          project_name (str): name of the project.
          output_writer (OutputWriter): an output writer.
        """
        self._WaitForRateLimit()

        download_url = (
            f"https://api.github.com/repos/{self._organization:s}/{project_name:s}/"
            f"issues?state=open"
        )
        issues_data, response = self._DownloadPageContent(download_url)
        if not issues_data:
            return

        for issue_json in json.loads(issues_data):
            self._WriteIssue(project_name, issue_json, output_writer)

        if not response:
            logging.error("Missing HTTP response message.")
            return

        # Handle the multi-page response.
        link_header = response.get("Link")
        if not link_header:
            return

        matches = self._LAST_PAGE_RE.findall(link_header)
        if len(matches) != 1 and len(matches[0]) != 2:
            logging.error(f"Unsupported Link HTTP header: {link_header:s}")
            return

        base_url = matches[0][0]

        try:
            last_page = int(matches[0][1], 10) + 1
        except ValueError:
            logging.error(f"Unsupported Link HTTP header: {link_header:s}")
            return

        for page_number in range(2, last_page):
            self._WaitForRateLimit()

            download_url = f"{base_url:s}{page_number:d}"
            issues_data, _ = self._DownloadPageContent(download_url)
            if not issues_data:
                logging.error(f"Missing issues page content: {download_url:s}")
                continue

            for issue_json in json.loads(issues_data):
                self._WriteIssue(project_name, issue_json, output_writer)

    def _WaitForRateLimit(self):
        """Checks and waits for the rate limit."""
        download_url = "https://api.github.com/rate_limit"

        remaining_count = 0
        while remaining_count == 0:
            rate_limit_data, _ = self._DownloadPageContent(download_url)
            if not rate_limit_data:
                logging.error("Missing rate limit page content.")
                return

            rate_limit_json = json.loads(rate_limit_data)

            rate_json = rate_limit_json.get("rate", None)
            if not rate_json:
                logging.error("Invalid rate limit information - missing rate.")
                return

            remaining_count = rate_json.get("remaining", None)
            if remaining_count is None:
                logging.error("Invalid rate limit information - missing remaining.")
                return

            reset_timestamp = rate_json.get("reset", None)
            if reset_timestamp is None:
                logging.error("Invalid rate limit information - missing reset.")
                return

            if remaining_count > 0:
                break

            current_timestamp = int(time.time())
            if current_timestamp > reset_timestamp:
                break

            reset_timestamp -= current_timestamp
            logging.info(
                f"Rate limiting calls to Github API - sleeping for {reset_timestamp:d} "
                f"seconds."
            )
            time.sleep(reset_timestamp)

    def _WriteHeader(self, output_writer):
        """Writes a header to CSV.

        Args:
          output_writer (OutputWriter): an output writer.
        """
        csv_keys = "\t".join([f"{key:s}:" for key in self._KEYS])
        output_writer.Write("project:\t{csv_keys:s}\n")

    def _WriteIssue(self, project_name, issue_json, output_writer):
        """Writes an issue to CSV.

        Args:
          project_name (str): name of the project.
          issue_json (dict[str, object]): issue formatted in JSON.
          output_writer (OutputWriter): an output writer.
        """
        # https://developer.github.com/v3/issues/
        # Keys: {
        #   assignee: {
        #     login:
        #   }
        #   body:
        #   closed_at:
        #   comments:
        #   comments_url:
        #   created_at:
        #   events_url:
        #   html_url:
        #   id:
        #   labels: [{
        #     name:
        #   }]
        #   labels_url:
        #   locked:
        #   milestone: {
        #     title:
        #   }
        #   number:
        #   state:
        #   title:
        #   updated_at:
        #   url:
        #   user: {}
        # }

        csv_values = []
        for key in self._KEYS:
            csv_value = ""
            if key == "assignee":
                assignee_json = issue_json[key]
                if assignee_json:
                    csv_value = assignee_json["login"]

            elif key == "milestone":
                milestone_json = issue_json[key]
                if milestone_json:
                    csv_value = milestone_json["title"]

            elif key == "labels":
                labels_json = issue_json[key]
                if labels_json:
                    csv_value = ", ".join(
                        [label_json["name"] for label_json in labels_json]
                    )
            else:
                csv_value = str(issue_json[key])

            csv_values.append(csv_value)

        csv_values = "\t".join(csv_values)
        csv_line = f"{project_name:s}\t{csv_values:s}\n"

        output_writer.Write(csv_line)

    def ListIssues(self, project_names, output_writer):
        """Lists the issues of projects.

        Args:
          project_names (list[str]): names of the projects to list.
          output_writer (OutputWriter): an output writer.
        """
        self._WriteHeader(output_writer)

        for project_name in project_names:
            self._ListIssuesForProject(project_name, output_writer)

        output_writer.Write("\n")


class FileWriter:
    """Output writer that writes to file."""

    def __init__(self, name):
        """Initializes an output writer.

        Args:
          name (str): name of the output.
        """
        super().__init__()
        self._file_object = None
        self._name = name

    def Open(self):
        """Opens the output writer.

        Returns:
          bool: True if successful or False if not.
        """
        self._file_object = open(
            self._name, "w", encoding="utf8"
        )  # pylint: disable=consider-using-with
        return True

    def Close(self):
        """Closes the output writer."""
        self._file_object.close()

    def Write(self, data):
        """Writes the data to file.

        Args:
          data (str): the data to write.
        """
        self._file_object.write(data)


class StdoutWriter:
    """Output writer that writes to stdout."""

    def Open(self):
        """Opens the output writer.

        Returns:
          bool: True if successful or False if not.
        """
        return True

    def Close(self):
        """Closes the output writer."""
        return

    def Write(self, data):
        """Writes the data to stdout (without the default trailing newline).

        Args:
          data (str): the data to write.
        """
        print(data, end="")


def Main():
    """The main program function.

    Returns:
      bool: True if successful or False if not.
    """
    argument_parser = argparse.ArgumentParser(
        description=(
            "Generates an overview of open Github issues of the libyal libraries."
        )
    )

    argument_parser.add_argument(
        "configuration_file",
        action="store",
        metavar="CONFIGURATION_FILE",
        default="projects.ini",
        help=("The overview generation configuration file."),
    )

    argument_parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        action="store",
        metavar="OUTPUT_FILE",
        default=None,
        help=("path of the output file to write to."),
    )

    argument_parser.add_argument(
        "-p",
        "--projects",
        dest="projects",
        action="store",
        metavar="PROJECT_NAME(S)",
        default=None,
        help="comma separated list of specific project names to query.",
    )

    options = argument_parser.parse_args()

    if not options.configuration_file:
        print("Configuration file missing.")
        print("")
        argument_parser.print_help()
        print("")
        return False

    if not os.path.exists(options.configuration_file):
        print(f"No such configuration file: {options.configuration_file:s}")
        print("")
        return False

    projects_reader = ProjectsReader()

    if options.projects:
        project_names = options.projects.split(",")
    else:
        projects = projects_reader.ReadFromFile(options.configuration_file)
        if not projects:
            print(
                f"Unable to read projects from configuration file: "
                f"{options.configuration_file:s}"
            )
            print("")
            return False

        project_names = [project.name for project in projects]

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    if options.output_file:
        output_writer = FileWriter(options.output_file)
    else:
        output_writer = StdoutWriter()

    if not output_writer.Open():
        print("Unable to open output writer.")
        print("")
        return False

    issue_helper = GithubIssueHelper("libyal")
    issue_helper.ListIssues(project_names, output_writer)

    return True


if __name__ == "__main__":
    if not Main():
        sys.exit(1)
    else:
        sys.exit(0)
