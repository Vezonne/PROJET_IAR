import random
import math
import numpy as np

class GeneticAlgorithm:
    def __init__(self, population_size=100, mutation_rate=0.04, crossover_rate=0.5, generations=200):
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
        return [random.uniform(-100, 100) for _ in range(83)]

    def evaluate_fitness(self, individual, Robot, WIDTH, HEIGHT, objects):
        
        for i, param in enumerate(individual):
            print(f"Individual[{i}]: {param}, Type: {type(param)}")
        # Suite de l'évaluation de la fitness

        # Simuler le robot avec ces paramètres et calculer sa fitness
        robot = Robot(WIDTH // 2, HEIGHT // 2)  # Créez une instance de robot
        for i, link in enumerate(robot.links):
            # Supposons que chaque individu a autant de paramètres que de liens
            link.transfer_function = self.create_transfer_function(individual[i])
        
        fitness = 0
        for _ in range(100):  # Simuler un certain nombre d'étapes
            robot.react_to_sensors()
            robot.update(WIDTH, HEIGHT, objects)
            # Calculer la fitness selon la fonction F = B1 + B2 / 400
            fitness += (robot.battery1 + robot.battery2 / 400)
            if not robot.alive:
                break
        return fitness

    def scale_value(self, value, min_range, max_range):
        """Mise à l'échelle d'une valeur entre 0 et 99 vers une nouvelle plage."""
        return min_range + (max_range - min_range) * (value / 99)

    def create_transfer_function(self, params):
        if isinstance(params, (list, tuple)):
            offset = self.scale_value(params[0], -100, 100)
            # Logique supplémentaire ici pour gérer plusieurs paramètres si nécessaire
        elif isinstance(params, (int, float)):
            offset = self.scale_value(params, -100, 100)
            # Logique pour un paramètre unique
            return lambda x: x * offset  # Exemple simple de fonction de transfert
        else:
            raise TypeError("Expected params to be a list, tuple, int, or float")

        threshold1 = self.scale_value(params[1], -100, 100)
        threshold2 = self.scale_value(params[2], threshold1, 100)
        gradient1 = np.tan(self.scale_value(params[3], -np.pi/2, np.pi/2))
        gradient2 = np.tan(self.scale_value(params[4], -np.pi/2, np.pi/2))
        sigmoid_threshold = self.scale_value(params[5], -3.0, 3.0)

        def transfer_function(sensor_value, battery_level):
            x = sensor_value * (battery_level / 100) + offset
            if x < threshold1:
                return gradient1 * (x - threshold1)
            elif x > threshold2:
                return gradient2 * (x - threshold2)
            else:
                return 1 / (1 + np.exp(-sigmoid_threshold * (x - (threshold1 + threshold2) / 2)))
        
        return transfer_function
    
    def crossover(self, parent1, parent2):
        # Mélange les paramètres des deux parents bit à bit
        child = []
        for i in range(len(parent1)):
            if random.random() < self.crossover_rate:
                child.append(parent1[i])
            else:
                child.append(parent2[i])
        return child

    def mutate(self, individual):
        # Modifie légèrement les paramètres d'un individu
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                individual[i] += random.uniform(-0.1, 0.1)
        return individual

    def select_parents(self, Robot, WIDTH, HEIGHT, objects):
        # Calculer la fitness pour chaque individu et sélectionner les parents basés sur ces valeurs
        fitnesses = [self.evaluate_fitness(ind, Robot, WIDTH, HEIGHT, objects) for ind in self.population]
        return random.choices(self.population, k=2, weights=fitnesses)

    def evolve(self, Robot, WIDTH, HEIGHT, objects):
        self.initialize_population()
        for generation in range(self.generations):
            new_population = []
            for _ in range(self.population_size):
                parent1, parent2 = self.select_parents(Robot, WIDTH, HEIGHT, objects)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            self.population = new_population
            
            # Affichage de la génération actuelle
            print(f"Generation {generation + 1}/{self.generations} completed.")

