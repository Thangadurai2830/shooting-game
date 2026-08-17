import pygame
import random
import math
from typing import List, Dict, Tuple, Optional
from settings import *
from bullet import Bullet
from utils import load_sound, bezier_curve, particle_explosion

class Player(pygame.sprite.Sprite):
    """Next-generation player ship with advanced systems and effects."""
    
    def __init__(self, sound_system):
        super().__init__()
        self.sound = sound_system
        self._init_ship_systems()
        self._setup_powerups()
        self._init_ship_design()
        self._setup_physics()
        self._create_hitbox()
        
        # Load sounds
        self.shoot_sounds = [
            load_sound("laser1.wav"),
            load_sound("laser2.wav"),
            load_sound("laser3.wav")
        ]
        self.damage_sound = load_sound("player_hit.wav")
        self.powerup_sound = load_sound("powerup.wav")
        
    def _init_ship_design(self):
        """Creates a procedurally generated ship design with multiple layers."""
        # Base surface with per-pixel alpha
        self.base_image = pygame.Surface((64, 80), pygame.SRCALPHA)
        self.glow_image = pygame.Surface((64, 80), pygame.SRCALPHA)
        
        # Ship hull - procedurally generated
        hull_points = self._generate_hull_shape()
        pygame.draw.polygon(self.base_image, SHIP_BLUE, hull_points)
        
        # Energy core glow
        self._create_energy_core()
        
        # Engine details
        self._create_engine_details()
        
        # Wing patterns with animated energy lines
        self._create_wing_patterns()
        
        # Combine base and glow layers
        self.image = pygame.Surface((64, 80), pygame.SRCALPHA)
        self._update_ship_appearance()
        
        # Mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)
        
    def _generate_hull_shape(self) -> List[Tuple[int, int]]:
        """Generates a procedural ship hull with variations."""
        # Base points
        points = [
            (32, 0),    # Nose
            (12, 25),    # Left shoulder
            (8, 60),     # Left engine
            (25, 75),    # Left tail
            (32, 65),    # Center tail
            (39, 75),    # Right tail
            (56, 60),    # Right engine
            (52, 25),    # Right shoulder
        ]
        
        # Add procedural variations
        for i in range(1, len(points)-1):
            variation = random.uniform(-2, 2)
            points[i] = (points[i][0] + variation, points[i][1] + variation)
            
        return points
    
    def _create_energy_core(self):
        """Creates the ship's central energy core with glow effects."""
        # Core gradient
        for radius in range(10, 4, -1):
            alpha = 200 - radius * 20
            color = (*CORE_BLUE, alpha)
            pygame.draw.circle(self.glow_image, color, (32, 30), radius)
        
        # Inner core
        pygame.draw.circle(self.base_image, CORE_WHITE, (32, 30), 4)
        
        # Energy tendrils
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(8, 15)
            end_pos = (
                32 + math.cos(angle) * length,
                30 + math.sin(angle) * length
            )
            
            # Bezier curve for organic look
            control1 = (
                32 + math.cos(angle) * length * 0.3,
                30 + math.sin(angle) * length * 0.3
            )
            control2 = (
                32 + math.cos(angle + 0.5) * length * 0.6,
                30 + math.sin(angle + 0.5) * length * 0.6
            )
            
            points = bezier_curve((32, 30), control1, control2, end_pos, 10)
            pygame.draw.lines(self.glow_image, (*CORE_BLUE, 150), False, points, 2)
    
    def _create_engine_details(self):
        """Adds detailed engine components with glow."""
        # Main engines
        for x in [20, 44]:
            # Engine housing
            pygame.draw.ellipse(self.base_image, ENGINE_GRAY, (x-5, 55, 10, 20))
            
            # Exhaust glow
            for i in range(3, 0, -1):
                alpha = 150 - i * 50
                height = 10 + i * 5
                pygame.draw.ellipse(
                    self.glow_image, 
                    (*ENGINE_ORANGE, alpha), 
                    (x-3-i, 75, 6+i*2, height)
                )
        
        # Afterburner rings
        for ring in range(3):
            radius = 6 + ring * 2
            alpha = 100 - ring * 30
            for x in [20, 44]:
                pygame.draw.circle(
                    self.glow_image,
                    (*ENGINE_BLUE, alpha),
                    (x, 65), 
                    radius, 
                    1
                )
    
    def _create_wing_patterns(self):
        """Adds animated energy patterns to wings."""
        # Left wing energy channels
        wing_left = [(12, 25), (8, 60), (25, 75)]
        for i in range(3):
            offset = i * 3
            points = [
                (wing_left[0][0] + offset, wing_left[0][1] + offset),
                (wing_left[1][0] + offset, wing_left[1][1] - offset),
                (wing_left[2][0] - offset, wing_left[2][1] - offset)
            ]
            pygame.draw.lines(
                self.base_image, 
                WING_ENERGY, 
                False, 
                points, 
                2
            )
        
        # Right wing energy channels
        wing_right = [(52, 25), (56, 60), (39, 75)]
        for i in range(3):
            offset = i * 3
            points = [
                (wing_right[0][0] - offset, wing_right[0][1] + offset),
                (wing_right[1][0] - offset, wing_right[1][1] - offset),
                (wing_right[2][0] + offset, wing_right[2][1] - offset)
            ]
            pygame.draw.lines(
                self.base_image, 
                WING_ENERGY, 
                False, 
                points, 
                2
            )
    
    def _update_ship_appearance(self):
        """Updates the ship's visual appearance based on state."""
        self.image.fill((0, 0, 0, 0))
        
        # Base ship
        self.image.blit(self.base_image, (0, 0))
        
        # Power level effects
        if self.power_level > 1:
            # Create power aura
            aura = pygame.Surface((80, 80), pygame.SRCALPHA)
            color = POWER_GOLD if self.power_level >= 3 else POWER_RED
            
            for radius in range(15, 5, -1):
                alpha = 50 - radius * 2
                pygame.draw.circle(
                    aura, 
                    (*color, alpha), 
                    (40, 40), 
                    radius
                )
            
            self.image.blit(aura, (-8, -8), special_flags=pygame.BLEND_ADD)
        
        # Shield effects
        if self.shield_timer > pygame.time.get_ticks():
            shield = pygame.Surface((80, 80), pygame.SRCALPHA)
            time_left = (self.shield_timer - pygame.time.get_ticks()) / 1000
            pulse = 1 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01)
            
            for radius in range(40, 30, -2):
                alpha = int(100 * (time_left / SHIELD_DURATION) * pulse)
                # Extract RGB from SHIELD_BLUE and apply our alpha
                shield_rgb = SHIELD_BLUE[:3]  # Get RGB part only
                pygame.draw.circle(
                    shield, 
                    (*shield_rgb, alpha), 
                    (40, 40), 
                    radius, 
                    2
                )
            
            self.image.blit(shield, (-8, -8), special_flags=pygame.BLEND_ADD)
        
        # Damage flash
        if self.invulnerable_time > 0 and self.invulnerable_time % 10 < 5:
            flash = pygame.Surface((64, 80), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 100))
            self.image.blit(flash, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Apply glow layer
        self.image.blit(self.glow_image, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Update mask for collision
        self.mask = pygame.mask.from_surface(self.image)
    
    def _setup_physics(self):
        """Configures the ship's movement physics."""
        self.position = pygame.math.Vector2(WIDTH // 2, HEIGHT - 100)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.max_speed = PLAYER_SPEED
        self.rotation = 0
        self.rotation_speed = 0
        
        # Initialize rect - will be updated after image is created
        self.rect = pygame.Rect(0, 0, 64, 80)
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        # Hitbox smaller than visual
        self.hitbox = pygame.Rect(0, 0, 40, 60)
        
    def _init_ship_systems(self):
        """Initializes all ship systems and stats."""
        self.lives = PLAYER_LIVES
        self.max_lives = PLAYER_LIVES
        # Health system: 4 damage points = 1 life lost
        # Player can take 4 hits before losing a life and continuing
        self.health = 4  # 4 health points = 1 life (each hit = 1 damage)
        self.max_health = 4  # Maximum health per life
        self.power_level = 1
        
        # Timers
        self.invulnerable_time = 0
        self.last_shot = 0
        self.last_damage_time = 0
        self.engine_pulse = 0
        
        # Particle systems
        self.engine_particles = []
        self.damage_particles = []
        self.energy_trails = []
        
    def _setup_powerups(self):
        """Sets up power-up related variables."""
        # Power-up timers
        self.rapid_fire_timer = 0
        self.damage_boost_timer = 0
        self.shield_timer = 0
        self.speed_boost_timer = 0
        
        # Power-up durations
        self.RAPID_FIRE_DURATION = 10000  # 10 seconds
        self.DAMAGE_BOOST_DURATION = 8000  # 8 seconds
        self.SHIELD_DURATION = 15000       # 15 seconds
        self.SPEED_BOOST_DURATION = 5000   # 5 seconds
    
    def _create_hitbox(self):
        """Creates a precise hitbox for collision detection."""
        self.hitbox = pygame.Rect(0, 0, 40, 60)
        self.hitbox.center = self.rect.center
    
    def update(self, keys: Dict[int, bool], dt: float):
        """Updates all player systems."""
        self._handle_movement(keys, dt)
        self._update_timers(dt)
        self._update_particles(dt)
        self._update_ship_appearance()
        self._update_hitbox()
        
        # Engine pulse for visual effect
        self.engine_pulse += dt * 10
    
    def _handle_movement(self, keys: Dict[int, bool], dt: float):
        """Handles player movement with advanced physics."""
        # Reset acceleration
        self.acceleration = pygame.math.Vector2(0, 0)
        
        # Keyboard input
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.acceleration.x = -PLAYER_ACCELERATION
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.acceleration.x = PLAYER_ACCELERATION
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.acceleration.y = -PLAYER_ACCELERATION
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.acceleration.y = PLAYER_ACCELERATION
            
        # Apply speed boost if active
        speed_multiplier = 1.5 if self.speed_boost_timer > pygame.time.get_ticks() else 1.0
        max_speed = self.max_speed * speed_multiplier
        
        # Apply acceleration
        self.velocity += self.acceleration * dt * 60
        self.velocity.x = max(-max_speed, min(max_speed, self.velocity.x))
        self.velocity.y = max(-max_speed, min(max_speed, self.velocity.y))
        
        # Apply friction when no input
        if not any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], 
                   keys[pygame.K_UP], keys[pygame.K_DOWN],
                   keys[pygame.K_a], keys[pygame.K_d],
                   keys[pygame.K_w], keys[pygame.K_s]]):
            self.velocity *= 0.9 ** (dt * 60)  # Frame-rate independent friction
        
        # Update position
        self.position += self.velocity * dt * 60
        
        # Boundary checking
        self.position.x = max(self.rect.width // 2, 
                             min(WIDTH - self.rect.width // 2, self.position.x))
        self.position.y = max(self.rect.height // 2, 
                             min(HEIGHT - self.rect.height // 2, self.position.y))
        
        # Update rect position
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        # Create engine particles
        self._create_engine_particles(keys, dt)
    
    def _create_engine_particles(self, keys: Dict[int, bool], dt: float):
        """Creates engine exhaust particles."""
        if random.random() < 0.8 * dt * 60:  # Scale by delta time
            for engine_pos in [(20, 75), (44, 75)]:  # Left and right engines
                # Base particle
                self.engine_particles.append({
                    "position": pygame.math.Vector2(
                        self.position.x + engine_pos[0] - 32 + random.uniform(-2, 2),
                        self.position.y + engine_pos[1] - 40 + random.uniform(0, 5)
                    ),
                    "velocity": pygame.math.Vector2(
                        random.uniform(-1, 1),
                        random.uniform(2, 5)
                    ),
                    "life": random.uniform(0.5, 1.5),
                    "size": random.uniform(3, 6),
                    "color": random.choice([
                        ENGINE_ORANGE,
                        ENGINE_YELLOW,
                        ENGINE_BLUE
                    ]),
                    "growth_rate": random.uniform(0.7, 1.3)
                })
                
                # Afterburner effect when boosting
                if (keys[pygame.K_UP] or keys[pygame.K_w]) and random.random() < 0.3:
                    for _ in range(2):
                        self.engine_particles.append({
                            "position": pygame.math.Vector2(
                                self.position.x + engine_pos[0] - 32,
                                self.position.y + engine_pos[1] - 40
                            ),
                            "velocity": pygame.math.Vector2(
                                random.uniform(-2, 2),
                                random.uniform(5, 10)
                            ),
                            "life": random.uniform(0.3, 0.8),
                            "size": random.uniform(5, 8),
                            "color": ENGINE_RED,
                            "growth_rate": 1.5
                        })
    
    def _update_timers(self, dt: float):
        """Updates all timed player states."""
        current_time = pygame.time.get_ticks()
        
        # Invulnerability timer
        if self.invulnerable_time > 0:
            self.invulnerable_time -= dt * 60  # Convert to frames
            
        # Create damage particles if recently hit
        if current_time - self.last_damage_time < 1000:  # 1 second
            if random.random() < 0.3 * dt * 60:
                self._create_damage_particles()
    
    def _create_damage_particles(self):
        """Creates particles when player is damaged."""
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            self.damage_particles.append({
                "position": pygame.math.Vector2(self.position),
                "velocity": pygame.math.Vector2(
                    math.cos(angle) * random.uniform(1, 3),
                    math.sin(angle) * random.uniform(1, 3)
                ),
                "life": random.uniform(0.5, 1.0),
                "size": random.uniform(2, 4),
                "color": DAMAGE_RED,
                "growth_rate": 0.8
            })
    
    def _update_particles(self, dt: float):
        """Updates all particle systems."""
        # Engine particles
        for p in self.engine_particles[:]:
            p["life"] -= dt
            p["position"] += p["velocity"] * dt * 60
            p["size"] *= p["growth_rate"] ** (dt * 60)
            
            if p["life"] <= 0:
                self.engine_particles.remove(p)
        
        # Damage particles
        for p in self.damage_particles[:]:
            p["life"] -= dt
            p["position"] += p["velocity"] * dt * 60
            p["velocity"].y += 0.5 * dt * 60  # Gravity
            p["size"] *= p["growth_rate"] ** (dt * 60)
            
            if p["life"] <= 0:
                self.damage_particles.remove(p)
    
    def _update_hitbox(self):
        """Updates the hitbox position."""
        self.hitbox.center = self.rect.center
    
    def shoot(self, bullet_group: pygame.sprite.Group, all_sprites: pygame.sprite.Group) -> bool:
        """Fires bullets based on current weapon state."""
        current_time = pygame.time.get_ticks()
        
        # Determine fire rate based on power-ups
        if self.rapid_fire_timer > current_time:
            fire_delay = 100  # Rapid fire delay
        else:
            fire_delay = 300  # Normal fire delay
            
        # Check if can shoot
        if current_time - self.last_shot > fire_delay:
            self.last_shot = current_time
            
            # Determine bullet damage
            if self.damage_boost_timer > current_time:
                damage = 3  # Triple damage
            elif self.power_level >= 2:
                damage = 2  # Double damage
            else:
                damage = 1  # Normal damage
            
            # Create bullets based on power level
            if self.power_level >= 3:
                # Triple shot spread
                for angle in [-15, 0, 15]:
                    bullet = Bullet(
                        self.position.x,
                        self.position.y - 30,
                        damage=damage,
                        angle=angle
                    )
                    bullet_group.add(bullet)
                    all_sprites.add(bullet)
            elif self.power_level >= 2:
                # Dual shot
                for offset in [-15, 15]:
                    bullet = Bullet(
                        self.position.x + offset,
                        self.position.y - 20,
                        damage=damage
                    )
                    bullet_group.add(bullet)
                    all_sprites.add(bullet)
            else:
                # Single shot
                bullet = Bullet(
                    self.position.x,
                    self.position.y - 30,
                    damage=damage
                )
                bullet_group.add(bullet)
                all_sprites.add(bullet)
            
            # Play shoot sound with variation
            sound = random.choice(self.shoot_sounds)
            sound.play()
            
            # Muzzle flash effect
            self._create_muzzle_flash()
            
            return True
        return False
    
    def _create_muzzle_flash(self):
        """Creates a muzzle flash effect when shooting."""
        for _ in range(5):
            angle = random.uniform(math.pi * 0.75, math.pi * 1.25)
            speed = random.uniform(3, 6)
            
            self.energy_trails.append({
                "position": pygame.math.Vector2(
                    self.position.x,
                    self.position.y - 30
                ),
                "velocity": pygame.math.Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                ),
                "life": random.uniform(0.2, 0.5),
                "size": random.uniform(2, 4),
                "color": MUZZLE_FLASH,
                "growth_rate": 0.5
            })
    
    def take_damage(self, amount: int) -> bool:
        """Applies damage to the player with invulnerability frames and 4-damage-per-life system.
        Returns True if player died (lives <= 0), False otherwise."""
        current_time = pygame.time.get_ticks()
        
        # Check if vulnerable
        if current_time - self.last_damage_time > 2000:  # 2 second cooldown
            self.health -= amount
            self.last_damage_time = current_time
            self.invulnerable_time = 120  # 2 seconds at 60 FPS
            
            # Play damage sound
            self.damage_sound.play()
            
            # Create hit effect
            self._create_hit_effect()
            
            # Check for life loss (4 damage = 1 life lost)
            if self.health <= 0:
                self.lives -= 1
                
                # Check for game over FIRST
                if self.lives <= 0:
                    self.kill()
                    self._create_death_explosion()
                    return True  # Player died - game over
                else:
                    # Player continues with new life
                    self.health = self.max_health  # Reset to full health (4 points)
                    # Brief invulnerability after losing a life
                    self.invulnerable_time = 240  # 4 seconds of invulnerability
            
            return False  # Player survived
        return False  # No damage taken
    
    def _create_hit_effect(self):
        """Creates visual effects when player is hit."""
        # Play damage sound
        damage_sound = self.sound.get_sound("player_hit")
        damage_sound.play()
        
        # Damage particles
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            
            self.damage_particles.append({
                "position": pygame.math.Vector2(self.position),
                "velocity": pygame.math.Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                ),
                "life": random.uniform(0.5, 1.0),
                "size": random.uniform(3, 6),
                "color": random.choice([DAMAGE_RED, DAMAGE_ORANGE]),
                "growth_rate": 0.8
            })
    
    def _create_death_explosion(self):
        """Creates an explosion effect when player dies."""
        # Large explosion
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            
            self.damage_particles.append({
                "position": pygame.math.Vector2(self.position),
                "velocity": pygame.math.Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                ),
                "life": random.uniform(1.0, 2.0),
                "size": random.uniform(5, 10),
                "color": random.choice([DAMAGE_RED, DAMAGE_ORANGE, DAMAGE_YELLOW]),
                "growth_rate": 0.9
            })
        
        # Play explosion sound
        explosion_sound = self.sound.get_sound("explosion_large")
        explosion_sound.play()
    
    def apply_powerup(self, powerup_type: str):
        """Applies a power-up effect to the player."""
        current_time = pygame.time.get_ticks()
        self.powerup_sound.play()
        
        if powerup_type == "health":
            self.health = min(self.max_health, self.health + 50)
        elif powerup_type == "rapid_fire":
            self.rapid_fire_timer = current_time + self.RAPID_FIRE_DURATION
        elif powerup_type == "damage_boost":
            self.damage_boost_timer = current_time + self.DAMAGE_BOOST_DURATION
        elif powerup_type == "shield":
            self.shield_timer = current_time + self.SHIELD_DURATION
        elif powerup_type == "speed_boost":
            self.speed_boost_timer = current_time + self.SPEED_BOOST_DURATION
        elif powerup_type == "power_level":
            self.power_level = min(3, self.power_level + 1)
    
    def draw_particles(self, surface: pygame.Surface, offset: Tuple[float, float] = (0, 0)):
        """Draws all particle effects."""
        # Engine particles
        for p in self.engine_particles:
            alpha = int(255 * (p["life"] / 1.5))
            size = int(p["size"])
            color = (*p["color"], alpha)
            
            # Glow effect
            for i in range(2, 0, -1):
                glow_size = size + i
                glow_alpha = alpha // (i + 1)
                glow_color = (*p["color"], glow_alpha)
                pygame.draw.circle(
                    surface, 
                    glow_color, 
                    (int(p["position"].x + offset[0]), 
                     int(p["position"].y + offset[1])), 
                    glow_size
                )
            
            # Main particle
            pygame.draw.circle(
                surface, 
                color, 
                (int(p["position"].x + offset[0]), 
                 int(p["position"].y + offset[1])), 
                size
            )
        
        # Damage particles
        for p in self.damage_particles:
            alpha = int(255 * (p["life"] / 1.0))
            size = int(p["size"])
            color = (*p["color"], alpha)
            
            pygame.draw.circle(
                surface, 
                color, 
                (int(p["position"].x + offset[0]), 
                 int(p["position"].y + offset[1])), 
                size
            )
        
        # Energy trails
        for trail in self.energy_trails:
            alpha = int(255 * (trail["life"] / 0.5))
            size = int(trail["size"])
            color = (*trail["color"], alpha)
            
            pygame.draw.circle(
                surface, 
                color, 
                (int(trail["position"].x + offset[0]), 
                 int(trail["position"].y + offset[1])), 
                size
            )
    
    @property
    def invulnerable(self) -> bool:
        """Check if player is currently invulnerable."""
        return self.invulnerable_time > 0