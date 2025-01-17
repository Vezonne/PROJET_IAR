import pygame
import pygame.gfxdraw
import math
import random

import myclass
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
    running = True

    # Création du robot et des objets dans l'environnement
    robot = Robot(WIDTH // 2, HEIGHT // 2)
    objects = [
        # 3 objets de nourriture
        Object(
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50),
            GREEN,
            "food",
        ),
        Object(
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50),
            GREEN,
            "food",
        ),
        Object(
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50),
            GREEN,
            "food",
        ),
        # 3 objets d'eau
        Object(
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50),
            BLUE,
            "water",
        ),
        Object(
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50),
            BLUE,
            "water",
        ),
        Object(
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50),
            BLUE,
            "water",
        ),
        # 9 pièges
        Object(
            random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), RED, "trap"
        ),
        Object(
            random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), RED, "trap"
        ),
        Object(
            random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), RED, "trap"
        ),
    ]

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
        robot.update(WIDTH, HEIGHT)
        robot.check_collision(objects)
        robot.check_sensors(objects, WIDTH, HEIGHT)

        # Dessiner les objets et le robot
        for obj in objects:
            obj.draw_toric_object(screen, WIDTH, HEIGHT)
        robot.draw_sensors(screen)
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
            f"Food: {robot.sensors['food'][0]:.2f} | {robot.sensors['food'][1]:.2f}",
            True,
            WHITE,
        )
        water_sensor_text = font.render(
            f"Water: {robot.sensors['water'][0]:.2f} | {robot.sensors['water'][1]:.2f}",
            True,
            WHITE,
        )
        trap_sensor_text = font.render(
            f"Trap: {robot.sensors['trap'][0]:.2f} | {robot.sensors['trap'][1]:.2f}",
            True,
            WHITE,
        )
        screen.blit(food_sensor_text, (10, 30))
        screen.blit(water_sensor_text, (10, 50))
        screen.blit(trap_sensor_text, (10, 70))

        # Affichage des caractéristiques du robot
        font = pygame.font.SysFont(None, 18)
        robot_text = font.render(
            f"Vitesse: {robot.speed_left:.2f}, {robot.speed_right:.2} | Angle: {robot.angle:.2f}",
            True,
            WHITE,
        )
        screen.blit(robot_text, (10, 90))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
