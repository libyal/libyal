#!/usr/bin/env python3
# pylint: disable=invalid-name
"""Script to automate generation of wiki pages of the libyal libraries."""

import abc
import argparse
import os
import re
import string
import sys

from yaldevtools import configuration


class TemplateString(string.Template):
    """Template string."""

    idpattern = r"(?a:[_a-z][_a-z0-9.]*(|:[_a-z][_a-z0-9]*))"

    def substitute(self, mapping=None):
        """Substitutes placeholders in the template string.

        Args:
          mapping (dict[str, str]): values of placeholders.
        """

        def convert_placeholder(match):
            """Converts a placeholder into a mapped value.

            Args:
              match (re.Match): expression match.

            Returns:
              str: mapped value.

            Raises:
              ValueError: if the pattern is not supported.
            """
            identifier = match.group("named") or match.group("braced")
            if identifier is not None:
                identifier, _, modifier = identifier.partition(":")

                identifiers = identifier.split(".")
                try:
                    value = mapping[identifiers[0]]
                except KeyError:
                    raise ValueError(f"No mapping for placeholder: {identifiers[0]:s}")

                for attribute_name in identifiers[1:]:
                    value = getattr(value, attribute_name, None)
                value = str(value)

                if modifier == "camel_case":
                    value = "".join([word.title() for word in value.split("_")])
                elif modifier == "lower_case":
                    value = value.lower()
                elif modifier == "upper_case":
                    value = value.upper()
                elif modifier:
                    raise ValueError("Unrecognized modifier in pattern", self.pattern)

                return value

            if match.group("escaped") is not None:
                return self.delimiter

            if match.group("invalid") is not None:
                self._invalid(match)

            raise ValueError("Unrecognized named group in pattern", self.pattern)

        return self.pattern.sub(convert_placeholder, self.template)


