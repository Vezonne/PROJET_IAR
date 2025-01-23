import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import pygame.gfxdraw
import math
import cv2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import myclass as myclass
import AlgoGenetique as AG
from myclass import Object, Robot


# Couleurs
WHITE = (247, 247, 255)
GREY = (50, 60, 68)
RED = (189, 72, 125)
GREEN = (76, 173, 139)
BLUE = (57, 88, 146)

# Taille de l'écran
WIDTH, HEIGHT = 720, 720


def visual_execution(objects, param=None, video_filename=None):
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Création de l'écran
    pygame.display.set_caption("Simulateur d'Animat")  # Titre de la fenêtre
    fps = 30

    if video_filename:
        video_filename = "./data/" + video_filename
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(video_filename, fourcc, fps, (WIDTH, HEIGHT))

    clock = pygame.time.Clock()

    robot = Robot(WIDTH - 5, HEIGHT // 2, WIDTH, HEIGHT)
    if param is not None:
        robot.set_all_param(param)
    robot.set_sensors_screen(screen, True)

    running = True

    # Boucle principale
    while running:
        screen.fill(GREY)

        # Vérifier si le robot est mort
        if not robot.alive:
            running = False  # Arrêter la boucle principale si le robot est mort

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Réagir aux données des capteurs
        robot.react_to_sensors()

        # Mise à jour du robot
        robot.x, robot.y = myclass.ajuster_coordonnees_toriques(
            robot.x
            + (robot.speed_left + robot.speed_right) / 2 * math.cos(robot.angle),
            robot.y
            + (robot.speed_left + robot.speed_right) / 2 * math.sin(robot.angle),
            WIDTH,
            HEIGHT,
        )
        robot.update(WIDTH, HEIGHT, objects)
        robot.check_collision(objects, WIDTH, HEIGHT)

        # Dessiner les objets et le robot
        for obj in objects:
            obj.draw_toric_object(screen, WIDTH, HEIGHT)
        robot.draw(screen)

        # Affichage des batteries
        font = pygame.font.SysFont(None, 24)
        battery_text = font.render(
            f"Batterie1: {robot.battery1:.2f} | Batterie2: {robot.battery2:.2f}",
            True,
            WHITE,
        )
        screen.blit(battery_text, (10, 10))

        # Affichage des capteurs
        font = pygame.font.SysFont(None, 18)
        food_sensor_text = font.render(
            f"Food: {robot.sensors['food_left'].value:.2f} | {robot.sensors['food_right'].value:.2f}",
            True,
            WHITE,
        )
        water_sensor_text = font.render(
            f"Water: {robot.sensors['water_left'].value:.2f} | {robot.sensors['water_right'].value:.2f}",
            True,
            WHITE,
        )
        trap_sensor_text = font.render(
            f"Trap: {robot.sensors['trap_left'].value:.2f} | {robot.sensors['trap_right'].value:.2f}",
            True,
            WHITE,
        )
        screen.blit(food_sensor_text, (10, 30))
        screen.blit(water_sensor_text, (10, 50))
        screen.blit(trap_sensor_text, (10, 70))

        # Affichage des caractéristiques du robot
        font = pygame.font.SysFont(None, 18)
        robot_text = font.render(
            f"Vitesse: {robot.speed_left:.2f}, {robot.speed_right:.2f} | Angle: {robot.angle:.2f}",
            True,
            WHITE,
        )

        position_text = font.render(
            f"Position: ({robot.x:.2f}, {robot.y:.2f})",
            True,
            WHITE,
        )
        left_angle = math.degrees(robot.sensors["food_left"].angle)
        left_rad = math.degrees(
            robot.sensors["food_left"].rad + robot.sensors["food_left"].angle
        )

        right_angle = math.degrees(robot.sensors["food_right"].angle)
        right_rad = math.degrees(
            robot.sensors["food_right"].rad + robot.sensors["food_right"].angle
        )
        screen.blit(robot_text, (10, 90))
        screen.blit(position_text, (10, 110))
        pygame.display.flip()

        # Capturer la frame pour la vidéo
        if video_filename:
            frame = pygame.surfarray.array3d(screen)  # Convertir l'écran en tableau 3D (RGB)
            # frame = np.rot90(np.rot90(np.rot90(frame)))  # Faire pivoter pour correspondre au format OpenCV
            frame = np.rot90(frame[::-1], 3)  # Faire pivoter pour correspondre au format OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convertir en BGR pour OpenCV
            out.write(frame)  # Enregistrer la frame

        clock.tick(fps)

    if video_filename:
        out.release()
    pygame.quit()


def ask_to_continue():
    """
    Demande à l'utilisateur s'il souhaite continuer.
    """
    while True:
        response = (
            input("Lancer l'execution visuel du meilleur individu ? (o/n) : ")
            .strip()
            .lower()
        )
        if response in ["o", "oui"]:
            return True
        elif response in ["n", "non"]:
            return False
        else:
            print("Veuillez répondre par 'o' pour oui ou 'n' pour non.")


def visualise_fitness_stats(filename="./data/fitness_stats.csv"):
    data = pd.read_csv(filename)

    # Tracer les courbes
    plt.figure(figsize=(10, 6))
    plt.plot(data["generation"], data["average"], label="Fitness Moyenne", color="blue")
    plt.plot(data["generation"], data["min"], label="Fitness Minimale", color="red")
    plt.plot(data["generation"], data["max"], label="Fitness Maximale", color="green")

    # Ajouter des titres et des labels
    plt.title("Évolution de la Fitness au fil des Générations", fontsize=16)
    plt.xlabel("Génération", fontsize=14)
    plt.ylabel("Fitness", fontsize=14)
    plt.legend()  # Afficher la légende
    plt.grid(True)  # Ajouter une grille
    plt.tight_layout()  # Ajuster les marges

    # Afficher le graphique
    plt.show()


def transfer_function(sensor_value, battery_level, params):
    init_offset = 200 / 99 * params[0] - 100
    gradient1 = math.tan(math.pi / 99 * params[1] - math.pi / 2)
    threshold1 = params[2] + 1
    gradient2 = math.tan(math.pi / 99 * params[3] - math.pi / 2)
    threshold2 = params[4] + 1
    gradient3 = math.tan(math.pi / 99 * params[5] - math.pi / 2)
    slope_modulation = 1 / 99 * params[6]
    offset_modulation = 2 / 99 * params[7] - 1
    battery_number = int(params[8] % 2)

    if sensor_value < threshold1:
        output = init_offset + gradient1 * sensor_value
    elif sensor_value < threshold2:
        output = (init_offset + gradient1 * threshold1) + gradient2 * (
            sensor_value - threshold1
        )
    else:
        output = (
            (init_offset + gradient1 * threshold1 + gradient2 * threshold2 - threshold1)
            + gradient3 * sensor_value
            - threshold2
        )

    output = output + ((battery_level[battery_number] / 2) * offset_modulation)
    output = output + (
        output * (((battery_level[battery_number] - 100) / 100) * slope_modulation)
    )

    if output > 100:
        output = 100
    elif output < -100:
        output = -100

    return output / 100


def visualise_tranfer_fonction(all_params, battery_levels=[200, 100, 0]):
    sensor_values = np.linspace(0, 100, 500)

    # Tracer les 9 graphiques
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))  # Grille 3x3
    fig.suptitle("Courbes des fonctions de transfert (81 paramètres)", fontsize=18)

    for idx, ax in enumerate(axes.flatten()):  # Parcourir les 9 sous-graphiques
        params = all_params[idx*9: idx*9 + 9]  # Groupe de paramètres correspondant

        for battery in battery_levels:  # Tracer pour chaque niveau de batterie
            outputs = [transfer_function(value, [battery, battery], params) for value in sensor_values]
            ax.plot(sensor_values, outputs, label=f"Batterie: {battery}")
        
        # Configurer chaque sous-graphe
        ax.set_title(f"Lien {idx + 1} (batterie {params[8]%2 + 1})", fontsize=14)
        ax.set_xlabel("Valeurs des capteurs", fontsize=12)
        ax.set_ylabel("Sortie normalisée", fontsize=12)
        ax.legend()
        ax.grid(True)

    # Ajuster l'espacement entre les graphiques
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Afficher les graphiques
    plt.show()


