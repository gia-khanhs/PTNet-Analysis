from utilities.multiProc import multiProcFunc

def lol(rng):
        l, r = rng
        return (l, r)

def skibidi():
    print(multiProcFunc(lol, 10))
