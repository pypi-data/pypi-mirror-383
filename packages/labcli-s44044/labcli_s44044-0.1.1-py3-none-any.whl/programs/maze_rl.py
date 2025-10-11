import numpy as np, random

maze = np.array([[0,0,0,-1],[0,-1,0,-1],[0,0,0,1]])
actions = ['up','down','left','right']
Q = {(i,j):{a:0 for a in actions} for i in range(3) for j in range(4) if maze[i,j]!=-1}

def move(s,a):
    i,j=s
    i,j = (i-1,j) if a=='up' else (i+1,j) if a=='down' else (i,j-1) if a=='left' else (i,j+1)
    return (i,j) if 0<=i<3 and 0<=j<4 and maze[i,j]!=-1 else s

for _ in range(500):
    s=(0,0)
    while maze[s]!=1:
        a = random.choice(actions) if random.random()<0.2 else max(Q[s],key=Q[s].get)
        ns = move(s,a); r=100 if maze[ns]==1 else -1
        Q[s][a] += 0.8*(r + 0.9*max(Q[ns].values()) - Q[s][a]); s=ns

for k in Q: print(k,Q[k])
