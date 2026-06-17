
$$Profiles = @(${tests_info_tool_profiles_ps1})

For ($$ProfileIndex = 0; $$ProfileIndex -le ($$Profiles.length - 1); $$ProfileIndex += 1)
{
	$$TestProfile = $$Profiles[$$ProfileIndex]

	$$TestInputs = GenerateTestInputs $${TestProfile} $${OptionSets}

	ForEach ($$TestInput in $${TestInputs})
	{
		$$Result = RunToolsBinaryAndCompareStdout $${TestExecutablesDirectory} "${library_name_suffix}info" $${TestProfile} $${TestInput}

		If (($${Result} -ne $${ExitSuccess}) -And ($${Result} -ne $${ExitIgnore}))
		{
			Break
		}
	}
	If (($${Result} -ne $${ExitSuccess}) -And ($${Result} -ne $${ExitIgnore}))
	{
		Break
	}
}
