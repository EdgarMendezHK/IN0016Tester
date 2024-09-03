import logging
import json
import libraries.serialDisplay as serialDisplay
from services.openOCD import openOCD
from datetime import datetime
from services.display import display


def loadConfig():
    with open("appsettings.json", "r") as file:
        config = json.load(file)
    return config


# end def


def main(name, config):
    # initializing logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # initializing openocd service
    openOCDService = openOCD(config["openocd"])
    print(openOCDService.burn_test_program())
    # initializing screen service
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


# end def

if __name__ == "__main__":
    try:
        config = loadConfig()
        main(__name__, config)
    except Exception as s:
        print(s)
# end if
