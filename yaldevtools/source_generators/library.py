"""The source file generator for library source files."""

import logging
import os

from yaldevtools.source_generators import interface


class LibrarySourceFileGenerator(interface.SourceFileGenerator):
    """Library source file generator."""

    def _GetLibraryPath(self, project_configuration):
        """Retrieves the library path.

        Args:
          project_configuration (ProjectConfiguration): project configuration.

        Returns:
          str: the library path.
        """
        return os.path.join(
            self._projects_directory,
            project_configuration.library_name,
            project_configuration.library_name,
        )

    def _GenerateTypesHeader(
        self, project_configuration, template_mappings, output_writer
    ):
        """Generates the library types header file.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          template_mappings (dict[str, str]): template mappings, where the key
              maps to the name of a template variable.
          output_writer (OutputWriter): output writer.
        """
        # TODO: add support for libuna/libuna_types.h
        # TODO: types.h alignment of debug types?

        templates_path = os.path.join(self._templates_path, "libyal_types.h")

        library_path = self._GetLibraryPath(project_configuration)
        library_name_upper = project_configuration.library_name.upper()

        output_filename = os.path.join(
            library_path, f"{project_configuration.library_name:s}_types.h"
        )
        if project_configuration.library_name in ("libcerror", "libcthreads"):
            return

        internal_types_start_line = (
            f"#endif /* defined( HAVE_LOCAL_{library_name_upper:s} ) */"
        )
        internal_types_end_line = (
            f"#endif /* !defined( _{library_name_upper:s}_INTERNAL_TYPES_H ) */"
        )
        in_internal_types = False

        internal_types = []
        if os.path.exists(output_filename):
            with open(output_filename, "r", encoding="utf8") as file_object:
                for line in file_object.readlines():
                    line = line.rstrip()

                    if in_internal_types:
                        if line == internal_types_end_line:
                            in_internal_types = False
                        else:
                            internal_types.append(line)

                    if line == internal_types_start_line:
                        in_internal_types = True

        template_filename = os.path.join(templates_path, "header.h")

        self._GenerateSection(template_filename, template_mappings, output_filename)

        if internal_types:
            output_data = "\n".join(internal_types)
            output_writer.WriteFile(output_filename, output_data, access_mode="a")

        template_filename = os.path.join(templates_path, "footer.h")

        self._GenerateSection(
            template_filename, template_mappings, output_filename, access_mode="a"
        )
        self._VerticalAlignTabs(output_filename)

    def Generate(self, project_configuration, output_writer):
        """Generates library source files.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        # TODO: libcsplit skip wide_string.[ch]
        # TODO: libsmraw/libsmraw_codepage.h alignment of definitions
        # TODO: libfvalue/libfvalue_codepage.h different

        include_header_file = self._GetTypesIncludeHeaderFile(project_configuration)

        if not include_header_file:
            logging.warning(
                f"Missing: {self._types_include_header_path:s} skipping generation of "
                f"library source files."
            )
            return

        library_path = self._GetLibraryPath(project_configuration)

        codepage_header_file = os.path.join(
            library_path, f"{project_configuration.library_name:s}_codepage.h"
        )
        error_header_file = os.path.join(
            library_path, f"{project_configuration.library_name:s}_error.h"
        )
        notify_header_file = os.path.join(
            library_path, f"{project_configuration.library_name:s}_notify.h"
        )
        # if include_header_file.types:
        #     longest_type_name = max(include_header_file.types, key=len)
        #     longest_library_debug_type_prefix = (
        #         f"typedef struct {project_configuration.library_name:s}_"
        #         f"{longest_type_name:s} {{}}"
        #     )

        library_debug_type_definitions = []
        type_definitions = []
        for type_name in include_header_file.types:
            # library_debug_type_prefix = (
            #     f"typedef struct {project_configuration.library_name:s}_"
            #     f"{type_name:s} {{}}"
            # )
            library_debug_type_definition = (
                f"typedef struct {project_configuration.library_name:s}_{type_name:s} "
                f"{{}}\t{project_configuration.library_name:s}_{type_name:s}_t;"
            )
            library_debug_type_definitions.append(library_debug_type_definition)

            type_definition = (
                f"typedef intptr_t {project_configuration.library_name:s}_"
                f"{type_name:s}_t;"
            )
            type_definitions.append(type_definition)

        template_mappings = self._GetTemplateMappings(
            project_configuration, authors_separator=",\n *                          "
        )
        template_mappings["library_debug_type_definitions"] = "\n".join(
            library_debug_type_definitions
        )
        template_mappings["library_type_definitions"] = "\n".join(type_definitions)

        authors_template_mapping = template_mappings["authors"]

        self._GenerateTypesHeader(
            project_configuration, template_mappings, output_writer
        )
        for directory_entry in os.listdir(self._templates_path):
            if not directory_entry.startswith("libyal"):
                continue

            if directory_entry.endswith(f"_{project_configuration.library_name:s}.h"):
                continue

            if directory_entry == "libyal_codepage.h" and (
                not os.path.exists(codepage_header_file)
                or project_configuration.library_name == "libclocale"
            ):
                continue

            if directory_entry in (
                "libyal_libcerror.h",
                "libyal_error.c",
                "libyal_error.h",
            ) and (
                not os.path.exists(error_header_file)
                or project_configuration.library_name == "libcerror"
            ):
                continue

            if directory_entry in (
                "libyal_libcnotify.h",
                "libyal_notify.c",
                "libyal_notify.h",
            ) and (
                not os.path.exists(notify_header_file)
                or project_configuration.library_name == "libcnotify"
            ):
                continue

            if directory_entry in ("libyal_wide_string.c", "libyal_wide_string.h") and (
                not os.path.exists(notify_header_file)
                or project_configuration.library_name == "libcsplit"
            ):
                continue

            template_filename = os.path.join(self._templates_path, directory_entry)
            if not os.path.isfile(template_filename):
                continue

            output_filename = "".join(
                [project_configuration.library_name, directory_entry[6:]]
            )
            output_filename = os.path.join(
                project_configuration.library_name, output_filename
            )
            if not directory_entry in (
                "libyal.c",
                "libyal_extern.h",
                "libyal.rc.in",
                "libyal_support.c",
                "libyal_support.h",
                "libyal_unused.h",
            ):
                # Only update if the file exists.
                if not os.path.exists(output_filename):
                    continue

            if directory_entry == "libyal.rc.in":
                template_mappings["authors"] = ", ".join(
                    project_configuration.project_authors
                )
            else:
                template_mappings["authors"] = authors_template_mapping

            self._GenerateSection(template_filename, template_mappings, output_filename)

            if directory_entry == "libyal_codepage.h":
                self._VerticalAlignTabs(output_filename)
