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

    def update(self, t, orbit_speed, centroid_x, centroid_y):
        angle = self.orbit_angle + t * orbit_speed
        base_x = centroid_x + math.cos(angle) * self.orbit_dist
        base_y = centroid_y + math.sin(angle) * self.orbit_dist
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


ALL_COLORS = [
    (80, 200, 255),
    (50, 160, 220),
    (110, 230, 255),
    (255, 100, 180),
    (220, 60, 140),
    (255, 140, 200),
    (120, 255, 120),
    (80, 210, 80),
    (160, 255, 160),
    (255, 200, 60),
    (220, 170, 30),
    (255, 220, 100),
    (180, 120, 255),
    (140, 80, 220),
    (210, 160, 255),
    (255, 130, 60),
    (60, 255, 200),
    (255, 80, 80),
    (200, 200, 200),
    (30, 180, 180),
]

CLUSTER_LAYOUTS = ["ring", "scatter", "grid", "spiral", "tight"]


class Cluster:
    def __init__(self, cx, cy, layout, blob_count, orbit_speed):
        self.centroid_x = cx
        self.centroid_y = cy
        self.orbit_speed = orbit_speed
        self.blobs = []
        positions = self._generate_layout(cx, cy, layout, blob_count)
        for i, (bx, by) in enumerate(positions):
            r = random.randint(30, 70)
            color = random.choice(ALL_COLORS)
            blob = Blob(bx, by, r, color)
            blob.init_x = bx
            blob.init_y = by
            self.blobs.append(blob)
        for blob in self.blobs:
            blob.init_orbit(self.centroid_x, self.centroid_y)

    def _generate_layout(self, cx, cy, layout, count):
        positions = []
        if layout == "ring":
            ring_radius = random.uniform(80, 150)
            for i in range(count):
                angle = math.tau * i / count + random.uniform(-0.15, 0.15)
                px = cx + math.cos(angle) * ring_radius
                py = cy + math.sin(angle) * ring_radius
                positions.append((px, py))
        elif layout == "scatter":
            for _ in range(count):
                px = cx + random.uniform(-140, 140)
                py = cy + random.uniform(-140, 140)
                positions.append((px, py))
        elif layout == "grid":
            cols = math.ceil(math.sqrt(count))
            spacing = 70
            for i in range(count):
                gx = (i % cols) * spacing - (cols - 1) * spacing / 2
                gy = (i // cols) * spacing - (cols - 1) * spacing / 2
                positions.append((cx + gx, cy + gy))
        elif layout == "spiral":
            for i in range(count):
                frac = i / max(1, count - 1)
                angle = frac * math.tau * 2
                dist = 40 + frac * 120
                px = cx + math.cos(angle) * dist
                py = cy + math.sin(angle) * dist
                positions.append((px, py))
        elif layout == "tight":
            for _ in range(count):
                angle = random.uniform(0, math.tau)
                dist = random.uniform(20, 80)
                px = cx + math.cos(angle) * dist
                py = cy + math.sin(angle) * dist
                positions.append((px, py))
        return positions

    def update(self, t):
        for blob in self.blobs:
            blob.update(t, self.orbit_speed, self.centroid_x, self.centroid_y)

    def get_blobs(self):
        return self.blobs


NUM_CLUSTERS = 12
clusters = []
margin = 250
for i in range(NUM_CLUSTERS):
    cx = random.randint(margin, WIDTH * 3 - margin)
    cy = random.randint(margin, HEIGHT * 3 - margin)
    layout = CLUSTER_LAYOUTS[i % len(CLUSTER_LAYOUTS)]
    blob_count = random.randint(5, 9)
    orbit_speed = random.choice([
        random.uniform(0.08, 0.2),
        random.uniform(0.3, 0.6),
        random.uniform(0.7, 1.2),
    ]) * random.choice([-1, 1])
    clusters.append(Cluster(cx, cy, layout, blob_count, orbit_speed))

all_centroids_x = [c.centroid_x for c in clusters]
all_centroids_y = [c.centroid_y for c in clusters]
cam_x = sum(all_centroids_x) / len(all_centroids_x)
cam_y = sum(all_centroids_y) / len(all_centroids_y)

running = True
t = 0.0
zoom = 0.35

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
            zoom = max(0.05, min(zoom, 10.0))
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

    all_blobs = []
    for cluster in clusters:
        cluster.update(t)
        all_blobs.extend(cluster.get_blobs())

    all_blobs.sort(key=lambda b: b.scale)
    for blob in all_blobs:
        blob.draw(screen, zoom, cam_x, cam_y)

    pygame.display.flip()

pygame.quit()
