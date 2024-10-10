import RPi.GPIO as gpio
from enum import Enum


class OutputPin(Enum):
    FLOATING_SWITCH = 21
    HARNESS_RED = 16
    HARNESS_GREEN = 19
    HARNESS_BLACK = 20
    HARNESS_WHITE = 26


# end class


class InputPin(Enum):
    HARNESS_RED = 5
    HARNESS_GREEN = 6
    HARNESS_BLACK = 12
    HARNESS_WHITE = 13


# end class


class GPIO:
    def __init__(self):

        # setting gpio mode
        gpio.setmode(gpio.BCM)

        # check for repeated values between input and output pins
        for output in OutputPin:
            for input in InputPin:
                if output.value == input.value:
                    raise ValueError(
                        f'Repeated value for input and output pins. "{output.name} at OutputPin enum and "{input.name}" at InputPin enum'
                    )
                    break

        # setting output pins
        for pin in OutputPin:
            if isinstance(pin.value, int):
                gpio.setup(pin.value, gpio.OUT, initial=gpio.LOW)
            else:
                raise ValueError(
                    f"The {pin.name}'s value, at OutputPin enum in {__file__}, must be an integer. Type = {type(pin.value)}"
                )

        # setting input pins
        for pin in InputPin:
            if isinstance(pin.value, int):
                gpio.setup(pin.value, gpio.IN, pull_up_down=gpio.PUD_DOWN)
            else:
                raise ValueError(
                    f"The {pin.name}'s value at InputPin enum in {__file__}, must be an integer. Type = {type(pin.value)}"
                )

    # end def

    def readPin(self, pin: InputPin | list[InputPin]) -> bool | list[bool]:

        if isinstance(pin, InputPin):
            return gpio.input(pin.value)
        # end if

        result = []

        for p in pin:
            result.append(gpio.input(p.value))
        # end for

        return result

    # end def

    def setPin(self, pin: OutputPin | list[OutputPin], level: bool) -> None:
        pinv = []
        if isinstance(pin, list):
            for p in pin:
                pinv.append(p.value)
        else:
            pinv = pin.value
        # end if

        gpio.output(pinv, level)

    # end def

    def togglePin(self, pin: OutputPin | list[OutputPin]) -> None:
        if isinstance(pin, OutputPin):
            pin = [pin]
        # end if

        for p in pin:
            level = gpio.input(p.value)
            gpio.output(p.value, not level)

    # end def

    def cleanup(self) -> None:
        gpio.cleanup()

    # end def
