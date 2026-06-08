# Export tool testing script
#
# Version: 20260608

$$ExitSuccess = 0
$$ExitFailure = 1
$$ExitIgnore = 77

$$Profiles = @(${tests_export_tool_profiles_ps1})
$$OptionsPerProfile = @(${tests_export_tool_options_per_profile_ps1})
$$OptionSets = "${tests_export_tool_option_sets_ps1}"

$$InputGlob = "${tests_input_glob}"

$$VSDirectories = @(
	"msvscpp",
	"vs2008",
	"vs2010",
	"vs2012",
	"vs2013",
	"vs2015",
	"vs2017",
	"vs2019",
	"vs2022",
	"vs2026"
)

$$VSConfigurations = @(
	"Release",
	"VSDebug"
)

$$VSPlatforms = @(
	"Win32",
	"x64"
)

Function GetTestExecutablesDirectory
{
	$$TestExecutablesDirectory = ""

	ForEach ($${VSDirectory} in $$VSDirectories)
	{
		ForEach ($${VSConfiguration} in $$VSConfigurations)
		{
			ForEach ($${VSPlatform} in $$VSPlatforms)
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

