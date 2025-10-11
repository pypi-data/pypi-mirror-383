import random

def q_learning():
    Q = {}
    for _ in range(100):
        s = random.randint(0,4)
        a = random.randint(0,1)
        Q[(s,a)] = Q.get((s,a), 0) + 0.1
    print('Q sample:', list(Q.items())[:5])

if __name__ == '__main__':
    q_learning()
