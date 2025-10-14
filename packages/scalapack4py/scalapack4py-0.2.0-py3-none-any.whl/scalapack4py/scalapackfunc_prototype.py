class ScaLAPACKfunc():
    #
    # A generic Pythonic implementation of a given ScaLAPACK function.
    #
    
    def __init__(self, symbol, argtypes, restypes, argcasts):
        # Symbol of function from BLACS library
        self.symbol = symbol
        # Argument types used by Cfunc
        self.symbol.argtypes = argtypes
        # Residual types
        self.symbol.restypes = restypes
        # Argument casting functions for each arg type
        self.argcasts = argcasts

    def argtypes_cast(self, *args):
        # Performs the relevant type casts before executing Cfunc
        args_list = []
        for idx, arg in enumerate(args):
            if self.argcasts[idx] is None:
                args_list.append(arg)
            else:
                try:
                    args_list.append(self.argcasts[idx](arg))
                except TypeError as err:
                    print(f"Mismatched type casting for input {idx}")
                    print("TypeError:", err)
                    raise

        return tuple(args_list)

    def __call__(self, *args):
        args = self.argtypes_cast(*args)
        self.symbol(*args)
