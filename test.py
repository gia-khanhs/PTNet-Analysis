import multiprocessing as mp
from threading import Thread

def runChunk(lr):
    l, r = lr
    return (l, r)

def test():
    N = 10

    nProcs = min(N, 4)
    chunkSize = int(N / nProcs)
    chunk = []
    preR = 0
    for i in range(nProcs):
        if i == nProcs - 1: chunk.append((preR + 1, N))
        else: 
            chunk.append((preR + 1, preR + chunkSize))
            preR = preR + chunkSize

    
    if __name__ == "__main__":
        with mp.Pool(nProcs) as p:
            print(p.map(runChunk, chunk))

test()