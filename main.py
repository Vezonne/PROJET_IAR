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
WHITE = (247, 247, 255)
GREY = (50, 60, 68)
RED = (189, 72, 125)
GREEN = (76, 173, 139)
BLUE = (57, 88, 146)

# Paramètres du robot
ROBOT_RADIUS = 15
ROBOT_SPEED = 2


def toric_distance(x1, y1, x2, y2, width, height):
    """Calcule la distance torique minimale entre deux points."""
    dx = min(
        abs(x2 - x1), width - abs(x2 - x1)
    )  # Distance en X (via bord opposé si plus court)
    dy = min(abs(y2 - y1), height - abs(y2 - y1))  # Distance en Y
    return math.sqrt(dx**2 + dy**2)


def draw_toric_object(screen, obj, width, height):
    """Dessine un objet avec toricité (répétition aux bords)."""
    for dx in [-width, 0, width]:
        for dy in [-height, 0, height]:
            pygame.draw.circle(
                screen,
                obj.color,
                (int(obj.x + dx) % width, int(obj.y + dy) % height),
                obj.radius,
            )


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
        self.sensor_range = 200  # Portée maximale des capteurs
        self.sensors = {
            "food": [0, 0],
            "water": [0, 0],
            "trap": [0, 0],
        }  # Capteurs gauche et droit

    def update(self):
        # Réduire les niveaux des batteries au fil du temps
        if self.alive:
            self.battery1 -= 0.1  # Dégradation de la batterie 1
            self.battery2 -= 0.1  # Dégradation de la batterie 2

            # Vérifier si les batteries sont vides
            if self.battery1 <= 0 or self.battery2 <= 0:
                self.alive = False  # Le robot meurt

            # Mise à jour de la position basée sur les vitesses des roues
            left = self.speed_left
            right = self.speed_right
            delta_angle = (right - left) / 2  # Rotation
            self.angle += delta_angle
            move = (left + right) / 2  # Déplacement avant/arrière
            self.x += move * math.cos(self.angle)
            self.y += move * math.sin(self.angle)

            # Appliquer les règles de toricité
            self.x %= WIDTH  # Revenir de l'autre côté si hors limite
            self.y %= HEIGHT

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

    def check_sensors(self, objects):
        """Met à jour les distances des capteurs pour chaque type d'objet."""
        sensor_angles = [-math.pi / 6, math.pi / 6]  # Angles gauche et droit
        for obj_type in self.sensors:
            for i, sensor_angle in enumerate(sensor_angles):  # Gauche et droit
                sensor_x = (
                    self.x + self.sensor_range * math.cos(self.angle + sensor_angle)
                ) % WIDTH
                sensor_y = (
                    self.y + self.sensor_range * math.sin(self.angle + sensor_angle)
                ) % HEIGHT
                closest_distance = self.sensor_range

                # Vérifier chaque objet du type concerné
                for obj in objects:
                    if obj.type == obj_type:  # Ne traiter que les objets du type actuel
                        distance = toric_distance(
                            self.x, self.y, obj.x, obj.y, WIDTH, HEIGHT
                        )
                        if distance < closest_distance and distance < obj.radius:
                            closest_distance = distance
                # Normaliser la distance (0 à 1)
                self.sensors[obj_type][i] = 1 - (closest_distance / self.sensor_range)

    @staticmethod
    def _distance_to_line(start, end, point):
        """Calculer la distance entre une ligne et un point."""
        x1, y1 = start
        x2, y2 = end
        px, py = point
        line_mag = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if line_mag == 0:
            return float("inf")
        u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_mag**2
        if u < 0 or u > 1:
            return float("inf")  # Point hors de la ligne
        ix = x1 + u * (x2 - x1)
        iy = y1 + u * (y2 - y1)
        return math.sqrt((ix - px) ** 2 + (iy - py) ** 2)

    def react_to_sensors(self):
        """Réagir en fonction des données des capteurs."""
        if (
            self.sensors["trap"][0] > 0.8 or self.sensors["trap"][1] > 0.8
        ):  # Éviter un piège proche
            self.set_wheel_speeds(-ROBOT_SPEED, -ROBOT_SPEED)  # Reculer
        elif self.sensors["food"][0] > self.sensors["food"][1]:
            self.set_wheel_speeds(
                ROBOT_SPEED, ROBOT_SPEED / 2
            )  # Tourner vers la nourriture gauche

        elif self.sensors["food"][0] < self.sensors["food"][1]:
            self.set_wheel_speeds(
                ROBOT_SPEED, ROBOT_SPEED / 2
            )  # Tourner vers la nourriture droite

        elif self.sensors["water"][0] > self.sensors["water"][1]:
            self.set_wheel_speeds(
                ROBOT_SPEED / 2, ROBOT_SPEED
            )  # Tourner vers l'eau gauche

        elif self.sensors["water"][1] > self.sensors["water"][0]:
            self.set_wheel_speeds(
                ROBOT_SPEED / 2, ROBOT_SPEED
            )  # Tourner vers l'eau droite

        else:
            self.set_wheel_speeds(ROBOT_SPEED, ROBOT_SPEED)  # Avancer


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
        screen.fill(GREY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Réagir aux données des capteurs
        robot.react_to_sensors()

        # Mise à jour du robot
        robot.update()
        robot.check_collision(objects)
        robot.check_sensors(objects)

        # Dessiner les objets et le robot
        for obj in objects:
            draw_toric_object(screen, obj, WIDTH, HEIGHT)
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
        sensor_text = font.render(
            f"Food: {robot.sensors['food']} | Water: {robot.sensors['water']} | Trap: {robot.sensors['trap']}",
            True,
            WHITE,
        )
        screen.blit(sensor_text, (10, 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
