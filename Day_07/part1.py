from intCode.intCodeInterpreter import IntCodeInterpreter, readTape
from itertools import permutations

result = 0

intCodeTape = readTape("input.txt")

allPermutations = permutations([0, 1, 2, 3, 4])

for perm in allPermutations:
    amp0 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[0], 0])
    (out0,) = amp0.run()
    amp1 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[1], out0])
    (out1,) = amp1.run()
    amp2 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[2], out1])
    (out2,) = amp2.run()
    amp3 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[3], out2])
    (out3,) = amp3.run()
    amp4 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[4], out3])
    (out4,) = amp4.run()

    if out4 > result:
        result = out4

with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))
