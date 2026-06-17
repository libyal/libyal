
Function CompareWithReference
{
	param( [string]$$TestProfileDirectory, [string]$$TestSet, [string]$$TestFileName, [string]$$TestResults )

	$$ExpectedTestResults = "$${TestProfileDirectory}\$${TestSet}\$${TestFileName}"

	If (Test-Path -Path $${ExpectedTestResults} -PathType Leaf)
	{
		$$Difference = Compare-Object -ReferenceObject (Get-Content -Path $${ExpectedTestResults}) -DifferenceObject (Get-Content -Path $${TestResults})

		If ($${Difference})
		{
			Return $${ExitFailure}
		}
	}
	Else
	{
		New-Item -Force -ItemType Directory -Path "$${TestProfileDirectory}\$${TestSet}" | Out-Null
		Move-Item -Path $${TestResults} -Destination $${ExpectedTestResults}
	}
	Return $${ExitSuccess}
}

Function RunToolsBinaryAndCompareStdout
{
	param( [string]$$TestExecutablesDirectory, [string]$$ToolName, [string]$$TestProfile, [string[]]$$TestInput )

	$$OptionSet = $$TestInput[0]
	$$Options = $$TestInput[1]
	$$TestFile = $$TestInput[2]

	$$TestProfileDirectory = "input\.$${TestProfile}"
	$$TestSet = Split-Path (Split-Path -Path $${TestFile} -Parent) -Leaf
	$$TestFileName = Split-Path -Path $${TestFile} -Leaf

	If ($$OptionSet)
	{
		$$OutputFile = "$${TestFileName}-$${OptionSet}.log"
	}
	Else
	{
		$$OutputFile = "$${TestFileName}.log"
	}
	$$TmpDir = "tmp$${PID}"

	New-Item -Name $${TmpDir} -ItemType "directory" | Out-Null

	Push-Location $${TmpDir}

	Try
	{
		Invoke-Expression "..\$${TestExecutablesDirectory}\$${ToolName}.exe $${Options} $${TestFile} > $${OutputFile}"
		$$Result = $$global:LastExitCode

		If ($${Result} -eq $${ExitSuccess})
		{
			# Strip header with version.
			(Get-Content $${OutputFile} | Select-Object -Skip 2) | Set-Content $${OutputFile}

			$$Result = CompareWithReference "..\$${TestProfileDirectory}" $${TestSet} $${TestFileName} $${OutputFile}
		}
	}
	Finally
	{
		Pop-Location

		Remove-Item $${TmpDir} -Force -Recurse
	}
	$$TestDescription = "$${ToolName} with input: '$${TestSet}\$${TestFileName}"

	WriteTestResult $${TestDescription} $${Result}

	Return $${Result}
}
