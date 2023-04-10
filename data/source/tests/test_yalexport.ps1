# Export tool testing script
#
# Version: 20230409

$$ExitSuccess = 0
$$ExitFailure = 1
$$ExitIgnore = 77

$$InputGlob = "${tests_input_glob}"

Function GetTestExecutablesDirectory
{
	$$TestExecutablesDirectory = ""

	ForEach ($${VSDirectory} in "msvscpp vs2008 vs2010 vs2012 vs2013 vs2015 vs2017 vs2019 vs2022" -split " ")
	{
		ForEach ($${VSConfiguration} in "Release VSDebug" -split " ")
		{
			ForEach ($${VSPlatform} in "Win32 x64" -split " ")
			{
				$$TestExecutablesDirectory = "..\$${VSDirectory}\$${VSConfiguration}\$${VSPlatform}"

				If (Test-Path $${TestExecutablesDirectory})
				{
					Return $${TestExecutablesDirectory}
				}
			}
			$$TestExecutablesDirectory = "..\$${VSDirectory}\$${VSConfiguration}"

			If (Test-Path $${TestExecutablesDirectory})
			{
				Return $${TestExecutablesDirectory}
			}
		}
	}
	Return $${TestExecutablesDirectory}
}

$$TestExecutablesDirectory = GetTestExecutablesDirectory

If (-Not (Test-Path $${TestExecutablesDirectory}))
{
	Write-Host "Missing test executables directory." -foreground Red

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

