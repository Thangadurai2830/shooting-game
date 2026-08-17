import pygame
import random
import math
from typing import List, Dict, Tuple, Optional
from settings import *
from utils import load_sound, bezier_curve

class Bullet(pygame.sprite.Sprite):
    """Advanced bullet system with smart targeting, weapon types, and cinematic effects."""
    
    # Class-wide texture cache
    _texture_cache = {}
    
    def __init__(self, 
                 x: float, 
                 y: float, 
                 weapon_type: str = "plasma", 
                 damage: int = 1,
                 target: Optional[pygame.sprite.Sprite] = None,
                 angle: float = -90):
        super().__init__()
        
        # Core properties
        self.weapon_type = weapon_type
        self.damage = damage
        self.lifetime = 0
        self.max_lifetime = 180  # 3 seconds at 60 FPS
        self.target = target
        self.angle = math.radians(angle)
        self.piercing = False
        
        # Physics
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.homing_strength = 0.0
        
        # Effects
        self.trail_particles: List[Dict] = []
        self.energy_field: List[Dict] = []
        self.impact_prediction = None
        self._init_weapon_properties()
        self._load_textures()
        
        # Audio
        self.fire_sound = load_sound(f"{weapon_type}_fire.wav")
        self.impact_sound = load_sound(f"{weapon_type}_impact.wav")
        self.fire_sound.play()
    
    def _init_weapon_properties(self):
        """Configures bullet behavior based on weapon type."""
        weapon_stats = {
            "plasma": {
                "speed": 12,
                "color": PLASMA_BLUE,
                "size": (8, 24),
                "homing": 0.3,
                "trail_density": 0.9,
                "glow_intensity": 1.5,
                "piercing": False
            },
            "laser": {
                "speed": 20,
                "color": LASER_RED,
                "size": (4, 40),
                "homing": 0.0,
                "trail_density": 0.6,
                "glow_intensity": 2.0,
                "piercing": True
            },
            "railgun": {
                "speed": 30,
                "color": ELECTRIC_CYAN,
                "size": (6, 30),
                "homing": 0.1,
                "trail_density": 0.7,
                "glow_intensity": 1.8,
                "piercing": True
            },
            "quantum": {
                "speed": 8,
                "color": QUANTUM_PURPLE,
                "size": (12, 12),
                "homing": 0.5,
                "trail_density": 1.0,
                "glow_intensity": 2.5,
                "piercing": False
            }
        }
        
        stats = weapon_stats.get(self.weapon_type, weapon_stats["plasma"])
        
        # Apply damage scaling
        damage_scale = 1 + (self.damage - 1) * 0.3
        self.velocity = pygame.math.Vector2(
            math.cos(self.angle) * stats["speed"] * damage_scale,
            math.sin(self.angle) * stats["speed"] * damage_scale
        )
        self.homing_strength = stats["homing"] * damage_scale
        self.piercing = stats["piercing"]
        
        # Visual properties
        self.base_color = stats["color"]
        self.size = stats["size"]
        self.trail_density = stats["trail_density"]
        self.glow_intensity = stats["glow_intensity"]
        
        # Special case for quantum bullets
        if self.weapon_type == "quantum":
            self.quantum_phase = random.uniform(0, 2 * math.pi)
    
    def _load_textures(self):
        """Preloads and caches bullet textures."""
        if self.weapon_type not in Bullet._texture_cache:
            # Generate procedural textures for each weapon type
            size = (max(self.size) * 3, max(self.size) * 3)
            texture = pygame.Surface(size, pygame.SRCALPHA)
            
            if self.weapon_type == "plasma":
                self._create_plasma_texture(texture)
            elif self.weapon_type == "laser":
                self._create_laser_texture(texture)
            elif self.weapon_type == "railgun":
                self._create_railgun_texture(texture)
            elif self.weapon_type == "quantum":
                self._create_quantum_texture(texture)
                
            Bullet._texture_cache[self.weapon_type] = texture
        
        self.texture = Bullet._texture_cache[self.weapon_type]
        self.image = self.texture  # Pygame sprites need image attribute
        self.rect = pygame.Rect(0, 0, *self.size)
        self.rect.center = (int(self.position.x), int(self.position.y))
        self.mask = pygame.mask.from_surface(self.texture)
    
    def _create_plasma_texture(self, surface):
        """Generates a plasma orb texture with energy tendrils."""
        center = (surface.get_width() // 2, surface.get_height() // 2)
        max_radius = min(self.size) // 2
        
        # Core glow
        for i in range(3, 0, -1):
            radius = max_radius * (0.3 + 0.7 * i/3)
            alpha = 200 - i * 50
            color = (*self.base_color[:3], alpha)
            pygame.draw.circle(surface, color, center, radius)
        
        # Energy tendrils
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(max_radius * 0.5, max_radius * 1.5)
            end_pos = (
                center[0] + math.cos(angle) * length,
                center[1] + math.sin(angle) * length
            )
            
            # Bezier curve for organic look
            control1 = (
                center[0] + math.cos(angle) * length * 0.3,
                center[1] + math.sin(angle) * length * 0.3
            )
            control2 = (
                center[0] + math.cos(angle + 0.5) * length * 0.6,
                center[1] + math.sin(angle + 0.5) * length * 0.6
            )
            
            points = bezier_curve(center, control1, control2, end_pos, 10)
            pygame.draw.lines(surface, (*self.base_color[:3], 150), False, points, 2)
    
    def _create_laser_texture(self, surface):
        """Creates a high-energy laser beam texture."""
        width, height = self.size
        center_x = surface.get_width() // 2
        
        # Core beam
        pygame.draw.rect(surface, WHITE, (center_x - width//2, 0, width, height))
        
        # Energy sheath
        for i in range(3, 0, -1):
            sheath_width = width + i * 2
            alpha = 100 - i * 20
            pygame.draw.rect(
                surface, 
                (*self.base_color[:3], alpha), 
                (center_x - sheath_width//2, 0, sheath_width, height)
            )
        
        # Tip glow
        tip_glow = pygame.Surface((width * 3, height // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(tip_glow, (*WHITE, 150), (0, 0, tip_glow.get_width(), tip_glow.get_height()))
        surface.blit(tip_glow, (center_x - tip_glow.get_width()//2, height - tip_glow.get_height()//2))
    
    def _create_railgun_texture(self, surface):
        """Generates a charged railgun projectile."""
        width, height = self.size
        center = (surface.get_width() // 2, surface.get_height() // 2)
        
        # Charged core
        pygame.draw.ellipse(surface, WHITE, (center[0] - width//2, center[1] - height//2, width, height))
        
        # Energy arcs
        for _ in range(6):
            start_angle = random.uniform(0, 2 * math.pi)
            end_angle = start_angle + random.uniform(-0.5, 0.5)
            start_radius = random.uniform(width//3, width//2)
            end_radius = random.uniform(width//1.5, width)
            
            start_pos = (
                center[0] + math.cos(start_angle) * start_radius,
                center[1] + math.sin(start_angle) * start_radius
            )
            end_pos = (
                center[0] + math.cos(end_angle) * end_radius,
                center[1] + math.sin(end_angle) * end_radius
            )
            
            pygame.draw.line(
                surface, 
                (*self.base_color[:3], 180), 
                start_pos, end_pos, 2
            )
    
    def _create_quantum_texture(self, surface):
        """Creates a quantum-entangled particle effect."""
        center = (surface.get_width() // 2, surface.get_height() // 2)
        radius = min(self.size) // 2
        
        # Quantum core
        pygame.draw.circle(surface, (*self.base_color[:3], 200), center, radius)
        
        # Probability waves
        for i in range(5):
            wave_radius = radius * (1 + i * 0.3)
            alpha = 80 - i * 15
            pygame.draw.circle(
                surface, 
                (*self.base_color[:3], alpha), 
                center, wave_radius, 1
            )
        
        # Entanglement particles
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(radius * 0.5, radius * 1.2)
            pos = (
                center[0] + math.cos(angle) * dist,
                center[1] + math.sin(angle) * dist
            )
            size = random.randint(1, 3)
            pygame.draw.circle(
                surface, 
                WHITE, 
                pos, size
            )
    
    def update(self, dt: float, enemies: pygame.sprite.Group):
        """Advanced physics update with homing and lifetime management."""
        self.lifetime += 1
        
        # Homing behavior
        if self.target and self.homing_strength > 0:
            if not self.target.alive():
                self.target = self._find_new_target(enemies)
            
            if self.target:
                target_vec = pygame.math.Vector2(self.target.rect.center) - self.position
                if target_vec.length() > 0:
                    target_vec = target_vec.normalize() * self.velocity.length()
                    self.velocity = self.velocity.lerp(target_vec, self.homing_strength * dt * 60)
        
        # Apply acceleration
        self.velocity += self.acceleration * dt * 60
        self.position += self.velocity * dt * 60
        
        # Update rect position
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        # Quantum bullet phase shifting
        if self.weapon_type == "quantum":
            self.quantum_phase += 0.1 * dt * 60
            self.position.x += math.sin(self.quantum_phase) * 2
            self.position.y += math.cos(self.quantum_phase * 0.7) * 1.5
        
        # Generate trail effects
        self._generate_trail(dt)
        
        # Predict impact point for leading shots
        if self.target and random.random() < 0.05:
            self._calculate_impact_prediction()
        
        # Expire if lifetime exceeded
        if self.lifetime > self.max_lifetime:
            self.kill()
    
    def _find_new_target(self, enemies: pygame.sprite.Group) -> Optional[pygame.sprite.Sprite]:
        """Finds the most threatening target within seek radius."""
        closest = None
        min_dist = 300  # Homing seek range
        
        for enemy in enemies:
            dist_vec = pygame.math.Vector2(enemy.rect.center) - self.position
            dist = dist_vec.length()
            
            if dist < min_dist:
                min_dist = dist
                closest = enemy
                
        return closest
    
    def _calculate_impact_prediction(self):
        """Predicts where the bullet will hit the target."""
        if not self.target:
            self.impact_prediction = None
            return
            
        # Simple linear prediction
        target_pos = pygame.math.Vector2(self.target.rect.center)
        target_vel = pygame.math.Vector2(self.target.velocity) if hasattr(self.target, 'velocity') else pygame.math.Vector2(0, 0)
        
        rel_pos = target_pos - self.position
        rel_vel = target_vel - self.velocity
        
        if rel_vel.length_squared() == 0:
            self.impact_prediction = None
            return
            
        # Time of closest approach
        tca = rel_pos.dot(rel_vel) / rel_vel.length_squared()
        
        if tca < 0:
            self.impact_prediction = None
        else:
            self.impact_prediction = target_pos + target_vel * tca
    
    def _generate_trail(self, dt: float):
        """Creates advanced trail effects based on weapon type."""
        # Base trail particles
        if random.random() < self.trail_density * dt * 60:
            self._add_trail_particles()
        
        # Special weapon effects
        if self.weapon_type == "plasma":
            self._add_plasma_effects(dt)
        elif self.weapon_type == "railgun":
            self._add_railgun_effects(dt)
        elif self.weapon_type == "quantum":
            self._add_quantum_effects(dt)
        
        # Update all particles
        self._update_particles(dt)
    
    def _add_trail_particles(self):
        """Adds base trail particles with physics."""
        num_particles = {
            "plasma": 3,
            "laser": 1,
            "railgun": 2,
            "quantum": 4
        }.get(self.weapon_type, 1)
        
        for _ in range(num_particles):
            angle_variation = random.uniform(-0.3, 0.3)
            particle_angle = math.atan2(self.velocity.y, self.velocity.x) + math.pi + angle_variation
            
            self.trail_particles.append({
                "position": pygame.math.Vector2(self.position),
                "velocity": pygame.math.Vector2(
                    math.cos(particle_angle) * random.uniform(0.5, 2.0),
                    math.sin(particle_angle) * random.uniform(0.5, 2.0)
                ),
                "life": random.uniform(0.3, 0.8),
                "max_life": 1.0,
                "size": random.uniform(2, 5),
                "color": random.choice([
                    self.base_color,
                    (*self.base_color[:3], 180),
                    WHITE
                ]),
                "growth_rate": random.uniform(0.5, 1.5)
            })
    
    def _add_plasma_effects(self, dt: float):
        """Adds plasma-specific energy flares."""
        if random.random() < 0.4 * dt * 60:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(5, 15)
            
            self.energy_field.append({
                "position": pygame.math.Vector2(
                    self.position.x + math.cos(angle) * distance,
                    self.position.y + math.sin(angle) * distance
                ),
                "life": random.uniform(0.2, 0.5),
                "max_life": 1.0,
                "size": random.uniform(3, 8),
                "color": (*self.base_color[:3], 180),
                "angle": angle,
                "rotation_speed": random.uniform(-5, 5)
            })
    
    def _add_railgun_effects(self, dt: float):
        """Adds railgun-specific energy arcs."""
        if random.random() < 0.3 * dt * 60 and len(self.trail_particles) > 2:
            # Create an energy arc between two trail particles
            p1, p2 = random.sample(self.trail_particles, 2)
            self.energy_field.append({
                "type": "arc",
                "positions": [p1["position"].copy(), p2["position"].copy()],
                "life": random.uniform(0.3, 0.6),
                "max_life": 1.0,
                "width": random.uniform(1, 3),
                "color": (*self.base_color[:3], 150)
            })
    
    def _add_quantum_effects(self, dt: float):
        """Adds quantum entanglement effects."""
        if random.random() < 0.5 * dt * 60:
            # Create quantum echo particles
            for _ in range(2):
                self.trail_particles.append({
                    "position": pygame.math.Vector2(self.position),
                    "velocity": pygame.math.Vector2(
                        random.uniform(-1, 1),
                        random.uniform(-1, 1)
                    ),
                    "life": random.uniform(0.5, 1.5),
                    "max_life": 2.0,
                    "size": random.uniform(1, 3),
                    "color": (*QUANTUM_PURPLE[:3], 200),
                    "quantum_phase": random.uniform(0, 2 * math.pi)
                })
    
    def _update_particles(self, dt: float):
        """Updates all particle systems with physics."""
        # Update trail particles
        for p in self.trail_particles[:]:
            p["life"] -= 0.02 * dt * 60
            p["position"] += p["velocity"] * dt * 60
            p["size"] *= p["growth_rate"] ** (dt * 60)
            
            if p["life"] <= 0:
                self.trail_particles.remove(p)
        
        # Update energy field
        for ef in self.energy_field[:]:
            ef["life"] -= 0.03 * dt * 60
            
            if ef.get("type") == "arc":
                # Update arc endpoints
                for pos in ef["positions"]:
                    pos += self.velocity * -0.2 * dt * 60
            else:
                # Update orb position and rotation
                ef["position"] += self.velocity * -0.1 * dt * 60
                ef["angle"] += ef.get("rotation_speed", 0) * dt * 60
                ef["size"] *= 0.95 ** (dt * 60)
            
            if ef["life"] <= 0:
                self.energy_field.remove(ef)
    
    def draw(self, screen: pygame.Surface, offset: Tuple[float, float] = (0, 0)):
        """Renders the bullet with all effects."""
        # Draw impact prediction
        if self.impact_prediction and self.weapon_type == "railgun":
            self._draw_impact_prediction(screen, offset)
        
        # Draw energy field first (behind bullet)
        self._draw_energy_field(screen, offset)
        
        # Draw trail particles
        self._draw_trail_particles(screen, offset)
        
        # Draw the bullet
        self._draw_bullet(screen, offset)
    
    def _draw_impact_prediction(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """Draws the predicted impact point for homing bullets."""
        screen_pos = (self.impact_prediction.x + offset[0], self.impact_prediction.y + offset[1])
        
        # Pulsing target reticle
        pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.005)
        size = 15 * pulse
        
        # Outer ring
        pygame.draw.circle(
            screen, 
            (*self.base_color[:3], 150), 
            (int(screen_pos[0]), int(screen_pos[1])), 
            int(size), 2
        )
        
        # Inner crosshair
        pygame.draw.line(
            screen, WHITE,
            (screen_pos[0] - size * 0.7, screen_pos[1]),
            (screen_pos[0] + size * 0.7, screen_pos[1]), 2
        )
        pygame.draw.line(
            screen, WHITE,
            (screen_pos[0], screen_pos[1] - size * 0.7),
            (screen_pos[0], screen_pos[1] + size * 0.7), 2
        )
    
    def _draw_energy_field(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """Renders all energy field effects."""
        for ef in self.energy_field:
            alpha = int(255 * (ef["life"] / ef["max_life"]))
            
            if ef.get("type") == "arc":
                # Draw energy arc
                points = [
                    (p.x + offset[0], p.y + offset[1])
                    for p in ef["positions"]
                ]
                
                # Draw multiple passes for glow effect
                for i in range(3, 0, -1):
                    width = ef["width"] + i
                    color = (*ef["color"][:3], alpha // (i + 1))
                    pygame.draw.line(screen, color, points[0], points[1], width)
            else:
                # Draw energy orb
                pos = (ef["position"].x + offset[0], ef["position"].y + offset[1])
                
                # Glow effect
                for i in range(3, 0, -1):
                    glow_size = ef["size"] + i * 2
                    glow_alpha = alpha // (i * 2)
                    pygame.draw.circle(
                        screen, 
                        (*ef["color"][:3], glow_alpha), 
                        (int(pos[0]), int(pos[1])), 
                        int(glow_size)
                    )
                
                # Main orb
                pygame.draw.circle(
                    screen, 
                    (*ef["color"][:3], alpha), 
                    (int(pos[0]), int(pos[1])), 
                    int(ef["size"])
                )
    
    def _draw_trail_particles(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """Renders all trail particles with advanced effects."""
        for p in self.trail_particles:
            alpha = int(255 * (p["life"] / p["max_life"]))
            pos = (p["position"].x + offset[0], p["position"].y + offset[1])
            size = p["size"]
            
            if "quantum_phase" in p:
                # Quantum particle special rendering
                phase = p["quantum_phase"] + pygame.time.get_ticks() * 0.001
                wave_size = size * (1 + 0.3 * math.sin(phase * 3))
                
                pygame.draw.circle(
                    screen, 
                    (*p["color"][:3], alpha), 
                    (int(pos[0]), int(pos[1])), 
                    int(wave_size)
                )
                
                # Entanglement connection lines
                if random.random() < 0.3:
                    other_pos = random.choice([
                        (self.position.x + offset[0], self.position.y + offset[1]),
                        *[(tp["position"].x + offset[0], tp["position"].y + offset[1]) 
                          for tp in self.trail_particles if tp != p]
                    ])
                    
                    pygame.draw.line(
                        screen, 
                        (*QUANTUM_PURPLE[:3], alpha // 2), 
                        (int(pos[0]), int(pos[1])), 
                        other_pos, 
                        1
                    )
            else:
                # Standard particle rendering
                # Glow effect
                for i in range(2, 0, -1):
                    glow_size = size + i
                    glow_alpha = alpha // (i + 1)
                    pygame.draw.circle(
                        screen, 
                        (*p["color"][:3], glow_alpha), 
                        (int(pos[0]), int(pos[1])), 
                        int(glow_size)
                    )
                
                # Core particle
                pygame.draw.circle(
                    screen, 
                    (*p["color"][:3], alpha), 
                    (int(pos[0]), int(pos[1])), 
                    int(size)
                )
    
    def _draw_bullet(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """Renders the bullet itself with proper rotation and effects."""
        # Calculate rotation angle from velocity
        angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x)) - 90
        
        # Special case for quantum bullets - phase shifting
        if self.weapon_type == "quantum":
            phase = pygame.time.get_ticks() * 0.005
            size_scale = 1 + 0.2 * math.sin(phase * 3)
            alpha = 200 + int(55 * math.sin(phase * 2))
            
            # Create temporary surface with current phase
            bullet_surf = pygame.Surface((self.size[0] * 3, self.size[1] * 3), pygame.SRCALPHA)
            self._create_quantum_texture(bullet_surf)  # Recreate with current phase
            
            # Scale and rotate
            scaled_size = (
                int(self.size[0] * size_scale),
                int(self.size[1] * size_scale)
            )
            bullet_surf = pygame.transform.scale(bullet_surf, scaled_size)
            rotated_bullet = pygame.transform.rotate(bullet_surf, angle)
        else:
            # Standard bullet rendering
            rotated_bullet = pygame.transform.rotate(self.texture, angle)
        
        # Calculate position with offset
        screen_pos = (
            self.position.x + offset[0] - rotated_bullet.get_width() // 2,
            self.position.y + offset[1] - rotated_bullet.get_height() // 2
        )
        
        # Add muzzle flash for new bullets
        if self.lifetime < 5:
            flash_size = 30 * (1 - self.lifetime / 5)
            flash_surf = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                flash_surf, 
                (*self.base_color[:3], 200), 
                (flash_size, flash_size), 
                flash_size
            )
            screen.blit(
                flash_surf,
                (
                    self.position.x + offset[0] - flash_size,
                    self.position.y + offset[1] - flash_size
                ),
                special_flags=pygame.BLEND_ADD
            )
        
        # Draw the bullet
        screen.blit(rotated_bullet, screen_pos)
        
        # Add weapon-specific overlay effects
        if self.weapon_type == "plasma":
            self._draw_plasma_overlay(screen, offset)
        elif self.weapon_type == "railgun":
            self._draw_railgun_overlay(screen, offset)
    
    def _draw_plasma_overlay(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """Adds plasma-specific screen-space effects."""
        # Energy corona around bullet
        corona_size = 30 * (0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01))
        corona_surf = pygame.Surface((corona_size * 2, corona_size * 2), pygame.SRCALPHA)
        
        # Radial gradient
        for i in range(10, 0, -1):
            radius = corona_size * (i / 10)
            alpha = 30 - i * 3
            pygame.draw.circle(
                corona_surf, 
                (*self.base_color[:3], alpha), 
                (corona_size, corona_size), 
                int(radius)
            )
        
        screen.blit(
            corona_surf,
            (
                self.position.x + offset[0] - corona_size,
                self.position.y + offset[1] - corona_size
            ),
            special_flags=pygame.BLEND_ADD
        )
    
    def _draw_railgun_overlay(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """Adds railgun-specific screen distortion."""
        # Create shockwave effect
        if random.random() < 0.3:
            shock_time = pygame.time.get_ticks() % 1000 / 1000
            shock_size = 50 * shock_time
            shock_alpha = int(100 * (1 - shock_time))
            
            pygame.draw.circle(
                screen, 
                (*self.base_color[:3], shock_alpha), 
                (
                    int(self.position.x + offset[0]),
                    int(self.position.y + offset[1])
                ), 
                int(shock_size), 
                2
            )
    
    def on_impact(self, target: Optional[pygame.sprite.Sprite] = None):
        """Handles impact effects and sound."""
        self.impact_sound.play()
        
        # Create impact explosion
        impact_particles = []
        
        if self.weapon_type == "plasma":
            # Plasma explosion
            for _ in range(30):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 5)
                
                impact_particles.append({
                    "position": pygame.math.Vector2(self.position),
                    "velocity": pygame.math.Vector2(
                        math.cos(angle) * speed,
                        math.sin(angle) * speed
                    ),
                    "life": random.uniform(0.5, 1.5),
                    "size": random.uniform(3, 8),
                    "color": (*self.base_color[:3], 200),
                    "growth_rate": 0.8
                })
        elif self.weapon_type == "railgun":
            # Railgun pierce effect
            if target:
                for _ in range(10):
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.uniform(0, target.rect.width // 2)
                    
                    impact_particles.append({
                        "position": pygame.math.Vector2(
                            target.rect.centerx + math.cos(angle) * dist,
                            target.rect.centery + math.sin(angle) * dist
                        ),
                        "velocity": pygame.math.Vector2(
                            math.cos(angle) * 2,
                            math.sin(angle) * 2
                        ),
                        "life": random.uniform(0.3, 0.8),
                        "size": random.uniform(2, 5),
                        "color": (*self.base_color[:3], 180),
                        "growth_rate": 1.2
                    })
        
        return impact_particles