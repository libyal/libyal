# Script that synchronizes the local test data
#
# Version: 20260608

$$Repository = "${test_data_repository}"
$$TestDataPath = "${test_data_path}"
$$TestSet = "public"
$$TestInputDirectory = "tests\input"
$$TestFiles = "${test_data_files}"

If (-Not (Test-Path $${TestInputDirectory}))
{
	New-Item -Name $${TestInputDirectory} -ItemType "directory" | Out-Null
}
If (-Not (Test-Path "$${TestInputDirectory}\$${TestSet}"))
{
	New-Item -Name "$${TestInputDirectory}\$${TestSet}" -ItemType "directory" | Out-Null
}
ForEach ($$TestFile in $${TestFiles} -split " ")
{
	$$UrlTestFile = [System.Uri]::EscapeDataString("$${TestFile}")
	$$Url = "https://raw.githubusercontent.com/$${Repository}/refs/heads/main/$${TestDataPath}/$${UrlTestFile}"

	$$ProgressPreference = 'SilentlyContinue'
	Invoke-WebRequest -Uri $${Url} -OutFile "$${TestInputDirectory}\$${TestSet}\$${TestFile}"
}