class WikiPageGenerator:
    """Generates wiki pages."""

    def __init__(self, templates_path):
        """Initializes a wiki page generator.

        Args:
          templates_path (str): path of the directory containing the template files.
        """
        super().__init__()
        self._templates_path = templates_path

    def _GenerateSection(self, template_filename, template_mappings, output_writer):
        """Generates a section from template filename.

        Args:
          template_filename (str): path of the template file.
          template_mpppings (dict[str, str]): the template mappings, where
              the key maps to the name of a template variable.
          output_writer (OutputWriter): output writer.
        """
        template_string = self._ReadTemplateFile(template_filename)
        output_data = template_string.substitute(mapping=template_mappings)
        output_writer.Write(output_data)

    def _GetCygwinBuildDependencies(self, project_configuration):
        """Retrieves the Cygwin build dependencies.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: Cygwin build dependencies.
        """
        dependencies = [
            "autoconf",
            "automake",
            "binutils",
            "gcc-core",
            "gcc-g++",
            "gettext-devel",
            "libiconv",
            "libtool",
            "make",
            "pkg-config",
        ]
        if project_configuration.HasDependencyLex():
            dependencies.append("flex")

        if project_configuration.HasDependencyYacc():
            dependencies.append("byacc")

        if project_configuration.HasDependencyZlib():
            dependencies.append(
                "zlib-devel (for DEFLATE compression support) (optional but "
                "recommended, can be disabled by --with-zlib=no)"
            )

        if project_configuration.HasDependencyBzip2():
            dependencies.append("libbz2-devel (required for bzip2 compression support)")

        if project_configuration.HasDependencyCrypto():
            dependencies.append(
                "libssl-devel (optional but recommended, can be disabled by "
                "--with-openssl=no)"
            )

        dependencies.extend(project_configuration.cygwin_build_dependencies)

        return dependencies

    def _GetCygwinDLLDependencies(self, project_configuration):
        """Retrieves the Cygwin DLL dependencies.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: Cygwin DLL dependencies.
        """
        dependencies = ["cygwin1.dll"]

        dependencies.extend(project_configuration.cygwin_dll_dependencies)

        return dependencies

    def _GetDpkgBuildDependencies(self, project_configuration):
        """Retrieves the dpkg build dependencies.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: dpkg build dependencies.
        """
        dependencies = list(project_configuration.dpkg_build_dependencies)

        if project_configuration.HasDependencyLex():
            dependencies.append("flex")

        if project_configuration.HasDependencyYacc():
            dependencies.append("bison")

        if project_configuration.HasDependencyZlib():
            dependencies.append("zlib1g-dev")

        if project_configuration.HasDependencyBzip2():
            dependencies.append("bzip2-dev")

        if project_configuration.HasDependencyCrypto():
            dependencies.append("libssl-dev")

        if "fuse" in project_configuration.tools_build_dependencies:
            dependencies.append("libfuse3-dev")

        if project_configuration.HasPythonModule():
            dependencies.extend(["python3-dev", "python3-setuptools"])

        return dependencies

    def _GetDpkgFilenames(self, project_configuration):
        """Retrieves the dpkg filenames.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: dpkg filenames.
        """
        project_name = project_configuration.project_name

        filenames = [
            f"{project_name:s}_<version>-1_<arch>.deb",
            f"{project_name:s}-dev_<version>-1_<arch>.deb",
        ]
        if project_configuration.HasPythonModule():
            filenames.append(f"{project_name:s}-python3_<version>-1_<arch>.deb")

        if project_configuration.HasTools():
            filenames.append(f"{project_name:s}-tools_<version>-1_<arch>.deb")

        return filenames

    def _GetMinGWBuildDependencies(self, project_configuration):
        """Retrieves the MinGW build dependencies.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: MinGW build dependencies.
        """
        dependencies = []

        if project_configuration.HasDependencyLex():
            dependencies.append("flex")

        if project_configuration.HasDependencyYacc():
            dependencies.append("byacc")

        if project_configuration.HasDependencyZlib():
            dependencies.append(
                "MinGW build of zlib library and source headers (for DEFLATE "
                "compression support) (optional but recommended, can be disabled "
                "by --with-zlib=no)"
            )

        if project_configuration.HasDependencyBzip2():
            dependencies.append(
                "MinGW build of bzip2 library and source headers (required for "
                "bzip2 compression support)"
            )

        dependencies.extend(project_configuration.mingw_build_dependencies)

        return dependencies

    def _GetMinGWDLLDependencies(self, project_configuration):
        """Retrieves the MinGW DLL dependencies.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: MinGW DLL dependencies.
        """
        dependencies = ["libgcc_s_dw2-1.dll (or equivalent)"]

        dependencies.extend(project_configuration.mingw_dll_dependencies)

        return dependencies

    def _GetRpmBuildDependencies(self, project_configuration):
        """Retrieves the rpm build dependencies.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: rpm build dependencies.
        """
        dependencies = list(project_configuration.rpm_build_dependencies)

        if project_configuration.HasDependencyLex():
            dependencies.append("flex")

        if project_configuration.HasDependencyYacc():
            dependencies.append("byacc")

        if project_configuration.HasDependencyZlib():
            dependencies.append("zlib-devel")

        if project_configuration.HasDependencyBzip2():
            dependencies.append("bzip2-devel")

        if project_configuration.HasDependencyCrypto():
            dependencies.append("openssl-devel")

        if "fuse" in project_configuration.tools_build_dependencies:
            dependencies.append("fuse3-devel")

        if project_configuration.HasPythonModule():
            dependencies.append("python3-devel")

        return dependencies

    def _GetRpmFilenames(self, project_configuration):
        """Retrieves the rpm filenames.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: rpm filenames.
        """
        project_name = project_configuration.project_name

        filenames = [
            f"~/rpmbuild/RPMS/<arch>/{project_name:s}-<version>-1.<arch>.rpm",
            f"~/rpmbuild/RPMS/<arch>/{project_name:s}-devel-<version>-1.<arch>.rpm",
        ]
        if project_configuration.HasPythonModule():
            filenames.append(
                f"~/rpmbuild/RPMS/<arch>/{project_name:s}-python3-<version>-1.<arch>.rpm"
            )

        if project_configuration.HasTools():
            filenames.append(
                f"~/rpmbuild/RPMS/<arch>/{project_name:s}-tools-<version>-1.<arch>.rpm"
            )

        filenames.append(f"~/rpmbuild/SRPMS/{project_name:s}-<version>-1.src.rpm")

        return filenames

    def _GetTemplateMappings(self, project_configuration):
        """Retrieves the template mappings.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          dict[str, str]: string template mappings, where the key maps to the name
              of a template variable.
        """
        building_table_of_contents = ""

        project_status = ""

        build_dependencies = ""

        documentation = ""

        development_table_of_contents = ""

        development_main_object_python_pre_open = ""
        development_main_object_python_post_open = ""
        development_main_object_python_post_open_file_object = ""

        tests_profiles = ""

        troubleshooting_example = ""

        cygwin_executables = ""

        gcc_mount_tool = ""

        mingw_executables = ""

        msvscpp_build_git = ""
        msvscpp_mount_tool = ""

        rpm_rename_source_package = ""

        mount_tool_additional_arguments = ""
        mount_tool_source_description_long = ""
        mount_tool_file_entry_example = ""

        project_name = project_configuration.project_name
        project_name_suffix = project_name[3:]
        python_bindings_name = f"py{project_name_suffix:s}"
        mount_tool_name = f"{project_name_suffix:s}mount"
        tools_name = f"{project_name_suffix:s}tools"

        if project_configuration.project_status:
            project_status += f"-{project_configuration.project_status:s}"

        if project_configuration.project_documentation_url:
            documentation = f"* [Documentation]({project_configuration.project_documentation_url:s})\n"

        if project_configuration.library_build_dependencies:
            for dependency in project_configuration.library_build_dependencies:
                build_dependencies += f"* {dependency:s}\n"

        if project_configuration.HasTests() and project_configuration.tests_profiles:
            for profile in project_configuration.tests_profiles:
                tests_profiles += f"* {profile:s}\n"

        if project_configuration.troubleshooting_example:
            troubleshooting_example = project_configuration.troubleshooting_example

        building_table_of_contents += (
            f"The {project_name:s} source code can be build with different "
            f"compilers:\n\n"
        )
        # Git support.
        git_apt_dependencies = [
            "git",
            "autoconf",
            "automake",
            "autopoint",
            "libtool",
            "make",
            "pkg-config",
        ]
        if project_configuration.HasDependencyLex():
            git_apt_dependencies.append("flex")

        if project_configuration.HasDependencyYacc():
            git_apt_dependencies.append("bison")

        git_apt_dependencies = " ".join(git_apt_dependencies)

        git_dnf_dependencies = [
            "git",
            "autoconf",
            "automake",
            "gettext-devel",
            "libtool",
            "make",
            "pkg-config",
        ]
        if project_configuration.HasDependencyLex():
            git_dnf_dependencies.append("flex")

        if project_configuration.HasDependencyYacc():
            git_dnf_dependencies.append("byacc")

        git_dnf_dependencies = " ".join(git_dnf_dependencies)

        git_build_dependencies = [
            "git",
            "aclocal",
            "autoconf",
            "automake",
            "autopoint or gettextize",
            "libtoolize",
            "make",
            "pkg-config",
        ]
        if project_configuration.HasDependencyLex():
            git_build_dependencies.append("flex")

        if project_configuration.HasDependencyYacc():
            git_build_dependencies.append("byacc")

        git_build_dependencies = "\n".join(
            [f"* {dependency:s}" for dependency in git_build_dependencies]
        )
        git_macports_dependencies = [
            "git",
            "autoconf",
            "automake",
            "gettext",
            "libtool",
            "make",
            "pkgconfig",
        ]
        if project_configuration.HasDependencyLex():
            git_macports_dependencies.append("flex")

        if project_configuration.HasDependencyYacc():
            git_macports_dependencies.append("byacc")

        git_macports_dependencies = " ".join(git_macports_dependencies)

        git_msvscpp_dependencies = [".\\synclibs.ps1"]

        if (
            project_configuration.HasDependencyLex()
            or project_configuration.HasDependencyYacc()
        ):
            git_msvscpp_dependencies.append(".\\syncwinflexbison.ps1")

        if project_configuration.HasDependencyZlib():
            git_msvscpp_dependencies.append(".\\synczlib.ps1")

        git_msvscpp_dependencies = "\n".join(git_msvscpp_dependencies)

        # GCC support.
        building_table_of_contents += (
            "* [Using GNU Compiler Collection (GCC)]"
            "(Building#using-gnu-compiler-collection-gcc)\n"
        )
        gcc_build_dependencies = []
        gcc_static_build_dependencies = []

        if project_configuration.HasDependencyLex():
            gcc_build_dependencies.append("flex")

        if project_configuration.HasDependencyYacc():
            gcc_build_dependencies.append("byacc")

        if project_configuration.HasDependencyZlib():
            gcc_build_dependencies.append(
                "zlib (for DEFLATE compression support) (optional but recommended, "
                "can be disabled by --with-zlib=no)"
            )
            gcc_static_build_dependencies.append(
                "zlib (for DEFLATE compression support) (optional but recommended, "
                "can be disabled by --with-zlib=no)"
            )

        if project_configuration.HasDependencyBzip2():
            gcc_build_dependencies.append(
                "bzip2 (required for bzip2 compression support)"
            )
            gcc_static_build_dependencies.append(
                "bzip2 (required for bzip2 compression support)"
            )

        if project_configuration.HasDependencyCrypto():
            gcc_build_dependencies.append(
                "libcrypto (part of OpenSSL) (optional but recommended, can be "
                "disabled by --with-openssl=no)"
            )
            gcc_static_build_dependencies.append(
                "libcrypto (part of OpenSSL) (optional but recommended, can be "
                "disabled by --with-openssl=no)"
            )

        if "fuse" in project_configuration.tools_build_dependencies:
            gcc_static_build_dependencies.append(
                "fuse (optional, can be disabled by --with-libfuse=no)"
            )

        gcc_build_dependencies.extend(project_configuration.gcc_build_dependencies)
        gcc_static_build_dependencies.extend(
            project_configuration.gcc_build_dependencies
        )
        gcc_build_dependencies = "\n".join(
            [f"* {dependency:s}" for dependency in gcc_build_dependencies]
        )
        if gcc_build_dependencies:
            gcc_build_dependencies = (
                f"\n"
                f"Also make sure to have the following dependencies including source "
                f"headers installed:\n"
                f"{gcc_build_dependencies:s}\n"
            )

        gcc_static_build_dependencies = "\n".join(
            [f"* {dependency:s}" for dependency in gcc_static_build_dependencies]
        )
        # Cygwin support.
        building_table_of_contents += "  * [Using Cygwin](Building#cygwin)\n"

        cygwin_build_dependencies = self._GetCygwinBuildDependencies(
            project_configuration
        )
        cygwin_build_dependencies = "\n".join(
            [f"* {dependency:s}" for dependency in cygwin_build_dependencies]
        )
        cygwin_dll_dependencies = self._GetCygwinDLLDependencies(project_configuration)
        cygwin_dll_dependencies = "\n".join(
            [f"* {dependency:s}" for dependency in cygwin_dll_dependencies]
        )
        if project_configuration.HasTools():
            cygwin_executables += "And the following executables:\n" "```\n"

            # TODO: use tools_features to generate tools_names
            for name in project_configuration.tools_names:
                cygwin_executables += (
                    f"{project_configuration.tools_directory:s}/.libs/{name:s}.exe\n"
                )

            cygwin_executables += "```\n"

        # Fuse support.
        if "fuse" in project_configuration.tools_build_dependencies:
            gcc_mount_tool += (
                f"\n"
                f"If you want to be able to use {mount_tool_name:s}, make sure that:\n"
                f"\n"
                f"* on a Linux system you have libfuse3-dev (Debian-based) or "
                f"fuse3-devel (RedHat-based) installed.\n"
                f"* on a macOS system, you have OSXFuse (http://osxfuse.github.com/) "
                f"installed.\n"
            )

        # MinGW support.
        building_table_of_contents += (
            "* [Using Minimalist GNU for Windows (MinGW)]"
            "(Building#using-minimalist-gnu-for-windows-mingw)\n"
        )
        mingw_build_dependencies = self._GetMinGWBuildDependencies(
            project_configuration
        )
        mingw_build_dependencies = "\n".join(
            [f"* {dependency:s}" for dependency in mingw_build_dependencies]
        )
        mingw_dll_dependencies = self._GetMinGWDLLDependencies(project_configuration)
        mingw_dll_dependencies = "\n".join(
            [f"* {dependency:s}" for dependency in mingw_dll_dependencies]
        )
        if project_configuration.HasTools():
            mingw_executables += "And the following executables:\n" "```\n"

            # TODO: use tools_features to generate tools_names
            for name in project_configuration.tools_names:
                mingw_executables += (
                    f"{project_configuration.tools_directory:s}/.libs/{name:s}.exe\n"
                )

            mingw_executables += "```\n" "\n"

        # Visual Studio support.
        building_table_of_contents += (
            "* [Using Microsoft Visual Studio]"
            "(Building#using-microsoft-visual-studio)\n"
        )
        msvscpp_build_dependencies = self._GetVisualStudioBuildDependencies(
            project_configuration
        )
        msvscpp_build_dependencies = "\n".join(
            [f"* {dependency:s}" for dependency in msvscpp_build_dependencies]
        )
        if msvscpp_build_dependencies:
            msvscpp_build_dependencies = (
                f"\n"
                f"To compile {project_name:s} using Microsoft Visual Studio you'll "
                f"need:\n"
                f"\n"
                f"{msvscpp_build_dependencies:s}\n"
            )

        msvscpp_dll_dependencies = self._GetVisualStudioDLLDependencies(
            project_configuration
        )
        msvscpp_dll_dependencies = "\n".join(
            [f"* {dependency:s}" for dependency in msvscpp_dll_dependencies]
        )
        if msvscpp_dll_dependencies:
            msvscpp_dll_dependencies = (
                f"{project_name:s}.dll is dependent on:\n"
                f"{msvscpp_dll_dependencies:s}\n"
                f"\n"
                f"These DLLs can be found in the same directory as "
                f"{project_name:s}.dll.\n"
            )

        msvscpp_build_git = (
            f"\n"
            f"Note that if you want to build {project_name:s} from source checked out "
            f"of git with Visual Studio make sure the autotools are able to make a "
            f"distribution package of {project_name:s} before trying to build it.\n"
            f'You can create distribution package by running: "make dist".\n'
        )
        if project_configuration.HasDependencyDokan():
            msvscpp_mount_tool += (
                f"\n"
                f"If you want to be able to use {mount_tool_name:s} you'll need Dokan "
                f"library see the corresponding section below.\n"
                f"Otherwise ignore or remove the dokan_dll and {mount_tool_name:s} "
                f"Visual Studio project files.\n"
            )

        building_table_of_contents += "\n"

        building_table_of_contents += (
            "Or directly packaged with different package managers:\n\n"
        )
        # Dpkg support.
        dpkg_build_dependencies = ""
        dpkg_filenames = ""
        if project_configuration.HasDpkg():
            building_table_of_contents += (
                "* [Using Debian package tools (DEB)]"
                "(Building#using-debian-package-tools-deb)\n"
            )
            dpkg_build_dependencies = [
                "autotools-dev",
                "build-essential",
                "debhelper",
                "dh-autoreconf",
                "dh-python",
                "fakeroot",
                "pkg-config",
            ]
            dpkg_build_dependencies.extend(
                self._GetDpkgBuildDependencies(project_configuration)
            )
            dpkg_build_dependencies = " ".join(sorted(dpkg_build_dependencies))

            dpkg_filenames = self._GetDpkgFilenames(project_configuration)
            dpkg_filenames = "\n".join(dpkg_filenames)

        # Rpm support.
        rpm_build_dependencies = ""
        rpm_filenames = ""
        rpm_rename_source_package = ""
        if project_configuration.HasRpm():
            building_table_of_contents += (
                "* [Using RedHat package tools (RPM)]"
                "(Building#using-redhat-package-tools-rpm)\n"
            )
            rpm_build_dependencies = self._GetRpmBuildDependencies(
                project_configuration
            )
            rpm_build_dependencies = " ".join(rpm_build_dependencies)

            if project_configuration.project_status != "stable":
                rpm_rename_source_package += (
                    f"mv {project_name:s}-{project_configuration.project_status:s}-"
                    f"<version>.tar.gz {project_name:s}-<version>.tar.gz\n"
                )

            rpm_filenames = self._GetRpmFilenames(project_configuration)
            rpm_filenames = "\n".join(rpm_filenames)

        # macOS pkgbuild support.
        building_table_of_contents += (
            "* [Using macOS pkgbuild](Building#using-macos-pkgbuild)\n"
        )
        macos_pkg_configure_options = ""
        if project_configuration.HasPythonModule():
            macos_pkg_configure_options = " --enable-python --with-pyprefix"

        if project_configuration.HasPythonModule():
            building_table_of_contents += (
                "* [Building a Python wheel](Building#building-a-python-wheel)\n"
            )

        development_table_of_contents += "* [C/C++ development](C-development)\n"

        if project_configuration.HasPythonModule():
            development_table_of_contents += (
                "* [Python development](Python-development)\n"
            )

        development_item_path = project_configuration.development_item_path or ""
        if development_item_path:
            development_item_path = development_item_path.replace("\\", "\\\\")

        if project_configuration.development_main_object_python_pre_open:
            python_pre_open_string = (
                project_configuration.development_main_object_python_pre_open
            )
            development_main_object_python_pre_open = f"{python_pre_open_string:s}\n"

        if project_configuration.development_main_object_python_post_open:
            python_post_open_string = "\n".join(
                project_configuration.development_main_object_python_post_open
            )
            development_main_object_python_post_open = f"{python_post_open_string:s}\n"

        if project_configuration.development_main_object_python_post_open_file_object:
            python_post_open_file_object_string = "\n".join(
                project_configuration.development_main_object_python_post_open_file_object
            )
            development_main_object_python_post_open_file_object = (
                f"{python_post_open_file_object_string:s}\n"
            )
        elif project_configuration.development_main_object_python_post_open:
            python_post_open_string = "\n".join(
                project_configuration.development_main_object_python_post_open
            )
            development_main_object_python_post_open_file_object = (
                f"{python_post_open_string:s}\n"
            )

        if project_configuration.mount_tool_file_entry_example:
            mount_tool_file_entry_example = (
                project_configuration.mount_tool_file_entry_example
            )
            mount_tool_file_entry_example_windows = (
                mount_tool_file_entry_example.replace("\\x", "^x").replace("/", "\\")
            )
        else:
            mount_tool_file_entry_example = f"{project_name[3:]:s}1"
            mount_tool_file_entry_example_windows = (
                mount_tool_file_entry_example.upper()
            )

        if project_configuration.mount_tool_additional_arguments:
            mount_tool_additional_arguments = (
                project_configuration.mount_tool_additional_arguments
            )

        if project_configuration.mount_tool_source_description_long:
            mount_tool_source_description_long = (
                project_configuration.mount_tool_source_description_long
            )
        else:
            mount_tool_source_description_long = (
                project_configuration.mount_tool_source_description
            )

        if project_configuration.library_name == "libewf":
            shared_object_version = "3"
        else:
            shared_object_version = "1"

        tests_example_filename1 = (
            project_configuration.tests_example_filename1 or "example1"
        )
        tests_example_filename2 = (
            project_configuration.tests_example_filename2 or "example2"
        )
        template_mappings = {
            "building_table_of_contents": building_table_of_contents,
            "project_name": project_name,
            "project_name_suffix": project_name_suffix,
            "project_status": project_status,
            "project_description": project_configuration.project_description,
            "project_git_url": project_configuration.project_git_url,
            "project_downloads_url": project_configuration.project_downloads_url,
            "build_dependencies": build_dependencies,
            "python_bindings_name": python_bindings_name,
            "mount_tool_file_entry_example": mount_tool_file_entry_example,
            "mount_tool_file_entry_example_windows": (
                mount_tool_file_entry_example_windows
            ),
            "mount_tool_name": mount_tool_name,
            "tools_name": tools_name,
            "documentation": documentation,
            "development_table_of_contents": development_table_of_contents,
            "development_prefix": project_name_suffix,
            "development_item_object": (project_configuration.development_item_object),
            "development_item_path": development_item_path,
            "development_main_object": (project_configuration.development_main_object),
            "development_main_object_filename": (
                project_configuration.development_main_object_filename
            ),
            "development_main_object_python_pre_open": (
                development_main_object_python_pre_open
            ),
            "development_main_object_python_post_open": (
                development_main_object_python_post_open
            ),
            "development_main_object_python_post_open_file_object": (
                development_main_object_python_post_open_file_object
            ),
            "development_main_object_size": (
                project_configuration.development_main_object_size
            ),
            "tests_profiles": tests_profiles,
            "tests_example_filename1": tests_example_filename1,
            "tests_example_filename2": tests_example_filename2,
            "troubleshooting_example": troubleshooting_example,
            "cygwin_build_dependencies": cygwin_build_dependencies,
            "cygwin_dll_dependencies": cygwin_dll_dependencies,
            "cygwin_dll_filename": project_configuration.cygwin_dll_filename,
            "cygwin_executables": cygwin_executables,
            "gcc_build_dependencies": gcc_build_dependencies,
            "gcc_static_build_dependencies": gcc_static_build_dependencies,
            "gcc_mount_tool": gcc_mount_tool,
            "git_apt_dependencies": git_apt_dependencies,
            "git_build_dependencies": git_build_dependencies,
            "git_dnf_dependencies": git_dnf_dependencies,
            "git_macports_dependencies": git_macports_dependencies,
            "git_msvscpp_dependencies": git_msvscpp_dependencies,
            "mingw_build_dependencies": mingw_build_dependencies,
            "mingw_dll_dependencies": mingw_dll_dependencies,
            "mingw_dll_filename": project_configuration.mingw_dll_filename,
            "mingw_executables": mingw_executables,
            "msvscpp_build_dependencies": msvscpp_build_dependencies,
            "msvscpp_build_git": msvscpp_build_git,
            "msvscpp_dll_dependencies": msvscpp_dll_dependencies,
            "msvscpp_mount_tool": msvscpp_mount_tool,
            "dpkg_build_dependencies": dpkg_build_dependencies,
            "dpkg_filenames": dpkg_filenames,
            "macos_pkg_configure_options": macos_pkg_configure_options,
            "rpm_build_dependencies": rpm_build_dependencies,
            "rpm_filenames": rpm_filenames,
            "rpm_rename_source_package": rpm_rename_source_package,
            "mount_tool_additional_arguments": mount_tool_additional_arguments,
            "mount_tool_mounted_description": (
                project_configuration.mount_tool_mounted_description
            ),
            "mount_tool_source": project_configuration.mount_tool_source,
            "mount_tool_source_description": (
                project_configuration.mount_tool_source_description
            ),
            "mount_tool_source_description_long": (mount_tool_source_description_long),
            "shared_object_version": shared_object_version,
        }
        return template_mappings

    def _GetVisualStudioBuildDependencies(self, project_configuration):
        """Retrieves the Visual Studio build dependencies.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: Visual Studio build dependencies.
        """
        dependencies = []

        if "zlib" in project_configuration.library_build_dependencies:
            dependencies.append("zlib (for DEFLATE compression support)")

        if project_configuration.HasDependencyBzip2():
            dependencies.append("bzip2 (required for bzip2 compression support)")

        dependencies.extend(project_configuration.msvscpp_build_dependencies)

        return dependencies

    def _GetVisualStudioDLLDependencies(self, project_configuration):
        """Retrieves the Visual Studio DLL dependencies.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          list[str]: Visual Studio DLL dependencies.
        """
        dependencies = []

        if "zlib" in project_configuration.library_build_dependencies:
            dependencies.append("zlib.dll")

        if project_configuration.HasDependencyBzip2():
            dependencies.append("bzip2.dll")

        dependencies.extend(project_configuration.msvscpp_dll_dependencies)

        return dependencies

    def _ReadTemplateFile(self, filename):
        """Reads a template string from file.

        Args:
          filename (str): path of the file containing the template string.

        Returns:
          TemplateString: template string.
        """
        path = os.path.join(self._templates_path, filename)

        # Read with binary mode to make sure end of line characters are not
        # converted.
        with open(path, "rb") as file_object:
            file_data = file_object.read()

        file_data = file_data.decode("utf8")

        return TemplateString(file_data)

    @abc.abstractmethod
    def Generate(self, project_configuration, output_writer):
        """Generates a wiki page.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """

    @abc.abstractmethod
    def HasContent(self, project_configuration):
        """Determines if the generator will generate content.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          bool: True if the generator will generate content.
        """


