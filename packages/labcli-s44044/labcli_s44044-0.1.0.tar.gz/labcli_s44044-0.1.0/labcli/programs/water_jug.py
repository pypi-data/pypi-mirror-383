from math import gcd

def water_jug_problem(m, n, d):
    if d > max(m, n):
        return "Not possible"
    if d % gcd(m, n) != 0:
        return "Not possible"

    def pour(fromCap, toCap, target):
        fromJug, toJug = fromCap, 0
        steps = [(fromJug, toJug)]
        while (fromJug != target) and (toJug != target):
            temp = min(fromJug, toCap - toJug)
            toJug += temp
            fromJug -= temp
            steps.append((fromJug, toJug))
            if fromJug == target or toJug == target:
                break
            if fromJug == 0:
                fromJug = fromCap
                steps.append((fromJug, toJug))
            if toJug == toCap:
                toJug = 0
                steps.append((fromJug, toJug))
        return steps

    steps1 = pour(m, n, d)
    steps2 = pour(n, m, d)
    return steps1 if len(steps1) <= len(steps2) else steps2

if __name__ == '__main__':
    m, n, d = 4, 3, 2
    solution = water_jug_problem(m, n, d)
    print("Steps to solve:")
    for step in solution:
        print(step)
