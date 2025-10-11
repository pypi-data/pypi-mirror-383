import heapq

def heuristic(board, goal):
    return sum(abs(i//3 - (goal.index(val)//3)) + abs(i%3 - (goal.index(val)%3)) 
               for i, val in enumerate(board) if val != 0)

def get_neighbors(board):
    i = board.index(0)
    neighbors = []
    moves = [(-3, "up"), (3, "down"), (-1, "left"), (1, "right")]
    for m, _ in moves:
        ni = i + m
        if 0 <= ni < 9 and not (i%3==0 and m==-1) and not (i%3==2 and m==1):
            new_board = board[:]
            new_board[i], new_board[ni] = new_board[ni], new_board[i]
            neighbors.append(new_board)
    return neighbors

def astar(start, goal):
    open_list = [(heuristic(start, goal), 0, start, [start])]
    visited = set()
    while open_list:
        f, g, board, path = heapq.heappop(open_list)
        if board == goal: return path
        visited.add(tuple(board))
        for nb in get_neighbors(board):
            if tuple(nb) not in visited:
                heapq.heappush(open_list, (g+1+heuristic(nb, goal), g+1, nb, path+[nb]))
    return None

if __name__ == '__main__':
    start = [1,2,3,4,0,6,7,5,8]
    goal  = [1,2,3,4,5,6,7,8,0]
    solution = astar(start, goal)
    for step in solution:
        print(step[:3], step[3:6], step[6:])
        print("------")
