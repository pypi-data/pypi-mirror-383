def minimax(tree, depth, maximizing):
    if depth == 0 or not isinstance(tree, list):
        return tree
    if maximizing:
        return max(minimax(child, depth-1, False) for child in tree)
    else:
        return min(minimax(child, depth-1, True) for child in tree)

if __name__ == '__main__':
    tree = [[3,5],[2,9]]
    print(minimax(tree, 2, True))
