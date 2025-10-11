import itertools

dist = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
]
n = len(dist)

def tour_distance(tour):
    d = 0
    for i in range(len(tour)-1):
        d += dist[tour[i]][tour[i+1]]
    d += dist[tour[-1]][tour[0]]
    return d

def brute_force_tsp():
    cities = list(range(n))
    best_dist = float('inf')
    best_tour = None
    for perm in itertools.permutations(cities[1:]):
        tour = [0] + list(perm)
        d = tour_distance(tour)
        if d < best_dist:
            best_dist = d
            best_tour = tour
    return best_tour, best_dist

if __name__ == "__main__":
    tour, dist_val = brute_force_tsp()
    print("Best tour (city indices):", tour)
    print("Minimum distance:", dist_val)
