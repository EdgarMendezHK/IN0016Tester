import serial
import threading
import libraries.cancellationToken as ct
from queue import Queue


class spiScreen:

    def __del__(self):
        if len(self.tasks.items()) > 0 or self.serialConnection.is_open:
            self.closeConnection()

    # end def
    def __init__(self, logger, port, baudrate, rtsCts, timeout=0):
        self.__loggingSerivice = logger
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

        self.tasks = {
            "readingTask": self.__createTask(readingThread),
            "writingTask": self.__createTask(writingThread),
        }

    # end def

    def __read(self, serial, token):
        m = b""
        self.__loggingSerivice.info("readingThread started started")

        while not token.cancelled:
            try:
                s = serial.read(100)
                if s != b"":
                    self.__loggingSerivice.info("Message being read")
                    m = m + s
                if len(m) >= 2 and m[-2] == b"\r"[0] and m[-1] == b"\n"[0]:
                    message = m.decode("utf-8", errors="ignore").strip()
                    self.__loggingSerivice.info("Message received.\n" + message)
                    self.__inputMessages.put(message)
                    m = b""
            except Exception as e:
                self.__loggingSerivice.error(f"Read error: {e}")
                print(f"Read error: {e}")
            # end try-except
        # end while
        self.__loggingSerivice.warning("readingThread finished")

    # end def

    def __write(self, serial, token):
        self.__loggingSerivice.info("writingThread started")
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
                self.__loggingSerivice.info("Message sent. " + userMessage)
            except Exception as e:
                self.__loggingSerivice.error(f"writting error: {e}")
            # end try-catch
        # end while
        self.__loggingSerivice.warning("WritingThread finished")

    # end def

    def __writingTaskAux(self, task, token, identifier):
        self.__loggingSerivice.info(f"{identifier}Thread started")

        while not self.token.cancelled and not token.cancelled:
            self.__outputMessages.put(task())
        # end while

        self.__loggingSerivice.warning(f"{identifier}Thread finished")

    # end def

    def __createTask(self, task, cancellationToken=None):
        if cancellationToken is None:
            cancellationToken = ct.cancellationToken()
        # end if

        return {"task": task, "cancellationToken": cancellationToken}

    # end def

    def closeConnection(self):
        self.token.cancel()
        self.__loggingSerivice.warning("canceling all tasks")

        for taskName, task in self.tasks.items():
            self.__loggingSerivice.info(f"joining {taskName}Thread")
            task["task"].join()
            self.__loggingSerivice.info(f"{taskName}Thread joined")
        # end for

        self.tasks.clear()
        self.serialConnection.close()
        self.__loggingSerivice.info(f"serial port closed")

    # end def

    def getInputMessage(self):
        if self.__inputMessages.qsize() == 0:
            return None
        return self.__inputMessages.get()

    # end def

    def runWritingTask(self, task, identifier):
        if identifier in self.tasks:
            raise KeyError("Repeted key value")
        # end if
        token = ct.cancellationToken()
        t = threading.Thread(
            target=self.__writingTaskAux, args=[task, token, identifier]
        )
        t.start()

        self.tasks[identifier] = self.__createTask(t, token)

    # end def

    def stopTask(self, identifier):
        if identifier in self.tasks:
            self.tasks[identifier]["cancellationToken"].cancel()
            self.__loggingSerivice.warning(f"cancelling {identifier}Thread")
            self.tasks[identifier]["task"].join()
            self.__loggingSerivice.info(f"{identifier}Thread joined")
            del self.tasks[identifier]
            self.__loggingSerivice.warning(f"{identifier}Thread deleted from tasks")
        else:
            self.__loggingSerivice.warining(f"{identifier} not in tasks")

    # end def


# end class
