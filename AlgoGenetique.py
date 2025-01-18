import random
import math

class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, generations):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations
        self.population = []

    def initialize_population(self):
        # Initialiser la population avec des paramètres aléatoires
        self.population = [self.random_individual() for _ in range(self.population_size)]

    def random_individual(self):
        # Génère un individu avec des paramètres aléatoires pour les liens
        return [random.uniform(-1, 1) for _ in range(10)]  # Exemple de 10 paramètres

    def evaluate_fitness(self, individual, Robot, WIDTH, HEIGHT):
    # Simuler le robot avec ces paramètres et calculer sa fitness
        robot = Robot(WIDTH // 2, HEIGHT // 2)  # Créez une instance de robot
        for i, link in enumerate(robot.links):
            # Supposons que chaque individu a autant de paramètres que de liens
            link.transfer_function = self.create_transfer_function(individual[i])
        
        fitness = 0
        for _ in range(100):  # Simuler un certain nombre d'étapes
            robot.react_to_sensors()
            robot.update(WIDTH, HEIGHT)
            # Mesurez la performance, par exemple, en fonction de la durée de vie et des batteries
            fitness += (robot.battery1 + robot.battery2) / 2
            if not robot.alive:
                break
        return fitness

    def create_transfer_function(self, param):
        # Exemple de création d'une fonction de transfert simple basée sur un paramètre
        return lambda sensor_value, battery_level: param * sensor_value * (battery_level / 100)

    def select_parents(self):
        # Sélectionne deux parents basés sur la fitness
        return random.choices(self.population, k=2)

    def crossover(self, parent1, parent2):
        # Mélange les paramètres des deux parents
        if random.random() < self.crossover_rate:
            point = random.randint(1, len(parent1) - 1)
            return parent1[:point] + parent2[point:]
        return parent1

    def mutate(self, individual):
        # Modifie légèrement les paramètres d'un individu
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                individual[i] += random.uniform(-0.1, 0.1)
        return individual

    def evolve(self):
        self.initialize_population()
        for _ in range(self.generations):
            new_population = []
            for _ in range(self.population_size):
                parent1, parent2 = self.select_parents()
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            self.population = new_population

