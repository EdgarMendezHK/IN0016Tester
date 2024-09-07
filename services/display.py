from numpy import sin, pi
import libraries.serialDisplay as serilDisplay
from datetime import datetime
import logging
from typing import Dict, Any
import threading
from services.board import board
import time


class display:
    def __init__(
        self,
        communicationInfoJson: Dict[str, Any],
        boardService: board,
        logger: logging.Logger = None,
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

        if not boardService:
            raise ValueError("openOCDService must not be None")
        # end if

        screen = serilDisplay.spiScreen(
            logger,
            communicationInfoJson["port"],
            communicationInfoJson["baudrate"],
            communicationInfoJson["rtscts"],
            communicationInfoJson["timeout"],
        )

        self.__showLoadingAnimation_lock = threading.Lock()
        self.__showLoadingAnimation = False
        self.__waveID = 0

        self.__clock_lock = threading.Lock()
        self.__runClock = False

        screen.runWritingTask(self.__updateTime, "datetimeUpdate", 1)
        screen.runWritingTask(self.__processLoadingAnnimation, "loading", 1 / 60)

        screen.onMessageReceivedEvent(self.__message_received)

        self.__screen = screen

        self.__onMessageReceivedevents = {}

        self.__mapEvents()

        self.__boardService = boardService

        self.__message_received("page0")

    # end def

    def __mapEvents(self):
        # map every command and its related function. Then at __message_received
        # check if the message receved is in the dicctionary and execute the function asosiated with it
        self.__onMessageReceivedevents = {
            "page0": self.__startPage0,
            "page1": self.__startPage1,
            "page2": self.__startPage2,
            "page3": self.__startPage3,
        }

    # end def

    def __message_received(self, message):
        function = message.split(";")[0]
        params = message.split(";")

        if len(params) > 1:
            params = params[1:]

            if params[-1].index("\r\n") > -1:
                params[-1] = params[-1][:-2]
        else:
            params = []
        # end if

        if "\r\n" in function:
            function = function[:-2]
        # end if

        if function in self.__onMessageReceivedevents:

            # if the command is different to page0 the clock task will stop in order to free the outputMessages queue
            if function == "page0":
                self.__runClockTask(True)
            else:
                self.__runClockTask(False)

            return (
                self.__onMessageReceivedevents[function](params)
                if len(params) > 0
                else self.__onMessageReceivedevents[function]()
            )

        # end if

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
            ret = None

            if display.__processLoadingAnnimation.i > 0:
                ret = "cle 2,255"

            # end if

            display.__processLoadingAnnimation.i = 0
            time.sleep(1)

            return ret
        # end if

    # end def

    def __runClockTask(self, run: bool):
        with self.__clock_lock:
            self.__runClock = run

    # end with

    def __startPage0(self):
        self.sendMessage("page 0")

    # end def

    def __startPage1(self):
        self.sendMessage("page 1")

    # end def

    def __startPage2(self, message):
        # separating command from parameters.

        # checking for wave id to run the loading animation thread
        animationStarted = False

        for part in message:
            if part.lower().index("waveid=") >= 0:
                waveId = part.split("=")
                if len(waveId) == 2:
                    self.showLoadingAnimation(True, waveId[1])
                    animationStarted = True
                # end if
            # end if
        # end for

        # go to page 2
        self.sendMessage("page 2")

        # load test program to microcontroller
        attempts = 0
        xd = False

        while attempts < 3 and not xd:
            time.sleep(1)
            xd = self.__boardService.LoadTestProgram()
            attempts = attempts + 1

        # end while

        # turn off loadiding animation
        if animationStarted:
            self.showLoadingAnimation(False, waveId[1])
            self.sendMessage("cle 2,255")  # cleaning id 2 waveform

        # go to page 3 if succesfuly programmed
        if xd:
            self.sendMessage("page 3")

        else:
            self.sendMessage("page 8")

    # end def

    def __startPage3(self):
        # start a timer for 5 seconds or something
        # check on modbus messages to check if the button was pressed
        timeout = 30
        startTime = time.time()

        print("running page 3")
        while True:
            if time.time() - startTime > timeout:
                return
            # end if
            message = self.__boardService.getMessage()
            print(message)

            if message is not None and message.strip() == "DispBtn On":
                self.__screen.sendMessage("page 4")
                break
            # end if

        # end while

        # need to add a cancel test button on every screen
        pass

    # end def

    def __updateTime(self):
        with self.__clock_lock:
            execute = self.__runClock
        # end with

        if execute:
            now = datetime.now()
            hours = 'hourTxt.txt="' + str(now.hour).zfill(2) + '"'
            minutes = 'minuteTxt.txt="' + str(now.minute).zfill(2) + '"'
            return [hours, minutes]
        # end if

        return None

    # end def

    def dispose(self) -> None:
        """
        Free resources and close serial communication.

        Returns:
            None
        """
        self.__screen.closeConnection()
        self.__boardService.dispose()

    # end def

    def sendMessage(self, message):
        self.__screen.sendMessage(message)

    def showLoadingAnimation(self, show, waveFormObjectId):
        with self.__showLoadingAnimation_lock:
            self.__showLoadingAnimation = show
            self.__waveID = waveFormObjectId

    # end def


# end class
