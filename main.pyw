import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Vibrating Blobs")
clock = pygame.time.Clock()


def make_blob_surface(radius, color):
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = radius, radius
    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < radius:
                norm = dist / radius
                # 3D shading: bright highlight off-center, falloff to edge
                highlight_x, highlight_y = cx - radius * 0.3, cy - radius * 0.3
                hdx, hdy = x - highlight_x, y - highlight_y
                hdist = math.sqrt(hdx * hdx + hdy * hdy) / radius
                brightness = max(0.0, 1.0 - hdist * 0.9)
                alpha = int(255 * (1.0 - norm ** 2) ** 0.5)
                r = min(255, int(color[0] * 0.4 + color[0] * 0.6 * brightness))
                g = min(255, int(color[1] * 0.4 + color[1] * 0.6 * brightness))
                b = min(255, int(color[2] * 0.4 + color[2] * 0.6 * brightness))
                surf.set_at((x, y), (r, g, b, alpha))
    return surf


def color_lightness(color):
    return (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255.0


ORBIT_SPEED = 0.15


class Blob:
    def __init__(self, x, y, radius, color):
        self.radius = radius
        self.surface = make_blob_surface(radius, color)
        lightness = color_lightness(color)
        speed = 0.3 + lightness * 0.7
        self.phase_x = random.uniform(0, math.tau)
        self.phase_y = random.uniform(0, math.tau)
        self.freq_x = random.uniform(1.0, 2.5) * speed + 0.5
        self.freq_y = random.uniform(1.0, 2.5) * speed + 0.5
        self.amp_x = random.uniform(2, 6) + lightness * 8
        self.amp_y = random.uniform(2, 6) + lightness * 8
        self.scale_phase = random.uniform(0, math.tau)
        self.scale_freq = random.uniform(1.5, 3.0) * speed + 0.5
        self.scale_amp = 0.02 + lightness * 0.08
        self.orbit_angle = 0.0
        self.orbit_dist = 0.0

    def init_orbit(self, centroid_x, centroid_y):
        dx = self.init_x - centroid_x
        dy = self.init_y - centroid_y
        self.orbit_angle = math.atan2(dy, dx)
        self.orbit_dist = math.sqrt(dx * dx + dy * dy)

    def update(self, t):
        angle = self.orbit_angle + t * ORBIT_SPEED
        base_x = self.centroid_x + math.cos(angle) * self.orbit_dist
        base_y = self.centroid_y + math.sin(angle) * self.orbit_dist
        self.x = base_x + math.sin(t * self.freq_x + self.phase_x) * self.amp_x
        self.y = base_y + math.sin(t * self.freq_y + self.phase_y) * self.amp_y
        self.scale = 1.0 + math.sin(t * self.scale_freq + self.scale_phase) * self.scale_amp

    def draw(self, surface, zoom, cam_x, cam_y):
        w = max(1, int(self.radius * 2 * self.scale * zoom))
        h = max(1, int(self.radius * 2 * self.scale * zoom))
        sx = (self.x - cam_x) * zoom + WIDTH / 2
        sy = (self.y - cam_y) * zoom + HEIGHT / 2
        scaled = pygame.transform.smoothscale(self.surface, (w, h))
        surface.blit(scaled, (sx - w // 2, sy - h // 2))


colors = [
    (80, 200, 255),
    (255, 100, 180),
    (120, 255, 120),
    (255, 200, 60),
    (180, 120, 255),
    (255, 130, 60),
    (60, 255, 200),
]

blobs = []
for i in range(7):
    x = random.randint(150, WIDTH - 150)
    y = random.randint(150, HEIGHT - 150)
    r = random.randint(50, 100)
    blob = Blob(x, y, r, colors[i % len(colors)])
    blob.init_x = x
    blob.init_y = y
    blobs.append(blob)

centroid_x = sum(b.init_x for b in blobs) / len(blobs)
centroid_y = sum(b.init_y for b in blobs) / len(blobs)
for blob in blobs:
    blob.centroid_x = centroid_x
    blob.centroid_y = centroid_y
    blob.init_orbit(centroid_x, centroid_y)

running = True
t = 0.0
zoom = 1.0
cam_x = WIDTH / 2
cam_y = HEIGHT / 2

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x = (mouse_x - WIDTH / 2) / zoom + cam_x
            world_y = (mouse_y - HEIGHT / 2) / zoom + cam_y
            zoom *= 1.1 ** event.y
            zoom = max(0.1, min(zoom, 10.0))
            cam_x = world_x - (mouse_x - WIDTH / 2) / zoom
            cam_y = world_y - (mouse_y - HEIGHT / 2) / zoom

    dt = clock.tick(60) / 1000.0
    t += dt

    cam_speed = 400 / zoom
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        cam_y -= cam_speed * dt
    if keys[pygame.K_s]:
        cam_y += cam_speed * dt
    if keys[pygame.K_a]:
        cam_x -= cam_speed * dt
    if keys[pygame.K_d]:
        cam_x += cam_speed * dt

    screen.fill((15, 10, 30))

    for blob in blobs:
        blob.update(t)

    blobs.sort(key=lambda b: b.scale)
    for blob in blobs:
        blob.draw(screen, zoom, cam_x, cam_y)

    pygame.display.flip()

pygame.quit()
