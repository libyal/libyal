"""The source file generator for man page files."""

import difflib
import logging
import os
import re
import shutil
import time

from yaldevtools.source_generators import interface


class LibraryManPageGenerator(interface.SourceFileGenerator):
    """Library man page file (libyal.3) generator."""

    _TOKEN_RE = re.compile(r'"(?:[^"\\])*"|[^\s"]+')

    def _WrapFunctionLine(self, text, maximum_length=80):
        """Wraps a function line.

        Args:
          line (str): line to wrap.
          maximum_length (int): maximum line length.

        Returns:
          str: wrapped line.
        """
        tokens = self._TOKEN_RE.findall(text)
        if not tokens:
            return text

        lines = []
        current_line = f".Fn {tokens[0]:s}"

        for token in tokens[1:]:
            line = f"{current_line:s} {token:s}"
            line_length = len(line)

            if line_length <= maximum_length:
              current_line = line

            else:
                lines.append(f"{current_line:s} \\")
                current_line = token

        lines.append(current_line)
        return "\n".join(lines)[4:]

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
          template_mappings (dict[str, str]): template mappings, where the key
              maps to the name of a template variable.
          include_header_file (LibraryIncludeHeaderFile): library include header
              file.
          output_writer (OutputWriter): output writer.
          output_filename (str): path of the output file.
        """
        pid = os.getpid()
        backup_filename = f"{output_filename:s}.{pid:d}"
        shutil.copyfile(output_filename, backup_filename)

        template_mappings["date"] = time.strftime("%B %d, %Y", time.gmtime()).replace(
            " 0", "  "
        )
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
                function_arguments_string = function_prototype.CopyToManpageString()
                function = self._WrapFunctionLine(
                    f"{function_prototype.name:s} {function_arguments_string:s}"
                )
                function_template_mappings = {
                    "function": function,
                    "function_return_type": function_prototype.return_type,
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
                    function_arguments_string = function_prototype.CopyToManpageString()
                    function = self._WrapFunctionLine(
                        f"{function_prototype.name:s} {function_arguments_string:s}"
                    )
                    function_template_mappings = {
                        "function": function,
                        "function_return_type": function_prototype.return_type,
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
                template_filename = os.path.join(
                    self._templates_path, "function.txt"
                )
                for function_prototype in bfio_functions:
                    function_arguments_string = function_prototype.CopyToManpageString()
                    function = self._WrapFunctionLine(
                        f"{function_prototype.name:s} {function_arguments_string:s}"
                    )
                    function_template_mappings = {
                        "function": function,
                        "function_return_type": function_prototype.return_type,
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
        with open(backup_filename, "r", encoding="utf8") as backup_file:
            backup_lines = backup_file.readlines()

        with open(output_filename, "r", encoding="utf8") as output_file:
            output_lines = output_file.readlines()

        diff_lines = list(difflib.ndiff(backup_lines[1:], output_lines[1:]))
        diff_lines = [line for line in diff_lines if line[0] in ("-", "+")]

        # Check if there are changes besides the date.
        if diff_lines:
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
