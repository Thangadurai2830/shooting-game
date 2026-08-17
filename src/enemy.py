import pygame
import random
import math
from typing import List, Dict, Optional, Tuple
from settings import *
from utils import load_sound, load_sprite_sheet, bezier_curve, particle_explosion
from bullet import Bullet

class Enemy(pygame.sprite.Sprite):
    """Advanced enemy class with state-driven AI, attack patterns, and visual effects."""
    
    # Class-wide assets cache
    _assets_loaded = False
    _textures = {}
    _sounds = {}
    
    def __init__(self, enemy_type: str, difficulty: int = 1, spawn_pos: Optional[Tuple[int, int]] = None):
        super().__init__()
        self._load_shared_assets()
        
        # Core properties
        self.enemy_type = enemy_type
        self.difficulty = difficulty
        self.state = "enter"  # enter, idle, attack, evade, dying
        self.state_time = 0
        self.health = 1
        self.max_health = 1
        self.score_value = 100
        self.attack_cooldown = 0
        
        # Physics
        self.position = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.rotation = 0
        self.rotation_speed = 0
        
        # AI
        self.ai_timer = 0
        self.ai_pattern = []
        self.current_pattern_index = 0
        self.current_pattern = "direct_assault"
        self.pattern_time = 0.0
        self.pattern_duration = 3.0
        self.target_position = None
        self.attack_phase = 0
        self.rage_mode = False
        
        # Visual effects
        self.engine_particles = []
        self.damage_particles = []
        self.shield_particles = []
        self.hit_flash = 0
        self.afterimages = []
        
        # Weapons
        self.bullet_spawn_points = []
        self.weapon_heat = 0
        self.max_weapon_heat = 100
        
        # Initialize enemy type
        self._init_enemy_type(spawn_pos)
        
    def _load_shared_assets(self):
        """Loads assets shared across all enemy instances."""
        if not Enemy._assets_loaded:
            # Load sprite sheets
            Enemy._textures = {
                "scout": load_sprite_sheet("enemies/scout.png", 64, 64),
                "fighter": load_sprite_sheet("enemies/fighter.png", 96, 96),
                "cruiser": load_sprite_sheet("enemies/cruiser.png", 128, 128),
                "boss": load_sprite_sheet("enemies/boss.png", 256, 256)
            }
            
            # Load sounds
            Enemy._sounds = {
                "engine": load_sound("sfx/enemy_engine.wav", volume=0.3),
                "hit": load_sound("sfx/enemy_hit.wav"),
                "explosion": load_sound("sfx/enemy_explosion.wav"),
                "shield": load_sound("sfx/shield_impact.wav")
            }
            
            Enemy._assets_loaded = True
    
    def _init_enemy_type(self, spawn_pos: Optional[Tuple[int, int]]):
        """Configures properties based on enemy type."""
        type_config = {
            "scout": {
                "size": (64, 64),
                "health": 2,
                "speed": 3,
                "texture_key": "scout",
                "enter_pattern": [(0, 1)],
                "attack_patterns": [
                    ["move_sinusoidal", "shoot_spread"],
                    ["move_circle", "shoot_targeted"]
                ],
                "bullet_type": "plasma",
                "bullet_damage": 1,
                "score": 100
            },
            "fighter": {
                "size": (96, 96),
                "health": 4,
                "speed": 2.5,
                "texture_key": "fighter",
                "enter_pattern": [(0.5, 0), (0, 1)],
                "attack_patterns": [
                    ["move_zigzag", "shoot_wave"],
                    ["move_charge", "shoot_burst"]
                ],
                "bullet_type": "laser",
                "bullet_damage": 2,
                "score": 250
            },
            "cruiser": {
                "size": (128, 128),
                "health": 8,
                "speed": 1.5,
                "texture_key": "cruiser",
                "enter_pattern": [(-1, 0), (0, 1)],
                "attack_patterns": [
                    ["move_strafe", "shoot_barrage"],
                    ["move_orbital", "shoot_swirl"]
                ],
                "bullet_type": "railgun",
                "bullet_damage": 3,
                "score": 500
            },
            "boss": {
                "size": (256, 256),
                "health": 50,
                "speed": 1,
                "texture_key": "boss",
                "enter_pattern": [(0, 0.5)],
                "attack_patterns": [
                    ["move_boss1", "shoot_pattern1"],
                    ["move_boss2", "shoot_pattern2"],
                    ["move_boss3", "shoot_pattern3"]
                ],
                "bullet_type": "quantum",
                "bullet_damage": 5,
                "score": 5000
            }
        }
        
        config = type_config.get(self.enemy_type, type_config["scout"])
        
        # Apply difficulty scaling
        difficulty_scale = 1 + (self.difficulty - 1) * 0.2
        self.max_health = int(config["health"] * difficulty_scale)
        self.health = self.max_health
        self.score_value = int(config["score"] * difficulty_scale)
        
        # Set up sprite
        self._setup_sprite(config["texture_key"], config["size"])
        
        # Movement properties
        self.base_speed = config["speed"]
        self.enter_pattern = config["enter_pattern"]
        self.attack_patterns = config["attack_patterns"]
        
        # Combat properties
        self.bullet_type = config["bullet_type"]
        self.bullet_damage = config["bullet_damage"]
        
        # Set spawn position
        if spawn_pos:
            self.position = pygame.math.Vector2(spawn_pos)
        else:
            self._set_default_spawn_position()
            
        # Play engine sound
        Enemy._sounds["engine"].play()
    
    def _setup_sprite(self, texture_key: str, size: Tuple[int, int]):
        """Configures the enemy's visual appearance."""
        self.frames = Enemy._textures.get(texture_key, [pygame.Surface(size, pygame.SRCALPHA)])
        self.current_frame = 0
        self.animation_speed = 0.1
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        # Set up hitbox (smaller than visual)
        self.hitbox = pygame.Rect(0, 0, size[0] * 0.7, size[1] * 0.7)
        
        # Configure weapon hardpoints
        self._setup_weapon_hardpoints()
    
    def _setup_weapon_hardpoints(self):
        """Defines where bullets spawn relative to the enemy."""
        if self.enemy_type == "scout":
            self.bullet_spawn_points = [
                {"position": (0.5, 1.0), "angle": 90, "offset": (0, 15)}
            ]
        elif self.enemy_type == "fighter":
            self.bullet_spawn_points = [
                {"position": (0.3, 0.9), "angle": 100, "offset": (-10, 10)},
                {"position": (0.7, 0.9), "angle": 80, "offset": (10, 10)}
            ]
        elif self.enemy_type == "cruiser":
            self.bullet_spawn_points = [
                {"position": (0.2, 0.8), "angle": 110, "offset": (-20, 5)},
                {"position": (0.8, 0.8), "angle": 70, "offset": (20, 5)},
                {"position": (0.5, 0.9), "angle": 90, "offset": (0, 10)}
            ]
        elif self.enemy_type == "boss":
            self.bullet_spawn_points = [
                {"position": (0.1, 0.7), "angle": 120, "offset": (-40, 0)},
                {"position": (0.3, 0.8), "angle": 100, "offset": (-20, 10)},
                {"position": (0.7, 0.8), "angle": 80, "offset": (20, 10)},
                {"position": (0.9, 0.7), "angle": 60, "offset": (40, 0)},
                {"position": (0.5, 0.9), "angle": 90, "offset": (0, 20)}
            ]
    
    def _set_default_spawn_position(self):
        """Determines where the enemy appears based on its type."""
        if self.enemy_type == "boss":
            self.position = pygame.math.Vector2(WIDTH // 2, -200)
        else:
            side = random.choice(["top", "left", "right"])
            
            if side == "top":
                self.position = pygame.math.Vector2(
                    random.randint(100, WIDTH - 100),
                    random.randint(-200, -100)
                )
            elif side == "left":
                self.position = pygame.math.Vector2(
                    random.randint(-150, -50),
                    random.randint(100, HEIGHT - 100)
                )
            else:
                self.position = pygame.math.Vector2(
                    random.randint(WIDTH + 50, WIDTH + 150),
                    random.randint(100, HEIGHT - 100)
                )
    
    def update(self, dt: float, player_pos: pygame.math.Vector2, bullets: pygame.sprite.Group):
        """Main update loop with state machine and AI."""
        self.state_time += dt
        
        # State machine
        if self.state == "enter":
            self._update_enter_state(dt)
        elif self.state == "idle":
            self._update_idle_state(dt, player_pos)
        elif self.state == "attack":
            self._update_attack_state(dt, player_pos, bullets)
        elif self.state == "evade":
            self._update_evade_state(dt, player_pos)
        elif self.state == "dying":
            self._update_dying_state(dt)
        
        # Update physics
        self._update_physics(dt)
        
        # Update visual effects
        self._update_visuals(dt)
        
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt * 60
        
        # Update AI timer
        self.ai_timer += dt
        
        # Update hitbox position
        self.hitbox.center = self.rect.center
    
    def _update_enter_state(self, dt: float):
        """Handles the enemy's entry animation."""
        if self.state_time < len(self.enter_pattern):
            move_vec = pygame.math.Vector2(self.enter_pattern[min(int(self.state_time), len(self.enter_pattern)-1)])
            self.velocity = move_vec * self.base_speed * 2
        else:
            self.state = "idle"
            self.state_time = 0
            self.velocity = pygame.math.Vector2(0, 0)
    
    def _update_idle_state(self, dt: float, player_pos: pygame.math.Vector2):
        """Transition between attack patterns."""
        if self.state_time > 1.0:  # 1 second idle
            self.state = "attack"
            self.state_time = 0
            self._choose_attack_pattern()
            
            # Face toward player
            direction = player_pos - self.position
            if direction.length() > 0:
                self.rotation = math.degrees(math.atan2(-direction.y, direction.x)) - 90
    
    def _update_attack_state(self, dt: float, player_pos: pygame.math.Vector2, bullets: pygame.sprite.Group):
        """Executes the current attack pattern."""
        if self.current_pattern_index < len(self.ai_pattern):
            current_action = self.ai_pattern[self.current_pattern_index]
            
            # Execute movement action
            if current_action.startswith("move_"):
                move_method = getattr(self, current_action)
                move_complete = move_method(dt, player_pos)
                
                if move_complete:
                    self.current_pattern_index += 1
            
            # Execute attack action
            elif current_action.startswith("shoot_"):
                shoot_method = getattr(self, current_action)
                shoot_complete = shoot_method(dt, player_pos, bullets)
                
                if shoot_complete:
                    self.current_pattern_index += 1
        else:
            # Pattern complete
            self.state = "idle"
            self.state_time = 0
            self.current_pattern_index = 0
    
    def _update_evade_state(self, dt: float, player_pos: pygame.math.Vector2):
        """Emergency dodging behavior."""
        # Move away from player bullets
        evade_vector = pygame.math.Vector2(0, 0)
        
        if random.random() < 0.7:
            # General evasion
            evade_vector.x = math.cos(self.ai_timer * 5) * self.base_speed * 2
            evade_vector.y = math.sin(self.ai_timer * 3) * self.base_speed * 2
        else:
            # Targeted dodge
            direction = self.position - player_pos
            if direction.length() > 0:
                evade_vector = direction.normalize() * self.base_speed * 3
        
        self.velocity = evade_vector
        
        # Return to attack after short time
        if self.state_time > 2.0:
            self.state = "attack"
            self.state_time = 0
    
    def _update_dying_state(self, dt: float):
        """Death animation and cleanup."""
        self.velocity *= 0.95  # Slow down
        
        # Expand explosion
        if self.state_time < 1.0:
            scale = 1 + self.state_time * 2
            self.image = pygame.transform.scale(self.frames[0], 
                (int(self.rect.width * scale), int(self.rect.height * scale)))
        else:
            self.kill()
            Enemy._sounds["engine"].stop()
    
    def _choose_attack_pattern(self):
        """Choose an attack pattern based on enemy type and current situation."""
        if self.enemy_type == "scout":
            # Fast, hit-and-run attacks
            self.current_pattern = random.choice(["strafe", "dive_bomb"])
        elif self.enemy_type == "fighter":
            # Balanced attack patterns
            self.current_pattern = random.choice(["circle_strafe", "zigzag", "direct_assault"])
        elif self.enemy_type == "cruiser":
            # Heavy, sustained attacks
            self.current_pattern = random.choice(["broadside", "siege", "ram"])
        elif self.enemy_type == "boss":
            # Complex multi-phase attacks
            self.current_pattern = random.choice(["laser_sweep", "missile_barrage", "teleport_strike"])
        else:
            # Default pattern
            self.current_pattern = "direct_assault"
        
        # Set pattern-specific parameters
        self.pattern_time = 0.0
        self.pattern_duration = random.uniform(2.0, 5.0)
    
    def _update_physics(self, dt: float):
        """Updates position, rotation, and collisions."""
        # Apply acceleration
        self.velocity += self.acceleration * dt * 60
        
        # Clamp velocity magnitude only if it's not zero
        max_speed = self.base_speed * (3 if self.rage_mode else 1)
        if self.velocity.length() > 0:
            self.velocity = self.velocity.clamp_magnitude(max_speed)
        
        # Update position
        self.position += self.velocity * dt * 60
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        # Update rotation
        if self.rotation_speed != 0:
            self.rotation += self.rotation_speed * dt * 60
            self.image = pygame.transform.rotate(self.frames[self.current_frame], self.rotation)
            self.rect = self.image.get_rect(center=self.rect.center)
        
        # Screen boundaries
        self._enforce_boundaries()
    
    def _enforce_boundaries(self):
        """Keep enemy within screen bounds with wrapping for certain types."""
        from settings import Engine
        
        # For most enemies, remove them if they go too far off screen
        margin = 100
        if (self.position.x < -margin or self.position.x > Engine.SCREEN_WIDTH + margin or
            self.position.y < -margin or self.position.y > Engine.SCREEN_HEIGHT + margin):
            
            # For certain enemy types, wrap around instead of removing
            if self.enemy_type in ["scout", "fighter"]:
                if self.position.x < -margin:
                    self.position.x = Engine.SCREEN_WIDTH + margin
                elif self.position.x > Engine.SCREEN_WIDTH + margin:
                    self.position.x = -margin
                    
                if self.position.y < -margin:
                    self.position.y = Engine.SCREEN_HEIGHT + margin
                elif self.position.y > Engine.SCREEN_HEIGHT + margin:
                    self.position.y = -margin
            else:
                # For bosses and other large enemies, just destroy
                self.kill()
    
    def _update_visuals(self, dt: float):
        """Handles animations and visual effects."""
        # Animation
        self.current_frame = (self.current_frame + self.animation_speed * dt * 60) % len(self.frames)
        
        # Hit flash
        if self.hit_flash > 0:
            self.hit_flash -= dt * 60
            flash_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash_surf.fill((255, 100, 100, self.hit_flash * 2))
            self.image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Engine particles
        if random.random() < 0.3 * dt * 60:
            self._add_engine_particles()
        
        # Update particles
        self._update_particles(dt)
        
        # Afterimages for fast movement
        if self.velocity.length() > self.base_speed * 1.5:
            self._add_afterimage()
        
        # Update afterimages
        self._update_afterimages(dt)
    
    def _add_afterimage(self):
        """Add an afterimage for fast movement effects."""
        if len(self.afterimages) < 5:  # Limit number of afterimages
            afterimage = {
                'position': pygame.math.Vector2(self.position),
                'image': self.image.copy(),
                'life': 0.3  # Seconds
            }
            self.afterimages.append(afterimage)
    
    def _update_afterimages(self, dt: float):
        """Update and remove expired afterimages."""
        for afterimage in self.afterimages[:]:
            afterimage['life'] -= dt
            if afterimage['life'] <= 0:
                self.afterimages.remove(afterimage)
            else:
                # Fade out the afterimage
                alpha = int(255 * (afterimage['life'] / 0.3))
                afterimage['image'].set_alpha(alpha)
    
    def _draw_afterimages(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """Draw afterimages behind the enemy."""
        for afterimage in self.afterimages:
            pos = (
                int(afterimage['position'].x - offset[0] - afterimage['image'].get_width() // 2),
                int(afterimage['position'].y - offset[1] - afterimage['image'].get_height() // 2)
            )
            screen.blit(afterimage['image'], pos)
    
    # === MOVEMENT PATTERNS ===
    def move_sinusoidal(self, dt: float, target_pos: pygame.math.Vector2) -> bool:
        """Sinusoidal wave movement pattern."""
        self.velocity.x = math.cos(self.ai_timer * 2) * self.base_speed * 1.5
        self.velocity.y = self.base_speed * 0.7
        return self.position.y > HEIGHT * 0.3
    
    def move_circle(self, dt: float, target_pos: pygame.math.Vector2) -> bool:
        """Circular orbiting movement."""
        radius = 150
        center_x = WIDTH // 2
        angular_speed = 0.02 * self.difficulty
        
        self.position.x = center_x + math.cos(self.ai_timer * angular_speed) * radius
        self.position.y = 200 + math.sin(self.ai_timer * angular_speed) * radius
        self.rotation = math.degrees(self.ai_timer * angular_speed) - 90
        
        return self.ai_timer > (math.pi * 2 / angular_speed)  # Complete circle
    
    def move_zigzag(self, dt: float, target_pos: pygame.math.Vector2) -> bool:
        """Zig-zag pattern toward player."""
        zig_speed = 4 if self.ai_timer % 1 < 0.5 else -4
        self.velocity.x = zig_speed * self.difficulty
        self.velocity.y = self.base_speed * 0.5
        
        return self.position.y > HEIGHT * 0.4
    
    # === ATTACK PATTERNS ===
    def shoot_spread(self, dt: float, target_pos: pygame.math.Vector2, bullets: pygame.sprite.Group) -> bool:
        """Fan-shaped bullet spread."""
        if self.attack_cooldown <= 0:
            for angle in range(-30, 31, 15):
                for hardpoint in self.bullet_spawn_points:
                    spawn_pos = self._get_hardpoint_position(hardpoint)
                    bullet = Bullet(
                        spawn_pos[0], spawn_pos[1],
                        self.bullet_type,
                        self.bullet_damage,
                        angle=hardpoint["angle"] + angle
                    )
                    bullets.add(bullet)
            
            self.attack_cooldown = 1.0 / self.difficulty
            return True
        return False
    
    def shoot_targeted(self, dt: float, target_pos: pygame.math.Vector2, bullets: pygame.sprite.Group) -> bool:
        """Target-seeking bullets."""
        if self.attack_cooldown <= 0:
            for hardpoint in self.bullet_spawn_points:
                spawn_pos = self._get_hardpoint_position(hardpoint)
                direction = target_pos - pygame.math.Vector2(spawn_pos)
                angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
                
                bullet = Bullet(
                    spawn_pos[0], spawn_pos[1],
                    self.bullet_type,
                    self.bullet_damage,
                    angle=angle,
                    target=self  # Homing will find player
                )
                bullets.add(bullet)
            
            self.attack_cooldown = 2.0 / self.difficulty
            return True
        return False
    
    # === PARTICLE SYSTEMS ===
    def _add_engine_particles(self):
        """Creates engine exhaust particles."""
        for _ in range(2):
            angle = self.rotation + 180 + random.uniform(-15, 15)
            speed = random.uniform(0.5, 2.0)
            
            self.engine_particles.append({
                "position": pygame.math.Vector2(
                    self.position.x + math.cos(math.radians(self.rotation)) * -self.rect.height * 0.4,
                    self.position.y + math.sin(math.radians(self.rotation)) * -self.rect.height * 0.4
                ),
                "velocity": pygame.math.Vector2(
                    math.cos(math.radians(angle)) * speed,
                    math.sin(math.radians(angle)) * speed
                ),
                "life": random.uniform(0.5, 1.5),
                "size": random.uniform(3, 6),
                "color": random.choice([
                    (255, 100, 50),
                    (255, 150, 30),
                    (255, 200, 100)
                ])
            })
    
    def _update_particles(self, dt: float):
        """Updates all particle systems."""
        # Engine particles
        for p in self.engine_particles[:]:
            p["life"] -= 0.02 * dt * 60
            p["position"] += p["velocity"] * dt * 60
            p["size"] *= 0.95
            
            if p["life"] <= 0:
                self.engine_particles.remove(p)
        
        # Damage particles
        for p in self.damage_particles[:]:
            p["life"] -= 0.03 * dt * 60
            p["position"] += p["velocity"] * dt * 60
            p["velocity"].y += 0.05 * dt * 60  # Gravity
            
            if p["life"] <= 0:
                self.damage_particles.remove(p)
    
    def take_damage(self, amount: int, impact_pos: Optional[Tuple[float, float]] = None):
        """Handles damage with visual and audio feedback."""
        if self.state == "dying":
            return False
        
        self.health -= amount
        self.hit_flash = 10
        
        # Create damage particles
        if impact_pos:
            direction = pygame.math.Vector2(impact_pos) - self.position
            if direction.length() > 0:
                direction = direction.normalize()
            
            for _ in range(amount * 5):
                self.damage_particles.append({
                    "position": pygame.math.Vector2(impact_pos),
                    "velocity": direction.rotate(random.uniform(-30, 30)) * random.uniform(2, 5),
                    "life": random.uniform(0.5, 1.0),
                    "size": random.uniform(2, 4),
                    "color": random.choice([
                        (255, 50, 50),
                        (255, 150, 50),
                        (255, 255, 100)
                    ])
                })
        
        Enemy._sounds["hit"].play()
        
        # Check for death
        if self.health <= 0:
            self._die()
            return True
        
        # Chance to enter evade state
        if random.random() < 0.3 and self.state != "enter":
            self.state = "evade"
            self.state_time = 0
        
        return False
    
    def _die(self):
        """Initiates death sequence."""
        self.state = "dying"
        self.state_time = 0
        Enemy._sounds["explosion"].play()
        
        # Create explosion particles
        particle_explosion(
            self.position.x,
            self.position.y,
            color=(255, 100, 50),
            count=50
        )
    
    def draw(self, screen: pygame.Surface, offset: Tuple[float, float] = (0, 0)):
        """Renders the enemy with all effects."""
        # Draw afterimages first
        self._draw_afterimages(screen, offset)
        
        # Draw engine particles
        self._draw_engine_particles(screen, offset)
        
        # Draw damage particles
        self._draw_damage_particles(screen, offset)
        
        # Draw the enemy sprite
        screen.blit(self.image, (self.rect.x + offset[0], self.rect.y + offset[1]))
        
        # Draw health bar if damaged
        if self.health < self.max_health and self.state != "dying":
            self._draw_health_bar(screen, offset)
    
    def _draw_health_bar(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """Renders an advanced health bar."""
        bar_width = self.rect.width * 0.8
        bar_height = 6
        bar_x = self.rect.x + (self.rect.width - bar_width) // 2 + offset[0]
        bar_y = self.rect.y - 15 + offset[1]
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=3)
        
        # Health fill
        health_ratio = self.health / self.max_health
        fill_width = max(2, int(bar_width * health_ratio))
        
        # Color gradient
        if health_ratio > 0.6:
            color = (100, 255, 100)
        elif health_ratio > 0.3:
            color = (255, 200, 50)
        else:
            color = (255, 50, 50)
        
        # Animate critical health
        if health_ratio < 0.3:
            pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.01)
            color = tuple(int(c * pulse) for c in color)
        
        # Draw fill
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height), border_radius=2)
        
        # Draw shield indicator if applicable
        if hasattr(self, 'shield_strength'):
            shield_ratio = self.shield_strength / self.max_shield
            shield_width = int(bar_width * shield_ratio)
            pygame.draw.rect(screen, (100, 150, 255), (bar_x, bar_y - 8, shield_width, 3), border_radius=1)