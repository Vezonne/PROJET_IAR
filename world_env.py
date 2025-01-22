import pygame
import pygame.gfxdraw
import math
import random

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


def visual_execution(objects, param=None):
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Création de l'écran
    pygame.display.set_caption("Simulateur d'Animat")  # Titre de la fenêtre

    clock = pygame.time.Clock()

    robot = Robot(WIDTH - 5, HEIGHT // 2, WIDTH, HEIGHT)
    if param is not None:
        robot.set_all_param(param)
    robot.set_sensors_screen(screen, True)

    running = True

    # Boucle principale
    while running:
        screen.fill(GREY)
        clock.tick(60)

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
        # running = ask_to_continue()

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


def genetic_execution(num_generations, objects):

    ga = AG.GeneticAlgorithm(
        generations=num_generations,
    )
    best_individual = ga.evolve(WIDTH, HEIGHT, objects)
    print("Meilleur individu trouvé :", best_individual)

    if ask_to_continue():

        visual_execution(objects, best_individual)


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

    # param_1 = [99 for _ in range(83)]

    #visual_execution(objects=objects)
    genetic_execution(num_generations=1, objects=objects)


if __name__ == "__main__":
    main()
