# Tests library functions and types.

$$LibraryTests = "${library_tests}"
$$LibraryTestsWithInput = "${library_tests_with_input}"
# TODO: read options sets from project.ini
$$OptionSets = "${tests_option_sets_ps1}" -split " "

. .\test_functions.ps1

$$TestExecutablesDirectory = GetTestExecutablesDirectory

If (-Not (Test-Path $${TestExecutablesDirectory}))
{
	Write-Error "Missing test executables directory"

	Exit $${ExitFailure}
}

$$Result = $${ExitSuccess}

Foreach ($${TestName} in $${LibraryTests} -split " ")
{
	# Split will return an array of a single empty string when LibraryTests is empty.
	If (-Not ($${TestName}))
	{
		Continue
	}
	$$ResultRun = RunTestBinary $${TestExecutablesDirectory} "${library_name_suffix}_test_$${TestName}"

	If (($${ResultRun} -ne $${ExitSuccess}) -And ($${ResultRun} -ne $${ExitIgnore}))
	{
		$$Result = $${ResultRun}
	}
}

$$TestInputs = GenerateTestInputs "${library_name}" $${OptionSets}

Foreach ($${TestName} in $${LibraryTestsWithInput} -split " ")
{
	# Split will return an array of a single empty string when LibraryTestsWithInput is empty.
	If (-Not ($${TestName}))
	{
		Continue
	}
	ForEach ($$TestInput in $${TestInputs})
	{
		$$ResultRun = RunTestBinaryWithInput $${TestExecutablesDirectory} "${library_name_suffix}_test_$${TestName}" $${TestInput}

		If (($${ResultRun} -ne $${ExitSuccess}) -And ($${ResultRun} -ne $${ExitIgnore}))
		{
			$$Result = $${ResultRun}
		}
	}
}

Exit $${Result}
