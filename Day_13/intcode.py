from __future__ import annotations
from typing import Iterable, Optional, Callable
from threading import Thread, Semaphore
from collections import defaultdict


class Interpreter(Thread):
    """
    Interpreter class: required for half of AoC2019 puzzles.
    Inherits from Thread

    Syntax: Interpreter(intCodeTape, interactive=True, inputs=[], debug=False)

    In order to function, the interpreter requires the program tape (usually the puzzle input).
    inputs is the list of starting inputs available to the interpreter before the start
    
    The interpreter has two main modes: interactiveand non-interactive.
    
    The interactive mode (default) asks for inputs from stdin and prints outputs to stdout.

    The non-interactive mode is based on a concurrent threading model, with threads sending and receiving inputs from each other.
    The input/output behaviour is based on the setOutputCallback, setInputCallback and addInput methods:
        - addInput(n) adds a value to the interpreter input queue. It is never called in the code proper,
          and it is expected to be used in conjunction with setOutputCallback and setInputCallback;
        - setOutputCallback(callback: int -> None) is used to run a function after emitting an output.
          This function is usually addInput from another thread;
        - setInputCallback(callback: [] -> None) is used to run a function as the thread requests an input:
          this is usually a function inserting an input (using addInput) based on the current interpreter state
    A semaphore is used in order to block the interpreter when there are no inputs available.

    In order to start the thread, we need to use the Thread method interpreter.start().
    We can await completion using interpreter.join(), and we can stop a running Thread using interpreter.stop()

    The interpreter can advance one step using the step() method, or can run until termination using the run() method.
    
    If the output is needed after the thread completion, the property outputs is available, and the runOutput() method also returns the outputs
    """
    def __init__(
        self,
        intCodeTape: Iterable[int],
        interactive: bool = True,
        inputs: list[int] = [],
        debug: bool = False
    ):
        Thread.__init__(self)
        self.currentPosition = 0
        self.tape: defaultdict[int, int] = defaultdict(lambda: 0)
        for (position, value) in enumerate(intCodeTape):
            self.tape[position] = value
        self.interactive = interactive
        self.outputs: list[int] = []
        self.inputs = inputs.copy()
        self.currentInput = 0
        self.inputLock = Semaphore(len(inputs))
        self.outputCallback: Optional[Callable[[int], None]] = None
        self.inputCallback: Optional[Callable[[], None]] = None
        self.relativeBase = 0
        self.debug = debug

    def setOutputCallback(self, callback: Callable[[int], None]) -> None:
        self.outputCallback = callback

    def setInputCallback(self, callback: Callable[[], None]) -> None:
        self.inputCallback = callback

    def addInput(self, input: int) -> None:
        if self.debug:
            print("intcode")
            print(input)
        self.inputs.append(input)
        self.inputLock.release()

    def _instructionAndMode(self, iCode: int) -> tuple[int, int, int, int]:
        iCodeStr = "{0:05d}".format(iCode)
        mode3 = int(iCodeStr[0])
        mode2 = int(iCodeStr[1])
        mode1 = int(iCodeStr[2])
        opcode = int(iCodeStr[-2:])
        return (opcode, mode1, mode2, mode3)

    def _getValue(self, value: int, mode: int) -> int:
        if mode == 0:
            return self.tape[value]
        elif mode == 1:
            return value
        elif mode == 2:
            return self.tape[value + self.relativeBase]
        else:
            raise(ValueError("mode not recognised"))

    def _getPosition(self, value: int, mode: int) -> int:
        if mode == 0:
            return value
        elif mode == 1:
            raise(ValueError("Cannot get position for immediate mode"))
        elif mode == 2:
            return value + self.relativeBase
        else:
            raise(ValueError("mode not recognised"))

    def _input(self) -> int:
        if self.interactive:
            ret = None
            while ret is None:
                try:
                    ret = int(input("Input: "))
                except KeyboardInterrupt:
                    raise(KeyboardInterrupt)
                except:
                    pass
            return ret
        else:
            if self.inputCallback is not None:
                self.inputCallback()
            self.inputLock.acquire()
            inputVal = self.inputs[self.currentInput]
            self.currentInput += 1
            return inputVal

    def _output(self, value: int) -> None:
        if self.interactive:
            print("Output:", value)
        else:
            self.outputs.append(value)
            if self.outputCallback is not None:
                self.outputCallback(value)

    def _opCode1(self, mode1: int, mode2: int, mode3: int) -> bool:
        # Add
        par1 = self.tape[self.currentPosition + 1]
        par2 = self.tape[self.currentPosition + 2]
        parOut = self.tape[self.currentPosition + 3]

        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)
        posOut = self._getPosition(parOut, mode3)

        self.tape[posOut] = val1 + val2
        self.currentPosition += 4
        return True

    def _opCode2(self, mode1: int, mode2: int, mode3: int) -> bool:
        # Multiply
        par1 = self.tape[self.currentPosition + 1]
        par2 = self.tape[self.currentPosition + 2]
        parOut = self.tape[self.currentPosition + 3]

        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)
        posOut = self._getPosition(parOut, mode3)

        self.tape[posOut] = val1 * val2
        self.currentPosition += 4
        return True

    def _opCode3(self, mode1: int, mode2: int, mode3: int) -> bool:
        # Input
        val = self._input()

        parIn = self.tape[self.currentPosition + 1]
        posIn = self._getPosition(parIn, mode1)

        self.tape[posIn] = val
        self.currentPosition += 2
        return True

    def _opCode4(self, mode1: int, mode2: int, mode3: int) -> bool:
        # Output
        parOut = self.tape[self.currentPosition + 1]
        valOut = self._getValue(parOut, mode1)

        self._output(valOut)
        self.currentPosition += 2
        return True

    def _opCode5(self, mode1: int, mode2: int, mode3: int) -> bool:
        # Jump-if-true
        par1 = self.tape[self.currentPosition + 1]
        par2 = self.tape[self.currentPosition + 2]
        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)

        if val1 != 0:
            self.currentPosition = val2
        else:
            self.currentPosition += 3
        return True

    def _opCode6(self, mode1: int, mode2: int, mode3: int) -> bool:
        # Jump-if-false
        par1 = self.tape[self.currentPosition + 1]
        par2 = self.tape[self.currentPosition + 2]
        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)

        if val1 == 0:
            self.currentPosition = val2
        else:
            self.currentPosition += 3
        return True

    def _opCode7(self, mode1: int, mode2: int, mode3: int) -> bool:
        # less than
        par1 = self.tape[self.currentPosition + 1]
        par2 = self.tape[self.currentPosition + 2]
        parOut = self.tape[self.currentPosition + 3]

        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)
        posOut = self._getPosition(parOut, mode3)

        if val1 < val2:
            self.tape[posOut] = 1
        else:
            self.tape[posOut] = 0
        self.currentPosition += 4
        return True

    def _opCode8(self, mode1: int, mode2: int, mode3: int) -> bool:
        # less than
        par1 = self.tape[self.currentPosition + 1]
        par2 = self.tape[self.currentPosition + 2]
        parOut = self.tape[self.currentPosition + 3]

        val1 = self._getValue(par1, mode1)
        val2 = self._getValue(par2, mode2)
        posOut = self._getPosition(parOut, mode3)

        if val1 == val2:
            self.tape[posOut] = 1
        else:
            self.tape[posOut] = 0
        self.currentPosition += 4
        return True

    def _opCode9(self, mode1: int, mode2: int, mode3: int) -> bool:
        # set relative base
        par1 = self.tape[self.currentPosition + 1]
        val1 = self._getValue(par1, mode1)

        self.relativeBase += val1
        self.currentPosition += 2
        return True

    def _opCode99(self) -> bool:
        return False

    def step(self) -> bool:
        code = self.tape[self.currentPosition]
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
                    "Unknown code: {} at position {}".format(code, self.currentPosition)
                )
            )

    def run(self) -> None:
        while self.step():
            pass

    def runOutput(self) -> list[int]:
        self.run()
        return self.outputs


def readTape(file: str) -> list[int]:
    """
    Auxiliary function, taking in input a file name and returning the intCodeTape written inside that file
    """
    with open(file, "r") as input:
        return([int(n) for n in input.read().strip().split(",")])
