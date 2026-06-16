# Export tool testing script
#
# Version: 20260616

$$Profiles = @(${tests_export_tool_profiles_ps1})
$$OptionSets = "${tests_option_sets_ps1}" -split " "

. .\test_functions.ps1

$$TestExecutablesDirectory = GetTestExecutablesDirectory

If (-Not (Test-Path $${TestExecutablesDirectory}))
{
	Write-Error "Missing test executables directory"

	Exit $${ExitFailure}
}

$$TestExecutable = "$${TestExecutablesDirectory}\${library_name_suffix}export.exe"

If (-Not (Test-Path -Path "input"))
{
	Exit $${ExitSuccess}
}

Get-ChildItem -Path "input\$${InputGlob}" | Foreach-Object
{
	Invoke-Expression $${TestExecutable} $$_

	If ($${LastExitCode} -ne $${ExitSuccess})
	{
		Break
	}
}

Exit $${LastExitCode}