class BuildingPageGenerator(WikiPageGenerator):
    """Class that generates the "Building from source" wiki page."""

    def Generate(self, project_configuration, output_writer):
        """Generates a wiki page.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        template_mappings = self._GetTemplateMappings(project_configuration)
        self._GenerateSection("introduction.txt", template_mappings, output_writer)

        self._GenerateSection("source.txt", template_mappings, output_writer)
        self._GenerateSection(
            "source_distribution_package.txt", template_mappings, output_writer
        )
        self._GenerateSection("source_git.txt", template_mappings, output_writer)

        self._GenerateSection("gcc.txt", template_mappings, output_writer)

        if project_configuration.HasDebugOutput():
            self._GenerateSection(
                "gcc_debug_output.txt", template_mappings, output_writer
            )

        self._GenerateSection(
            "gcc_static_library.txt", template_mappings, output_writer
        )

        if project_configuration.HasTools():
            self._GenerateSection(
                "gcc_static_executables.txt", template_mappings, output_writer
            )

        if project_configuration.HasPythonModule():
            self._GenerateSection("gcc_python.txt", template_mappings, output_writer)

        self._GenerateSection("cygwin.txt", template_mappings, output_writer)
        self._GenerateSection("gcc_macos.txt", template_mappings, output_writer)

        if project_configuration.HasPythonModule():
            self._GenerateSection(
                "gcc_macos_python.txt", template_mappings, output_writer
            )

        self._GenerateSection("gcc_solaris.txt", template_mappings, output_writer)

        # MinGW support.
        self._GenerateSection("mingw.txt", template_mappings, output_writer)
        # TODO: generate MinGW-MSYS2 information
        # self._GenerateSection('mingw_msys2.txt', template_mappings, output_writer)
        self._GenerateSection("mingw_dll.txt", template_mappings, output_writer)
        self._GenerateSection(
            "mingw_troubleshooting.txt", template_mappings, output_writer
        )

        # Visual Studio support.
        self._GenerateSection("msvscpp.txt", template_mappings, output_writer)

        if project_configuration.HasDebugOutput():
            self._GenerateSection("msvscpp_debug.txt", template_mappings, output_writer)

        if "zlib" in project_configuration.library_build_dependencies:
            self._GenerateSection("msvscpp_zlib.txt", template_mappings, output_writer)

        if project_configuration.HasDependencyDokan():
            self._GenerateSection("msvscpp_dokan.txt", template_mappings, output_writer)

        if project_configuration.HasPythonModule():
            self._GenerateSection(
                "msvscpp_python.txt", template_mappings, output_writer
            )

        self._GenerateSection("msvscpp_build.txt", template_mappings, output_writer)
        self._GenerateSection("msvscpp_dll.txt", template_mappings, output_writer)

        self._GenerateSection("msvscpp_2010.txt", template_mappings, output_writer)

        if project_configuration.HasDpkg():
            self._GenerateSection("dpkg.txt", template_mappings, output_writer)

        if project_configuration.HasRpm():
            self._GenerateSection("rpm.txt", template_mappings, output_writer)

        self._GenerateSection("macos_pkg.txt", template_mappings, output_writer)

        if project_configuration.HasPythonModule():
            self._GenerateSection("python_wheel.txt", template_mappings, output_writer)

    def HasContent(self, project_configuration):
        """Determines if the generator will generate content.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          bool: True if the generator will generate content.
        """
        return True


class DevelopmentPageGenerator(WikiPageGenerator):
    """Class that generates the "Development" wiki page."""

    def Generate(self, project_configuration, output_writer):
        """Generates a wiki page.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        template_mappings = self._GetTemplateMappings(project_configuration)
        self._GenerateSection("main.txt", template_mappings, output_writer)

    def HasContent(self, project_configuration):
        """Determines if the generator will generate content.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          bool: True if the generator will generate content.
        """
        return project_configuration.HasPythonModule()


