from intCode.intCodeInterpreter import IntCodeInterpreter, readTape
import time
from itertools import permutations

result = 0

intCodeTape = readTape("input.txt")

allPermutations = permutations([5, 6, 7, 8, 9])

for perm in allPermutations:
    amp0 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[0], 0])
    amp1 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[1]])
    amp2 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[2]])
    amp3 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[3]])
    amp4 = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[perm[4]])

    amp0.setOutputCallback(lambda value: amp1.addInput(value))
    amp1.setOutputCallback(lambda value: amp2.addInput(value))
    amp2.setOutputCallback(lambda value: amp3.addInput(value))
    amp3.setOutputCallback(lambda value: amp4.addInput(value))
    amp4.setOutputCallback(lambda value: amp0.addInput(value))

    amp0.start()
    amp1.start()
    amp2.start()
    amp3.start()
    amp4.start()

    while amp4.is_alive():
        time.sleep(0.001)

    r = amp4.outputs[-1]
    if r > result:
        result = r

with open("output2.txt", "w") as output:
    output.write(str(result))
    print(str(result))
