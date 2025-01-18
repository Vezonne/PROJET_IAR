import pygame
import pygame.gfxdraw
import math
import random
import AlgoGenetique as AG

# Couleurs
WHITE = (247, 247, 255)
GREY = (50, 60, 68)
RED = (189, 72, 125)
GREEN = (76, 173, 139)
BLUE = (57, 88, 146)

# Paramètres du robot
ROBOT_RADIUS = 10
ROBOT_SPEED = 1.5


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

    def draw_toric_object(self, screen, width, height):
        """Dessine un objet avec toricité (répétition aux bords)."""
        for dx in [-width, 0, width]:
            for dy in [-height, 0, height]:
                pygame.draw.circle(
                    screen,
                    self.color,
                    (int(self.x + dx) % width, int(self.y + dy) % height),
                    self.radius,
                )
class SensorimotorLink:
    def __init__(self, sensor, motor, transfer_function):
        self.sensor = sensor
        self.motor = motor
        self.transfer_function = transfer_function

    def compute_moto_command(self, sensor_value, battery_level):
        return self.transfer_function(sensor_value, battery_level)

class Sensor:
    def __init__(self, sensor_type, position, color, radius):
        self.sensor_type = sensor_type
        self.position = position
        self.color = color
        self.radius = radius
        self.value = 0

    def update_value(self, objects):
        # Logique pour mettre à jour la valeur du capteur en fonction des objets détectés
        self.value = 0
        for obj in objects:
            if obj.type == self.sensor_type:
                distance = ((self.position[0] - obj.x) ** 2 + (self.position[1] - obj.y) ** 2) ** 0.5
                self.value += max(0, 1 - distance / 100)  # Exemple de calcul de la valeur du capteur

class Motor:
    def __init__(self):
        self.speed = 0

    def update_speed(self, command):
        self.speed = command

def ajuster_coordonnees_toriques(x, y, largeur, hauteur):
    """
    Ajuste les coordonnées (x, y) pour qu'elles se replient dans un monde torique de dimensions (largeur, hauteur).
    """
    x = x % largeur
    y = y % hauteur
    return x, y


class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed_left = 0
        self.speed_right = 0
        self.battery1 = 100
        self.battery2 = 100
        self.alive = True
        self.sensor_range = 350

        # Initialiser les capteurs
        self.sensors = {
            'food_left': Sensor('food', (x - 10, y), (0, 255, 0), 5),
            'food_right': Sensor('food', (x + 10, y), (0, 255, 0), 5),
            'water_left': Sensor('water', (x - 10, y), (0, 0, 255), 5),
            'water_right': Sensor('water', (x + 10, y), (0, 0, 255), 5),
            'trap_left': Sensor('trap', (x - 10, y), (255, 0, 0), 5),
            'trap_right': Sensor('trap', (x + 10, y), (255, 0, 0), 5)
        }

        # Initialiser les moteurs
        self.motors = {
            'left': Motor(),
            'right': Motor()
        }

        # Initialiser les liens sensorimoteurs
        self.links = [
            SensorimotorLink(self.sensors['food_left'], self.motors['left'], self.transfer_function),
            SensorimotorLink(self.sensors['food_right'], self.motors['right'], self.transfer_function),
            SensorimotorLink(self.sensors['water_left'], self.motors['left'], self.transfer_function),
            SensorimotorLink(self.sensors['water_right'], self.motors['right'], self.transfer_function),
            SensorimotorLink(self.sensors['trap_left'], self.motors['left'], self.transfer_function),
            SensorimotorLink(self.sensors['trap_right'], self.motors['right'], self.transfer_function)
        ]

    def transfer_function(self, sensor_value, battery_level):
        # Logique pour transformer les signaux des capteurs en commandes de moteur
        return sensor_value * (battery_level / 100)
    
    def evaluate_transfer_function(self, transfer_function):
        # Logique pour évaluer la performance d'une fonction de transfert
        # Implémentez votre logique d'évaluation ici
        fitness = 0
        # Exemple de calcul de la fitness
        for _ in range(100):  # Simuler 100 étapes
            sensor_value = random.uniform(0, 1)  # Valeur de capteur simulée
            battery_level = random.uniform(0, 100)  # Niveau de batterie simulé
            motor_command = transfer_function(sensor_value, battery_level)
            fitness += motor_command  # Exemple de calcul de la fitness
        return fitness

    def optimize_transfer_functions(self):
        # Utiliser l'algorithme génétique pour optimiser les fonctions de transfert
        ga = AG.GeneticAlgorithm(population_size=50, mutation_rate=0.1, crossover_rate=0.7, generations=100)
        ga.evolve()
        best_transfer_function = max(ga.population, key=self.evaluate_transfer_function)
        for link in self.links:
            link.transfer_function = best_transfer_function

    def react_to_sensors(self):
        for link in self.links:
            sensor_value = link.sensor.value
            battery_level = (self.battery1 + self.battery2) / 2
            motor_command = link.compute_motor_command(sensor_value, battery_level)
            link.motor.update_speed(motor_command)
        self.set_wheel_speeds(self.motors['left'].speed, self.motors['right'].speed)

    def set_wheel_speeds(self, left_speed, right_speed):
        self.speed_left = left_speed
        self.speed_right = right_speed

    def update(self, width, height):
        # Logique pour mettre à jour la position et l'état du robot
        self.x += (self.speed_left + self.speed_right) / 2 * math.cos(self.angle)
        self.y += (self.speed_left + self.speed_right) / 2 * math.sin(self.angle)
        self.angle += (self.speed_right - self.speed_left) / (2 * ROBOT_RADIUS)

        # Mise à jour des batteries
        self.battery1 -= 0.01
        self.battery2 -= 0.01

        # Vérifier les limites du monde torique
        self.x, self.y = ajuster_coordonnees_toriques(self.x, self.y, width, height)

        # Vérifier si le robot est mort
        if self.battery1 <= 0 or self.battery2 <= 0:
            self.alive = False

    # def draw_sensors(self, screen, largeur, hauteur):
    #     return
    
    def draw_sensors(self, screen):
        """Dessine le champ de vision des capteurs."""
        width = screen.get_width()
        height = screen.get_height()
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
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
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
        
    def draw(self, screen):
        # Logique pour dessiner le robot
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 10)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), 10, 1)
        
        # Dessiner les roues
        # Roue gauche
        pygame.draw.ellipse(screen, (0,0,0), (int(self.x) - 10, int(self.y) - 15, 20, 5))
        
        # Roue droite
        pygame.draw.ellipse(screen, (0, 0, 0), (int(self.x) - 10, int(self.y) + 10, 20, 5)) 
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x) + 10, int(self.y) - 5), 3)
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x) + 10, int(self.y) + 5), 3)       

    def check_collision(self, objects):
        # Logique pour vérifier les collisions avec les objets
        for obj in objects:
            distance = ((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2) ** 0.5
            if distance < 10:
                if obj.type == 'food':
                    self.battery1 = min(100, self.battery1 + 20)
                elif obj.type == 'water':
                    self.battery2 = min(100, self.battery2 + 20)
                elif obj.type == 'trap':
                    self.alive = False

    def check_sensors(self, objects, width, height):
        for sensor in self.sensors.values():
            sensor.update_value(objects)
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