def genetic_execution(num_generations, objects):
    ga = AG.GeneticAlgorithm(
        generations=num_generations,
    )
    best_individual, best_fitness, best_generation = ga.evolve(WIDTH, HEIGHT, objects)
    print(f"Meilleur individu trouvé :\ngeneration: {best_generation}, fitness: {best_fitness}, param: {best_individual}")

    visualise_fitness_stats()
    video_filename = "video_best_individual.mp4"
    visual_execution(objects, best_individual, video_filename)

    return best_individual


def main():
    trap_positions = [
        (300, 175),
        (120, 550),
        (565, 300),
        (400, 400),
        (700, 297),
        (238, 600),
    ]
    traps = [
        Object(trap_positions[i][0], trap_positions[i][1], RED, "trap")
        for i in range(6)
    ]  # 6 pièges
    # Liste de positions pour la nourriture (chaque objet a 6 positions)
    food_positions = [
        [
            (100, 100),
            (200, 50),
            (300, 100),
            (400, 50),
            (500, 100),
            (600, 150),
        ],  # Premier objet de nourriture
        [
            (100, 500),
            (200, 550),
            (300, 500),
            (400, 550),
            (500, 500),
            (600, 550),
        ],  # Deuxième objet de nourriture
        [
            (150, 200),
            (250, 250),
            (350, 300),
            (450, 350),
            (550, 400),
            (650, 450),
        ],  # Troisième objet de nourriture
    ]

    food_objects = [
        Object(
            food_positions[i][0][0],
            food_positions[i][0][1],
            GREEN,
            "food",
            positions=food_positions[i],
        )
        for i in range(3)
    ]

    # Liste de positions pour l'eau (3 objets)
    water_positions = [
        [
            (50, 200),
            (150, 250),
            (250, 300),
            (350, 350),
            (450, 400),
            (550, 450),
        ],  # Premier objet d'eau
        [
            (100, 650),
            (200, 700),
            (300, 650),
            (400, 700),
            (500, 650),
            (600, 700),
        ],  # Deuxième objet d'eau
        [
            (150, 50),
            (250, 100),
            (350, 150),
            (450, 200),
            (550, 250),
            (650, 300),
        ],  # Troisième objet d'eau
    ]

    water_objects = [
        Object(
            water_positions[i][0][0],
            water_positions[i][0][1],
            BLUE,
            "water",
            positions=water_positions[i],
        )
        for i in range(3)
    ]
    objects = traps + food_objects + water_objects

    #############################################
    trap_positions1 = [
        (100, 100),
        (100, 500),
        (150, 200),
        (50, 200),
        (100, 650),
        (150, 50)
    ]
    traps1 = [
        Object(trap_positions1[i][0], trap_positions1[i][1], RED, "trap")
        for i in range(6)
    ]  # 6 pièges
    # Liste de positions pour la nourriture (chaque objet a 6 positions)
    food_positions1 = [
        [
            (300, 175),
            (400, 50),
            (600, 150),
            (200, 50),
            (500, 100),
            (300, 100),
        ],  # Premier objet de nourriture
        [
            (120, 550),
            (600, 550),
            (500, 500),
            (200, 550),
            (300, 500),
            (300, 550),
        ],  # Deuxième objet de nourriture
        [
            (565, 300),
            (650, 450),
            (350, 400),
            (450, 350),
            (550, 300),
            (250, 250),
        ],  # Troisième objet de nourriture
    ]

    food_objects1 = [
        Object(
            food_positions1[i][0][0],
            food_positions1[i][0][1],
            GREEN,
            "food",
            positions=food_positions1[i],
        )
        for i in range(3)
    ]

    # Liste de positions pour l'eau (3 objets)
    water_positions1 = [
        [
            (400, 400),
            (150, 250),
            (250, 300),
            (350, 350),
            (450, 400),
            (550, 450),
        ],  # Premier objet d'eau
        [
            (700, 297),
            (200, 700),
            (300, 650),
            (600, 700),
            (500, 650),
            (400, 700),
        ],  # Deuxième objet d'eau
        [
            (238, 600),
            (250, 100),
            (350, 150),
            (450, 200),
            (550, 250),
            (650, 300),
        ],  # Troisième objet d'eau
    ]

    water_objects1 = [
        Object(
            water_positions1[i][0][0],
            water_positions1[i][0][1],
            BLUE,
            "water",
            positions=water_positions1[i],
        )
        for i in range(3)
    ]
    objects1 = traps1 + food_objects1 + water_objects1

    #############################################
    trap_positions2 = [
        (300, 175),
        (120, 550),
        (565, 300),
        (50, 200),
        (100, 650),
        (150, 50)
    ]
    traps2 = [
        Object(trap_positions2[i][0], trap_positions2[i][1], RED, "trap")
        for i in range(6)
    ]  # 6 pièges
    # Liste de positions pour la nourriture (chaque objet a 6 positions)
    food_positions2 = [
        [
            (100, 100),
            (400, 50),
            (600, 150),
            (200, 50),
            (500, 100),
            (300, 100),
        ],  # Premier objet de nourriture
        [
            (100, 500),
            (600, 550),
            (500, 500),
            (200, 550),
            (300, 500),
            (300, 550),
        ],  # Deuxième objet de nourriture
        [
            (150, 200),
            (650, 450),
            (350, 400),
            (450, 350),
            (550, 300),
            (250, 250),
        ],  # Troisième objet de nourriture
    ]

    food_objects2 = [
        Object(
            food_positions2[i][0][0],
            food_positions2[i][0][1],
            GREEN,
            "food",
            positions=food_positions2[i],
        )
        for i in range(3)
    ]

    # Liste de positions pour l'eau (3 objets)
    water_positions2 = [
        [
            (400, 400),
            (150, 250),
            (250, 300),
            (350, 350),
            (450, 400),
            (550, 450),
        ],  # Premier objet d'eau
        [
            (700, 297),
            (200, 700),
            (300, 650),
            (600, 700),
            (500, 650),
            (400, 700),
        ],  # Deuxième objet d'eau
        [
            (238, 600),
            (250, 100),
            (350, 150),
            (450, 200),
            (550, 250),
            (650, 300),
        ],  # Troisième objet d'eau
    ]

    water_objects2 = [
        Object(
            water_positions2[i][0][0],
            water_positions2[i][0][1],
            BLUE,
            "water",
            positions=water_positions2[i],
        )
        for i in range(3)
    ]
    objects2 = traps2 + food_objects2 + water_objects2

    param_1 = [54, 99, 99, 99, 68, 55, 68, 3, 0, 
               21, 85, 99, 23, 99, 35, 66, 29, 6, 
               99, 97, 99, 99, 99, 97, 67, 21, 5, 
               11, 35, 12, 67, 16, 87, 76, 27, 21, 
               4, 91, 85, 99, 99, 97, 98, 63, 99, 
               77, 68, 15, 51, 83, 67, 66, 55, 95, 
               99, 12, 83, 21, 50, 88, 99, 66, 93, 
               17, 99, 71, 0, 99, 62, 7, 99, 17, 
               32, 61, 64, 12, 98, 52, 99, 84, 99, 
               66, 97]
    
    param_2 = [98, 99, 23, 99, 98, 99, 99, 9, 67, 
               29, 85, 69, 7, 72, 95, 99, 14, 58, 
               37, 98, 83, 79, 0, 98, 52, 27, 99, 
               99, 6, 99, 46, 16, 35, 89, 13, 99, 
               59, 14, 23, 99, 38, 75, 56, 58, 99, 
               99, 77, 99, 87, 30, 68, 99, 0, 83, 
               87, 39, 99, 75, 73, 33, 7, 0, 44, 
               87, 43, 45, 64, 54, 23, 99, 91, 27, 
               99, 64, 93, 4, 89, 13, 39, 47, 68, 
               70, 11]

    # visual_execution(objects=objects, param=param_1)
    # param = genetic_execution(num_generations=250, objects=objects)

    visual_execution(objects=objects, param=param_1)
    visualise_tranfer_fonction(param_1)
    # visual_execution(objects=objects1, param=param, video_filename="video_env1.mp4")
    # visual_execution(objects=objects2, param=param, video_filename="video_env2.mp4")


if __name__ == "__main__":
    main()
