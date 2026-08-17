import pygame
import random
import math
from typing import List, Dict, Tuple, Optional
from settings import *
from utils import load_sound, particle_explosion, bezier_curve

class PowerUp(pygame.sprite.Sprite):
    """Next-generation power-up system with dynamic effects and behaviors."""
    
    # Class-level assets cache
    _textures_loaded = False
    _powerup_textures = {}
    _sound_effects = {}
    
    def __init__(self, powerup_type: str, position: Optional[Tuple[int, int]] = None):
        super().__init__()
        self._load_shared_assets()
        
        # Core properties
        self.type = powerup_type
        self.lifetime = 0
        self.max_lifetime = 15000  # 15 seconds
        self.collected = False
        self.animation_time = 0
        self.float_offset = random.uniform(0, 2 * math.pi)
        
        # Physics
        self.position = pygame.math.Vector2(position if position else self._random_spawn_position())
        self.velocity = pygame.math.Vector2(0, random.uniform(0.5, 1.5))
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        
        # Visual effects
        self.particles = []
        self.energy_rings = []
        self.sparkles = []
        self.trail = []
        
        # Configure based on type
        self._configure_powerup()
        
        # Set up sprite
        self._setup_sprite()
        
        # Sound
        self.collect_sound = PowerUp._sound_effects["collect"]
        self.hum_sound = PowerUp._sound_effects["hum"]
        self.hum_sound.play(-1)  # Loop continuously
        
    def _load_shared_assets(self):
        """Loads assets shared across all power-up instances."""
        if not PowerUp._textures_loaded:
            # Load textures for each power-up type
            PowerUp._powerup_textures = {
                "health": self._create_texture("health"),
                "attack": self._create_texture("attack"),
                "shield": self._create_texture("shield"),
                "rapid": self._create_texture("rapid"),
                "mega": self._create_texture("mega")
            }
            
            # Load sounds
            PowerUp._sound_effects = {
                "collect": load_sound("powerup_collect.wav"),
                "hum": load_sound("powerup_hum.wav", volume=0.3)
            }
            
            PowerUp._textures_loaded = True
    
    def _create_texture(self, powerup_type: str) -> pygame.Surface:
        """Creates a procedurally generated texture for the power-up."""
        size = (64, 64)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        glow_surface = pygame.Surface(size, pygame.SRCALPHA)
        
        if powerup_type == "health":
            self._draw_health_icon(surface, glow_surface)
        elif powerup_type == "attack":
            self._draw_attack_icon(surface, glow_surface)
        elif powerup_type == "shield":
            self._draw_shield_icon(surface, glow_surface)
        elif powerup_type == "rapid":
            self._draw_rapid_icon(surface, glow_surface)
        elif powerup_type == "mega":
            self._draw_mega_icon(surface, glow_surface)
        
        # Combine base and glow layers
        surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)
        return surface
    
    def _draw_health_icon(self, base: pygame.Surface, glow: pygame.Surface):
        """Draws the health power-up icon."""
        # Cross shape
        cross_rects = [
            pygame.Rect(22, 10, 20, 44),
            pygame.Rect(10, 22, 44, 20)
        ]
        
        # Outer glow
        for rect in cross_rects:
            pygame.draw.rect(glow, (*HEALTH_GLOW, 150), rect, border_radius=3)
        
        # Main cross
        for rect in cross_rects:
            pygame.draw.rect(base, HEALTH_COLOR, rect.inflate(-8, -8), border_radius=2)
        
        # Inner highlight
        for rect in cross_rects:
            pygame.draw.rect(base, HEALTH_HIGHLIGHT, rect.inflate(-12, -12))
        
        # Pulsing core
        pygame.draw.rect(glow, (*HEALTH_CORE, 200), (28, 16, 8, 32))
        pygame.draw.rect(glow, (*HEALTH_CORE, 200), (16, 28, 32, 8))
    
    def _draw_attack_icon(self, base: pygame.Surface, glow: pygame.Surface):
        """Draws the attack power-up icon."""
        center = (32, 32)
        
        # Star shape
        star_points = []
        for i in range(8):
            angle = (2 * math.pi * i) / 8
            radius = 24 if i % 2 == 0 else 16
            star_points.append((
                center[0] + radius * math.cos(angle),
                center[1] + radius * math.sin(angle)
            ))
        
        # Glow effect
        pygame.draw.polygon(glow, (*ATTACK_GLOW, 150), star_points)
        
        # Main star
        pygame.draw.polygon(base, ATTACK_COLOR, star_points)
        
        # Inner circle
        pygame.draw.circle(glow, (*ATTACK_CORE, 200), center, 10)
        pygame.draw.circle(base, ATTACK_HIGHLIGHT, center, 6)
    
    def _draw_shield_icon(self, base: pygame.Surface, glow: pygame.Surface):
        """Draws the shield power-up icon."""
        center = (32, 32)
        
        # Shield shape
        shield_points = [
            (center[0], center[1] - 20),
            (center[0] + 15, center[1] - 10),
            (center[0] + 18, center[1] + 10),
            (center[0], center[1] + 20),
            (center[0] - 18, center[1] + 10),
            (center[0] - 15, center[1] - 10)
        ]
        
        # Glow effect
        pygame.draw.polygon(glow, (*SHIELD_GLOW, 150), shield_points)
        
        # Main shield
        pygame.draw.polygon(base, SHIELD_COLOR, shield_points)
        
        # Inner design
        inner_points = [
            (center[0], center[1] - 12),
            (center[0] + 9, center[1] - 6),
            (center[0] + 10, center[1] + 6),
            (center[0], center[1] + 12),
            (center[0] - 10, center[1] + 6),
            (center[0] - 9, center[1] - 6)
        ]
        pygame.draw.polygon(glow, (*SHIELD_CORE, 200), inner_points)
    
    def _draw_rapid_icon(self, base: pygame.Surface, glow: pygame.Surface):
        """Draws the rapid fire power-up icon."""
        # Lightning bolt shape
        bolt_points = [
            (32, 10), (42, 20), (30, 20),
            (42, 40), (32, 50), (22, 40),
            (34, 40), (22, 20), (32, 20)
        ]
        
        # Glow effect
        pygame.draw.polygon(glow, (*RAPID_GLOW, 150), bolt_points)
        
        # Main bolt
        pygame.draw.polygon(base, RAPID_COLOR, bolt_points)
        
        # Inner highlights
        pygame.draw.line(base, RAPID_HIGHLIGHT, (32, 15), (38, 25), 3)
        pygame.draw.line(base, RAPID_HIGHLIGHT, (26, 35), (32, 45), 3)
    
    def _draw_mega_icon(self, base: pygame.Surface, glow: pygame.Surface):
        """Draws the mega power-up icon."""
        center = (32, 32)
        
        # Complex layered star
        for layer in range(3):
            points = []
            for i in range(12):
                angle = (2 * math.pi * i) / 12
                radius = 24 - layer * 6 if i % 2 == 0 else 16 - layer * 4
                points.append((
                    center[0] + radius * math.cos(angle),
                    center[1] + radius * math.sin(angle)
                ))
            
            if layer == 0:
                pygame.draw.polygon(glow, (*MEGA_GLOW, 150), points)
            pygame.draw.polygon(base, MEGA_COLORS[layer], points)
        
        # Pulsing core
        pygame.draw.circle(glow, (*MEGA_CORE, 200), center, 8)
        pygame.draw.circle(base, WHITE, center, 4)
    
    def _configure_powerup(self):
        """Sets up properties based on power-up type."""
        self.config = {
            "health": {
                "color": HEALTH_COLOR,
                "glow": HEALTH_GLOW,
                "value": 2,  # Restore 2 health points (half a life in 4-damage system)
                "size": 1.0
            },
            "attack": {
                "color": ATTACK_COLOR,
                "glow": ATTACK_GLOW,
                "value": 2,
                "size": 1.1
            },
            "shield": {
                "color": SHIELD_COLOR,
                "glow": SHIELD_GLOW,
                "value": 15,
                "size": 1.0
            },
            "rapid": {
                "color": RAPID_COLOR,
                "glow": RAPID_GLOW,
                "value": 10,
                "size": 1.05
            },
            "mega": {
                "color": MEGA_COLORS[0],
                "glow": MEGA_GLOW,
                "value": 0,
                "size": 1.2
            }
        }.get(self.type)
        
        # Set rarity-based properties
        self.rarity = {
            "health": 1,
            "attack": 2,
            "shield": 2,
            "rapid": 3,
            "mega": 5
        }.get(self.type, 1)
    
    def _setup_sprite(self):
        """Initializes the sprite's visual appearance."""
        self.base_image = PowerUp._powerup_textures[self.type]
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)
        
        # Scale based on rarity
        self.base_scale = self.config["size"]
        self.current_scale = self.base_scale
    
    def _random_spawn_position(self) -> Tuple[int, int]:
        """Generates a random spawn position near the top of the screen."""
        return (
            random.randint(100, WIDTH - 100),
            random.randint(-200, -100)
        )
    
    def update(self, dt: float):
        """Updates the power-up's state."""
        self.lifetime += dt * 1000  # Convert to milliseconds
        self.animation_time += dt
        
        # Remove if expired
        if self.lifetime > self.max_lifetime:
            self.kill()
            return
        
        # Physics update
        self._update_physics(dt)
        
        # Visual effects
        self._update_visuals(dt)
        
        # Sound effect volume based on distance to player
        self._update_sound()
    
    def _update_physics(self, dt: float):
        """Updates the power-up's physical movement."""
        # Apply floating motion
        float_offset = 5 * math.sin(self.animation_time * 2 + self.float_offset)
        self.position.y += self.velocity.y * dt * 60
        self.position.x += float_offset * 0.1 * dt * 60
        
        # Apply rotation
        self.rotation += self.rotation_speed * dt * 60
        
        # Update rect position
        self.rect.center = self.position
        
        # Screen wrapping
        if self.rect.left > WIDTH:
            self.rect.right = 0
            self.position.x = self.rect.centerx
        elif self.rect.right < 0:
            self.rect.left = WIDTH
            self.position.x = self.rect.centerx
        
        # Create movement trail
        if random.random() < 0.5 * dt * 60:
            self.trail.append({
                "position": pygame.math.Vector2(self.position),
                "life": random.uniform(0.5, 1.0),
                "size": random.uniform(3, 6),
                "color": self.config["color"]
            })
    
    def _update_visuals(self, dt: float):
        """Updates all visual effects and animations."""
        # Pulsing scale animation
        pulse = 1 + 0.1 * math.sin(self.animation_time * 5)
        self.current_scale = self.base_scale * pulse
        
        # Rotate and scale the image
        scaled_size = (
            int(self.base_image.get_width() * self.current_scale),
            int(self.base_image.get_height() * self.current_scale)
        )
        scaled_image = pygame.transform.scale(self.base_image, scaled_size)
        self.image = pygame.transform.rotate(scaled_image, self.rotation)
        
        # Update rect while preserving center
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
        # Create energy particles
        self._create_particles(dt)
        
        # Update all particle systems
        self._update_particles(dt)
    
    def _create_particles(self, dt: float):
        """Creates visual effect particles."""
        # Energy particles
        if random.random() < 0.8 * dt * 60:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(15, 30)
            
            self.particles.append({
                "position": pygame.math.Vector2(
                    self.position.x + math.cos(angle) * distance,
                    self.position.y + math.sin(angle) * distance
                ),
                "velocity": pygame.math.Vector2(
                    math.cos(angle + math.pi) * random.uniform(0.5, 1.5),
                    math.sin(angle + math.pi) * random.uniform(0.5, 1.5)
                ),
                "life": random.uniform(0.5, 1.0),
                "max_life": 1.0,
                "size": random.uniform(2, 4),
                "color": random.choice([
                    self.config["color"],
                    self.config["glow"],
                    WHITE
                ]),
                "growth_rate": random.uniform(0.8, 1.2)
            })
        
        # Energy rings
        if random.random() < 0.3 * dt * 60:
            self.energy_rings.append({
                "radius": 10,
                "max_radius": random.uniform(40, 60),
                "life": random.uniform(0.5, 1.0),
                "max_life": 1.0,
                "color": self.config["glow"],
                "thickness": random.randint(1, 3)
            })
        
        # Sparkles
        if random.random() < 0.6 * dt * 60:
            self.sparkles.append({
                "position": pygame.math.Vector2(
                    self.position.x + random.uniform(-20, 20),
                    self.position.y + random.uniform(-20, 20)
                ),
                "life": random.uniform(0.3, 0.6),
                "max_life": 0.6,
                "size": random.uniform(1, 2),
                "color": WHITE,
                "speed": random.uniform(1, 2)
            })
    
    def _update_particles(self, dt: float):
        """Updates all particle systems."""
        # Update energy particles
        for p in self.particles[:]:
            p["life"] -= dt
            p["position"] += p["velocity"] * dt * 60
            p["size"] *= p["growth_rate"] ** (dt * 60)
            
            if p["life"] <= 0:
                self.particles.remove(p)
        
        # Update energy rings
        for ring in self.energy_rings[:]:
            ring["life"] -= dt
            ring["radius"] += (ring["max_radius"] - ring["radius"]) * 0.1 * dt * 60
            
            if ring["life"] <= 0:
                self.energy_rings.remove(ring)
        
        # Update sparkles
        for sparkle in self.sparkles[:]:
            sparkle["life"] -= dt
            sparkle["position"].y += sparkle["speed"] * dt * 60
            
            if sparkle["life"] <= 0:
                self.sparkles.remove(sparkle)
        
        # Update trail
        for segment in self.trail[:]:
            segment["life"] -= dt
            segment["size"] *= 0.9 ** (dt * 60)
            
            if segment["life"] <= 0:
                self.trail.remove(segment)
    
    def _update_sound(self):
        """Updates sound effects based on game state."""
        # Implement distance-based volume if needed
        pass
    
    def collect(self) -> Dict[str, int]:
        """Handles collection of the power-up."""
        if self.collected:
            return {}
            
        self.collected = True
        self.collect_sound.play()
        self.hum_sound.stop()
        
        # Create collection effect
        self._create_collection_effect()
        
        # Return power-up effect
        return {
            "type": self.type,
            "value": self.config["value"],
            "rarity": self.rarity
        }
    
    def _create_collection_effect(self):
        """Creates visual effects when collected."""
        # Large explosion of particles
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            
            self.particles.append({
                "position": pygame.math.Vector2(self.position),
                "velocity": pygame.math.Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                ),
                "life": random.uniform(0.5, 1.5),
                "size": random.uniform(3, 6),
                "color": random.choice([
                    self.config["color"],
                    self.config["glow"],
                    WHITE
                ]),
                "growth_rate": random.uniform(0.8, 1.2)
            })
        
        # Energy wave
        for _ in range(5):
            self.energy_rings.append({
                "radius": 5,
                "max_radius": random.uniform(60, 100),
                "life": random.uniform(0.8, 1.2),
                "color": self.config["glow"],
                "thickness": random.randint(2, 4)
            })
        
        # Mark for removal
        self.kill()
    
    def apply(self, player):
        """Apply power-up effects to the player."""
        if self.collected:
            return
            
        # Collect the power-up first
        effect = self.collect()
        if not effect:
            return
            
        # Apply effects based on power-up type
        if self.type == "health":
            # Restore health (4 health = 1 life, so restore significant amount)
            if hasattr(player, 'health') and hasattr(player, 'max_health'):
                # Restore 2 damage points (half a life's worth)
                old_health = player.health
                player.health = min(player.health + effect["value"], player.max_health)
                print(f"Health restored: {old_health} -> {player.health}")
            elif hasattr(player, 'lives'):
                # If no health system, add a life directly (but this shouldn't happen)
                player.lives = min(player.lives + 1, 3)  # Max 3 lives to match heart display
                
        elif self.type == "attack":
            # Increase attack power temporarily
            if hasattr(player, 'attack_power'):
                player.attack_power = min(player.attack_power + effect["value"], 10)
            if hasattr(player, 'power_up_timer'):
                player.power_up_timer = 8000  # 8 seconds
                
        elif self.type == "shield":
            # Activate shield
            if hasattr(player, 'shield_active'):
                player.shield_active = True
            if hasattr(player, 'shield_timer'):
                player.shield_timer = 12000  # 12 seconds
                
        elif self.type == "rapid":
            # Increase fire rate
            if hasattr(player, 'fire_rate_multiplier'):
                player.fire_rate_multiplier = 3.0
            if hasattr(player, 'rapid_fire_timer'):
                player.rapid_fire_timer = 10000  # 10 seconds
                
        elif self.type == "mega":
            # Ultimate power-up - multiple effects
            if hasattr(player, 'health') and hasattr(player, 'max_health'):
                player.health = player.max_health  # Full health restoration
            if hasattr(player, 'lives'):
                # Only add life if not already at maximum (3 lives)
                if player.lives < 3:
                    player.lives = min(player.lives + 1, 3)  # Add 1 life (max 3)
                    print(f"Extra life! Lives: {player.lives}/3")
                else:
                    print("Already at maximum lives (3/3)")
                    # Give extra score instead of life when already at max
                    return {"score_bonus": 1000}
            if hasattr(player, 'attack_power'):
                player.attack_power = 10
            if hasattr(player, 'shield_active'):
                player.shield_active = True
            if hasattr(player, 'fire_rate_multiplier'):
                player.fire_rate_multiplier = 5.0
            if hasattr(player, 'mega_timer'):
                player.mega_timer = 15000  # 15 seconds
    
    def draw_effects(self, surface: pygame.Surface, offset: Tuple[float, float] = (0, 0)):
        """Draws all visual effects associated with the power-up."""
        # Draw trail first (behind power-up)
        for segment in self.trail:
            alpha = int(255 * (segment["life"] / 1.0))
            size = int(segment["size"])
            color = (*segment["color"], alpha)
            
            pygame.draw.circle(
                surface,
                color,
                (int(segment["position"].x + offset[0]), 
                 int(segment["position"].y + offset[1])),
                size
            )
        
        # Draw energy rings
        for ring in self.energy_rings:
            alpha = int(255 * (ring["life"] / ring["max_life"]))
            color = (*ring["color"], alpha)
            
            pygame.draw.circle(
                surface,
                color,
                (int(self.position.x + offset[0]), 
                 int(self.position.y + offset[1])),
                int(ring["radius"]),
                ring["thickness"]
            )
        
        # Draw particles
        for p in self.particles:
            alpha = int(255 * (p["life"] / p["max_life"]))
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
        
        # Draw sparkles
        for sparkle in self.sparkles:
            alpha = int(255 * (sparkle["life"] / sparkle["max_life"]))
            size = int(sparkle["size"])
            color = (*sparkle["color"], alpha)
            
            # Twinkling effect
            pos = (int(sparkle["position"].x + offset[0]), 
                   int(sparkle["position"].y + offset[1]))
            
            pygame.draw.line(
                surface, color,
                (pos[0] - size, pos[1]),
                (pos[0] + size, pos[1]),
                2
            )
            pygame.draw.line(
                surface, color,
                (pos[0], pos[1] - size),
                (pos[0], pos[1] + size),
                2
            )