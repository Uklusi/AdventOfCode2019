result = 0

input = "356261-846303"

startNum = 356261
endNum = 846303


for num in range(startNum, endNum + 1):
    strNum = str(num)
    isAscending = all([a <= b for (a, b) in zip(strNum, strNum[1:])])
    hasDoublesInside = any([a < b == c < d for (a, b, c, d) in zip(strNum, strNum[1:], strNum[2:], strNum[3:])])
    hasDoublesOutside = strNum[0] == strNum[1] < strNum[2] or strNum[3] < strNum[4] == strNum[5]
    hasDoubles = hasDoublesInside or hasDoublesOutside
    if isAscending and hasDoubles:
        result += 1


with open("output2.txt", "w") as output:
    output.write(str(result))
    print(str(result))
