import RPi.GPIO as gpio
from enum import Enum


class pinDefinition(Enum):
    floatingSwitch_Output = 21
    harnessRed_Output = 16
    harnessGreen_Output = 19
    harnessBlack_Output = 20
    harnessWhite_Output = 26
    harnessRed_Input = 5
    harnessGreen_Input = 6
    harnessBlack_Input = 12
    harnessWhite_Input = 13


# end class


class GPIO:
    def __init__(self):

        # setting gpio mode
        gpio.setmode(gpio.BCM)
        """
        gpio.setup(__pinDefinition.floatingSwitch_Output, gpio.OUT)
        gpio.setup(__pinDefinition.harnessRed_Output, gpio.OUT)
        gpio.setup(__pinDefinition.harnessBlack_Output, gpio.OUT)
        gpio.setup(__pinDefinition.harnessGreen_Output, gpio.OUT)
        gpio.setup(__pinDefinition.harnessWhite_Output, gpio.OUT)
        gpio.setup(__pinDefinition.harnessRed_Input, gpio.IN)
        gpio.setup(__pinDefinition.harnessBlack_Input, gpio.IN)
        gpio.setup(__pinDefinition.harnessWhite_Input, gpio.IN)
        gpio.setup(__pinDefinition.harnessGreen_Input, gpio.IN)
        """
        for pin in pinDefinition:
            if isinstance(pin.value, int):
                if "_Output" in pin.name:
                    gpio.setup(pin.value, gpio.OUT, initial=gpio.LOW)
                elif "_Input" in pin.name:
                    gpio.setup(pin.value, gpio.IN, pull_up_down=gpio.PUD_DOWN)
                else:
                    raise Exception(
                        f"Invalid format. Pin at __pinDefinition enum must follow the format [pin name]_Input or [pin name]_Output. Current name is {pin.name}"
                    )
            else:
                raise ValueError(
                    f"The {pin.name}'s value, at {__file__}, must be an integer. Type = {type(pin.value)}"
                )

    # end def

    def readPin(self, pin: pinDefinition | list[pinDefinition]) -> bool | list[bool]:

        if isinstance(pin, pinDefinition):
            return gpio.input(pin.value)
        # end if

        result = []

        for p in pin:
            result.append(gpio.input(p.value))
        # end for

        return result

    # end def

    # end def

    def setPin(self, pin: pinDefinition | list[pinDefinition], level: bool) -> None:
        pinv = []
        if isinstance(pin, list):
            for p in pin:
                pinv.append(p.value)
        else:
            pinv = pin.value
        # end if

        gpio.output(pinv, level)

    # end def

    def togglePin(self, pin: pinDefinition | list[pinDefinition]) -> None:
        if isinstance(pin, pinDefinition):
            pin = [pin]
        # end if

        for p in pin:
            level = gpio.input(p.value)
            gpio.output(p.value, not level)

    # end def

    def cleanup(self) -> None:
        gpio.cleanup()

    # end def
