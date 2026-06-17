# Tests tools functions and types.

$$ToolsTests = "${tools_tests}"
# TODO: read options sets from project.ini
$$OptionSets = "${tests_option_sets_ps1}" -split " "

. .\test_functions.ps1
