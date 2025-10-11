def alphabeta(coins, left, right, maximizing, alpha, beta):
    # Base case: no coins left
    if left > right:
        return 0

    if maximizing:  # First player's turn (maximize score)
        take_left = coins[left] + alphabeta(coins, left+1, right, False, alpha, beta)
        take_right = coins[right] + alphabeta(coins, left, right-1, False, alpha, beta)
        val = max(take_left, take_right)
        alpha = max(alpha, val)
        return val
    else:  # Opponent's turn (minimize first player's score)
        take_left = alphabeta(coins, left+1, right, True, alpha, beta)
        take_right = alphabeta(coins, left, right-1, True, alpha, beta)
        val = min(take_left, take_right)
        beta = min(beta, val)
        return val


if __name__ == '__main__':
    coins = [3, 9, 1, 2]
    print("Coins:", coins)
    best_score = alphabeta(coins, 0, len(coins)-1, True, float('-inf'), float('inf'))
    print("Best guaranteed score for Player 1:", best_score)
