from typing import Dict, Any
import os
import subprocess
import pathlib


class openOCD:
    _COMMAND = ["sudo", "openocd", "-f", "interface/raspberrypi-native.cfg", "-f"]

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize OpenOCD with the given configuration."""

        path = self._check_for_key_in_section("path", config)
        # changing directory so that it can look for the other keys if they exist
        os.chdir(path)

        test = self._check_for_key_in_section("testProgram", config)
        firmware = self._check_for_key_in_section("firmware", config)

        self.__test = test
        self.__firmware = firmware
        self.__path = path

    # end def

    def _check_for_key_in_section(self, key, dictionary):
        """Check for the given key in the dictionary and verify the path exists."""
        if key in dictionary:
            absolutePath = os.path.abspath(os.getcwd()) + "/"
            path = absolutePath + dictionary[key]

            if not os.path.exists(path):
                raise KeyError(f"path {path} does not exist")
            else:
                return path
            # end if

        else:
            raise KeyError("there's no path at openocd section")

        # end if

    # end def

    def _execute_command(self, file):
        """Execute the OpenOCD command with the given file."""
        command = self._COMMAND
        command.append(file)

        path = pathlib.Path(__file__).parent.resolve()
        path = path.parent / self.__path

        # os.chdir(path)

        result = subprocess.run(command, capture_output=True, text=True)

        # Print the output and errors
        return {
            "Output:": result.stdout,
            "Error:": result.stderr,
            "Success": result.returncode == 0,
        }

    # end def

    def burn_test_program(self):
        """Burn the microcontroller with the test program."""
        return self._execute_command(self.__test)

    # end def

    def burn_firmware(self):
        """Burn the microcontroller with the firmware."""
        return self._execute_command(self.__firmware)

    # end def


# end class
