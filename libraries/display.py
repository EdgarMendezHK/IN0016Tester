import serial
import threading
import numpy as nm
import libraries.cancellationToken as ct
from queue import Queue
from time import sleep


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
        self.__showLoadingAnimmation = False

        self.runWritingTask(self.__processLoadingAnnimation, "loading", 1 / 60)

    # end def

    def __read(self, serial, token):
        m = b""
        self.__loggingService.info("readingThread started started")

        while not token.cancelled:
            try:
                s = serial.readline(100)
                if s != b"":
                    self.__loggingService.info("Message being read")
                    m = m + s
                if len(m) >= 2 and m[-2] == b"\r"[0] and m[-1] == b"\n"[0]:
                    message = m.decode("utf-8", errors="ignore").strip()
                    self.__loggingService.info("Message received.\n" + message)

                    m = b""

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
                self.__loggingService.info("Message sent. " + userMessage)
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

    def __processLoadingAnnimation(self):
        if not hasattr(spiScreen.__processLoadingAnnimation, "i"):
            spiScreen.__processLoadingAnnimation.i = 0  # Initialize a static variable

        if self.__showLoadingAnimmation:
            results = []

            val = (
                int(100 * nm.sin(spiScreen.__processLoadingAnnimation.i * nm.pi / 16))
                + 150
            )

            for channel in [0, 1, 2, 3]:
                offset = channel * 10
                channelVal = val - offset

                if channelVal < 0:
                    channelVal = 0 + offset
                elif channelVal > 255:
                    channelVal = 255 - offset
                # end if

                s = f"add 2,{channel},{channelVal}"

                results.append(s)
            # end for

            spiScreen.__processLoadingAnnimation.i += 1

            return results
        else:
            spiScreen.__processLoadingAnnimation.i = 0
            return "cle 2,255"
        # end if

    # end def

    def runWritingTask(self, task, identifier, wait=0.2):
        if identifier in self.__tasks:
            raise KeyError("Repeted key value")
        # end if
        token = ct.cancellationToken()
        t = threading.Thread(
            target=self.__writingTaskAux, args=[task, token, identifier, wait]
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

    def showLoadingAnimation(self, show):
        self.__showLoadingAnimmation = show

    # end def


# end class
