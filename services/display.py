from services.board import board
from PIL import ImageFont, ImageDraw, Image
from numpy import sin, pi
from datetime import datetime
from typing import Dict, Any
import os
import logging
import threading
import time
import libraries.serialDevice as serialDisplay
import services.gpio as gpio
from enum import Enum


class firmware(Enum):
    testProgram = 0
    productionProgram = 1


# end class


class display:
    def __init__(
        self,
        communicationInfoJson: Dict[str, Any],
        errorFont: Dict[str, Any],
        boardService: board,
        gpioService: gpio.GPIO,
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

        self.__checkDictionaryParameter(
            communicationInfoJson, ["port", "baudrate", "rtscts", "timeout"]
        )

        self.__checkDictionaryParameter(errorFont, ["path", "fontSize"])

        if not boardService:
            raise ValueError("boardService must not be None")
        # end if

        # saving font values
        path = os.path.dirname(os.path.realpath(__file__))
        path = path[: path.rfind("services")]

        if errorFont["path"][0] == "/":
            errorFont["path"] = errorFont["path"][1:]

        self.__font_path = path + errorFont["path"]
        self.__font_size = errorFont["fontSize"]

        screen = serialDisplay.serialDevice(
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
        screen.runWritingTask(self.__handShake, "connectionHandShake", 5)

        screen.onMessageReceivedEvent(self.__message_received)

        self.__screenService = screen

        self.__onMessageReceivedevents = {}

        self.__mapEvents()

        self.__boardService = boardService

        self.__message_received("page0")

        self.__gpioService = gpioService

    # end def

    def __checkDictionaryParameter(self, dictionary: Dict[str, Any], keys: list):

        for key in keys:
            if key not in dictionary:
                raise ValueError(f"Missing required key: {key}")
            # end if
        # end for

    # end def

    def __getTextWidth(self, text: str):
        image = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(self.__font_path, self.__font_size)

        words = text.split()
        lines = []
        current_line = ""
        line_height = 0

        for word in words:
            test_line = f"{current_line} {word}".strip()
            txtbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = txtbox[2] - txtbox[0]

            if len(lines) == 0:
                line_height = txtbox[3] - txtbox[1]

            if text_width <= 250:
                current_line = test_line

            else:
                lines.append(current_line)
                current_line = word
            # end if

        # end for

        if current_line:
            lines.append(current_line)

        return (lines, line_height)

    # end def

    def __handShake(self):
        return "timeoutTMR.en=1"

    # end def

    def __loadProgramToBoard(self, programToLoad: firmware) -> bool:

        # load test program to microcontroller
        attempts = 0
        xd = False

        while attempts < 3 and not xd:
            time.sleep(1)
            if programToLoad == firmware.productionProgram:
                xd = self.__boardService.LoadFirmware()
            elif programToLoad == firmware.testProgram:
                xd = self.__boardService.LoadTestProgram()
            else:
                break
            attempts = attempts + 1

        # end while

        return xd

    # end def

    def __mapEvents(self):
        # map every command and its related function. Then at __message_received
        # check if the message receved is in the dicctionary and execute the function asosiated with it
        self.__onMessageReceivedevents = {
            "page0": self.__startPage0,
            "page1": self.__startPage1,
            "page2": self.__startPage2,
            "page3": self.__startPage3,
            "page4": self.__startPage4,
            "page5": self.__startPage5,
            "page10": self.__startPage10,
            "testCable": self.__testCable,
        }

    # end def

    def __message_received(self, message: str):
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
            self.__runClockTask(function == "page0")

            return (
                self.__onMessageReceivedevents[function](params)
                if len(params) > 0
                else self.__onMessageReceivedevents[function]()
            )

        # end if

    # end def

    def __printError(self, message: str):

        splittedMessage, lineHeight = self.__getTextWidth(message)

        # Only 3 lines can be displayed as maximum
        if len(splittedMessage) > 3:
            s = ""

            for line in splittedMessage[2:]:
                s = f"{s} {line.strip()}"
            # end for

            splittedMessage = splittedMessage[:2]
            splittedMessage.append(s)

        self.__screenService.sendMessage("page 6")

        self.__screenService.sendMessage('errorMsg.txt=""')

        self.__screenService.sendMessage('xstr 34,19,250,35,0,WHITE,0,1,1,0,"Error"')

        y = 19 + 35
        for line in splittedMessage:
            self.__screenService.sendMessage(
                f'xstr 34,{y},250,{lineHeight},2,WHITE,0,1,1,0,"{line}"'
            )
            y += lineHeight + 5
        # end for

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
        self.__screenService.sendMessage("page 0")

    # end def

    def __startPage1(self):
        self.__screenService.sendMessage("page 1")

    # end def

    def __startPage2(self, message: str):
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
        self.__screenService.sendMessage("page 2")

        # load test program to microcontroller
        boardCorrectlyProgrammed = self.__loadProgramToBoard(firmware.testProgram)

        # turn off loadiding animation
        if animationStarted:
            self.showLoadingAnimation(False, waveId[1])
            self.__screenService.sendMessage("cle 2,255")  # cleaning id 2 waveform

        # go to page 3 if succesfuly programmed
        if boardCorrectlyProgrammed:
            self.__screenService.sendMessage("page 3")
            self.__startPage3()
        else:
            self.__screenService.sendMessage("page 9")

    # end def

    def __startPage3(self):
        if self.__testButton("DispBtn On\r\n"):
            self.__screenService.sendMessage("page 4")
        else:
            self.__printError("No se detectó el botón.\n PRUEBA NO APROBADA")

    # end def

    def __startPage4(self):
        if self.__testButton("fillBtn On\r\n"):
            self.__screenService.sendMessage("page 5")
        else:
            self.__printError("No se detectó el botón.\n PRUEBA NO APROBADA")

    # end def

    def __startPage5(self, message: str):
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

        time.sleep(2)

        self.__gpioService.setPin(gpio.pinDefinition.floatingSwitch_Output, True)

        result = self.__testButton("FloatingSwitchOn\r\n", 10)

        self.__gpioService.togglePin(gpio.pinDefinition.floatingSwitch_Output)

        # turn off loadiding animation
        if animationStarted:
            self.showLoadingAnimation(False, waveId[1])
            self.__screenService.sendMessage("cle 2,255")  # cleaning id 2 waveform

        self.__loadProgramToBoard(firmware.productionProgram)

        if result:
            self.__screenService.sendMessage("page 8")
        else:
            self.__screenService.sendMessage("page 9")

    # end def

    def __startPage10(self):
        self.__screenService.sendMessage("page 10")

    def __testButton(self, expectedMessage: str, timeout: float = 60) -> bool:
        # start a timer for 60 seconds or something
        startTime = time.time()

        while True:
            if time.time() - startTime > timeout:
                return False
            # end if

            # check on input messages messages to check if the button was pressed
            message = self.__boardService.getMessage()

            if isinstance(message, str) and message.strip() == expectedMessage.strip():
                return True
            # end if

        # end while

        # need to add a cancel test button on every screen
        pass

    # end def

    def __testCable(self):
        self.__gpioService.setPin(
            [
                gpio.pinDefinition.harnessBlack_Output,
                gpio.pinDefinition.harnessRed_Output,
                gpio.pinDefinition.harnessWhite_Output,
                gpio.pinDefinition.harnessGreen_Output,
            ],
            True,
        )

        attempts = 0
        result = False

        while attempts < 5 and not result:

            for level in self.__gpioService.readPin(
                [
                    gpio.pinDefinition.harnessBlack_Input,
                    gpio.pinDefinition.harnessRed_Input,
                    gpio.pinDefinition.harnessWhite_Input,
                    gpio.pinDefinition.harnessGreen_Input,
                ]
            ):
                attempts += 1

                if not level:
                    result = False
                    break
                else:
                    result = True
                # end if

            # end for

        # end while

        self.__screenService.sendMessage(f"page { 8 if result else 9 }")

        self.__gpioService.togglePin(
            [
                gpio.pinDefinition.harnessBlack_Output,
                gpio.pinDefinition.harnessRed_Output,
                gpio.pinDefinition.harnessBlack_Output,
                gpio.pinDefinition.harnessBlack_Output,
            ]
        )

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
        self.__screenService.closeConnection()
        self.__boardService.dispose()
        self.__gpioService.cleanup()

    # end def

    def sendMessage(self, message: str):
        self.__screenService.sendMessage(message)

    # end def

    def showLoadingAnimation(self, show: bool, waveFormObjectId: int):
        with self.__showLoadingAnimation_lock:
            self.__showLoadingAnimation = show
            self.__waveID = waveFormObjectId

    # end def


# end class
