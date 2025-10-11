world = [['E','E','E','G'],
         ['E','E','P','P'],
         ['E','W','E','E'],
         ['E','E','E','E']]

agent_pos = [0,0]
alive = True
gold = False

def perceive(r,c):
    percepts = []
    adj = [(r-1,c),(r+1,c),(r,c-1),(r,c+1)]
    for x,y in adj:
        if 0<=x<4 and 0<=y<4:
            if world[x][y] == 'P':
                percepts.append('Breeze')
            if world[x][y] == 'W':
                percepts.append('Stench')
    if world[r][c] == 'G': percepts.append('Glitter')
    return percepts

moves = [(0,1),(1,0),(1,0),(0,1)]
for dr,dc in moves:
    if not alive: break
    agent_pos[0]+=dr
    agent_pos[1]+=dc
    r,c = agent_pos
    if world[r][c] == 'P' or world[r][c] == 'W':
        alive = False
        print("Agent died!")
    elif world[r][c] == 'G':
        gold = True
        print("Gold found!")
    print(f"Position: {agent_pos}, Percepts: {perceive(r,c)}")
