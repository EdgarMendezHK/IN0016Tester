import libraries.display as display
from datetime import datetime
from time import sleep


def updateSeconds():
    sleep(1)
    now = datetime.now()
    xd = 't0.txt="' + str(now.second) + '"'
    return xd


screen = display.spiScreen("/dev/ttyS0", 9600, True, 0)
screen.runWritingTask(updateSeconds, "updateSeconds")


sleep(5)
while True:
    inputMsg = input()
    if not (inputMsg is None):
        if inputMsg.lower() == "quit":
            break

screen.closeConnection()
print("bye")
