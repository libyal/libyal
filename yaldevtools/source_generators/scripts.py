"""The source file generator for script files."""

import os
import stat

from yaldevtools.source_generators import interface


class TestProfile:
    """Test profile.

    Attributes:
      glob (str): glob of the input files.
      name (str): name of the profile.
      options (str): options.
    """

    def __init__(self, name):
        """Initializes a test profile.

        Args:
          name (str): name of the profile.
        """
        super().__init__()
        self.glob = "*"
        self.name = name
        self.options = ""


class ScriptFileGenerator(interface.SourceFileGenerator):
    """Script files generator."""

    def Generate(self, project_configuration, output_writer):
        """Generates script files.

        Args:
          project_configuration (ProjectConfiguration): project configuration.
          output_writer (OutputWriter): output writer.
        """
        makefile_am_file = self._GetMainMakefileAM(project_configuration)

        mount_tool_filename = os.path.join(
            project_configuration.tools_directory,
            f"{project_configuration.library_name_suffix:s}mount.c",
        )
        shared_libs = list(makefile_am_file.libraries)
        if "bzip2" in shared_libs:
            shared_libs.remove("bzip2")
        if "libcrypto" in shared_libs:
            shared_libs.remove("libcrypto")
        if "libdl" in shared_libs:
            shared_libs.remove("libdl")
        if "lzma" in shared_libs:
            shared_libs.remove("lzma")
        if "pthread" in shared_libs:
            shared_libs.remove("pthread")
        if "zlib" in shared_libs:
            shared_libs.remove("zlib")

        template_mappings = self._GetTemplateMappings(project_configuration)
        template_mappings["local_libs"] = " ".join(sorted(makefile_am_file.libraries))
        template_mappings["shared_libs"] = " ".join(shared_libs)

        for directory_entry in os.listdir(self._templates_path):
            template_filename = os.path.join(self._templates_path, directory_entry)
            if not os.path.isfile(template_filename):
                continue

            if template_filename.endswith(".swp"):
                continue

            if template_filename.endswith(".yaml"):
                continue

            if directory_entry in (
                "syncbzip2.ps1",
                "syncwinflexbison.ps1",
                "synczlib.ps1",
            ):
                if not os.path.exists(directory_entry):
                    continue

            if directory_entry in ("builddokan.ps1", "syncdokan.ps1"):
                if not os.path.exists(mount_tool_filename):
                    continue

            output_filename = directory_entry

            self._GenerateSection(template_filename, template_mappings, output_filename)

            if output_filename.endswith(".sh"):
                # Set the x-bit for a shell script (.sh).
                stat_info = os.stat(output_filename)
                os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

        if os.path.exists("synctestdata.sh"):
            test_profiles = []

            for index, name in enumerate(project_configuration.tests_profiles):
                glob_per_profile = ""
                options_per_profile = ""
                if project_configuration.tests_glob_per_profile:
                    glob_per_profile = project_configuration.tests_glob_per_profile[
                        index
                    ]
                if project_configuration.tests_options_per_profile:
                    options_per_profile = (
                        project_configuration.tests_options_per_profile[index]
                    )

                if glob_per_profile or options_per_profile:
                    test_profile = TestProfile(name)
                    if glob_per_profile:
                        test_profile.glob = glob_per_profile
                    if options_per_profile:
                        test_profile.options = options_per_profile

                    test_profiles.append(test_profile)

            template_mappings["test_data_files"] = " ".join(
                project_configuration.test_data_files
            )
            template_mappings["test_data_path"] = project_configuration.test_data_path
            template_mappings["test_data_repository"] = (
                project_configuration.test_data_repository
            )
            template_mappings["test_profiles"] = test_profiles

            for extension in ("ps1", "sh"):
                self._GenerateSectionsFromOperationsFile(
                    f"synctestdata.{extension:s}.yaml",
                    "main",
                    project_configuration,
                    template_mappings,
                    f"synctestdata.{extension:s}",
                )

            del template_mappings["test_data_files"]
            del template_mappings["test_data_path"]
            del template_mappings["test_data_repository"]
            del template_mappings["test_profiles"]
