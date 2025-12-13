from utilities.multiProc import multiProcFunc

def skibidi():
    def lol(rng):
        l, r = rng
        return (l, r)

    if __name__ == "__main__":
        print(multiProcFunc(lol, 10))

skibidi()