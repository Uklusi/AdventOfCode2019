from threading import Thread, Semaphore
# import time


class IntCodeInterpreter(Thread):
    def __init__(self, intCodeTape, interactive=True, inputs=[], debug=False):
        Thread.__init__(self)
        self.pos = 0
        self.tape = {i: j for (i, j) in enumerate(intCodeTape)}
        self.interactive = interactive
        self.outputs = []
        self.inputs = inputs.copy()
        self.currentInput = 0
        self.inputLock = Semaphore(len(inputs))
        self.outputCallback = None
        self.relativeBase = 0
        self.debug = debug

    def setOutputCallback(self, callback):
        self.outputCallback = callback

    def addInput(self, input):
        if self.debug:
            print("intcode")
            print(input)
        self.inputs.append(input)
        self.inputLock.release()

    def _instructionAndMode(self, iCode):
        iCodeStr = "{0:05d}".format(iCode)
        mode3 = int(iCodeStr[0])
        mode2 = int(iCodeStr[1])
        mode1 = int(iCodeStr[2])
        opcode = int(iCodeStr[-2:])
        return (opcode, mode1, mode2, mode3)

    def _getValue(self, value, mode):
        if mode == 0:
            return self.tape.get(value, 0)
        elif mode == 1:
            return value
        elif mode == 2:
            return self.tape.get(value + self.relativeBase, 0)

    def _getPosition(self, value, mode):
        if mode == 0:
            return value
        elif mode == 1:
            raise(ValueError("Cannot get position for immediate mode"))
        elif mode == 2:
            return value + self.relativeBase

    def _input(self):
        if self.interactive:
            return int(input("Input: "))
        else:
            self.inputLock.acquire()
            inputVal = self.inputs[self.currentInput]
            self.currentInput += 1
            return inputVal

    def _output(self, value):
        if self.interactive:
            print(value)
        else:
            self.outputs.append(value)
            if self.outputCallback is not None:
                self.outputCallback(value)

    def _opCode1(self, mode1, mode2, mode3):
        # Add
        par1 = self.tape[self.pos + 1]
        par2 = self.tape[self.pos + 2]
        parOut = self.tape[self.pos + 3]

        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)
        posOut = self._getPosition(parOut, mode3)

        self.tape[posOut] = val1 + val2
        self.pos += 4
        return True

    def _opCode2(self, mode1, mode2, mode3):
        # Multiply
        par1 = self.tape[self.pos + 1]
        par2 = self.tape[self.pos + 2]
        parOut = self.tape[self.pos + 3]

        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)
        posOut = self._getPosition(parOut, mode3)

        self.tape[posOut] = val1 * val2
        self.pos += 4
        return True

    def _opCode3(self, mode1, mode2, mode3):
        # Input
        val = self._input()

        parIn = self.tape[self.pos + 1]
        posIn = self._getPosition(parIn, mode1)

        self.tape[posIn] = val
        self.pos += 2
        return True

    def _opCode4(self, mode1, mode2, mode3):
        # Output
        parOut = self.tape[self.pos + 1]
        valOut = self._getValue(parOut, mode1)

        self._output(valOut)
        self.pos += 2
        return True

    def _opCode5(self, mode1, mode2, mode3):
        # Jump-if-true
        par1 = self.tape[self.pos + 1]
        par2 = self.tape[self.pos + 2]
        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)

        if val1 != 0:
            self.pos = val2
        else:
            self.pos += 3
        return True

    def _opCode6(self, mode1, mode2, mode3):
        # Jump-if-false
        par1 = self.tape[self.pos + 1]
        par2 = self.tape[self.pos + 2]
        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)

        if val1 == 0:
            self.pos = val2
        else:
            self.pos += 3
        return True

    def _opCode7(self, mode1, mode2, mode3):
        # less than
        par1 = self.tape[self.pos + 1]
        par2 = self.tape[self.pos + 2]
        parOut = self.tape[self.pos + 3]

        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)
        posOut = self._getPosition(parOut, mode3)

        if val1 < val2:
            self.tape[posOut] = 1
        else:
            self.tape[posOut] = 0
        self.pos += 4
        return True

    def _opCode8(self, mode1, mode2, mode3):
        # less than
        par1 = self.tape[self.pos + 1]
        par2 = self.tape[self.pos + 2]
        parOut = self.tape[self.pos + 3]

        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)
        posOut = self._getPosition(parOut, mode3)

        if val1 == val2:
            self.tape[posOut] = 1
        else:
            self.tape[posOut] = 0
        self.pos += 4
        return True

    def _opCode9(self, mode1, mode2, mode3):
        # set relative base
        par1 = self.tape[self.pos + 1]
        val1 = self._getValue(par1, mode1)

        self.relativeBase += val1
        self.pos += 2
        return True

    def _opCode99(self):
        return False

    def step(self):
        code = self.tape[self.pos]
        (opcode, mode1, mode2, mode3) = self._instructionAndMode(code)
        if opcode == 1:
            return self._opCode1(mode1, mode2, mode3)
        elif opcode == 2:
            return self._opCode2(mode1, mode2, mode3)
        elif opcode == 3:
            return self._opCode3(mode1, mode2, mode3)
        elif opcode == 4:
            return self._opCode4(mode1, mode2, mode3)
        elif opcode == 5:
            return self._opCode5(mode1, mode2, mode3)
        elif opcode == 6:
            return self._opCode6(mode1, mode2, mode3)
        elif opcode == 7:
            return self._opCode7(mode1, mode2, mode3)
        elif opcode == 8:
            return self._opCode8(mode1, mode2, mode3)
        elif opcode == 9:
            return self._opCode9(mode1, mode2, mode3)
        elif opcode == 99:
            return self._opCode99()
        else:
            raise(
                ValueError(
                    "Unknown code: {} at position {}".format(code, self.pos)
                )
            )

    def run(self):
        while self.step():
            pass
        if not self.interactive:
            return self.outputs


def readTape(file):
    with open(file, "r") as input:
        return([int(n) for n in input.read().strip().split(",")])
