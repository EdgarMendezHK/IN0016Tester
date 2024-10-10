import json
from services.openOCD import openOCD
from services.board import board
from datetime import datetime
from services.display import display
import services.gpio as gpio
from libraries.loggerSetup import setup_logger


def loadConfig():
    with open("appsettings.json", "r") as file:
        config = json.load(file)
    return config


# end def


def main(config):

    # initializing gpio service
    gpioService = gpio.GPIO()

    # initializing openocd service
    openOCDService = openOCD(config["openocd"])

    boardService = board(openOCDService, config["pcbConfig"])

    # initializing screen service
    screen = display(
        config["displayConfig"], config["errorFont"], boardService, gpioService
    )

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
    screen.dispose()

    print("bye")


# end def

if __name__ == "__main__":
    try:
        config = loadConfig()
        main(config)
    except Exception as s:
        print(s)
# end if
