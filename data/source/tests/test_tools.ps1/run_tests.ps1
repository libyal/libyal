
Foreach ($${TestName} in $${ToolsTests} -split " ")
{
	# Split will return an array of a single empty string when ToolsTests is empty.
	If (-Not ($${TestName}))
	{
		Continue
	}
	$$ResultRun = RunTestBinary $${TestExecutablesDirectory} "${library_name_suffix}_test_tools_$${TestName}"

	If (($${ResultRun} -ne $${ExitSuccess}) -And ($${ResultRun} -ne $${ExitIgnore}))
	{
		$$Result = $${ResultRun}
	}
}
