
$$TestExecutablesDirectory = GetTestExecutablesDirectory

If (-Not (Test-Path $${TestExecutablesDirectory}))
{
	Write-Error "Missing test executables directory"

	Exit $${ExitFailure}
}

$$Result = $${ExitSuccess}
