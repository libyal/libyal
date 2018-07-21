# Script that builds libcfile
#
# Version: 20180721

Param (
	[string]$$Configuration = $${Env:Configuration},
	[string]$$Platform = $${Env:Platform}
)

$$ProjectFile = "msvscpp\${library_name}.sln"

If (-not $${Configuration})
{
	$$Configuration = "Release"
}
If (-not $${Platform})
{
	$$Platform = "Win32"
}
$$MSBuildOptions = "/verbosity:quiet /target:Build /property:Configuration=$${Configuration},Platform=$${Platform}"

If ($${Env:VisualStudioVersion} = "15.0")
{
	Invoke-Expression -Command "& 'C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\amd64\MSBuild.exe' $${MSBuildOptions} /property:PlatformToolset=v141 $${ProjectFile}"
}
ElseIf ($${Env:VisualStudioVersion} = "9.0")
{
	Invoke-Expression -Command "C:\\Windows\Microsoft.NET\Framework\v3.5\MSBuild.exe $${MSBuildOptions} $${ProjectFile}"
}
Else
{
	Invoke-Expression -Command "C:\\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe $${MSBuildOptions} $${ProjectFile}"
}