class CDevelopmentPageGenerator(WikiPageGenerator):
    """Class that generates the "C/C++ development" wiki page."""

    def Generate(self, project_configuration, output_writer):
        """Generates a wiki page.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        # TODO: add support for also_see.txt, main_object.txt

        template_mappings = self._GetTemplateMappings(project_configuration)
        self._GenerateSection("main.txt", template_mappings, output_writer)

        if project_configuration.development_main_object:
            if project_configuration.development_glob:
                self._GenerateSection(
                    "main_object_with_glob.txt", template_mappings, output_writer
                )

            else:
                self._GenerateSection(
                    "main_object.txt", template_mappings, output_writer
                )

        self._GenerateSection("also_see.txt", template_mappings, output_writer)

    def HasContent(self, project_configuration):
        """Determines if the generator will generate content.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          bool: True if the generator will generate content.
        """
        return True


class PythonDevelopmentPageGenerator(WikiPageGenerator):
    """Class that generates the "Python development" wiki page."""

    def Generate(self, project_configuration, output_writer):
        """Generates a wiki page.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        template_mappings = self._GetTemplateMappings(project_configuration)
        self._GenerateSection("main.txt", template_mappings, output_writer)

        if project_configuration.development_main_object:
            if project_configuration.development_glob:
                self._GenerateSection(
                    "main_object_with_glob.txt", template_mappings, output_writer
                )

            else:
                self._GenerateSection(
                    "main_object.txt", template_mappings, output_writer
                )

        if project_configuration.development_item_object:
            self._GenerateSection("item_object.txt", template_mappings, output_writer)

        if project_configuration.development_pytsk3:
            if project_configuration.development_glob:
                self._GenerateSection(
                    "pytsk3_with_glob.txt", template_mappings, output_writer
                )

            else:
                self._GenerateSection("pytsk3.txt", template_mappings, output_writer)

        # TODO: move main object out of this template and create on demand.
        self._GenerateSection("also_see.txt", template_mappings, output_writer)

    def HasContent(self, project_configuration):
        """Determines if the generator will generate content.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          bool: True if the generator will generate content.
        """
        return project_configuration.HasPythonModule()


