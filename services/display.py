from numpy import sin, pi
import libraries.serialDisplay as serilDisplay
from datetime import datetime
import logging
from typing import Dict, Any
import threading


class display:
    def __init__(
        self, communicationInfoJson: Dict[str, Any], logger: logging.Logger = None
    ) -> None:
        """
        Initialize a new instance for the serial display device.

        Args:
            communicationInfoJson (Dict[str, Any]): JSON object containing the serial communication settings.
                Must contain the following keys: port, baudrate, rtscts, and timeout.
            logger (logging.Logger): instance of logger service.

            Returs:
                None
        """
        # Validate the required keys in communicationInfoJson

        required_keys = ["port", "baudrate", "rtscts", "timeout"]

        for key in required_keys:
            if key not in communicationInfoJson:
                raise ValueError(f"Missing required key: {key}")
            # end if
        # end for

        screen = serilDisplay.spiScreen(
            logger,
            communicationInfoJson["port"],
            communicationInfoJson["baudrate"],
            communicationInfoJson["rtscts"],
            communicationInfoJson["timeout"],
        )

        self.__showLoadingAnimation_lock = threading.Lock()
        self.__showLoadingAnimation = False

        screen.runWritingTask(self.__updateTime, "datetimeUpdate", 1)
        screen.runWritingTask(self.__processLoadingAnnimation, "loading", 1 / 60)

        screen.onMessageReceivedEvent(self.__message_received)

        self.__screen = screen

    # end def

    def __message_received(self, message):
        print(message)

    # end def

    def __processLoadingAnnimation(self):
        with self.__showLoadingAnimation_lock:
            show_loading = self.__showLoadingAnimation

        if not hasattr(display.__processLoadingAnnimation, "i"):
            display.__processLoadingAnnimation.i = 0  # Initialize a static variable

        if show_loading:
            results = []

            val = int(100 * sin(display.__processLoadingAnnimation.i * pi / 16)) + 150

            for channel in [0, 1, 2, 3]:
                offset = channel * 10
                channelVal = val - offset

                if channelVal < 0:
                    channelVal = 0 + offset
                elif channelVal > 255:
                    channelVal = 255 - offset
                # end if

                s = f"add {self.__waveID},{channel},{channelVal}"

                results.append(s)
            # end for

            display.__processLoadingAnnimation.i += 1

            return results
        else:
            display.__processLoadingAnnimation.i = 0
            return "cle 2,255"
        # end if

    # end def

    def __updateTime(self):
        now = datetime.now()
        hours = 'hourTxt.txt="' + str(now.hour).zfill(2) + '"'
        minutes = 'minuteTxt.txt="' + str(now.minute).zfill(2) + '"'
        return [hours, minutes]

    # end def

    def closeConnection(self) -> None:
        """
        Close serial communication and free resources

        Returns:
            None
        """
        self.__screen.closeConnection()

    # end def

    def sendMessage(self, message):
        self.__screen.sendMessage(message)

    def showLoadingAnimation(self, show, waveFormObjectId):
        with self.__showLoadingAnimation_lock:
            self.__showLoadingAnimation = show
            self.__waveID = waveFormObjectId

    # end def


# end class
