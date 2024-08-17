import serial
import threading
import libraries.cancellationToken as ct
from queue import Queue


class spiScreen:

    def __del__(self):
        self.closeConnection()

    # end def
    def __init__(self, port, baudrate, rtsCts, timeout=0):
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

        self.tasks = {"readingTask": readingThread, "writingTask": writingThread}

    # end def

    def __read(self, serial, token):
        m = b""

        while not token.cancelled:
            try:
                s = serial.read(100)
                if s != b"":
                    m = m + s
                if len(m) >= 2 and m[-2] == b"\r"[0] and m[-1] == b"\n"[0]:
                    self.__inputMessages.put(m.decode("utf-8", errors="ignore").strip())
                    m = b""
            except:
                print("error")

    # end def

    def __write(self, serial, token):
        while not token.cancelled:

            if self.__outputMessages.qsize() > 0:
                continue
            # end if

            userMessage = self.__outputMessages.get()

            # enter t0.txt="1" to set text to 1
            encodedMessage = (
                userMessage.encode("utf-8") + b"\xff\xff\xff"
            )  # b't0.txt="1"\xff\xff\xff'

            serial.write(encodedMessage)
        # end while

    # end def

    def __writingTaskAux(self, task):
        while not self.token.cancelled:
            self.__outputMessages.put(task())
        # end while

    # end def

    def closeConnection(self):
        self.token.cancel()

        for taskName, task in self.tasks.items():

            task.join()
            print(taskName + " finished and joined to main thread")
        # end for

        self.serialConnection.close()

        print("Connection with spi display closed")

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

        t = threading.Thread(target=self.__writingTaskAux, args=[task])
        t.start()

        self.tasks[identifier] = t

    # end def


# end class
