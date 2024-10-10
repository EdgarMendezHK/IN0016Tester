import logging
import json
from services.openOCD import openOCD
from services.board import board
from datetime import datetime
from services.display import display
import services.gpio as gpio


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

    # initializing gpio service
    gpioService = gpio.GPIO()

    # initializing openocd service
    openOCDService = openOCD(config["openocd"])

    boardService = board(openOCDService, config["pcbConfig"], logger)

    # initializing screen service
    screen = display(
        config["displayConfig"],
        config["errorFont"],
        boardService,
        gpioService,
        logger,
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
        main(__name__, config)
    except Exception as s:
        print(s)
# end if
