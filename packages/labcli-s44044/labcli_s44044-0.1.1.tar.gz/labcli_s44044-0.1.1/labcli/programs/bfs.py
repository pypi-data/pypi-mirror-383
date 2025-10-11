from collections import deque

def bfs(graph, start):
    visited = set()
    q = deque([start])
    visited.add(start)
    while q:
        v = q.popleft()
        print(v)
        for n in graph.get(v, []):
            if n not in visited:
                visited.add(n)
                q.append(n)

if __name__ == '__main__':
    g = {'A':['B','C'], 'B':['D'], 'C':['E'], 'D':[], 'E':[]}
    bfs(g, 'A')
