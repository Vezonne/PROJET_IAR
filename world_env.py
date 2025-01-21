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


def main():
    pygame.init()

    # Configuration de l'écran
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Création de l'écran
    pygame.display.set_caption("Simulateur d'Animat")  # Titre de la fenêtre

    clock = pygame.time.Clock()
    trap_positions = [
        (100, 100),
        (200, 200),
        (300, 300),
        (400, 400),
        (500, 500),
        (600, 600),
    ]
    traps = [
        Object(trap_positions[i][0], trap_positions[i][1], RED, "trap")
        for i in range(6)
    ]  # 6 pièges
    # Liste de positions pour la nourriture (chaque objet a 6 positions)
    food_positions = [
        [
            (400, 360),
            (100, 360),
            (200, 360),
            (250, 300),
            (300, 350),
            (350, 400),
        ],  # Positions pour le premier objet de nourriture
        [
            (50, 100),
            (100, 150),
            (150, 200),
            (200, 250),
            (250, 300),
            (300, 350),
        ],  # Positions pour le deuxième objet de nourriture
        [
            (75, 125),
            (125, 175),
            (175, 225),
            (225, 275),
            (275, 325),
            (325, 375),
        ],  # Positions pour le troisième objet de nourriture
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
            (150, 100),
            (200, 150),
            (250, 200),
            (300, 250),
            (350, 300),
            (400, 350),
        ],  # Positions pour le premier objet d'eau
        [
            (100, 50),
            (150, 100),
            (200, 150),
            (250, 200),
            (300, 250),
            (350, 300),
        ],  # Positions pour le deuxième objet d'eau
        [
            (125, 75),
            (175, 125),
            (225, 175),
            (275, 225),
            (325, 275),
            (375, 325),
        ],  # Positions pour le troisième objet d'eau
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

    ga = AG.GeneticAlgorithm(
        population_size=50, mutation_rate=0.1, crossover_rate=0.7, generations=100
    )
    ga.evolve()
    running = True

    # Création du robot et des objets dans l'environnement
    best_individual = max(
        ga.population,
        key=lambda ind: ga.evaluate_fitness(ind, myclass.Robot, WIDTH, HEIGHT, objects),
    )
    robot = Robot(WIDTH // 2, HEIGHT // 2)
    robot.set_sensors_screen(screen, True)
    for i, link in enumerate(robot.links):
        link.transfer_function = ga.create_transfer_function(best_individual[i])

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

        sensor_angle_text = font.render(
            f"Sensor Angle: {left_angle}, {left_rad}; {right_rad}, {right_angle}",
            True,
            WHITE,
        )
        screen.blit(robot_text, (10, 90))
        screen.blit(position_text, (10, 110))
        screen.blit(sensor_angle_text, (10, 130))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()