class HomePageGenerator(WikiPageGenerator):
    """Class that generates the "Home" wiki page."""

    def Generate(self, project_configuration, output_writer):
        """Generates a wiki page.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        template_mappings = self._GetTemplateMappings(project_configuration)
        self._GenerateSection("introduction.txt", template_mappings, output_writer)

    def HasContent(self, project_configuration):
        """Determines if the generator will generate content.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          bool: True if the generator will generate content.
        """
        return True


class MountingPageGenerator(WikiPageGenerator):
    """Class that generates the "Mounting a ..." wiki page."""

    def Generate(self, project_configuration, output_writer):
        """Generates a wiki page.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        template_mappings = self._GetTemplateMappings(project_configuration)
        if (
            project_configuration.HasDependencyDokan()
            or "fuse" in project_configuration.tools_build_dependencies
        ):
            self._GenerateSection("introduction.txt", template_mappings, output_writer)

            if project_configuration.mount_tool_source_type in (
                "file",
                "image",
                "volume",
            ):
                template_file = (
                    f"mounting_{project_configuration.mount_tool_source_type:s}.txt"
                )
                self._GenerateSection(template_file, template_mappings, output_writer)

            self._GenerateSection(
                "mounting_missing_backend.txt", template_mappings, output_writer
            )

            if project_configuration.mount_tool_file_entry_type in ("file", "volume"):
                template_file = (
                    f"mounting_{project_configuration.mount_tool_source_type:s}_"
                    f"contents.txt"
                )
                self._GenerateSection(template_file, template_mappings, output_writer)

            if project_configuration.mount_tool_source_type == "volume":
                self._GenerateSection(
                    "obtaining_volume_offset.txt", template_mappings, output_writer
                )

            self._GenerateSection(
                "mounting_root_access.txt", template_mappings, output_writer
            )
            if project_configuration.HasDependencyDokan():
                if project_configuration.mount_tool_source_type in (
                    "file",
                    "image",
                    "volume",
                ):
                    template_file = (
                        f"mounting_{project_configuration.mount_tool_source_type:s}_"
                        f"windows.txt"
                    )
                    self._GenerateSection(
                        template_file, template_mappings, output_writer
                    )

            self._GenerateSection("unmounting.txt", template_mappings, output_writer)

            if project_configuration.HasDependencyDokan():
                self._GenerateSection(
                    "unmounting_windows.txt", template_mappings, output_writer
                )

            self._GenerateSection(
                "troubleshooting.txt", template_mappings, output_writer
            )

    def HasContent(self, project_configuration):
        """Determines if the generator will generate content.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          bool: True if the generator will generate content.
        """
        if (
            project_configuration.HasDependencyDokan()
            or "fuse" in project_configuration.tools_build_dependencies
        ):
            return True

        return False


