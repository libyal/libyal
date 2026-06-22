
If (-Not (Test-Path $${TestsInputDirectory}))
{
	New-Item -Name $${TestsInputDirectory} -ItemType "directory" | Out-Null
}
If (-Not (Test-Path "$${TestsInputDirectory}\$${TestSet}"))
{
	New-Item -Name "$${TestsInputDirectory}\$${TestSet}" -ItemType "directory" | Out-Null
}
ForEach ($$TestFile in $${TestFiles} -split " ")
{
	$$UrlTestFile = [System.Uri]::EscapeDataString("$${TestFile}")
	$$Url = "https://raw.githubusercontent.com/${test_data_repository}/refs/heads/main/${test_data_path}/$${UrlTestFile}"

	$$ProgressPreference = 'SilentlyContinue'
	Invoke-WebRequest -Uri $${Url} -OutFile "$${TestsInputDirectory}\$${TestSet}\$${TestFile}"
}
