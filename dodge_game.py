import base64
import math
import random
import tkinter as tk
import zlib

PLAYER_SIZE = 28
PLAYER_SPEED = 7
MAX_HEALTH = 3
WORLD_W = 2200
WORLD_H = 1400


def build_png(width, height, fill_func):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            r, g, b, a = fill_func(x, y)
            raw.extend((r, g, b, a))
    compressed = zlib.compress(bytes(raw), 9)
    png = bytearray(b'\x89PNG\r\n\x1a\n')

    def chunk(chunk_type, data):
        png.extend(len(data).to_bytes(4, 'big'))
        png.extend(chunk_type)
        png.extend(data)
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        png.extend(crc.to_bytes(4, 'big'))

    chunk(b'IHDR', (width.to_bytes(4, 'big') + height.to_bytes(4, 'big') + b'\x08\x06\x00\x00\x00'))
    chunk(b'IDAT', compressed)
    chunk(b'IEND', b'')
    return base64.b64encode(bytes(png)).decode('ascii')


class DodgeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Arcade Survival")
        self.root.resizable(False, False)
        self.root.attributes("-fullscreen", True)

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<Motion>", self.on_mouse_move)
        self.root.bind("<Button-1>", self.on_mouse_left_click)
        self.root.bind("<Button-3>", self.on_mouse_right_click)
        self.root.bind("<Escape>", lambda event: self.root.destroy())
        self.canvas.focus_set()

        self.keys = {"a": False, "d": False, "w": False, "s": False}
        self.mouse_x = self.width // 2
        self.mouse_y = self.height // 2
        self.player_x = WORLD_W // 2 - PLAYER_SIZE // 2
        self.player_y = WORLD_H // 2 - PLAYER_SIZE // 2

        self.sprites = self.create_sprites()
        self.obstacles = [
            {"x": 250, "y": 220, "w": 180, "h": 100},
            {"x": 720, "y": 260, "w": 140, "h": 160},
            {"x": 1150, "y": 140, "w": 210, "h": 90},
            {"x": 1400, "y": 520, "w": 160, "h": 170},
            {"x": 980, "y": 760, "w": 250, "h": 120},
            {"x": 300, "y": 850, "w": 180, "h": 120},
            {"x": 1450, "y": 980, "w": 220, "h": 110},
            {"x": 820, "y": 1040, "w": 140, "h": 80},
        ]
        self.enemies = []
        self.bullets = []
        self.missiles = []
        self.pickups = []
        self.particles = []
        self.effects = []
        self.chests = [
            {"x": 180, "y": 1200, "collected": False},
            {"x": 1150, "y": 320, "collected": False},
            {"x": 1950, "y": 1180, "collected": False},
        ]
        self.score = 0
        self.health = MAX_HEALTH
        self.game_over = False
        self.spawn_timer = 0
        self.pickup_timer = 0
        self.missile_count = 3
        self.nuke_count = 1
        self.camera_x = 0
        self.camera_y = 0
        self.boss = None
        self.boss_spawned = False
        self.frame = 0

        self.start_game()
        self.root.mainloop()

    def create_sprites(self):
        sprites = {}
        sprite_specs = [
            ("enemy_0", (255, 90, 90), (90, 20, 20), (255, 255, 255), 0),
            ("enemy_1", (90, 160, 255), (20, 60, 140), (255, 255, 255), 1),
            ("enemy_2", (255, 200, 70), (140, 90, 20), (255, 255, 255), 2),
            ("enemy_3", (120, 120, 120), (60, 60, 60), (255, 255, 255), 3),
            ("enemy_4", (255, 80, 180), (140, 20, 100), (255, 255, 255), 4),
            ("enemy_5", (80, 255, 180), (20, 140, 90), (255, 255, 255), 5),
            ("enemy_6", (255, 255, 90), (140, 140, 20), (255, 255, 255), 6),
            ("enemy_7", (180, 100, 255), (80, 30, 140), (255, 255, 255), 7),
            ("enemy_8", (255, 140, 40), (140, 60, 20), (255, 255, 255), 8),
            ("enemy_9", (60, 220, 255), (20, 90, 140), (255, 255, 255), 9),
            ("bullet", (255, 255, 0), (255, 140, 0), (0, 0, 0), 10),
            ("rocket", (255, 0, 80), (120, 20, 40), (255, 255, 255), 11),
            ("chest", (180, 90, 0), (255, 200, 80), (255, 255, 255), 12),
        ]
        for name, primary, secondary, accent, kind in sprite_specs:
            sprites[name] = tk.PhotoImage(data=build_png(24, 24, lambda x, y: self.sprite_pixels(x, y, primary, secondary, accent, kind)))
        return sprites

    def sprite_pixels(self, x, y, primary, secondary, accent, kind):
        cx = x - 11.5
        cy = y - 11.5
        dist = math.hypot(cx, cy)
        if kind == 0:
            inner = dist < 9
            color = primary if inner else (0, 0, 0, 0)
        elif kind == 1:
            color = primary if abs(cx) < 6 and abs(cy) < 8 else (0, 0, 0, 0)
        elif kind == 2:
            color = primary if abs(cx) < 8 and abs(cy) < 5 else (0, 0, 0, 0)
        elif kind == 3:
            color = primary if dist < 8 else (0, 0, 0, 0)
        elif kind == 4:
            color = primary if (abs(cx) < 7 and abs(cy) < 4) or dist < 4 else (0, 0, 0, 0)
        elif kind == 5:
            color = primary if abs(cy) < 8 and abs(cx) < 3 else (0, 0, 0, 0)
        elif kind == 6:
            color = primary if (abs(cx) < 5 and abs(cy) < 2) or (abs(cy) < 7 and abs(cx) < 2) else (0, 0, 0, 0)
        elif kind == 7:
            color = primary if dist < 9 and abs(cy) < 7 else (0, 0, 0, 0)
        elif kind == 8:
            color = primary if (abs(cx) < 6 and abs(cy) < 6) and (abs(cx) > 2 or abs(cy) > 2) else (0, 0, 0, 0)
        elif kind == 9:
            color = primary if dist < 8 else (0, 0, 0, 0)
        elif kind == 10:
            color = primary if dist < 4 else (0, 0, 0, 0)
        elif kind == 11:
            color = primary if abs(cy) < 9 and abs(cx) < 4 else (0, 0, 0, 0)
        elif kind == 12:
            color = primary if (abs(cx) < 6 and abs(cy) < 8) or (abs(cx) < 9 and abs(cy) < 3) else (0, 0, 0, 0)
        else:
            color = primary
        if kind in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}:
            if abs(cy) < 2 and abs(cx) < 9:
                color = accent
        return (*color, 255) if len(color) == 3 else color

    def start_game(self):
        self.canvas.delete("all")
        self.player_x = WORLD_W // 2 - PLAYER_SIZE // 2
        self.player_y = WORLD_H // 2 - PLAYER_SIZE // 2
        self.enemies = []
        self.bullets = []
        self.missiles = []
        self.pickups = []
        self.particles = []
        self.effects = []
        self.chests = [
            {"x": 180, "y": 1200, "collected": False},
            {"x": 1150, "y": 320, "collected": False},
            {"x": 1950, "y": 1180, "collected": False},
        ]
        self.score = 0
        self.health = MAX_HEALTH
        self.game_over = False
        self.spawn_timer = 0
        self.pickup_timer = 0
        self.missile_count = 3
        self.nuke_count = 1
        self.boss = None
        self.boss_spawned = False
        self.frame = 0
        self.update_game()

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key in self.keys:
            self.keys[key] = True
        elif event.keysym == "space" and self.game_over:
            self.start_game()
        elif event.keysym == "space" and not self.game_over:
            self.use_nuke()

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.keys:
            self.keys[key] = False

    def on_mouse_move(self, event):
        self.mouse_x = event.x + self.camera_x
        self.mouse_y = event.y + self.camera_y

    def on_mouse_left_click(self, event):
        if not self.game_over:
            self.shoot_bullet(event.x + self.camera_x, event.y + self.camera_y)

    def on_mouse_right_click(self, event):
        if not self.game_over:
            self.fire_missile(event.x + self.camera_x, event.y + self.camera_y)

    def update_game(self):
        if not self.game_over:
            self.frame += 1
            self.move_player()
            self.update_camera()
            self.spawn_timer -= 1
            self.pickup_timer -= 1
            if self.boss is None and self.score > 180 and not self.boss_spawned:
                self.spawn_boss()
                self.boss_spawned = True
            if self.boss is None and self.spawn_timer <= 0 and len(self.enemies) < 8:
                self.spawn_enemy()
                self.spawn_timer = random.randint(35, 65)
            if self.pickup_timer <= 0 and random.random() < 0.25:
                self.spawn_pickup()
                self.pickup_timer = random.randint(300, 500)

            self.move_enemies()
            self.update_bullets()
            self.update_missiles()
            self.update_particles()
            self.update_effects()
            self.check_collisions()
            self.draw_scene()
            self.score += 1
            self.root.after(16, self.update_game)
        else:
            self.draw_scene()

    def update_camera(self):
        self.camera_x = max(0, min(WORLD_W - self.width, self.player_x + PLAYER_SIZE // 2 - self.width // 2))
        self.camera_y = max(0, min(WORLD_H - self.height, self.player_y + PLAYER_SIZE // 2 - self.height // 2))

    def move_player(self):
        old_x = self.player_x
        old_y = self.player_y
        if self.keys["a"]:
            self.player_x -= PLAYER_SPEED
        if self.keys["d"]:
            self.player_x += PLAYER_SPEED
        if self.keys["w"]:
            self.player_y -= PLAYER_SPEED
        if self.keys["s"]:
            self.player_y += PLAYER_SPEED

        self.player_x = max(0, min(WORLD_W - PLAYER_SIZE, self.player_x))
        self.player_y = max(0, min(WORLD_H - PLAYER_SIZE, self.player_y))
        if self.collides_with_obstacle(self.player_x, self.player_y):
            self.player_x = old_x
            self.player_y = old_y

    def collides_with_obstacle(self, x, y):
        for obstacle in self.obstacles:
            if x + PLAYER_SIZE > obstacle["x"] and x < obstacle["x"] + obstacle["w"] and y + PLAYER_SIZE > obstacle["y"] and y < obstacle["y"] + obstacle["h"]:
                return True
        return False

    def spawn_enemy(self):
        kind = random.choice(["chaser", "zigzag", "splitter", "tank", "shooter", "teleporter", "daser", "shield", "orbiter", "spawner"])
        size = 22 if kind not in {"tank", "boss"} else 32
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            x = -size
            y = random.randint(40, WORLD_H - size - 40)
        elif side == "right":
            x = WORLD_W
            y = random.randint(40, WORLD_H - size - 40)
        elif side == "top":
            x = random.randint(40, WORLD_W - size - 40)
            y = -size
        else:
            x = random.randint(40, WORLD_W - size - 40)
            y = WORLD_H
        speed = {"chaser": 1.8, "zigzag": 1.6, "splitter": 1.6, "tank": 1.0, "shooter": 1.4, "teleporter": 2.0, "daser": 2.7, "shield": 1.4, "orbiter": 1.7, "spawner": 1.5}[kind]
        hp = {"chaser": 1, "zigzag": 1, "splitter": 2, "tank": 4, "shooter": 2, "teleporter": 2, "daser": 2, "shield": 3, "orbiter": 1, "spawner": 2}[kind]
        self.enemies.append({"kind": kind, "x": x, "y": y, "size": size, "speed": speed, "hp": hp, "phase": random.random() * 2 * math.pi, "cooldown": random.randint(20, 60), "shield": 0, "state": 0})

    def spawn_boss(self):
        self.boss = {"x": WORLD_W // 2 - 80, "y": 100, "w": 160, "h": 160, "hp": 90, "max_hp": 90, "cooldown": 60, "phase": 0}

    def spawn_pickup(self):
        x = random.randint(30, WORLD_W - 30)
        y = random.randint(30, WORLD_H - 30)
        if self.collides_with_obstacle(x, y):
            return
        kind = random.choice(["missile", "nuke"])
        self.pickups.append({"x": x, "y": y, "size": 16, "kind": kind})

    def move_enemies(self):
        for enemy in self.enemies:
            if enemy["kind"] == "chaser":
                self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"])
            elif enemy["kind"] == "zigzag":
                self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"] * 0.9)
                enemy["phase"] += 0.2
                enemy["x"] += math.sin(enemy["phase"]) * 1.2
                enemy["y"] += math.cos(enemy["phase"]) * 1.2
            elif enemy["kind"] == "splitter":
                self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"] * 0.8)
            elif enemy["kind"] == "tank":
                self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"] * 0.7)
            elif enemy["kind"] == "shooter":
                self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"] * 0.8)
                if enemy["cooldown"] <= 0:
                    self.fire_enemy_bullet(enemy)
                    enemy["cooldown"] = 60
                enemy["cooldown"] -= 1
            elif enemy["kind"] == "teleporter":
                enemy["state"] += 1
                if enemy["state"] % 80 == 0:
                    enemy["x"] = random.randint(40, WORLD_W - 40)
                    enemy["y"] = random.randint(40, WORLD_H - 40)
                self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"] * 0.6)
            elif enemy["kind"] == "daser":
                enemy["cooldown"] -= 1
                if enemy["cooldown"] <= 0:
                    enemy["state"] = 12
                    enemy["cooldown"] = 90
                if enemy["state"] > 0:
                    self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"] * 3.0)
                    enemy["state"] -= 1
                else:
                    self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"] * 0.7)
            elif enemy["kind"] == "shield":
                self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"] * 0.8)
            elif enemy["kind"] == "orbiter":
                enemy["phase"] += 0.08
                enemy["x"] += math.cos(enemy["phase"]) * 1.4
                enemy["y"] += math.sin(enemy["phase"]) * 1.4
            elif enemy["kind"] == "spawner":
                self.move_toward(enemy, self.player_x + PLAYER_SIZE // 2, self.player_y + PLAYER_SIZE // 2, enemy["speed"] * 0.6)
                enemy["cooldown"] -= 1
                if enemy["cooldown"] <= 0:
                    self.spawn_enemy_minion(enemy)
                    enemy["cooldown"] = 120

        if self.boss:
            self.update_boss()

    def move_toward(self, entity, tx, ty, speed):
        dx = tx - (entity["x"] + entity["size"] // 2)
        dy = ty - (entity["y"] + entity["size"] // 2)
        dist = max(1, math.hypot(dx, dy))
        nx = dx / dist * speed
        ny = dy / dist * speed
        new_x = entity["x"] + nx
        new_y = entity["y"] + ny
        if self.entity_hits_obstacle(entity, new_x, new_y):
            for alt in [(-ny, nx), (ny, -nx), (nx * 0.5, 0), (0, ny * 0.5)]:
                test_x = entity["x"] + alt[0]
                test_y = entity["y"] + alt[1]
                if not self.entity_hits_obstacle(entity, test_x, test_y):
                    entity["x"] = test_x
                    entity["y"] = test_y
                    return
        else:
            entity["x"] = new_x
            entity["y"] = new_y

    def entity_hits_obstacle(self, entity, x, y):
        for obstacle in self.obstacles:
            if x + entity["size"] > obstacle["x"] and x < obstacle["x"] + obstacle["w"] and y + entity["size"] > obstacle["y"] and y < obstacle["y"] + obstacle["h"]:
                return True
        return False

    def spawn_enemy_minion(self, parent):
        self.enemies.append({"kind": "chaser", "x": parent["x"], "y": parent["y"], "size": 12, "speed": 2.1, "hp": 1, "phase": 0, "cooldown": 0, "shield": 0, "state": 0})

    def fire_enemy_bullet(self, enemy):
        dx = self.player_x + PLAYER_SIZE // 2 - (enemy["x"] + enemy["size"] // 2)
        dy = self.player_y + PLAYER_SIZE // 2 - (enemy["y"] + enemy["size"] // 2)
        dist = max(1, math.hypot(dx, dy))
        self.bullets.append({"x": enemy["x"] + enemy["size"] // 2, "y": enemy["y"] + enemy["size"] // 2, "vx": dx / dist * 4, "vy": dy / dist * 4, "enemy": True})

    def update_bullets(self):
        new_bullets = []
        for bullet in self.bullets:
            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]
            if self.is_outside_world(bullet["x"], bullet["y"]):
                continue
            if self.hit_obstacle(bullet["x"], bullet["y"]):
                self.add_particle(bullet["x"], bullet["y"], 10, "orange")
                continue
            if bullet.get("enemy"):
                if self.player_collides(bullet["x"], bullet["y"]):
                    self.health -= 1
                    if self.health <= 0:
                        self.game_over = True
                        return
                    continue
            else:
                for enemy in self.enemies:
                    if self.rect_hit(enemy["x"], enemy["y"], enemy["size"], bullet["x"], bullet["y"]):
                        enemy["hp"] -= 1
                        if enemy["kind"] == "shield":
                            enemy["shield"] = max(0, enemy["shield"] - 1)
                        self.add_particle(bullet["x"], bullet["y"], 8, "yellow")
                        break
                else:
                    new_bullets.append(bullet)
                    continue
            new_bullets.append(bullet)
        self.bullets = new_bullets

    def update_missiles(self):
        new_missiles = []
        for missile in self.missiles:
            missile["x"] += missile["vx"]
            missile["y"] += missile["vy"]
            missile["life"] -= 1
            if self.is_outside_world(missile["x"], missile["y"]) or missile["life"] <= 0:
                continue
            if self.hit_obstacle(missile["x"], missile["y"]):
                self.add_particle(missile["x"], missile["y"], 18, "purple")
                self.destroy_obstacle(missile["x"], missile["y"])
                continue
            hit = False
            for enemy in self.enemies:
                if self.rect_hit(enemy["x"], enemy["y"], enemy["size"], missile["x"], missile["y"]):
                    enemy["hp"] -= 3
                    hit = True
                    self.add_particle(missile["x"], missile["y"], 12, "purple")
                    break
            if hit:
                continue
            if self.boss and self.rect_hit(self.boss["x"], self.boss["y"], self.boss["w"], missile["x"], missile["y"]):
                self.boss["hp"] -= 8
                self.add_particle(missile["x"], missile["y"], 16, "purple")
                continue
            new_missiles.append(missile)
        self.missiles = new_missiles

    def update_particles(self):
        new_particles = []
        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
            if particle["life"] > 0:
                new_particles.append(particle)
        self.particles = new_particles

    def update_effects(self):
        new_effects = []
        for effect in self.effects:
            effect["life"] -= 1
            effect["size"] += 2
            if effect["life"] > 0:
                new_effects.append(effect)
        self.effects = new_effects

    def shoot_bullet(self, target_x, target_y):
        bullet_x = self.player_x + PLAYER_SIZE // 2
        bullet_y = self.player_y - 8
        dx = target_x - bullet_x
        dy = target_y - bullet_y
        dist = max(1, math.hypot(dx, dy))
        speed = 10
        self.bullets.append({"x": bullet_x, "y": bullet_y, "vx": dx / dist * speed, "vy": dy / dist * speed, "enemy": False})

    def fire_missile(self, target_x, target_y):
        if self.missile_count <= 0:
            return
        self.missile_count -= 1
        bullet_x = self.player_x + PLAYER_SIZE // 2
        bullet_y = self.player_y - 8
        dx = target_x - bullet_x
        dy = target_y - bullet_y
        dist = max(1, math.hypot(dx, dy))
        speed = 12
        self.missiles.append({"x": bullet_x, "y": bullet_y, "vx": dx / dist * speed, "vy": dy / dist * speed, "life": 110})

    def use_nuke(self):
        if self.nuke_count <= 0 or self.game_over:
            return
        self.nuke_count -= 1
        self.effects.append({"x": self.player_x + PLAYER_SIZE // 2, "y": self.player_y + PLAYER_SIZE // 2, "size": 10, "life": 24})
        for enemy in list(self.enemies):
            self.add_particle(enemy["x"] + enemy["size"] // 2, enemy["y"] + enemy["size"] // 2, 25, "white")
        self.enemies = []
        self.bullets = []
        self.missiles = []
        self.score += 40
        if self.boss:
            self.boss = None

    def check_collisions(self):
        new_enemies = []
        for enemy in self.enemies:
            if self.player_collides(enemy["x"], enemy["y"], enemy["size"]):
                self.health -= 1
                if self.health <= 0:
                    self.game_over = True
                    return
                continue
            if enemy["hp"] <= 0:
                self.add_particle(enemy["x"] + enemy["size"] // 2, enemy["y"] + enemy["size"] // 2, 18, "red")
                self.score += 6
                continue
            new_enemies.append(enemy)
        self.enemies = new_enemies

        new_pickups = []
        for pickup in self.pickups:
            if self.player_collides(pickup["x"], pickup["y"], pickup["size"]):
                if pickup["kind"] == "missile":
                    self.missile_count += 1
                else:
                    self.nuke_count += 1
                self.score += 16
            else:
                new_pickups.append(pickup)
        self.pickups = new_pickups

        if self.boss:
            if self.player_collides(self.boss["x"], self.boss["y"], self.boss["w"]):
                self.health -= 1
                if self.health <= 0:
                    self.game_over = True
                    return
            if self.boss["hp"] <= 0:
                self.score += 120
                self.boss = None
                self.effects.append({"x": self.boss["x"] + self.boss["w"] // 2, "y": self.boss["y"] + self.boss["h"] // 2, "size": 10, "life": 30})

        for chest in self.chests:
            if not chest["collected"] and self.player_collides(chest["x"], chest["y"], 24):
                chest["collected"] = True
                self.score += 40

        if all(chest["collected"] for chest in self.chests) and not self.game_over:
            self.game_over = True
            self.win_text = True

    def add_particle(self, x, y, count, color):
        for _ in range(count):
            self.particles.append({"x": x, "y": y, "vx": random.uniform(-2.5, 2.5), "vy": random.uniform(-2.5, 2.5), "life": random.randint(8, 20), "color": color})

    def draw_scene(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#060b16", outline="#060b16")

        self.canvas.create_oval(self.player_x - self.camera_x, self.player_y - self.camera_y, self.player_x + PLAYER_SIZE - self.camera_x, self.player_y + PLAYER_SIZE - self.camera_y, fill="#2a7fff", outline="white")
        self.canvas.create_rectangle(self.player_x + PLAYER_SIZE // 2 - 6 - self.camera_x, self.player_y - 10 - self.camera_y, self.player_x + PLAYER_SIZE // 2 + 6 - self.camera_x, self.player_y + 2 - self.camera_y, fill="#ffb347", outline="white")

        for obstacle in self.obstacles:
            self.canvas.create_rectangle(obstacle["x"] - self.camera_x, obstacle["y"] - self.camera_y, obstacle["x"] + obstacle["w"] - self.camera_x, obstacle["y"] + obstacle["h"] - self.camera_y, fill="#4f4b4b", outline="#8f8f8f")

        for enemy in self.enemies:
            sprite_name = f"enemy_{enemy['kind'] == 'chaser' and 0 or enemy['kind'] == 'zigzag' and 1 or enemy['kind'] == 'splitter' and 2 or enemy['kind'] == 'tank' and 3 or enemy['kind'] == 'shooter' and 4 or enemy['kind'] == 'teleporter' and 5 or enemy['kind'] == 'daser' and 6 or enemy['kind'] == 'shield' and 7 or enemy['kind'] == 'orbiter' and 8 or 9}"
            self.canvas.create_image(enemy["x"] + enemy["size"] // 2 - self.camera_x, enemy["y"] + enemy["size"] // 2 - self.camera_y, image=self.sprites[sprite_name])
        if self.boss:
            self.canvas.create_rectangle(self.boss["x"] - self.camera_x, self.boss["y"] - self.camera_y, self.boss["x"] + self.boss["w"] - self.camera_x, self.boss["y"] + self.boss["h"] - self.camera_y, fill="#8b0000", outline="white")
            self.canvas.create_text(self.width // 2, 40, text=f"Boss HP: {self.boss['hp']}/{self.boss['max_hp']}", fill="white", font=("Arial", 18, "bold"))

        for bullet in self.bullets:
            self.canvas.create_image(bullet["x"] - self.camera_x, bullet["y"] - self.camera_y, image=self.sprites["bullet"])

        for missile in self.missiles:
            self.canvas.create_image(missile["x"] - self.camera_x, missile["y"] - self.camera_y, image=self.sprites["rocket"])

        for pickup in self.pickups:
            color = "lime" if pickup["kind"] == "missile" else "cyan"
            self.canvas.create_oval(pickup["x"] - pickup["size"] // 2 - self.camera_x, pickup["y"] - pickup["size"] // 2 - self.camera_y, pickup["x"] + pickup["size"] // 2 - self.camera_x, pickup["y"] + pickup["size"] // 2 - self.camera_y, fill=color, outline="white")

        for effect in self.effects:
            self.canvas.create_oval(effect["x"] - effect["size"] - self.camera_x, effect["y"] - effect["size"] - self.camera_y, effect["x"] + effect["size"] - self.camera_x, effect["y"] + effect["size"] - self.camera_y, outline="white")

        for particle in self.particles:
            self.canvas.create_oval(particle["x"] - self.camera_x, particle["y"] - self.camera_y, particle["x"] + 2 - self.camera_x, particle["y"] + 2 - self.camera_y, fill=particle["color"], outline="")

        for chest in self.chests:
            if not chest["collected"]:
                self.canvas.create_image(chest["x"] - self.camera_x, chest["y"] - self.camera_y, image=self.sprites["chest"])

        self.canvas.create_text(20, 20, anchor="nw", text=f"Score: {self.score}", fill="white", font=("Arial", 18, "bold"))
        self.canvas.create_text(20, 50, anchor="nw", text=f"Missiles: {self.missile_count}   Nukes: {self.nuke_count}", fill="white", font=("Arial", 16, "bold"))
        self.canvas.create_text(self.width - 180, 20, anchor="nw", text=f"Health: {'♥' * self.health}{'♡' * (MAX_HEALTH - self.health)}", fill="white", font=("Arial", 16, "bold"))

        if self.game_over:
            if getattr(self, "win_text", False):
                self.canvas.create_text(self.width // 2, self.height // 2, text="You collected all 3 chests!\nYou win!", fill="white", font=("Arial", 24, "bold"))
            else:
                self.canvas.create_text(self.width // 2, self.height // 2, text="Game Over\nPress SPACE to restart", fill="white", font=("Arial", 24, "bold"))

    def update_boss(self):
        self.boss["cooldown"] -= 1
        self.boss["phase"] += 0.05
        self.boss["x"] = WORLD_W // 2 - 80 + math.sin(self.boss["phase"]) * 220
        self.boss["y"] = 120 + math.cos(self.boss["phase"]) * 140
        if self.boss["cooldown"] <= 0:
            self.fire_boss_attack()
            self.boss["cooldown"] = 80
        if self.boss["hp"] <= 0:
            self.boss = None

    def fire_boss_attack(self):
        for i in range(8):
            angle = i / 8 * 2 * math.pi
            self.bullets.append({"x": self.boss["x"] + self.boss["w"] // 2, "y": self.boss["y"] + self.boss["h"] // 2, "vx": math.cos(angle) * 5, "vy": math.sin(angle) * 5, "enemy": True})

    def player_collides(self, x, y, size=PLAYER_SIZE):
        return self.player_x + PLAYER_SIZE > x and self.player_x < x + size and self.player_y + PLAYER_SIZE > y and self.player_y < y + size

    def rect_hit(self, x, y, size, px, py):
        return px >= x and px <= x + size and py >= y and py <= y + size

    def hit_obstacle(self, x, y):
        for obstacle in self.obstacles:
            if x >= obstacle["x"] and x <= obstacle["x"] + obstacle["w"] and y >= obstacle["y"] and y <= obstacle["y"] + obstacle["h"]:
                return True
        return False

    def destroy_obstacle(self, x, y):
        new_obstacles = []
        for obstacle in self.obstacles:
            if x >= obstacle["x"] and x <= obstacle["x"] + obstacle["w"] and y >= obstacle["y"] and y <= obstacle["y"] + obstacle["h"]:
                self.add_particle(x, y, 18, "purple")
            else:
                new_obstacles.append(obstacle)
        self.obstacles = new_obstacles

    def is_outside_world(self, x, y):
        return x < 0 or y < 0 or x > WORLD_W or y > WORLD_H


if __name__ == "__main__":
    DodgeGame()
