"""The source file generator for man page files."""

import difflib
import logging
import os
import re
import shutil
import textwrap
import time

from yaldevtools.source_generators import interface


class BaseManPageGenerator(interface.SourceFileGenerator):
    """Man page file generator."""

    def _CheckForChanges(self, original_filename, output_filename):
        """Compares the generated man page with the original one.

        Args:
          original_filename (str): filename of the original man page.
          output_filename (str): filename of the generated man page.
        """
        with open(original_filename, "r", encoding="utf8") as backup_file:
            backup_lines = backup_file.readlines()

        with open(output_filename, "r", encoding="utf8") as output_file:
            output_lines = output_file.readlines()

        diff_lines = list(difflib.ndiff(backup_lines[1:], output_lines[1:]))
        diff_lines = [line for line in diff_lines if line[0] in ("-", "+")]

        # Check if there are changes besides the date.
        return bool(diff_lines)

    def _GetBackupFilename(self, output_filename):
        """Retrieves a filename for the backup of the original man page.

        Args:
          output_filename (str): filename of the generated man page.

        Returns:
          str: backup filename.
        """
        pid = os.getpid()
        return f"{output_filename:s}.{pid:d}"

    def _GetHeaderDateString(self):
        """Retrieves the header date string.

        Returns:
          str: header date string.
        """
        date_string = time.strftime("%B %d, %Y", time.gmtime())
        return date_string.replace(" 0", "  ")


