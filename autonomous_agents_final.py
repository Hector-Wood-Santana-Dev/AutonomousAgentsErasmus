import pygame
import math
import random

WIDTH = 800
HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        magnitude = self.magnitude()
        if magnitude > 0:
            self.x /= magnitude
            self.y /= magnitude

    def limit(self, max_value):
        magnitude = self.magnitude()
        if magnitude > max_value:
            self.x *= max_value / magnitude
            self.y *= max_value / magnitude

class Agent:
    def __init__(self, x, y):
        self.position = Vector(x, y)
        self.velocity = Vector(random.uniform(-1, 1), random.uniform(-1, 1))
        self.acceleration = Vector(0, 0)
        self.max_speed = 2
        self.max_force = 0.1

    def separation(self, agents):
        perception_radius = 50
        steering = Vector(0, 0)
        total = 0

        for other in agents:
            distance = self.position - other.position
            distance_norm = distance.magnitude()

            if 0 < distance_norm < perception_radius:
                steering += distance / distance_norm
                total += 1

        if total > 0:
            steering /= total

        if steering.magnitude() > 0:
            steering.normalize()
            steering *= self.max_speed
            steering -= self.velocity
            steering.limit(self.max_force)

        return steering

    def alignment(self, agents):
        perception_radius = 50
        steering = Vector(0, 0)
        total = 0

        for other in agents:
            distance = self.position - other.position
            distance_norm = distance.magnitude()

            if 0 < distance_norm < perception_radius:
                steering += other.velocity
                total += 1

        if total > 0:
            steering /= total

        if steering.magnitude() > 0:
            steering.normalize()
            steering *= self.max_speed
            steering -= self.velocity
            steering.limit(self.max_force)

        return steering

    def cohesion(self, agents):
        perception_radius = 50
        steering = Vector(0, 0)
        total = 0

        for other in agents:
            distance = self.position - other.position
            distance_norm = distance.magnitude()

            if 0 < distance_norm < perception_radius:
                steering += other.position
                total += 1

        if total > 0:
            steering /= total
            steering = self.seek(steering)

        return steering

    def seek(self, target):
        desired = target - self.position
        desired.normalize()
        desired *= self.max_speed

        steer = desired - self.velocity
        steer.limit(self.max_force)

        return steer

    def avoid_collision(self, agents):
        avoidance_radius = 20
        steering = Vector(0, 0)

        for other in agents:
            distance = self.position - other.position
            distance_norm = distance.magnitude()

            if 0 < distance_norm < avoidance_radius:
                difference = self.position - other.position
                difference.normalize()
                difference /= distance_norm
                steering += difference

        if steering.magnitude() > 0:
            steering.normalize()
            steering *= self.max_speed
            steering -= self.velocity
            steering.limit(self.max_force)

        return steering

    def stay_within_walls(self):
        margin = 50
        steering = Vector(0, 0)

        if self.position.x < margin:
            steering.x = self.max_speed
        elif self.position.x > WIDTH - margin:
            steering.x = -self.max_speed

        if self.position.y < margin:
            steering.y = self.max_speed
        elif self.position.y > HEIGHT - margin:
            steering.y = -self.max_speed

        return steering

    def follow_mouse(self, mouse_position):
        steering = Vector(0, 0)
        distance = mouse_position - self.position
        distance_norm = distance.magnitude()

        if distance_norm < 150:
            desired = mouse_position - self.position
            desired.normalize()
            desired *= self.max_speed

            steering = desired - self.velocity
            steering.limit(self.max_force)

        return steering

    def update(self, agents, angle, mouse_position):
        separation_force = self.separation(agents)
        alignment_force = self.alignment(agents)
        cohesion_force = self.cohesion(agents)
        collision_force = self.avoid_collision(agents)
        wall_force = self.stay_within_walls()
        mouse_force = self.follow_mouse(mouse_position)

        self.acceleration = (
            separation_force
            + alignment_force
            + cohesion_force
            + collision_force
            + wall_force
            + mouse_force
        )
        self.velocity += self.acceleration
        self.velocity.limit(self.max_speed)
        self.position += self.velocity

    def display(self, screen):
        triangle_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(triangle_image, GREEN, [(0, 0), (20, 10), (0, 20)])
        rotated_image = pygame.transform.rotate(triangle_image, math.degrees(math.atan2(self.velocity.y, self.velocity.x)))
        screen.blit(rotated_image, (self.position.x - 10, self.position.y - 10))


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flocking Behavior")
clock = pygame.time.Clock()

agents = []
for _ in range(10):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    agent = Agent(x, y)
    agents.append(agent)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_position = Vector(*pygame.mouse.get_pos())  # Get the mouse position

    screen.fill(BLACK)

    for agent in agents:
        agent.update(agents, angle=120, mouse_position=mouse_position)  # Pass the mouse position to the update method
        agent.display(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
