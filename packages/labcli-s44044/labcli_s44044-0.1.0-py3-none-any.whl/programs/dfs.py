def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start)
    for n in graph.get(start, []):
        if n not in visited:
            dfs(graph, n, visited)

if __name__ == '__main__':
    g = {'A':['B','C'], 'B':['D'], 'C':['E'], 'D':[], 'E':[]}
    dfs(g, 'A')