class LibraryManPageGenerator(BaseManPageGenerator):
    """Library man page file (libyal.3) generator."""

    def _GenerateLibraryManPage(
        self,
        project_configuration,
        template_mappings,
        include_header_file,
        output_writer,
        output_filename,
    ):
        """Generates a libyal.3 man page file.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          template_mappings (dict[str, str]): template mappings, where the key maps to
              the name of a template variable.
          include_header_file (LibraryIncludeHeaderFile): library include header file.
          output_writer (OutputWriter): output writer.
          output_filename (str): path of the output file.
        """
        backup_filename = self._GetBackupFilename(output_filename)
        shutil.copyfile(output_filename, backup_filename)

        template_mappings["date"] = self._GetHeaderDateString()

        template_filename = os.path.join(self._templates_path, "header.txt")
        self._GenerateSection(template_filename, template_mappings, output_filename)

        have_wide_character_type_functions = False
        for section_name in include_header_file.section_names:
            functions_per_section = include_header_file.functions_per_section.get(
                section_name, []
            )
            if not functions_per_section:
                continue

            section_template_mappings = {
                "section_name": section_name,
            }
            template_filename = os.path.join(self._templates_path, "section.txt")

            self._GenerateSection(
                template_filename,
                section_template_mappings,
                output_filename,
                access_mode="a",
            )
            bfio_functions = []
            debug_output_functions = []
            functions = []
            wide_character_type_functions = []
            for function_prototype in functions_per_section:
                if function_prototype.have_bfio:
                    bfio_functions.append(function_prototype)
                elif function_prototype.have_debug_output:
                    debug_output_functions.append(function_prototype)
                elif function_prototype.have_wide_character_type:
                    wide_character_type_functions.append(function_prototype)
                else:
                    functions.append(function_prototype)

            template_filename = os.path.join(self._templates_path, "function.txt")

            for function_prototype in functions:
                function_template_mappings = {
                    "function": function_prototype.CopyToManpageString()
                }
                self._GenerateSection(
                    template_filename,
                    function_template_mappings,
                    output_filename,
                    access_mode="a",
                )

            if wide_character_type_functions:
                have_wide_character_type_functions = True

                # Ignore adding the wide string support section header in some cases.
                if project_configuration.library_name != "libcsplit":
                    section_template_mappings = {
                        "section_name": (
                            "Available when compiled with wide character string "
                            "support:"
                        )
                    }
                    template_filename = os.path.join(
                        self._templates_path, "section.txt"
                    )
                    self._GenerateSection(
                        template_filename,
                        section_template_mappings,
                        output_filename,
                        access_mode="a",
                    )

                template_filename = os.path.join(self._templates_path, "function.txt")
                for function_prototype in wide_character_type_functions:
                    function_template_mappings = {
                        "function": function_prototype.CopyToManpageString()
                    }
                    self._GenerateSection(
                        template_filename,
                        function_template_mappings,
                        output_filename,
                        access_mode="a",
                    )

            if bfio_functions:
                section_template_mappings = {
                    "section_name": ("Available when compiled with libbfio support:")
                }
                template_filename = os.path.join(self._templates_path, "section.txt")
                self._GenerateSection(
                    template_filename,
                    section_template_mappings,
                    output_filename,
                    access_mode="a",
                )
                template_filename = os.path.join(self._templates_path, "function.txt")
                for function_prototype in bfio_functions:
                    function_template_mappings = {
                        "function": function_prototype.CopyToManpageString()
                    }
                    self._GenerateSection(
                        template_filename,
                        function_template_mappings,
                        output_filename,
                        access_mode="a",
                    )

            # TODO: add support for debug output functions.

        template_filename = os.path.join(self._templates_path, "description.txt")
        self._GenerateSection(
            template_filename, template_mappings, output_filename, access_mode="a"
        )
        if have_wide_character_type_functions:
            template_filename = os.path.join(self._templates_path, "notes.txt")
            self._GenerateSection(
                template_filename, template_mappings, output_filename, access_mode="a"
            )

        if have_wide_character_type_functions:
            template_filename = os.path.join(self._templates_path, "notes_wchar.txt")
            self._GenerateSection(
                template_filename, template_mappings, output_filename, access_mode="a"
            )

        template_filename = os.path.join(self._templates_path, "footer.txt")
        self._GenerateSection(
            template_filename, template_mappings, output_filename, access_mode="a"
        )
        if self._CheckForChanges(backup_filename, output_filename):
            os.remove(backup_filename)
        else:
            shutil.move(backup_filename, output_filename)

    def Generate(self, project_configuration, output_writer):
        """Generates a library man page file (libyal.3).

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        # TODO: add support for libcsystem.h - additional types
        # TODO: add support for libsigscan.h - not detecting wchar
        # TODO: add support for libsmraw.h - not detecting wchar
        #       (multiple function in single define?)
        # TODO: warn about [a-z]), in include header
        # TODO: fix libbde_volume_read_startup_key_wide ending up in wrong section

        include_header_file = self._GetLibraryIncludeHeaderFile(project_configuration)

        if include_header_file:
            template_mappings = self._GetTemplateMappings(project_configuration)

            output_filename = os.path.join(
                "manuals", f"{project_configuration.library_name:s}.3"
            )
            self._GenerateLibraryManPage(
                project_configuration,
                template_mappings,
                include_header_file,
                output_writer,
                output_filename,
            )


class InfoToolManPageGenerator(BaseManPageGenerator):
    """Info tool man page file (yalinfo.1) generator."""

    def Generate(self, project_configuration, output_writer):
        """Generates an info tool man page file (yalinfo.1).

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        info_tool_name = f"{project_configuration.library_name_suffix:s}info"

        info_tool_options = self._GetInfoToolOptions(
            project_configuration, info_tool_name
        )
        output_filename = os.path.join("manuals", f"{info_tool_name:s}.1")
        backup_filename = self._GetBackupFilename(output_filename)
        shutil.copyfile(output_filename, backup_filename)

        template_mappings = self._GetTemplateMappings(project_configuration)

        template_mappings["date"] = self._GetHeaderDateString()
        template_mappings["library_description"] = "".join(
            [
                project_configuration.library_description[0].lower(),
                project_configuration.library_description[1:],
            ]
        )
        template_mappings["info_tool_name"] = info_tool_name
        template_mappings["info_tool_source_description"] = (
            project_configuration.info_tool_source_description
        )
        template_mappings["info_tool_source_type"] = (
            project_configuration.info_tool_source_type
        )

        template_filename = os.path.join(self._templates_path, "header.txt")
        self._GenerateSection(template_filename, template_mappings, output_filename)

        nameless_options = []
        for option in info_tool_options:
            if not option.name:
                nameless_options.append(option.identifier)
                continue

            template_mappings["option"] = option
            template_filename = os.path.join(
                self._templates_path, "synopsis-option.txt"
            )
            self._GenerateSection(
                template_filename, template_mappings, output_filename, access_mode="a"
            )
            del template_mappings["option"]

        if nameless_options:
            template_mappings["option_identifiers"] = "".join(nameless_options)
            template_filename = os.path.join(
                self._templates_path, "synopsis-nameless_options.txt"
            )
            self._GenerateSection(
                template_filename, template_mappings, output_filename, access_mode="a"
            )
            del template_mappings["option_identifiers"]

        # TODO: generate SYNOPSIS (positional arguments)
        # TODO: generate DESCRIPTION (positional arguments)

        template_filename = os.path.join(self._templates_path, "description.txt")
        self._GenerateSection(
            template_filename, template_mappings, output_filename, access_mode="a"
        )
        for option in info_tool_options:
            if not option.name:
                template_filename = "description-nameless_option.txt"
            else:
                template_filename = "description-option.txt"

            template_filename = os.path.join(
                self._templates_path,
                template_filename,
            )
            template_mappings["option"] = option
            template_mappings["option_help_text"] = " \\\n".join(
                textwrap.wrap(option.help_text, width=79, break_long_words=False)
            )
            self._GenerateSection(
                template_filename, template_mappings, output_filename, access_mode="a"
            )
            del template_mappings["option"]
            del template_mappings["option_help_text"]

        template_filename = os.path.join(self._templates_path, "environment.txt")
        self._GenerateSection(
            template_filename, template_mappings, output_filename, access_mode="a"
        )
        with open(backup_filename) as input_file_object:
            with open(output_filename, "a") as output_file_object:
                in_examples = False
                for line in input_file_object.readlines():
                    if line.startswith(".Sh DIAGNOSTICS"):
                        break

                    if line.startswith(".Sh EXAMPLES"):
                        in_examples = True

                    if in_examples:
                        output_file_object.write(line)

        template_filename = os.path.join(self._templates_path, "footer.txt")
        self._GenerateSection(
            template_filename, template_mappings, output_filename, access_mode="a"
        )
        if self._CheckForChanges(backup_filename, output_filename):
            os.remove(backup_filename)
        else:
            shutil.move(backup_filename, output_filename)
