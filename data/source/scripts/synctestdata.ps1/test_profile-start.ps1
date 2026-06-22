If (-Not (Test-Path "$${TestsInputDirectory}\.${test_profile.name}"))
{
        New-Item -Name "$${TestsInputDirectory}\.${test_profile.name}" -ItemType "directory" | Out-Null
