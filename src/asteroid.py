import pygame
import random
import math
from settings import *
from utils import load_sound

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, size="small", difficulty=1):
        super().__init__()
        self.size = size
        self.difficulty = difficulty
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3) * (1 + difficulty * 0.2)
        self.pulse = random.uniform(0, 2 * math.pi)
        self.explosion_sound = load_sound("explosion.wav")
        self.hit_sound = load_sound("asteroid_hit.wav")
        
        # Dynamic asteroid properties
        size_data = {
            "large": {"base": 80, "damage": 3, "points": 30, "health": 4, "color": ASTEROID_GRAY},
            "medium": {"base": 50, "damage": 2, "points": 20, "health": 3, "color": ASTEROID_BROWN},
            "small": {"base": 30, "damage": 1, "points": 10, "health": 2, "color": (101, 67, 33)}
        }
        
        config = size_data[size]
        self.damage = config["damage"] * difficulty
        self.points = config["points"] * difficulty
        self.max_health = config["health"] * difficulty
        self.health = self.max_health
        
        # Procedural asteroid generation
        self.base_image = self._generate_asteroid_texture(
            config["base"], 
            config["color"],
            size
        )
        
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self._random_spawn_position()
        
        # Physics
        self.speedy = random.randint(2, 6) * (1 + difficulty * 0.15)
        self.speedx = random.randint(-3, 3) * (1 + difficulty * 0.1)
        self.velocity = pygame.math.Vector2(self.speedx, self.speedy)
        
        # Advanced effects
        self.damage_particles = []
        self.debris_trail = []
        self.crack_texture = None  # TODO: load from assets if available
        self.energy_core = random.random() < 0.15  # 15% chance for special asteroids
        self.core_color = random.choice([ELECTRIC_PURPLE, NEON_BLUE, LASER_RED])
        self.glowing_edge = False
        self.last_hit_time = 0
        
    def _generate_asteroid_texture(self, base_size, base_color, size_type):
        """Generates a high-quality procedural asteroid texture with normal mapping"""
        surface = pygame.Surface((base_size + 40, base_size + 40), pygame.SRCALPHA)
        center = (surface.get_width() // 2, surface.get_height() // 2)
        max_radius = base_size // 2
        
        # Generate irregular shape
        points = []
        num_points = random.randint(12, 16)
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            variation = max_radius // (3 if size_type == "large" else 4)
            r = max_radius + random.randint(-variation, variation)
            points.append((
                center[0] + r * math.cos(angle),
                center[1] + r * math.sin(angle)
            ))
        
        # Draw with lighting effects
        shadow_color = tuple(max(0, c - 40) for c in base_color)
        highlight_color = tuple(min(255, c + 30) for c in base_color)
        
        # Base shape with gradient
        pygame.draw.polygon(surface, base_color, points)
        
        # Add normal-mapped lighting
        light_angle = math.pi / 4  # Light from top-left
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            
            # Calculate edge normal
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            normal = (-edge[1], edge[0])
            normal_length = math.sqrt(normal[0]**2 + normal[1]**2)
            if normal_length > 0:
                normal = (normal[0]/normal_length, normal[1]/normal_length)
            
            # Calculate lighting
            light_intensity = max(0, normal[0] * math.cos(light_angle) + normal[1] * math.sin(light_angle))
            edge_color = (
                int(base_color[0] * (0.7 + 0.3 * light_intensity)),
                int(base_color[1] * (0.7 + 0.3 * light_intensity)),
                int(base_color[2] * (0.7 + 0.3 * light_intensity))
            )
            
            pygame.draw.line(surface, edge_color, p1, p2, 3)
        
        # Add mineral deposits
        for _ in range(random.randint(3, 7)):
            mineral_type = random.choice([
                (200, 200, 200, 150),  # Quartz
                (255, 215, 0, 180),     # Gold
                (100, 200, 255, 160)    # Ice
            ])
            pos = (
                random.randint(10, surface.get_width() - 10),
                random.randint(10, surface.get_height() - 10)
            )
            size = random.randint(3, 8)
            pygame.draw.circle(surface, mineral_type, pos, size)
        
        return surface
    
    def _random_spawn_position(self):
        """Improved spawn logic - prioritize top spawn for classic gameplay"""
        # 70% chance to spawn from top, 15% each from left and right
        spawn_choice = random.random()
        
        if spawn_choice < 0.7:  # Top spawn (70%)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-200, -50)
        elif spawn_choice < 0.85:  # Left spawn (15%)
            self.rect.x = random.randint(-150, -50)
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        else:  # Right spawn (15%)
            self.rect.x = random.randint(WIDTH, WIDTH + 100)
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)
    
    def update(self, dt):
        """Frame-rate independent movement with physics"""
        self.rotation += self.rotation_speed * dt * 60
        self.pulse += 0.05 * dt * 60
        
        # Apply acceleration based on difficulty
        if random.random() < 0.02 * self.difficulty:
            self.velocity.x += random.uniform(-0.5, 0.5) * self.difficulty
            self.velocity.y += random.uniform(0.1, 0.3) * self.difficulty
        
        # Apply movement
        self.rect.x += self.velocity.x * dt * 60
        self.rect.y += self.velocity.y * dt * 60
        
        # Screen wrapping
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        
        # Dynamic rotation and scaling
        self._update_visuals()
        self._update_particles(dt)
        self._update_trail(dt)
        
        # Energy core pulsing
        if self.energy_core:
            self._update_energy_core(dt)
    
    def _update_visuals(self):
        """Handles all visual transformations"""
        # Health-based scaling
        health_ratio = self.health / self.max_health
        scale_factor = 0.7 + 0.3 * health_ratio
        
        # Damage effect pulsing
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time < 500:  # 0.5s hit effect
            hit_pulse = 0.9 + 0.1 * math.sin(current_time * 0.02)
            scale_factor *= hit_pulse
        
        # Apply transformations
        scaled_size = (
            int(self.base_image.get_width() * scale_factor),
            int(self.base_image.get_height() * scale_factor)
        )
        scaled_image = pygame.transform.scale(self.base_image, scaled_size)
        self.image = pygame.transform.rotate(scaled_image, self.rotation)
        
        # Update rect while preserving center
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
        # Add glowing edge when critical
        if health_ratio < 0.3 and not self.glowing_edge:
            self._add_glowing_edge()
            self.glowing_edge = True
    
    def _add_glowing_edge(self):
        """Adds a glowing effect to damaged asteroids"""
        glow_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        mask = pygame.mask.from_surface(self.image)
        outline = mask.outline()
        
        if outline:
            pygame.draw.polygon(glow_surface, (*LASER_RED, 50), outline, 3)
            for i in range(3, 0, -1):
                alpha = 30 * i
                pygame.draw.polygon(
                    glow_surface, 
                    (*LASER_RED, alpha), 
                    [(x + i, y + i) for x, y in outline], 
                    3
                )
            self.image.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)
    
    def _update_particles(self, dt):
        """Advanced particle system with physics"""
        for p in self.damage_particles[:]:
            p['life'] -= 1 * dt * 60
            p['position'][0] += p['velocity'][0] * dt * 60
            p['position'][1] += p['velocity'][1] * dt * 60
            p['velocity'][1] += 0.1 * dt * 60  # Gravity
            
            if p['life'] <= 0:
                self.damage_particles.remove(p)
    
    def _update_trail(self, dt):
        """Debris trail with persistence"""
        if random.random() < 0.15 * (self.difficulty / 2):
            self.debris_trail.append({
                'position': [
                    self.rect.centerx + random.randint(-15, 15),
                    self.rect.centery + random.randint(-15, 15)
                ],
                'velocity': [
                    random.uniform(-1.5, 1.5),
                    random.uniform(0.5, 2)
                ],
                'life': random.randint(40, 80),
                'color': random.choice([ASTEROID_GRAY, ASTEROID_BROWN, SILVER]),
                'size': random.randint(1, 4),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-5, 5)
            })
        
        for debris in self.debris_trail[:]:
            debris['life'] -= 1 * dt * 60
            debris['position'][0] += debris['velocity'][0] * dt * 60
            debris['position'][1] += debris['velocity'][1] * dt * 60
            debris['rotation'] += debris['rotation_speed'] * dt * 60
            
            if debris['life'] <= 0:
                self.debris_trail.remove(debris)
    
    def _update_energy_core(self, dt):
        """Dynamic energy core effects"""
        if self.health <= 0:
            return
            
        core_pulse = 0.5 + 0.5 * math.sin(self.pulse * 3)
        core_size = int(8 * core_pulse)
        glow_size = int(15 * core_pulse)
        
        # Create glow surface
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface, 
            (*self.core_color, int(100 * core_pulse)), 
            (glow_size, glow_size), 
            glow_size
        )
        
        # Blit glow behind asteroid
        self.image.blit(
            glow_surface, 
            (self.rect.width // 2 - glow_size, self.rect.height // 2 - glow_size),
            special_flags=pygame.BLEND_ADD
        )
        
        # Draw core
        pygame.draw.circle(
            self.image, 
            self.core_color, 
            (self.rect.width // 2, self.rect.height // 2), 
            core_size + 2
        )
        pygame.draw.circle(
            self.image, 
            WHITE, 
            (self.rect.width // 2, self.rect.height // 2), 
            core_size
        )
    
    def take_damage(self, damage_amount, weapon_type="normal"):
        """Enhanced damage system with weapon effects"""
        if self.health <= 0:
            return 0
            
        self.health -= damage_amount
        self.last_hit_time = pygame.time.get_ticks()
        self.hit_sound.play()
        
        # Weapon-specific effects
        if weapon_type == "laser":
            self._add_laser_damage(damage_amount)
        elif weapon_type == "plasma":
            self._add_plasma_damage(damage_amount)
        else:
            self._add_normal_damage(damage_amount)
        
        # Return screen shake intensity
        return {
            "large": 10,
            "medium": 6,
            "small": 3
        }.get(self.size, 3) * (damage_amount / 3)
    
    def _add_normal_damage(self, damage_amount):
        """Standard bullet impact effects"""
        for _ in range(int(damage_amount * 8)):
            self.damage_particles.append({
                'position': [
                    self.rect.centerx + random.randint(-20, 20),
                    self.rect.centery + random.randint(-20, 20)
                ],
                'velocity': [
                    random.uniform(-5, 5),
                    random.uniform(-5, 0)
                ],
                'life': random.randint(30, 60),
                'color': random.choice([LASER_RED, NEON_YELLOW, ORANGE_RED, WHITE]),
                'size': random.randint(2, 6),
                'texture': None
            })
        
        # Add crack decals
        if random.random() < 0.3 * damage_amount and self.crack_texture:
            crack_size = random.randint(10, 20)
            crack_pos = (
                random.randint(0, self.image.get_width() - crack_size),
                random.randint(0, self.image.get_height() - crack_size)
            )
            crack = pygame.transform.scale(
                self.crack_texture,
                (crack_size, crack_size)
            )
            self.image.blit(crack, crack_pos, special_flags=pygame.BLEND_MULT)
    
    def _add_laser_damage(self, damage_amount):
        """Precision laser melting effects"""
        for _ in range(int(damage_amount * 5)):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, 15)
            pos = [
                self.rect.centerx + math.cos(angle) * dist,
                self.rect.centery + math.sin(angle) * dist
            ]
            
            self.damage_particles.append({
                'position': pos,
                'velocity': [
                    math.cos(angle) * random.uniform(0.5, 2),
                    math.sin(angle) * random.uniform(0.5, 2)
                ],
                'life': random.randint(40, 80),
                'color': (255, 100 + random.randint(0, 100), 50, 200),
                'size': random.randint(3, 8),
                'texture': "glow"
            })
        
        # Add scorch marks
        for _ in range(int(damage_amount / 2)):
            scorch_size = random.randint(8, 15)
            scorch_pos = (
                random.randint(0, self.image.get_width() - scorch_size),
                random.randint(0, self.image.get_height() - scorch_size)
            )
            pygame.draw.circle(
                self.image, 
                (50, 30, 20, 150), 
                scorch_pos, 
                scorch_size
            )
    
    def _add_plasma_damage(self, damage_amount):
        """Explosive plasma effects"""
        for _ in range(int(damage_amount * 15)):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, 25)
            pos = [
                self.rect.centerx + math.cos(angle) * dist,
                self.rect.centery + math.sin(angle) * dist
            ]
            
            self.damage_particles.append({
                'position': pos,
                'velocity': [
                    math.cos(angle) * random.uniform(1, 5),
                    math.sin(angle) * random.uniform(1, 5)
                ],
                'life': random.randint(20, 50),
                'color': (
                    random.randint(200, 255),
                    random.randint(50, 150),
                    random.randint(0, 50),
                    200
                ),
                'size': random.randint(4, 10),
                'texture': "plasma"
            })
    
    def explode(self):
        """Triggers destruction sequence"""
        self.explosion_sound.play()
        explosion_particles = []
        
        # Create explosion based on size
        particle_count = {
            "large": 120,
            "medium": 80,
            "small": 40
        }.get(self.size, 40)
        
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            
            explosion_particles.append({
                'position': [self.rect.centerx, self.rect.centery],
                'velocity': [
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                ],
                'life': random.randint(30, 90),
                'color': random.choice([
                    (255, 100, 50),  # Orange
                    (255, 200, 50),   # Yellow
                    (255, 50, 50)     # Red
                ]),
                'size': random.randint(3, 12),
                'growth_rate': random.uniform(0.5, 1.5)
            })
        
        # Special core explosion
        if self.energy_core:
            for _ in range(50):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(4, 12)
                
                explosion_particles.append({
                    'position': [self.rect.centerx, self.rect.centery],
                    'velocity': [
                        math.cos(angle) * speed,
                        math.sin(angle) * speed
                    ],
                    'life': random.randint(40, 100),
                    'color': (*self.core_color[:3], 200),
                    'size': random.randint(2, 6),
                    'growth_rate': random.uniform(0.8, 1.2)
                })
        
        return explosion_particles
    
    def draw_effects(self, screen, camera_offset=(0, 0)):
        """Renders all visual effects with camera offset"""
        # Draw debris trail
        for debris in self.debris_trail:
            life_ratio = debris['life'] / 80
            alpha = int(255 * life_ratio)
            size = max(1, int(debris['size'] * life_ratio))
            
            # Apply rotation to debris
            debris_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.rect(
                debris_surface, 
                (*debris['color'], alpha), 
                (size // 2, size // 2, size, size)
            )
            
            rotated_debris = pygame.transform.rotate(
                debris_surface, 
                debris['rotation']
            )
            
            screen.blit(
                rotated_debris,
                (
                    debris['position'][0] - rotated_debris.get_width() // 2 + camera_offset[0],
                    debris['position'][1] - rotated_debris.get_height() // 2 + camera_offset[1]
                )
            )
        
        # Draw damage particles
        for particle in self.damage_particles:
            life_ratio = particle['life'] / 60
            alpha = int(255 * life_ratio)
            
            if particle.get('texture') == "glow":
                # Glowing particle effect
                for i in range(3, 0, -1):
                    glow_size = particle['size'] + i * 2
                    glow_alpha = int(alpha * (0.3 - i * 0.1))
                    pygame.draw.circle(
                        screen,
                        (*particle['color'][:3], glow_alpha),
                        (
                            int(particle['position'][0] + camera_offset[0]),
                            int(particle['position'][1] + camera_offset[1])
                        ),
                        glow_size
                    )
            elif particle.get('texture') == "plasma":
                # Plasma orb effect
                pygame.draw.circle(
                    screen,
                    (*particle['color'][:3], alpha),
                    (
                        int(particle['position'][0] + camera_offset[0]),
                        int(particle['position'][1] + camera_offset[1])
                    ),
                    particle['size']
                )
                pygame.draw.circle(
                    screen,
                    WHITE,
                    (
                        int(particle['position'][0] + camera_offset[0]),
                        int(particle['position'][1] + camera_offset[1])
                    ),
                    max(1, particle['size'] // 2)
                )
            else:
                # Standard particle
                pygame.draw.circle(
                    screen,
                    (*particle['color'], alpha),
                    (
                        int(particle['position'][0] + camera_offset[0]),
                        int(particle['position'][1] + camera_offset[1])
                    ),
                    particle['size']
                )
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            self._draw_health_bar(screen, camera_offset)
    
    def _draw_health_bar(self, screen, camera_offset):
        """Dynamic health bar with advanced visuals"""
        bar_width = self.rect.width * 1.2
        bar_height = 8
        bar_x = self.rect.x + self.rect.width // 2 - bar_width // 2 + camera_offset[0]
        bar_y = self.rect.y - 20 + camera_offset[1]
        
        # Background with outline
        pygame.draw.rect(
            screen, 
            (20, 20, 20, 180), 
            (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4),
            border_radius=3
        )
        
        # Health fill with gradient
        health_ratio = self.health / self.max_health
        fill_width = int(bar_width * health_ratio)
        
        if health_ratio > 0.6:
            color1, color2 = NEON_GREEN, (50, 255, 50)
        elif health_ratio > 0.3:
            color1, color2 = NEON_YELLOW, (255, 200, 50)
        else:
            color1, color2 = LASER_RED, (255, 50, 50)
        
        # Animated low-health effect
        if health_ratio < 0.3:
            pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.005)
            color1 = tuple(int(c * pulse) for c in color1)
            color2 = tuple(int(c * pulse) for c in color2)
        
        # Draw gradient health bar
        if fill_width > 0:
            for i in range(fill_width):
                ratio = i / fill_width
                color = (
                    int(color1[0] * (1 - ratio) + color2[0] * ratio),
                    int(color1[1] * (1 - ratio) + color2[1] * ratio),
                    int(color1[2] * (1 - ratio) + color2[2] * ratio)
                )
                pygame.draw.rect(
                    screen, 
                    color, 
                    (bar_x + i, bar_y, 1, bar_height)
                )
        
        # Add energy core indicator
        if self.energy_core:
            core_size = 4
            pygame.draw.circle(
                screen,
                self.core_color,
                (int(bar_x + bar_width + 10 + camera_offset[0]), 
                int(bar_y + bar_height // 2 + camera_offset[1])),
                core_size
            )
            pygame.draw.circle(
                screen,
                WHITE,
                (int(bar_x + bar_width + 10 + camera_offset[0]), 
                int(bar_y + bar_height // 2 + camera_offset[1])),
                core_size - 2
            )