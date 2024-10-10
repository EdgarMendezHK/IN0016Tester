from typing import Dict, Any
from services.openOCD import openOCD
from libraries.serialDevice import serialDevice
import logging


class board:
    def __init__(
        self,
        openocdSerivce: openOCD,
        communicationInfoJson: Dict[str, Any],
        logger: logging,
    ) -> None:
        """Initialize board with the given configuration."""
        required_keys = ["port", "baudrate", "rtscts", "timeout"]

        for key in required_keys:
            if key not in communicationInfoJson:
                raise ValueError(f"Missing required key: {key}")
            # end if
        # end for

        self.__serial = serialDevice(
            logger,
            communicationInfoJson["port"],
            communicationInfoJson["baudrate"],
            communicationInfoJson["rtscts"],
            communicationInfoJson["timeout"],
            stopBits=communicationInfoJson["stopBits"],
            byteSize=communicationInfoJson["byteSize"],
            parity=communicationInfoJson["parity"],
        )

        self._openOCD_service = openocdSerivce

    # end def

    def LoadTestProgram(self) -> bool:
        result = self._openOCD_service.burn_test_program()

        if not result["Success"]:
            print(result)

        return result["Success"]

    # end def
    def LoadFirmware(self):
        return self._openOCD_service.burn_firmware()["Success"]

    # end def
    def getMessage(self) -> str:
        return self.__serial.getInputMessage()

    # end def
    def writeMessage(self, message: str) -> None:
        self.__serial.sendMessage(message)

    # end def
    def dispose(self) -> None:
        self.__serial.closeConnection()

    # end def

    def xd(self, message):
        print(message)

    # end def


# end class
