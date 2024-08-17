import logging
import libraries.serialDisplay as serialDisplay
from datetime import datetime


def updateMinutes():
    now = datetime.now()
    xd = 'minuteTxt.txt="' + str(now.minute).zfill(2) + '"'
    return xd


# end def


def updateHour():
    now = datetime.now()
    xd = 'hourTxt.txt="' + str(now.hour).zfill(2) + '"'
    return xd


# end def


def message_received(message):
    print("****  " + message + "  ****")


# initializing logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


# initializing screen
screen = serialDisplay.spiScreen(logger, "/dev/ttyS0", 921600, True, 0)
screen.runWritingTask(updateMinutes, "updateMinutes", 1)
screen.runWritingTask(updateHour, "updateHours", 1)
screen.onMessageReceivedEvent(message_received)

# main loop for sending messages and exit the program
loadAnimationVisible = False

try:
    while True:
        inputMsg = input()
        if not (inputMsg is None):
            if inputMsg.lower() == "quit":
                break
            elif inputMsg.lower() == "xd":
                loadAnimationVisible = not loadAnimationVisible
                screen.showLoadingAnimation(loadAnimationVisible, 5)
            else:
                screen.sendMessage(inputMsg)

            # end if
        # end if
    # end while
except KeyboardInterrupt:
    pass
# end try-catch

# cleaning up
screen.closeConnection()
print("bye")