class TestingPageGenerator(WikiPageGenerator):
    """Class that generates the "Testing" wiki page."""

    def Generate(self, project_configuration, output_writer):
        """Generates a wiki page.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        # TODO: implement testing page without input files.
        template_mappings = self._GetTemplateMappings(project_configuration)
        if project_configuration.HasTests():
            self._GenerateSection("tests.txt", template_mappings, output_writer)

            if project_configuration.tests_profiles:
                self._GenerateSection(
                    "tests_profiles.txt", template_mappings, output_writer
                )
                self._GenerateSection(
                    "tests_files.txt", template_mappings, output_writer
                )

    def HasContent(self, project_configuration):
        """Determines if the generator will generate content.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          bool: True if the generator will generate content.
        """
        if project_configuration.HasTests():
            return True

        return False


class TroubleshootingPageGenerator(WikiPageGenerator):
    """Class that generates the "Troubleshooting" wiki page."""

    def Generate(self, project_configuration, output_writer):
        """Generates a wiki page.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        template_mappings = self._GetTemplateMappings(project_configuration)
        self._GenerateSection("introduction.txt", template_mappings, output_writer)
        self._GenerateSection("build_errors.txt", template_mappings, output_writer)
        self._GenerateSection("runtime_errors.txt", template_mappings, output_writer)

        if project_configuration.HasDebugOutput():
            self._GenerateSection("format_errors.txt", template_mappings, output_writer)

        if project_configuration.HasTools():
            self._GenerateSection("crashes.txt", template_mappings, output_writer)

    def HasContent(self, project_configuration):
        """Determines if the generator will generate content.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          bool: True if the generator will generate content.
        """
        return True


