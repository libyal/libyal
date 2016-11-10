# Script to generate the necessary files for a msvscpp build
#
# Version: 20161110

$WinFlex = "..\win_flex_bison\win_flex.exe"
$WinBison = "..\win_flex_bison\win_bison.exe"

$Library = Get-Content -Path configure.ac | select -skip 3 -first 1 | % { $_ -Replace " \[","" } | % { $_ -Replace "\],","" }
$Version = Get-Content -Path configure.ac | select -skip 4 -first 1 | % { $_ -Replace " \[","" } | % { $_ -Replace "\],","" }

Get-Content -Path include\${Library}.h.in > include\${Library}.h
Get-Content -Path include\${Library}\definitions.h.in | % { $_ -Replace "@VERSION@",${Version} } > include\${Library}\definitions.h
Get-Content -Path include\${Library}\features.h.in | % { $_ -Replace "@[A-Z0-9_]*@","0" } > include\${Library}\features.h
Get-Content -Path include\${Library}\types.h.in | % { $_ -Replace "@[A-Z0-9_]*@","0" } > include\${Library}\types.h
Get-Content -Path common\types.h.in | % { $_ -Replace "@PACKAGE@",${Library} } > common\types.h
Get-Content -Path ${Library}\${Library}_definitions.h.in | % { $_ -Replace "@VERSION@",${Version} } > ${Library}\${Library}_definitions.h
Get-Content -Path ${Library}\${Library}.rc.in | % { $_ -Replace "@VERSION@",${Version} } > ${Library}\${Library}.rc

ForEach (${DirectoryElement} in Get-ChildItem -Path "${Library}\*.l")
{
	$OutputFile = ${DirectoryElement} -Replace ".l$", ".c"

	# PowerShell will raise NativeCommandError if win_flex writes to stdout or stderr
	# therefore 2>&1 is added and the output is stored in a variable.
	$Output = Invoke-Expression -Command "& '${WinFlex}' -Cf ${DirectoryElement} -o ${OutputFile} 2>&1"
	Write-Host ${Output}
}

ForEach (${DirectoryElement} in Get-ChildItem -Path "${Library}\*.y")
{
	$OutputFile = ${DirectoryElement} -Replace ".y$", ".c"

	# PowerShell will raise NativeCommandError if win_bison writes to stdout or stderr
	# therefore 2>&1 is added and the output is stored in a variable.
	$Output = Invoke-Expression -Command "& '${WinBison}' d -v -l -p ${NamePrefix} ${DirectoryElement} -o ${OutputFile} 2>&1"
	Write-Host ${Output}
}

