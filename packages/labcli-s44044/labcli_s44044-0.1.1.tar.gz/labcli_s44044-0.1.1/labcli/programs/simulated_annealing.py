import random, math

jobs = [2, 5, 7, 3, 1]
machines = 2

def makespan(schedule):
    loads = [0]*machines
    for i, m in enumerate(schedule):
        loads[m] += jobs[i]
    return max(loads)

def sa(schedule, T=1000, alpha=0.95, stop=1e-3):
    current = schedule[:]
    best = schedule[:]
    while T > stop:
        i = random.randint(0, len(schedule)-1)
        new_schedule = current[:]
        new_schedule[i] = 1 - new_schedule[i]
        delta = makespan(new_schedule) - makespan(current)
        if delta < 0 or random.random() < math.exp(-delta/T):
            current = new_schedule
            if makespan(current) < makespan(best):
                best = current
        T *= alpha
    return best

if __name__ == '__main__':
    init = [random.randint(0,1) for _ in jobs]
    best_schedule = sa(init)
    print("Best assignment:", best_schedule)
    print("Minimum makespan:", makespan(best_schedule))
