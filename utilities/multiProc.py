import multiprocessing

cpuCount = multiprocessing.cpu_count()

def chunk(N, nProcs):
    nProcs = min(N, nProcs)
    chunkSize = int(N / nProcs)
    chunks = []
    preR = 0
    
    for i in range(nProcs):
        if i == nProcs - 1: chunks.append((preR + 1, N))
        else:
            chunks.append((preR + 1, preR + chunkSize))
            preR = preR + chunkSize

    return chunks

def multiProcFunc(func, N, nProcs = 0):
    if nProcs == 0: #default
        nProcs = cpuCount
        
    chunks = chunk(N, nProcs)

    with multiprocessing.Pool(len(chunks)) as p:
        ret = p.map(func, chunks)

    return ret

'''
from utilities.multiProc import multiProcFunc
if __name__ == "__main__":
    print(multiProcFunc(funcName, N))
'''