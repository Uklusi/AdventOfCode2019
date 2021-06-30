$Number = [Int]$args[0]
$Folder = "Day_" + "{0:d2}" -f $Number
New-Item -Type Directory -Name $Folder | Out-Null

If ( Test-Path -Path input.txt ) {
	Move-Item -Path input.txt -Destination "$Folder/input.txt"
}

For ($i = 1; $i -le 2; $i++ ) {
	('result = 0

with open("input.txt", "r") as input:
    for line in input:
        line = line.strip()

with open("output' + $i + '.txt", "w") as output:
    output.write(str(result))
    print(str(result))') | Out-File -FilePath "$Folder/part${i}.py" -Encoding utf8 
}
