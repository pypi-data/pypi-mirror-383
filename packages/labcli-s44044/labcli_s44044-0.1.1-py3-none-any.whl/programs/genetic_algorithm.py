import random

weights = [2, 3, 4, 5]
values = [3, 4, 5, 6]
capacity = 5
num_items = len(weights)

def fitness(chromosome):
    total_weight = sum(weights[i] for i in range(num_items) if chromosome[i] == 1)
    total_value = sum(values[i] for i in range(num_items) if chromosome[i] == 1)
    if total_weight > capacity:
        return 0
    return total_value

def init_population(size):
    return [[random.randint(0, 1) for _ in range(num_items)] for _ in range(size)]

def selection(pop, fitnesses):
    total_fitness = sum(fitnesses)
    if total_fitness == 0:
        return random.choice(pop)
    pick = random.uniform(0, total_fitness)
    current = 0
    for i, f in enumerate(fitnesses):
        current += f
        if current > pick:
            return pop[i]

def crossover(parent1, parent2):
    point = random.randint(1, num_items - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(chromosome, rate=0.05):
    return [gene ^ 1 if random.random() < rate else gene for gene in chromosome]

def genetic_algorithm(pop_size=6, generations=20):
    population = init_population(pop_size)

    for gen in range(generations):
        fitnesses = [fitness(ch) for ch in population]
        best_idx = fitnesses.index(max(fitnesses))
        best_value = fitnesses[best_idx]
        best_items = population[best_idx]
        print(f"Gen {gen}: Best Value = {best_value}, Items = {best_items}")
        new_population = []
        while len(new_population) < pop_size:
            parent1 = selection(population, fitnesses)
            parent2 = selection(population, fitnesses)
            child1, child2 = crossover(parent1, parent2)
            new_population.append(mutate(child1))
            if len(new_population) < pop_size:
                new_population.append(mutate(child2))
        population = new_population

    fitnesses = [fitness(ch) for ch in population]
    best_idx = fitnesses.index(max(fitnesses))
    return population[best_idx], fitnesses[best_idx]

if __name__ == '__main__':
    best_solution, best_value = genetic_algorithm()
    print(f"\nBest solution found: Items = {best_solution}, Value = {best_value}")
