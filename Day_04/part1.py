result = 0

input = "356261-846303"

startNum = 356666
endNum = 799999


for num in range(startNum, endNum + 1):
    strNum = str(num)
    isAscending = all([a <= b for (a, b) in zip(strNum, strNum[1:])])
    hasDoubles = any([a == b for (a, b) in zip(strNum, strNum[1:])])
    if isAscending and hasDoubles:
        result += 1


with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))
