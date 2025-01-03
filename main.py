import pygame
import pygame.gfxdraw
import math
import random

# Initialisation de Pygame
pygame.init()

# Configuration de l'écran
WIDTH, HEIGHT = 720, 720  # Taille de l'écran
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Création de l'écran
pygame.display.set_caption("Simulateur d'Animat")  # Titre de la fenêtre

# Couleurs
WHITE = (247, 247, 255)
GREY = (50, 60, 68)
RED = (189, 72, 125)
GREEN = (76, 173, 139)
BLUE = (57, 88, 146)

# Paramètres du robot
ROBOT_RADIUS = 10
ROBOT_SPEED = 1.5


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
        self.radius = 16

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
        self.sensor_range = 720  # Portée maximale des capteurs
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
            if self.battery1 <= 0 and self.battery2 <= 0:
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
        sensor_x = self.x + 10 * math.cos(self.angle)
        sensor_y = self.y + 10 * math.sin(self.angle)
        pygame.draw.line(screen, RED, (self.x, self.y), (sensor_x, sensor_y), 2)

    def draw_sensors(self, screen):
        """Dessine le champ de vision des capteurs."""
        # Définir les champs de vision en radians
        sensor_fov = {
            "left": (-math.pi / 2, 0),  # De -90° à 0°
            "right": (0, math.pi / 2),  # De 0° à 90°
        }

        # Couleurs semi-transparentes
        colors = {
            "left": (0, 255, 0, 50),
            "right": (0, 0, 255, 50),
        }  # Vert pour gauche, bleu pour droit

        # Créer une surface semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for sensor_name, fov in sensor_fov.items():
            # Calcul des points pour dessiner le secteur
            points = [(self.x, self.y)]  # Commence au centre du robot
            for angle in range(
                int(fov[0] * 180 / math.pi), int(fov[1] * 180 / math.pi) + 1, 1
            ):
                # Convertir l'angle en radians
                rad = math.radians(angle)
                # Calculer les coordonnées du point sur le bord du champ de vision
                x = self.x + self.sensor_range * math.cos(self.angle + rad)
                y = self.y + self.sensor_range * math.sin(self.angle + rad)
                points.append((x, y))

            # Dessiner le secteur sur la surface semi-transparente
            pygame.draw.polygon(overlay, colors[sensor_name], points)

        # Superposer la surface semi-transparente à l'écran
        screen.blit(overlay, (0, 0))

    def relative_angle(self, obj_x, obj_y):
        """Calcule l'angle relatif entre le robot et un objet."""
        dx = obj_x - self.x
        dy = obj_y - self.y
        obj_angle = math.atan2(dy, dx)  # Angle vers l'objet
        angle_diff = (obj_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        return angle_diff  # Angle relatif (négatif = gauche, positif = droite)

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
        """Met à jour les distances des capteurs avec un angle de 90° par capteur."""
        # Définir les champs de vision des capteurs
        sensor_fov = {
            "left": (-math.pi / 2, 0),  # De -90° à 0°
            "right": (0, math.pi / 2),  # De 0° à 90°
        }

        for obj_type in self.sensors:
            for i, (sensor_name, fov) in enumerate(
                sensor_fov.items()
            ):  # Gauche et droite
                closest_distance = self.sensor_range

                for obj in objects:
                    if obj.type == obj_type:
                        # Calculer l'angle relatif entre le robot et l'objet
                        angle_to_obj = self.relative_angle(obj.x, obj.y)

                        # Vérifier si l'objet est dans le champ de vision du capteur
                        if not (fov[0] <= angle_to_obj <= fov[1]):
                            continue  # Ignorer l'objet s'il est hors du champ de vision

                        # Calcul de la distance torique
                        distance = self._toric_distance(
                            self.x, self.y, obj.x, obj.y, WIDTH, HEIGHT
                        )
                        if distance < closest_distance:
                            closest_distance = distance

                # Normaliser la distance (0 à 1)
                self.sensors[obj_type][i] = 1 - (closest_distance / self.sensor_range)

    def react_to_sensors(self):
        """Réagir en fonction des données des capteurs."""

        self.set_wheel_speeds(ROBOT_SPEED, ROBOT_SPEED)  # Avancer

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

    @staticmethod
    def _toric_distance(x1, y1, x2, y2, width, height):
        """Calcule la distance torique minimale entre deux points."""
        dx = min(
            abs(x2 - x1), width - abs(x2 - x1)
        )  # Distance en X (via bord opposé si plus court)
        dy = min(abs(y2 - y1), height - abs(y2 - y1))  # Distance en Y
        return math.sqrt(dx**2 + dy**2)


# Fonction principale
def main():
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
        robot.update()
        robot.check_collision(objects)
        robot.check_sensors(objects)

        # Dessiner les objets et le robot
        for obj in objects:
            draw_toric_object(screen, obj, WIDTH, HEIGHT)
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
