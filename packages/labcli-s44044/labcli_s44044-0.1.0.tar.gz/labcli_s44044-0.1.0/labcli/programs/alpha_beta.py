def alpha_beta(tree, depth, alpha, beta, agent_turn):
    if depth == 0 or not isinstance(tree, list):
        return tree
    if agent_turn:
        value = -float('inf')
        for node in tree:
            value = max(value, alpha_beta(node, depth-1, alpha, beta, False))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        for node in tree:
            value = min(value, alpha_beta(node, depth-1, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

if __name__ == '__main__':
    tree = [[3, 5, 6], [3, 2, 9], [0, 1, 4]]
    print("Best achievable value:", alpha_beta(tree, 2, -float('inf'), float('inf'), True))
