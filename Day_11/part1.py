from intCode.intCodeInterpreter import IntCodeInterpreter, readTape
from threading import Thread, Semaphore

result = 0

BLACK = 0
WHITE = 1

ROTLEFT = 0
ROTRIGHT = 1

intCodeTape = readTape("input.txt")


class ShipSide(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.direction = 0 # North
        self.grid = {}
        self.pos = (0, 0)
        self.rotation = None
        self.colorSemaphore = Semaphore()
        self.lastInput = None
        self.rotationSemaphore = Semaphore(0)
        self.stopFlag = False

    def stop(self):
        self.stopFlag = True

    def getColor(self):
        if not self.colorSemaphore.acquire(timeout=1):
            return
        return self.grid.get(self.pos, BLACK)

    def setColor(self, color):
        self.grid[self.pos] = color
        self.colorSemaphore.release()

    def setRotation(self, rot):
        self.rotation = rot
        self.rotationSemaphore.release()

    def move(self):
        if not self.rotationSemaphore.acquire(timeout=1):
            return
        if self.rotation == ROTLEFT:
            self.direction = (self.direction - 1) % 4
        elif self.rotation == ROTRIGHT:
            self.direction = (self.direction + 1) % 4

        pos = self.pos

        if self.direction == 0:
            pos = (pos[0], pos[1] + 1)
        elif self.direction == 1:
            pos = (pos[0] + 1, pos[1])
        elif self.direction == 2:
            pos = (pos[0], pos[1] - 1)
        elif self.direction == 3:
            pos = (pos[0] - 1, pos[1])
        self.pos = pos

    def provideInput(self, color):
        pass

    def receiveInput(self, input):
        if self.lastInput is None or self.lastInput == "direction":
            self.lastInput = "color"
            self.setColor(input)
        elif self.lastInput == "color":
            self.lastInput = "direction"
            self.setRotation(input)

    def run(self):
        while not self.stopFlag:
            color = self.getColor()
            self.provideInput(color)
            self.move()


shipSide = ShipSide()

paintingRobot = IntCodeInterpreter(intCodeTape, interactive=False, debug=False)

paintingRobot.setOutputCallback(lambda out: shipSide.receiveInput(out))
shipSide.provideInput = paintingRobot.addInput

paintingRobot.start()
shipSide.start()

while paintingRobot.is_alive():
    pass

shipSide.stop()

result = len(shipSide.grid)

with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))
