from utilities.multiProc import multiProcFunc

def lol(rng):
    l, r = rng
    return (l, r)

if __name__ == "__main__":
    print(multiProcFunc(lol, 10))