class FileWriter:
    """Class that defines a file output writer."""

    def __init__(self, name):
        """Initializes an output writer.

        Args:
          name (str): name of the output.
        """
        super().__init__()
        self._file_object = None
        self._name = name

    def Open(self):
        """Opens the output writer object.

        Returns:
          bool: True if successful or False if not.
        """
        self._file_object = open(self._name, "w", encoding="utf8")
        return True

    def Close(self):
        """Closes the output writer object."""
        self._file_object.close()

    def Write(self, data):
        """Writes the data to file.

        Args:
          data (bytes): data to write.
        """
        self._file_object.write(data)


class StdoutWriter:
    """Class that defines a stdout output writer."""

    def Open(self):
        """Opens the output writer object.

        Returns:
          bool: True if successful or False if not.
        """
        return True

    def Close(self):
        """Closes the output writer object."""
        return

    def Write(self, data):
        """Writes the data to stdout (without the default trailing newline).

        Args:
          data (bytes): data to write.
        """
        print(data, end="")


def Main():
    """Entry point of console script.

    Returns:
      int: exit code that is provided to sys.exit().
    """
    argument_parser = argparse.ArgumentParser(
        description="Generates wiki pages of the libyal libraries."
    )
    argument_parser.add_argument(
        "configuration_file",
        action="store",
        metavar="CONFIGURATION_FILE",
        default="project-wiki.ini",
        help="The wiki generation configuration file.",
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

    project_configuration = configuration.ProjectConfiguration()
    project_configuration.ReadFromFile(options.configuration_file)

    readme_file = os.path.join(os.path.dirname(options.configuration_file), "README")

    LINK_RE = re.compile(r"\* (.*): (http[s]://.*)")

    last_line_was_header = False

    project_description = []
    if os.path.exists(readme_file):
        with open(readme_file, encoding="utf8") as file_object:
            for line in file_object.readlines():
                if line.startswith("For more information see:"):
                    project_description.pop()
                    break

                if last_line_was_header:
                    last_line_was_header = False
                    if line != "\n":
                        # Add an empty line to make sure unnumbered list are formatted
                        # correctly by most markdown parsers.
                        project_description.append("\n")

                line = LINK_RE.sub(r"* [\1](\2)", line)
                project_description.append(line)

                if line.endswith(":\n"):
                    last_line_was_header = True

    project_configuration.project_description = "".join(project_description)

    libyal_directory = os.path.abspath(__file__)
    libyal_directory = os.path.dirname(libyal_directory)
    libyal_directory = os.path.dirname(libyal_directory)

    # TODO: generate more wiki pages.
    wiki_pages = [
        ("Building", BuildingPageGenerator),
        ("Development", DevelopmentPageGenerator),
        ("Home", HomePageGenerator),
        ("Mounting", MountingPageGenerator),
        ("C-development", CDevelopmentPageGenerator),
        ("Python-development", PythonDevelopmentPageGenerator),
        ("Testing", TestingPageGenerator),
        ("Troubleshooting", TroubleshootingPageGenerator),
    ]
    for page_name, page_generator_class in wiki_pages:
        templates_path = os.path.join(libyal_directory, "data", "wiki", page_name)
        wiki_page = page_generator_class(templates_path)

        if not wiki_page.HasContent(project_configuration):
            continue

        if options.output_directory:
            output_file = os.path.join(options.output_directory, f"{page_name:s}.md")
            output_writer = FileWriter(output_file)
        else:
            output_writer = StdoutWriter()

        if not output_writer.Open():
            print("Unable to open output writer.")
            print("")
            return 1

        wiki_page.Generate(project_configuration, output_writer)

        output_writer.Close()

    # TODO: add support for Unicode templates.

    return 0


if __name__ == "__main__":
    sys.exit(Main())
