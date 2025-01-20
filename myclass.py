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
    def __init__(self, x, y, color, obj_type,positions=None):
        self.x = x
        self.y = y
        self.color = color
        self.type = obj_type  # "food", "water" ou "trap"
        self.radius = 16
        self.positions = positions or []  # Liste des positions, ou vide si non fournie
        self.current_position_index = 0

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

    def compute_motor_command(self, battery_level):
        # Utilise la valeur du capteur et le niveau de la batterie pour générer une commande moteur
        return self.transfer_function(self.sensor.value, battery_level)

class Sensor:
    def __init__(self, sensor_type, position, color, radius):
        self.sensor_type = sensor_type
        self.position = position
        self.color = color
        self.radius = radius
        self.value = 0

    def update_value(self, objects):
        # Mettre à jour la valeur du capteur en fonction des objets détectés
        self.value = 0
        for obj in objects:
            if obj.type == self.sensor_type:  # Vérification du type d'objet
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

        # Initialisation des capteurs
        self.sensors = {
            'food_left': Sensor('food', (x - 10, y), (0, 255, 0), 350),
            'food_right': Sensor('food', (x + 10, y), (0, 255, 0), 350),
            'water_left': Sensor('water', (x - 10, y), (0, 0, 255), 350),
            'water_right': Sensor('water', (x + 10, y), (0, 0, 255), 350),
            'trap_left': Sensor('trap', (x - 10, y), (255, 0, 0), 350),
            'trap_right': Sensor('trap', (x + 10, y), (255, 0, 0), 350)
        }

        # Initialisation des moteurs
        self.motors = {
            'left': Motor(),
            'right': Motor()
        }

        # Initialisation des liens sensorimoteurs
        self.links = [
            SensorimotorLink(self.sensors['food_left'], self.motors['left'], self.transfer_function),
            SensorimotorLink(self.sensors['food_right'], self.motors['right'], self.transfer_function),
            SensorimotorLink(self.sensors['water_left'], self.motors['left'], self.transfer_function),
            SensorimotorLink(self.sensors['water_right'], self.motors['right'], self.transfer_function),
            SensorimotorLink(self.sensors['trap_left'], self.motors['left'], self.transfer_function),
            SensorimotorLink(self.sensors['trap_right'], self.motors['right'], self.transfer_function)
        ]

    def transfer_function(self, sensor_value, battery_level):
        # Transforme le signal des capteurs en commande moteur ajustée en fonction du niveau de batterie
        return sensor_value * (battery_level / 100)

    def evaluate_transfer_function(self, transfer_function):
        # Évalue la performance de la fonction de transfert par un calcul de fitness
        fitness = 0
        for _ in range(100):  # Simuler 100 étapes
            sensor_value = random.uniform(0, 1)
            battery_level = random.uniform(0, 100)
            motor_command = transfer_function(sensor_value, battery_level)
            fitness += motor_command
        return fitness

    def optimize_transfer_functions(self):
        # Implémenter l'optimisation de la fonction de transfert avec un algorithme génétique
        pass

    def react_to_sensors(self):
        # Simple réaction selon les capteurs, ajustement de la direction en fonction des valeurs
        food_left_value = self.sensors['food_left'].value
        food_right_value = self.sensors['food_right'].value
        if food_left_value > food_right_value:
            self.set_wheel_speeds(ROBOT_SPEED * 0.5, ROBOT_SPEED)  # Tourner à gauche
        elif food_right_value > food_left_value:
            self.set_wheel_speeds(ROBOT_SPEED, ROBOT_SPEED * 0.5)  # Tourner à droite
        else:
            self.set_wheel_speeds(ROBOT_SPEED, ROBOT_SPEED)  # Avancer droit

    def update(self, width, height, objects):
        # Met à jour la position et l'état du robot
        self.check_sensors(objects, width, height)  # Met à jour les valeurs des capteurs
        self.react_to_sensors()  # Réagit selon les capteurs
        self.check_collision(objects, width, height)  # Vérifie les collisions
        self.x += (self.speed_left + self.speed_right) / 2 * math.cos(self.angle)
        self.y += (self.speed_left + self.speed_right) / 2 * math.sin(self.angle)
        self.angle += (self.speed_right - self.speed_left) / (2 * ROBOT_RADIUS)

        # Consomme de l'énergie
        self.battery1 -= 0.1
        self.battery2 -= 0.1

        # Vérifie si les batteries sont épuisées
        if self.battery1 <= 0 or self.battery2 <= 0:
            self.alive = False

    def set_wheel_speeds(self, left_speed, right_speed):
        self.speed_left = left_speed
        self.speed_right = right_speed
    
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

    def move_object_randomly(self, obj, width, height):
        # Appliquer la toricité lors du déplacement de l'objet
        obj.x, obj.y = ajuster_coordonnees_toriques(obj.x, obj.y, width, height)


    def check_collision(self, objects, width, height):
        """Vérifie les collisions avec les objets en utilisant une distance torique."""
        for obj in objects:
            distance = self._toric_distance(self.x, self.y, obj.x, obj.y, width, height)
            if distance < (ROBOT_RADIUS + obj.radius):
                if obj.type == 'food':
                    self.battery1 = min(100, self.battery1 + 20)
                    self.move_object_randomly(obj, width, height)
                elif obj.type == 'water':
                    self.battery2 = min(100, self.battery2 + 20)
                    self.move_object_randomly(obj, width, height)
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
