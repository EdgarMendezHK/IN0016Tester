from typing import Dict, Any
import os
import subprocess
import pathlib


class openOCD:
    _COMMAND = ["sudo", "openocd", "-f", "interface/raspberrypi-native.cfg", "-f"]

    def __init__(self, config: Dict[str, Any]) -> None:
        """ """

        if "path" in config:
            absolutePath = os.path.abspath(os.getcwd())
            path = absolutePath + config["path"]
            os.chdir(path)

            if not os.path.exists(path):
                raise KeyError("path does not exist")
            # end if
        else:
            raise KeyError("there's no path at openocd section")

        # end if

        test = ""

        if "testProgram" in config:
            if os.path.exists(config["testProgram"]):
                test = config["testProgram"]
            else:
                raise KeyError("the file " + config["testProgram"] + " does not exist")
            # end if
        else:
            raise KeyError("there is not testPorgram section at opencd section")
        # end if

        firmware = ""

        if "firmware" in config:

            if os.path.exists(config["firmware"]):
                firmware = config["firmware"]
            else:
                raise KeyError("there file" + config["firmware"] + "does not exist")
            # end if
        else:
            raise KeyError("there is not testPorgram section at opencd section")
        # end if

        self.__test = test
        self.__firmware = firmware
        self.__path = path

    # end def

    def __executeCommand(self, file):
        command = self._COMMAND
        command.append(file)

        path = pathlib.Path(__file__).parent.resolve()
        path = path.parent / self.__path

        os.chdir(path)

        result = subprocess.run(command, capture_output=True, text=True)

        # Print the output and errors
        return {
            "Output:": result.stdout,
            "Error:": result.stderr,
            "Success": result.returncode == 0,
        }

    # end def

    def burnTestProgram(self):
        return self.__executeCommand(self.__test)

    # end def

    def burnFirmware(self):
        return self.__executeCommand(self.__firmware)

    # end defs


# end class
