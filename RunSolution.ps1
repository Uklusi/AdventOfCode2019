$Folder = "Day_" + "{0:d2}" -f [Int]$args[0]
$part = $args[1]

$env:PYTHONPATH += $(Get-Location).path + ";"

try {
    Set-Location $Folder
    python "part${part}.py"
}
finally {
    Set-Location ".."
}
