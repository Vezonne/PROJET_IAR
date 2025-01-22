import random
import numpy as np
from tqdm import tqdm

from myclass import *


class GeneticAlgorithm:
    def __init__(
        self,
        population_size=100,
        mutation_rate=0.04,
        crossover_rate=0.5,
        generations=200,
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations
        self.population = []

    def initialize_population(self):
        # Initialiser la population avec des paramètres aléatoires
        self.population = [
            self.random_individual() for _ in range(self.population_size)
        ]

    def random_individual(self):
        # Génère un individu avec des paramètres aléatoires pour les liens
        return [random.uniform(0, 99) for _ in range(83)]

    def evaluate_fitness(self, param, WIDTH, HEIGHT, objects):
        fitness = 0

        pygame.init()
        robot = Robot(WIDTH // 2, HEIGHT // 2)
        robot.set_all_param(param)

        max_time = 10_000
        for i in range(max_time):
            # Vérifier si le robot est mort
            if not robot.alive:
                running = False  # Arrêter la boucle principale si le robot est mort

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            robot.update(WIDTH, HEIGHT, objects)
            fitness += robot.battery1 + robot.battery2 / 400

        pygame.quit()

        return fitness

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
        mutated_list = []
        for param in individual:

            binary = format(int(param), "b").zfill(7)

            mutated_binary = "".join(
                bit if random.random() > self.mutation_rate else str(1 - int(bit))
                for bit in binary
            )

            mutated_param = int(mutated_binary, 2)

            if mutated_param > 99:
                mutated_param = 99

            mutated_list.append(mutated_param)

        return mutated_list

    def select_parents(self, fitnesses):
        fitnesses_tot = np.sum(fitnesses)
        prob = []
        for f in fitnesses:
            prob.append(f / fitnesses_tot)
        return random.choices(self.population, k=2, weights=prob)

    def evolve(self, WIDTH, HEIGHT, objects):
        self.initialize_population()
        for generation in range(self.generations):
            new_population = []
            fitnesses = [
                self.evaluate_fitness(ind, WIDTH, HEIGHT, objects)
                for ind in tqdm(
                    self.population, desc=f"Generation {generation + 1} progress"
                )
            ]
            for _ in range(self.population_size):
                parent1, parent2 = self.select_parents(fitnesses)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            self.population = new_population

            # Affichage de la génération actuelle
            print(
                f"Generation {generation + 1}/{self.generations} completed. Fitness Average: {np.mean(fitnesses):.2f} Fitness Min: {np.min(fitnesses):.2f} Fitness Max: {np.max(fitnesses):.2f}"
            )
        best_individual = max(
            self.population,
            key=lambda ind: self.evaluate_fitness(ind, WIDTH, HEIGHT, objects),
        )
        return best_individual
