import logging
import libraries.display as display
import logging
from datetime import datetime
from time import sleep


def updateSeconds():
    now = datetime.now()
    xd = 't1.txt="' + str(now.minute).zfill(2) + '"'
    return xd


# end def


def updateMinutes():
    now = datetime.now()
    xd = 't0.txt="' + str(now.hour).zfill(2) + '"'
    return xd


# end def

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

screen = display.spiScreen(logger, "/dev/ttyS0", 9600, -True, 0)
screen.runWritingTask(updateSeconds, "updateSeconds", 1)
screen.runWritingTask(updateMinutes, "updateMinutes", 1)


sleep(5)

while True:
    inputMsg = input()
    if not (inputMsg is None):
        if inputMsg.lower() == "quit":
            break
        elif inputMsg.lower() == "seconds":
            screen.stopTask("updateSeconds")
        else:
            print(screen.getInputMessage())
        # end if
    # end if
# end w hile

screen.closeConnection()
print("bye")
