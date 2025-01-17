import random
import json

import myclass
from myclass import Object, Robot


def generate_random_environment(
    num_food=3, num_water=3, num_traps=5, width=800, height=600
):
    """Génère un environnement aléatoire avec nourriture, eau, et pièges."""
    environment = {
        "food": [
            {"x": random.randint(0, width), "y": random.randint(0, height)}
            for _ in range(num_food)
        ],
        "water": [
            {"x": random.randint(0, width), "y": random.randint(0, height)}
            for _ in range(num_water)
        ],
        "traps": [
            {"x": random.randint(0, width), "y": random.randint(0, height)}
            for _ in range(num_traps)
        ],
        "width": width,
        "height": height,
    }
    return environment


def save_environment_to_file(environment, filename="environment.json"):
    """Sauvegarde un environnement dans un fichier JSON."""
    with open(filename, "w") as file:
        json.dump(environment, file, indent=4)


def load_environment_from_file(filename="environment.json"):
    """Charge un environnement depuis un fichier JSON."""
    with open(filename, "r") as file:
        environment = json.load(file)
    return environment


def convert_environment_to_objects(environment):
    """Convertit un environnement en objets utilisables dans la simulation."""
    objects = []
    for food in environment["food"]:
        objects.append(Object(food["x"], food["y"], (0, 255, 0), "food"))
    for water in environment["water"]:
        objects.append(Object(water["x"], water["y"], (0, 0, 255), "water"))
    for trap in environment["traps"]:
        objects.append(Object(trap["x"], trap["y"], (255, 0, 0), "trap"))
    return objects


def main():
    width, height = 800, 600
    num_food, num_water, num_traps = 3, 3, 5
    environment = generate_random_environment(
        num_food, num_water, num_traps, width, height
    )
    save_environment_to_file(environment)


if __name__ == "__main__":
    main()
