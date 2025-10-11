import random

def hill_climb(f, init, steps=100):
    current = init
    current_val = f(current)
    for _ in range(steps):
        neighbor = current + random.choice([-1,1])
        val = f(neighbor)
        if val > current_val:
            current, current_val = neighbor, val
    return current, current_val

if __name__ == '__main__':
    f = lambda x: -(x-5)**2 + 25
    print(hill_climb(f, 0))
