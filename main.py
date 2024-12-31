import pygame
import math
import random

# Initialisation de Pygame
pygame.init()

# Configuration de l'écran
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulateur d'Animat")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Paramètres du robot
ROBOT_RADIUS = 15
ROBOT_SPEED = 2


# Classes pour les objets de l'environnement
class Object:
    def __init__(self, x, y, color, obj_type):
        self.x = x
        self.y = y
        self.color = color
        self.type = obj_type  # "food", "water" ou "trap"
        self.radius = 10

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


# Classe du Robot
class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Angle de direction
        self.speed_left = 0
        self.speed_right = 0
        self.battery1 = 100  # Batterie pour la nourriture
        self.battery2 = 100  # Batterie pour l'eau
        self.alive = True

    def update(self):
        # Réduire les niveaux des batteries au fil du temps
        if self.alive:
            self.battery1 -= 0.1  # Dégradation de la batterie 1
            self.battery2 -= 0.1  # Dégradation de la batterie 2

            # Vérifier si les batteries sont vides
            if self.battery1 <= 0 or self.battery2 <= 0:
                self.alive = False  # Le robot meurt

        # Mise à jour de la position basée sur les vitesses des roues
        if self.alive:
            left = self.speed_left
            right = self.speed_right
            delta_angle = (right - left) / 2  # Rotation
            self.angle += delta_angle
            move = (left + right) / 2  # Déplacement avant/arrière
            self.x += move * math.cos(self.angle)
            self.y += move * math.sin(self.angle)

            # Garder le robot dans l'écran
            self.x = max(0, min(WIDTH, self.x))
            self.y = max(0, min(HEIGHT, self.y))

    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), ROBOT_RADIUS)
        # Dessiner un "capteur" pour montrer la direction
        sensor_x = self.x + 20 * math.cos(self.angle)
        sensor_y = self.y + 20 * math.sin(self.angle)
        pygame.draw.line(screen, RED, (self.x, self.y), (sensor_x, sensor_y), 2)

    def check_collision(self, objects):
        for obj in objects:
            distance = math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2)
            if distance < ROBOT_RADIUS + obj.radius:
                if obj.type == "trap":
                    self.alive = False  # Le robot meurt
                elif obj.type == "food":
                    self.battery1 = min(100, self.battery1 + 50)  # Recharge nourriture
                    objects.remove(obj)
                elif obj.type == "water":
                    self.battery2 = min(100, self.battery2 + 50)  # Recharge eau
                    objects.remove(obj)

    def set_wheel_speeds(self, left, right):
        self.speed_left = left
        self.speed_right = right


# Fonction principale
def main():
    clock = pygame.time.Clock()
    running = True

    # Création du robot et des objets dans l'environnement
    robot = Robot(WIDTH // 2, HEIGHT // 2)
    objects = [
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
            random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), RED, "trap"
        ),
        Object(
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50),
            BLUE,
            "water",
        ),
    ]

    # Boucle principale
    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Logique pour les capteurs et action simple
        # Par exemple : si batterie 1 faible, définir une vitesse pour chercher de la nourriture
        if robot.battery1 < 50:
            robot.set_wheel_speeds(ROBOT_SPEED, ROBOT_SPEED - 0.5)  # Tourne légèrement

        # Mise à jour du robot
        robot.update()
        robot.check_collision(objects)

        # Dessiner les objets et le robot
        for obj in objects:
            obj.draw(screen)
        robot.draw(screen)

        # Affichage des batteries
        font = pygame.font.SysFont(None, 24)
        battery_text = font.render(
            f"Batterie1: {robot.battery1} | Batterie2: {robot.battery2}", True, BLACK
        )
        screen.blit(battery_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
