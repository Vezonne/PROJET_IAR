import csv
from concurrent.futures import ProcessPoolExecutor
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

    def evaluate_fitness(self, param, width, height, objects):
        fitness = 0
        robot = Robot(width // 2, height // 2, width, height)
        robot.set_all_param(param)
        max_time = 1000

        for i in range(max_time):
            # Vérifier si le robot est mort
            if not robot.alive:
                break

            robot.update(width, height, objects)
            fitness += robot.battery1 + robot.battery2 / 400

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
            mutated_list.append(min(mutated_param, 99))
        return mutated_list

    def select_parents(self, fitnesses):
        fitnesses_tot = np.sum(fitnesses)
        prob = []
        for f in fitnesses:
            prob.append(f / fitnesses_tot)
        return random.choices(self.population, k=2, weights=prob)

    def parallel_evaluate_fitness(self, population, width, height, objects, generation):
        with ProcessPoolExecutor() as executor:
            fitnesses = list(
                executor.map(
                    self.evaluate_fitness,
                    population,
                    [width] * len(population),
                    [height] * len(population),
                    [objects] * len(population),
                )
            )
        return fitnesses

    def evolve(self, width, height, objects, output_file="fitness_stats.csv"):
        pygame.init()

        fitness_stats = []
        best_individual = []
        best_generation = 0
        best_fitness = -1

        try:
            self.initialize_population()
            for generation in tqdm(
                range(self.generations), desc="Evolution of population"
            ):
                fitnesses = self.parallel_evaluate_fitness(
                    self.population, width, height, objects, generation
                )

                if np.max(fitnesses) > best_fitness:
                    best_individual = self.population[np.argmax(fitnesses)]
                    best_fitness = np.max(fitnesses)
                    best_generation = generation +1

                avg_fitness = np.mean(fitnesses)
                min_fitness = np.min(fitnesses)
                max_fitness = np.max(fitnesses)
                fitness_stats.append(
                    {
                        "generation": generation + 1,
                        "average": avg_fitness,
                        "min": min_fitness,
                        "max": max_fitness,
                    }
                )

                # Affichage de la génération actuelle
                # print(
                #     f"Generation {generation + 1}/{self.generations} completed."
                #     f"Fitness Average: {avg_fitness:.2f}"
                #     f"Fitness Min: {min_fitness:.2f}"
                #     f"Fitness Max: {max_fitness:.2f}"
                # )

                new_population = []

                for _ in range(self.population_size):
                    parent1, parent2 = self.select_parents(fitnesses)
                    child = self.crossover(parent1, parent2)
                    child = self.mutate(child)
                    new_population.append(child)

                self.population = new_population

            # Sauvegarde des statistiques de fitness
            self.save_fitness_stats(fitness_stats, output_file)

            return best_individual, best_fitness, best_generation

        finally:
            pygame.quit()

    def get_best_individual(self, population, width, height, objects):
        best_individual = None
        best_fitness = float("-inf")

        # Barre de progression sur la population
        for ind in tqdm(population, desc="Évaluation des individus"):
            fitness = self.evaluate_fitness(ind, width, height, objects)
            if fitness > best_fitness:
                best_individual = ind
                best_fitness = fitness

        return best_individual

    def save_fitness_stats(self, stats, filename):
        filename = "./data/" + filename
        with open(filename, mode="w", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=["generation", "average", "min", "max"]
            )
            writer.writeheader()
            writer.writerows(stats)
