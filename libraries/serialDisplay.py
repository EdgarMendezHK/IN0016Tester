import serial
import threading
import libraries.cancellationToken as ct
from queue import Queue
from time import sleep
from typing import Callable, Union, List


class spiScreen:

    def __del__(self):
        if len(self.__tasks.items()) > 0 or self.serialConnection.is_open:
            self.closeConnection()

    # end def
    def __init__(self, logger, port, baudrate, rtsCts, timeout=0):
        self.__loggingService = logger
        self.__outputMessages = Queue(maxsize=100)
        self.__inputMessages = Queue(maxsize=100)

        self.serialConnection = serial.Serial(
            port, baudrate, timeout=timeout, rtscts=rtsCts
        )
        self.token = ct.cancellationToken()

        readingThread = threading.Thread(
            target=self.__read, args=[self.serialConnection, self.token]
        )
        writingThread = threading.Thread(
            target=self.__write, args=[self.serialConnection, self.token]
        )

        readingThread.start()
        writingThread.start()

        self.__tasks = {
            "readingTask": self.__createTask(readingThread),
            "writingTask": self.__createTask(writingThread),
        }

        self.__onMessageReceivedEventSet = None

    # end def

    def __read(self, serial: serial, token):
        m = b""
        self.__loggingService.info("readingThread started started")

        while not token.cancelled:
            try:
                m = serial.readline()
                m = bytes(filter(lambda x: x in range(32, 127), m))

                if m != b"":
                    m += b"\r\n"
                    message = m.decode("utf-8", errors="ignore")

                    if self.__onMessageReceivedEventSet:
                        self.__onMessageReceivedEventSet(message)
                    else:
                        self.__inputMessages.put(message)

            except Exception as e:
                self.__loggingService.error(f"Read error: {e}")
                print(f"Read error: {e}")
            # end try-except

        # end while
        self.__loggingService.warning("readingThread finished")

    # end def

    def __write(self, serial, token):
        self.__loggingService.info("writingThread started")
        while not token.cancelled:
            try:
                # if there are not queued messages will remain in here
                if self.__outputMessages.qsize() == 0:
                    continue
                # end if

                userMessage = self.__outputMessages.get()

                # enter t0.txt="1" to set text to 1
                encodedMessage = (
                    userMessage.encode("utf-8") + b"\xff\xff\xff"
                )  # b't0.txt="1"\xff\xff\xff'

                serial.write(encodedMessage)  # sendig message to spi device
            except Exception as e:
                self.__loggingService.error(f"writting error: {e}")
            # end try-catch
        # end while
        self.__loggingService.warning("WritingThread finished")

    # end def

    def __writingTaskAux(self, task, token, identifier, wait):
        self.__loggingService.info(f"{identifier}Thread started")

        while not self.token.cancelled and not token.cancelled:

            res = task()

            if isinstance(res, str):
                self.__outputMessages.put(res)

            elif isinstance(res, list):
                for item in res:
                    if item != None and item.strip() != "":
                        self.__outputMessages.put(item)
                    # end if
                # end for
            # end if
            sleep(wait)
        # end while

        self.__loggingService.warning(f"{identifier}Thread finished")

    # end def

    def __createTask(self, task, cancellationToken=None):
        if cancellationToken is None:
            cancellationToken = ct.cancellationToken()
        # end if

        return {"task": task, "cancellationToken": cancellationToken}

    # end def

    def closeConnection(self):
        self.token.cancel()
        self.__loggingService.warning("canceling all tasks")

        for taskName, task in self.__tasks.items():
            self.__loggingService.info(f"joining {taskName}Thread")
            task["task"].join()
            self.__loggingService.info(f"{taskName}Thread joined")
        # end for

        self.__tasks.clear()
        self.serialConnection.close()
        self.__loggingService.info(f"serial port closed")

    # end def

    def getInputMessage(self):
        if self.__inputMessages.qsize() == 0:
            return None
        return self.__inputMessages.get()

    # end def

    def onMessageReceivedEvent(self, callback):
        self.__onMessageReceivedEventSet = callback

    # end def

    def runWritingTask(
        self,
        callback: Callable[[], Union[str, List[str]]],
        identifier: str,
        wait: float = 0.2,
    ) -> None:
        """
        Executes the given callback in a new thread and sends it result to the spi device

        Arguments:
            callback (Callable[[], Union[str, List[str]]]): The callback function to call.
            identifier (str): Name of the thread. *This identifier can be used later to stop the thread*.
            wait (float): time for the thread to sleep in seconds after executing the call.

        Returns:
            None
        """
        if identifier in self.__tasks:
            raise KeyError("Repeted key value")
        # end if
        token = ct.cancellationToken()
        t = threading.Thread(
            target=self.__writingTaskAux,
            args=[callback, token, identifier, wait],
        )
        t.start()

        self.__tasks[identifier] = self.__createTask(t, token)

    # end def

    def sendMessage(self, message):
        self.__outputMessages.put(message)

    # end def

    def stopTask(self, identifier):
        if identifier in self.__tasks:
            self.__tasks[identifier]["cancellationToken"].cancel()
            self.__loggingService.warning(f"cancelling {identifier}Thread")
            self.__tasks[identifier]["task"].join()
            self.__loggingService.info(f"{identifier}Thread joined")
            del self.__tasks[identifier]
            self.__loggingService.warning(f"{identifier}Thread deleted from tasks")
        else:
            self.__loggingService.warning(f"{identifier} not in tasks")

    # end def

    def showLoadingAnimation(self, show, waveFormObjectId):
        self.__showLoadingAnimmation = show
        self.__waveID = waveFormObjectId

    # end def


# end class
