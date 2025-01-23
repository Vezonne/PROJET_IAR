import pygame
import pygame.gfxdraw
import math
import random

# Couleurs
WHITE = (247, 247, 255)
GREY = (50, 60, 68)
RED = (189, 72, 125)
GREEN = (76, 173, 139)
BLUE = (57, 88, 146)
PURPLE = (199, 0, 57)
YELLOW = (255, 195, 0)

# Paramètres du robot
ROBOT_RADIUS = 10
ROBOT_SPEED = 1.5


# Classes pour les objets de l'environnement
class Object:
    def __init__(self, x, y, color, obj_type, positions=None):
        self.x = x
        self.y = y
        self.color = color
        self.type = obj_type  # "food", "water" ou "trap"
        self.radius = 16
        self.positions = positions or []  # Liste des positions, ou vide si non fournie
        self.position_index = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move_to_next_position(self):
        """Passe à la prochaine position dans la liste ou revient à la première."""
        if self.positions:
            self.position_index = (self.position_index + 1) % len(self.positions)
            self.x, self.y = self.positions[self.position_index]

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
    def __init__(self, sensor, param=None):
        self.sensor = sensor
        self.param = []

        if param is not None:
            self.param = param
        else:
            for i in range(9):
                start = 0
                end = 99

                if i == 4:
                    start = self.param[2]
                    end = 99

                self.param.append(random.randint(start, end))

    def get_param(self):
        return self.param

    def set_param(self, param):
        self.param = param

    def update_param(self, index, value):
        self.param[index] = value

    def transfer_function(self, battery_level):
        # Fonction de transfert pour générer la commande moteur
        input = self.sensor.value

        init_offset = 200 / 99 * self.param[0] - 100
        gradient1 = math.tan(math.pi / 99 * self.param[1] - math.pi / 2)
        threshold1 = self.param[2] + 1
        gradient2 = math.tan(math.pi / 99 * self.param[3] - math.pi / 2)
        threshold2 = self.param[4] + 1
        gradient3 = math.tan(math.pi / 99 * self.param[5] - math.pi / 2)
        slope_modulation = 1 / 99 * self.param[6]
        offset_modulation = 2 / 99 * self.param[7] - 1
        battery_number = int(self.param[8] % 2)

        if input < threshold1:
            output = init_offset + gradient1 * input

        elif input < threshold2:
            output = (init_offset + gradient1 * threshold1) + gradient2 * (
                input - threshold1
            )

        else:
            output = (
                (
                    init_offset
                    + gradient1 * threshold1
                    + gradient2 * threshold2
                    - threshold1
                )
                + gradient3 * input
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


class Sensor:
    def __init__(self, sensor_type, x, y, color, range, rad, width, height):
        self.sensor_type = sensor_type
        self.x = x
        self.y = y
        self.angle = 0
        self.color = color
        self.range = range
        self.rad = rad
        self.width = width
        self.height = height
        self.value = 0
        self.screen = None
        self.draw_sensor = False

    def update(self, x, y, angle, objects):
        self.x = x
        self.y = y
        self.angle = angle % (2 * math.pi)  # S'assurer que l'angle est dans [0, 2π]
        if self.angle > math.pi:
            self.angle -= 2 * math.pi
        self.update_value(objects)

    def update_value(self, objects):
        # Mettre à jour la valeur du capteur en fonction des objets détectés
        self.value = 0
        x_obj = self.x
        y_obj = self.y
        x_to_obj = self.x
        y_to_obj = self.y
        x_from_obj = self.x
        y_from_obj = self.y
        dist_act = self.range + 1

        for obj in objects:
            if obj.type == self.sensor_type:
                tor_pos = []
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        tor_pos.append(
                            (obj.x + i * self.width, obj.y + j * self.height)
                        )
                # print("objects: ", obj.type)
                # print("obj pos: ", (obj.x, obj.y))
                # print("tor_pos: ", tor_pos)
                for obj_x, obj_y in tor_pos:
                    dx = obj_x - self.x
                    dy = obj_y - self.y

                    distance = math.sqrt(dx**2 + dy**2)
                    # print("pos: ", (obj_x, obj_y))
                    # print("\tdx, dy: ", (dx, dy))
                    # print("\tdistance: ", distance)
                    if distance > self.range or distance > dist_act:
                        continue

                    obj_angle = math.atan2(dy, dx)
                    start_angle = min(self.angle, self.angle + self.rad)
                    end_angle = max(self.angle, self.angle + self.rad)

                    # print("\tangle: ", obj_angle)
                    # print("\tvalue: ", (1 - distance / self.range) * 100)

                    if start_angle <= obj_angle <= end_angle:
                        self.value = max(self.value, (1 - distance / self.range) * 100)
                        if self.value == (1 - distance / self.range) * 100:
                            dist_act = distance
                            x_obj = obj.x
                            y_obj = obj.y
                            x_to_obj = self.x + dx
                            y_to_obj = self.y + dy
                            x_from_obj = obj.x - dx
                            y_from_obj = obj.y - dy

                    # print("Value: ", self.value)
                    # print()

        if self.draw_sensor:
            if self.x != x_to_obj or self.y != y_to_obj:
                pygame.draw.line(
                    self.screen,
                    self.color,
                    (self.x, self.y),
                    (x_to_obj, y_to_obj),
                    1,
                )
                pygame.draw.line(
                    self.screen,
                    self.color,
                    (x_obj, y_obj),
                    (x_from_obj, y_from_obj),
                    1,
                )

    def set_screen(self, screen, draw_sensor=False):
        self.screen = screen
        self.draw_sensor = draw_sensor

    def draw(self, screen):
        """Dessine le champ de vision des capteurs."""
        width = screen.get_width()
        height = screen.get_height()
        # Définir les champs de vision en radians
        if self.rad > 0:
            fov = (0, self.rad)
        else:
            fov = (self.rad, 0)

        # Couleurs semi-transparentes
        r, g, b = self.color
        color = (r, g, b, 15)

        # Créer une surface semi-transparente
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        # Calcul des points pour dessiner le secteur
        points = [(self.x, self.y)]  # Commence au centre du robot
        for angle in range(
            int(fov[0] * 180 / math.pi), int(fov[1] * 180 / math.pi) + 1, 1
        ):
            # Convertir l'angle en radians
            rad = math.radians(angle)
            # Calculer les coordonnées du point sur le bord du champ de vision
            x = self.x + self.range * math.cos(self.angle + rad)
            y = self.y + self.range * math.sin(self.angle + rad)

            points.append((x, y))

        # Dessiner le secteur sur la surface semi-transparente
        pygame.draw.polygon(overlay, color, points)

        # Superposer la surface semi-transparente à l'écran
        screen.blit(overlay, (0, 0))


def ajuster_coordonnees_toriques(x, y, largeur, hauteur):
    """
    Ajuste les coordonnées (x, y) pour qu'elles se replient dans un monde torique de dimensions (largeur, hauteur).
    """
    x = x % largeur
    y = y % hauteur
    return x, y


class Robot:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = 0
        self.speed_left = 0
        self.speed_right = 0
        self.battery1 = 200
        self.battery2 = 200
        self.alive = True
        self.sensor_range = 350
        self.param_left_wheel = random.randint(0, 99)
        self.param_right_wheel = random.randint(0, 99)

        left_rad = -math.pi / 2
        right_rad = math.pi / 2

        # Initialisation des capteurs
        self.sensors = {
            "food_left": Sensor(
                "food",
                x,
                y,
                YELLOW,
                self.sensor_range,
                left_rad,
                self.width,
                self.height,
            ),
            "food_right": Sensor(
                "food",
                x,
                y,
                PURPLE,
                self.sensor_range,
                right_rad,
                self.width,
                self.height,
            ),
            "water_left": Sensor(
                "water",
                x,
                y,
                YELLOW,
                self.sensor_range,
                left_rad,
                self.width,
                self.height,
            ),
            "water_right": Sensor(
                "water",
                x,
                y,
                PURPLE,
                self.sensor_range,
                right_rad,
                self.width,
                self.height,
            ),
            "trap_left": Sensor(
                "trap",
                x,
                y,
                YELLOW,
                self.sensor_range,
                left_rad,
                self.width,
                self.height,
            ),
            "trap_right": Sensor(
                "trap",
                x,
                y,
                PURPLE,
                self.sensor_range,
                right_rad,
                self.width,
                self.height,
            ),
        }

        # Initialisation des liens sensorimoteurs
        self.left_links = [
            SensorimotorLink(self.sensors["food_left"]),
            SensorimotorLink(self.sensors["food_left"]),
            SensorimotorLink(self.sensors["food_left"]),
            SensorimotorLink(self.sensors["water_left"]),
            SensorimotorLink(self.sensors["water_left"]),
            SensorimotorLink(self.sensors["water_left"]),
            SensorimotorLink(self.sensors["trap_left"]),
            SensorimotorLink(self.sensors["trap_left"]),
            SensorimotorLink(self.sensors["trap_left"]),
        ]

        self.right_links = [
            SensorimotorLink(self.sensors["food_right"]),
            SensorimotorLink(self.sensors["food_right"]),
            SensorimotorLink(self.sensors["food_right"]),
            SensorimotorLink(self.sensors["water_right"]),
            SensorimotorLink(self.sensors["water_right"]),
            SensorimotorLink(self.sensors["water_right"]),
            SensorimotorLink(self.sensors["trap_right"]),
            SensorimotorLink(self.sensors["trap_right"]),
            SensorimotorLink(self.sensors["trap_right"]),
        ]

    def get_all_param(self):
        all_param = []
        for link in self.left_links:
            all_param += link.get_param()
        all_param += self.param_left_wheel
        all_param += self.param_right_wheel
        return

    def set_all_param(self, all_param):
        for i in range(len(self.left_links)):
            self.left_links[i].set_param(all_param[i * 9 : i * 9 + 9])
            self.right_links[i].set_param(all_param[i * 9 : i * 9 + 9])
        self.param_left_wheel = all_param[-2]
        self.param_right_wheel = all_param[-1]

    def activation_function(self):
        battery_level = self.battery1, self.battery2
        left_sig = 6 / 99 * self.param_left_wheel - 3
        right_sig = 6 / 99 * self.param_right_wheel - 3

        link_sum = 0
        for link in self.left_links:
            link_sum += link.transfer_function(battery_level)

        output_left = 1 / (1 + math.exp(-link_sum)) * 2 * left_sig - left_sig
        output_left = output_left / left_sig * 10

        link_sum = 0
        for link in self.right_links:
            link_sum += link.transfer_function(battery_level)

        output_right = 1 / (1 + math.exp(-link_sum)) * 2 * right_sig - right_sig
        output_right = output_right / right_sig * 10

        return output_left, output_right

    def update(self, width, height, objects):
        # print("ROBOT objects: " + str(objects))
        # Met à jour la position et l'état du robot
        self.update_sensors(
            self.x, self.y, self.angle, objects
        )  # Met à jour les valeurs des capteurs
        left_speed, right_speed = (
            self.activation_function()
        )  # Calcule la réaction du robot
        self.set_wheel_speeds(
            left_speed, right_speed
        )  # Met à jour les vitesses des roues
        self.x += (self.speed_left + self.speed_right) / 2 * math.cos(self.angle)
        self.y += (self.speed_left + self.speed_right) / 2 * math.sin(self.angle)
        self.angle += (self.speed_right - self.speed_left) / (2 * ROBOT_RADIUS)
        self.check_collision(objects, width, height)  # Vérifie les collisions

        # Consomme de l'énergie
        if self.battery1 > 0:
            self.battery1 -= 1
        else:
            self.battery1 = 0

        if self.battery2 > 0:
            self.battery2 -= 1
        else:
            self.battery2 = 0

        # Vérifie si les batteries sont épuisées
        if self.battery1 <= 0 and self.battery2 <= 0:
            self.alive = False

    def update_sensors(self, x, y, angle, objects):
        for sensor in self.sensors.values():
            sensor.update(x, y, angle, objects)

    def set_wheel_speeds(self, left_speed, right_speed):
        self.speed_left = left_speed
        self.speed_right = right_speed

    def set_sensors_screen(self, screen, draw_sensors=False):
        for sensor in self.sensors.values():
            sensor.set_screen(screen, draw_sensors)

    def draw(self, screen):
        # Logique pour dessiner le robot
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 10)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), 10, 1)

        # Dessiner les roues
        # Roue gauche
        pygame.draw.ellipse(
            screen, (0, 0, 0), (int(self.x) - 10, int(self.y) - 15, 20, 5)
        )

        # Roue droite
        pygame.draw.ellipse(
            screen, (0, 0, 0), (int(self.x) - 10, int(self.y) + 10, 20, 5)
        )
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x) + 10, int(self.y) - 5), 3)
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x) + 10, int(self.y) + 5), 3)

        # dessiner les capteurs
        for sensor in self.sensors.values():
            sensor.draw(screen)

    def check_collision(self, objects, width, height):
        """Vérifie les collisions avec les objets en utilisant une distance torique."""
        for obj in objects:
            distance = self._toric_distance(self.x, self.y, obj.x, obj.y, width, height)
            if distance < (ROBOT_RADIUS + obj.radius):
                if obj.type == "food":
                    self.battery1 = 200
                    obj.move_to_next_position()  # Déplace l'objet à la prochaine position
                elif obj.type == "water":
                    self.battery2 = 200
                    obj.move_to_next_position()  # Déplace l'objet à la prochaine position
                elif obj.type == "trap":
                    self.alive = False

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
