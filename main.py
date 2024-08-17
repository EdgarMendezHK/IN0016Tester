import logging
import json
import libraries.serialDisplay as serialDisplay
from datetime import datetime
from services.display import display


# initializing logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


def loadConfig():
    with open("appsettings.json", "r") as file:
        config = json.load(file)
    return config


config = loadConfig()

screen = display(config["serial"], logger)

# main loop for sending messages and exit the program
loadAnimationVisible = False

try:
    while True:
        inputMsg = input()
        if not (inputMsg is None):
            if inputMsg.lower() == "quit":
                break
            elif inputMsg.lower() == "xd":
                screen.showLoadingAnimation(loadAnimationVisible, 2)
                loadAnimationVisible = not loadAnimationVisible
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
