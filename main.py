from utilities.topologicalGraph import buildTopoGraph

dict = [{} for i in range(5)]
dict[1][2] = (1, 2)
print(len(dict[1][2]))