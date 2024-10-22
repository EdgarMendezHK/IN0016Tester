class cancellationToken:
    def __init__(self):
        self.cancelled = False

    # end def

    def cancel(self):
        self.cancelled = True

    # end def


# end class
