
$$Profiles = @(${tests_info_tool_profiles_ps1})

For ($$ProfileIndex = 0; $$ProfileIndex -le ($$Profiles.length - 1); $$ProfileIndex += 1)
{
	$$TestProfile = $$Profiles[$$ProfileIndex]

	$$TestInputs = GenerateTestInputs $${TestProfile} $${OptionSets}

	ForEach ($$TestInput in $${TestInputs})
	{
		$$ResultRun = RunToolsBinaryAndCompareStdout $${TestExecutablesDirectory} "${library_name_suffix}info" $${TestProfile} "${tests_info_tool_options}" $${TestInput}

		If (($${ResultRun} -ne $${ExitSuccess}) -And ($${ResultRun} -ne $${ExitIgnore}))
		{
			$$Result = $${ResultRun}
		}
	}
}
