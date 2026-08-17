import pygame
import sys
import random
import math
from typing import List, Dict, Tuple, Optional
from settings import (
    Engine, Colors, WIDTH, HEIGHT,
    NEON_BLUE, ELECTRIC_CYAN, NEON_GREEN, LASER_RED, GOLD, 
    ELECTRIC_PURPLE, SILVER, NEON_YELLOW, WHITE
)

# Import constants
FPS = Engine.FPS

# Import UI constants
UI_BLACK = Colors.UI_BLACK
UI_WHITE = Colors.UI_WHITE
UI_GRAY = Colors.UI_GRAY
UI_GREEN = Colors.UI_GREEN
UI_YELLOW = Colors.UI_YELLOW
UI_PURPLE = Colors.UI_PURPLE
UI_DARK_PURPLE = Colors.UI_DARK_PURPLE
from player import Player
from bullet import Bullet
from asteroid import Asteroid
from enemy import Enemy
from powerup import PowerUp
from utils import (
    load_highscore, save_highscore, 
    asset_manager, initialize_assets
)

# Simple implementations of missing classes
class GameFont:
    """Simple font manager with caching"""
    def __init__(self):
        self.font_cache = {}
    
    def get_font(self, font_type: str, size: int) -> pygame.font.Font:
        cache_key = f"{font_type}_{size}"
        if cache_key not in self.font_cache:
            # Use system fonts with fallback
            if font_type == "title":
                self.font_cache[cache_key] = pygame.font.SysFont("arial", size, bold=True)
            elif font_type == "hud":
                self.font_cache[cache_key] = pygame.font.SysFont("arial", size, bold=True)
            else:
                self.font_cache[cache_key] = pygame.font.SysFont("arial", size)
        return self.font_cache[cache_key]

class SoundSystem:
    """Simple sound system with fallback"""
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
    
    def play(self, sound_name: str):
        """Play a sound effect"""
        try:
            if sound_name in self.sounds:
                self.sounds[sound_name].play()
        except:
            pass  # Fail silently if sound system not working
    
    def play_music(self, music_name: str, loop: bool = False):
        """Play background music"""
        try:
            if not self.music_playing:
                self.music_playing = True
        except:
            pass
    
    def get_sound(self, sound_name: str):
        """Get a sound object (return dummy sound if not found)"""
        if sound_name in self.sounds:
            return self.sounds[sound_name]
        else:
            # Return a dummy sound that does nothing
            return DummySound()

class DummySound:
    """Dummy sound object that does nothing"""
    def play(self):
        pass
    
    def stop(self):
        pass
    
    def set_volume(self, volume):
        pass

class ParticleManager:
    """Simple particle manager"""
    def __init__(self):
        self.particles = []
    
    def update(self, dt: float):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def render(self, surface: pygame.Surface):
        """Render all particles"""
        for particle in self.particles:
            if particle['life'] > 0:
                # Ensure color is RGB (3 values) not RGBA (4 values)
                color = particle['color'][:3] if len(particle['color']) > 3 else particle['color']
                pos = (int(particle['x']), int(particle['y']))
                pygame.draw.circle(surface, color, pos, particle['size'])
    
    def create_asteroid_explosion(self, position: Tuple[float, float], size: str):
        """Create asteroid explosion particles"""
        x, y = position
        count = {"small": 10, "medium": 20, "large": 30}.get(size, 15)
        for _ in range(count):
            self.particles.append({
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'color': (random.randint(100, 255), random.randint(50, 150), 0),
                'life': random.uniform(0.5, 1.5),
                'size': random.randint(2, 6)
            })
    
    def create_enemy_explosion(self, position: Tuple[float, float]):
        """Create enemy explosion particles"""
        x, y = position
        for _ in range(15):
            self.particles.append({
                'x': x + random.randint(-15, 15),
                'y': y + random.randint(-15, 15),
                'color': (255, random.randint(0, 100), 0),
                'life': random.uniform(0.5, 1.2),
                'size': random.randint(3, 8)
            })
    
    def create_boss_explosion(self, position: Tuple[float, float]):
        """Create boss explosion particles"""
        x, y = position
        for _ in range(50):
            self.particles.append({
                'x': x + random.randint(-30, 30),
                'y': y + random.randint(-30, 30),
                'color': (255, random.randint(50, 255), random.randint(0, 100)),
                'life': random.uniform(1.0, 2.0),
                'size': random.randint(4, 12)
            })
    
    def create_player_hit_effect(self, position: Tuple[float, float]):
        """Create player hit effect"""
        x, y = position
        for _ in range(10):
            self.particles.append({
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'color': (255, 0, 0),
                'life': random.uniform(0.3, 0.8),
                'size': random.randint(2, 5)
            })
    
    def create_powerup_effect(self, position: Tuple[float, float]):
        """Create power-up collection effect"""
        x, y = position
        for _ in range(8):
            self.particles.append({
                'x': x + random.randint(-8, 8),
                'y': y + random.randint(-8, 8),
                'color': (255, 255, 0),
                'life': random.uniform(0.4, 1.0),
                'size': random.randint(2, 4)
            })
    
    def create_hit_effect(self, position: Tuple[float, float]):
        """Create hit effect"""
        x, y = position
        for _ in range(5):
            self.particles.append({
                'x': x + random.randint(-5, 5),
                'y': y + random.randint(-5, 5),
                'color': (255, 255, 255),
                'life': random.uniform(0.2, 0.5),
                'size': random.randint(1, 3)
            })
    
    def create_large_explosion(self, position: Tuple[float, float]):
        """Create large explosion"""
        x, y = position
        for _ in range(25):
            self.particles.append({
                'x': x + random.randint(-20, 20),
                'y': y + random.randint(-20, 20),
                'color': (255, random.randint(100, 200), 0),
                'life': random.uniform(0.8, 1.8),
                'size': random.randint(3, 10)
            })
    
    def has_explosions(self) -> bool:
        """Check if there are any explosion particles"""
        return len(self.particles) > 0

class PostProcessor:
    """Simple post-processing effects"""
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.surface = None
        self.output_surface = None
        self.screen_shake = 0
        self.flash_color = None
        self.flash_intensity = 0
    
    def resize(self, width, height):
        """Resize surfaces when screen size changes"""
        self.width = width
        self.height = height
        self.surface = None
        self.output_surface = None
    
    def start_capture(self):
        """Start capturing to post-processing surface"""
        if self.surface is None or self.surface.get_size() != (self.width, self.height):
            self.surface = pygame.Surface((self.width, self.height))
            self.output_surface = pygame.Surface((self.width, self.height))
        self.surface.fill((0, 0, 0))
    
    def update(self, dt: float):
        """Update post-processing effects"""
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 50)
        if self.flash_intensity > 0:
            self.flash_intensity = max(0, self.flash_intensity - dt * 100)
    
    def add_screen_shake(self, intensity: float):
        """Add screen shake effect"""
        self.screen_shake = max(self.screen_shake, intensity)
    
    def add_flash(self, color: Tuple[int, int, int], intensity: float):
        """Add flash effect"""
        self.flash_color = color
        self.flash_intensity = intensity
    
    def apply_effects(self):
        """Apply all post-processing effects"""
        self.output_surface.blit(self.surface, (0, 0))
        
        # Apply screen shake
        if self.screen_shake > 0:
            shake_x = random.randint(-int(self.screen_shake), int(self.screen_shake))
            shake_y = random.randint(-int(self.screen_shake), int(self.screen_shake))
            temp_surface = pygame.Surface((self.width, self.height))
            temp_surface.blit(self.output_surface, (shake_x, shake_y))
            self.output_surface = temp_surface
        
        # Apply flash effect
        if self.flash_intensity > 0 and self.flash_color:
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            alpha = min(255, int(self.flash_intensity))
            flash_surface.fill((*self.flash_color, alpha))
            self.output_surface.blit(flash_surface, (0, 0))

class AdvancedStarField:
    """Simple starfield background"""
    def __init__(self, width: int, height: int, star_count: int = 300):
        self.width = width
        self.height = height
        self.stars = []
        for _ in range(star_count):
            self.stars.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'brightness': random.randint(100, 255),
                'speed': random.uniform(0.1, 0.5)
            })
    
    def draw(self, surface: pygame.Surface):
        """Draw the starfield"""
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.height:
                star['y'] = 0
                star['x'] = random.randint(0, self.width)
            
            color = (star['brightness'], star['brightness'], star['brightness'])
            pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), 1)

class NebulaBackground:
    """Simple nebula background"""
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.nebula_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create a simple nebula pattern
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(50, 200)
            alpha = random.randint(10, 30)
            color = (random.randint(20, 60), random.randint(10, 40), random.randint(40, 80), alpha)
            pygame.draw.circle(self.nebula_surface, color, (x, y), radius)
    
    def draw(self, surface: pygame.Surface):
        """Draw the nebula background"""
        surface.blit(self.nebula_surface, (0, 0))

class Boss(Enemy):
    """Boss enemy class - simple extension of Enemy"""
    def __init__(self, difficulty: int):
        super().__init__("boss", difficulty)
        self.health = 100
        self.max_health = 100
        self.score_value = 5000
    
    def update_boss_behavior(self, dt: float, player_pos: Tuple[float, float], bullet_group):
        """Update boss-specific behavior"""
        # Simple boss behavior - just use regular enemy behavior for now
        pass

class GameState:
    """Manages the game's state and progression."""
    def __init__(self):
        self.score = 0
        self.highscore = load_highscore()
        self.difficulty = 1
        self.wave = 1
        self.combo = 1
        self.combo_timer = 0
        self.combo_count = 0
        self.kill_count = 0
        self.time_played = 0
        self.boss_active = False
        self.boss_defeated = False
        self.game_over = False

    def update(self, dt: float):
        """Updates timed state elements."""
        self.time_played += dt
        if pygame.time.get_ticks() > self.combo_timer:
            self.reset_combo()
            
    def add_score(self, amount: int):
        """Adds score with combo multiplier."""
        self.score += amount * self.combo
        if self.score > self.highscore:
            self.highscore = self.score
            
    def add_kill(self):
        """Handles kill combos."""
        self.kill_count += 1
        self.combo_count += 1
        self.combo_timer = pygame.time.get_ticks() + 3000  # 3 second combo window
        
        # Tiered combo system
        if self.combo_count >= 5:
            self.combo = min(self.combo + 1, 5)
            self.combo_count = 0
            
    def reset_combo(self):
        """Resets the combo multiplier."""
        self.combo = 1
        self.combo_count = 0
        
    def increase_difficulty(self):
        """Progressively makes the game harder."""
        self.difficulty += 0.2
        if self.difficulty % 5 == 0:
            self.wave += 1

class GameUI:
    """Handles all user interface rendering."""
    def __init__(self):
        self.font = GameFont()
        self.health_bar_cache = {}
        self.pulse_time = 0
        
    def draw_health_bar(self, surface: pygame.Surface, position: Tuple[float, float], 
                       size: Tuple[float, float], ratio: float, color_theme: str = "player"):
        """Draws an advanced health bar with caching."""
        # Generate cache key
        cache_key = f"{size[0]}_{size[1]}_{color_theme}"
        
        # Create surface if not cached
        if cache_key not in self.health_bar_cache:
            bar_surface = pygame.Surface(size, pygame.SRCALPHA)
            
            # Background
            pygame.draw.rect(bar_surface, (*UI_BLACK, 200), (0, 0, *size), border_radius=3)
            pygame.draw.rect(bar_surface, UI_GRAY, (1, 1, size[0]-2, size[1]-2), border_radius=2)
            
            # Store in cache
            self.health_bar_cache[cache_key] = bar_surface
        
        # Draw cached background
        surface.blit(self.health_bar_cache[cache_key], position)
        
        # Draw fill based on ratio
        fill_width = max(4, int((size[0] - 4) * ratio))
        
        # Color based on theme and ratio
        if color_theme == "player":
            if ratio > 0.7:
                color = UI_GREEN
            elif ratio > 0.4:
                color = UI_YELLOW
            else:
                # Pulsing effect for low health
                self.pulse_time += 0.05
                pulse = 0.7 + 0.3 * math.sin(self.pulse_time * 5)
                color = (int(Colors.ENEMY_BASE[0] * pulse), int(Colors.ENEMY_BASE[1] * pulse), int(Colors.ENEMY_BASE[2] * pulse))
        else:  # enemy/boss
            color = Colors.ENEMY_BASE if ratio < 0.3 else Colors.UI_WARNING
            
        pygame.draw.rect(surface, color, (position[0] + 2, position[1] + 2, fill_width, size[1] - 4), 
                         border_radius=2)
        
        # Glow effect
        if ratio > 0.9:
            glow_surf = pygame.Surface((fill_width, size[1] - 4), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, 50), (0, 0, fill_width, size[1] - 4), border_radius=2)
            surface.blit(glow_surf, (position[0] + 2, position[1] + 2))
    
    def draw_combo_meter(self, surface: pygame.Surface, position: Tuple[float, float], 
                        combo: int, max_combo: int = 5):
        """Draws a visual combo meter."""
        meter_width = 200
        meter_height = 10
        segment_width = meter_width / max_combo
        
        # Background
        pygame.draw.rect(surface, UI_BLACK, (position[0], position[1], meter_width, meter_height))
        
        # Segments
        for i in range(max_combo):
            color = UI_PURPLE if i < combo else UI_DARK_PURPLE
            pygame.draw.rect(surface, color, 
                            (position[0] + i * segment_width, position[1], 
                             segment_width - 2, meter_height))
        
        # Animated sparkle for max combo
        if combo >= max_combo:
            sparkle_x = position[0] + random.random() * meter_width
            sparkle_y = position[1] - 5
            pygame.draw.circle(surface, UI_WHITE, (int(sparkle_x), int(sparkle_y)), 3)
    
    def draw_hud(self, surface: pygame.Surface, game_state: GameState, player: Player, screen_width: int = WIDTH, screen_height: int = HEIGHT):
        """Renders the complete heads-up display."""
        # Score and high score (top left)
        self.draw_text(surface, f"SCORE: {game_state.score:,}", 24, 
                      (20, 20), NEON_BLUE, "hud", glow=True)
        self.draw_text(surface, f"HIGH: {game_state.highscore:,}", 24, 
                      (20, 50), NEON_YELLOW, "hud", glow=True)
        
        # Lives (top right)
        lives_text = "♥" * player.lives
        self.draw_text(surface, lives_text, 32, 
                      (screen_width - 100, 30), LASER_RED, "hud", glow=True)
        
        # Health bar (top right, below lives)
        health_ratio = player.health / player.max_health
        self.draw_health_bar(surface, (screen_width - 220, 65), (200, 20), health_ratio)
        
        # Combo system (top center)
        if game_state.combo > 1:
            combo_text = f"COMBO x{game_state.combo}"
            self.draw_text(surface, combo_text, 28, 
                          (screen_width // 2 - 80, 30), ELECTRIC_PURPLE, "hud", glow=True, pulse=True)
            self.draw_combo_meter(surface, (screen_width // 2 - 100, 60), game_state.combo)
        
        # Wave indicator (bottom center)
        wave_text = f"WAVE {game_state.wave}"
        self.draw_text(surface, wave_text, 24, 
                      (screen_width // 2 - 50, screen_height - 40), SILVER, "hud")
        
        # Power-up indicators (bottom left)
        current_time = pygame.time.get_ticks()
        y_offset = screen_height - 70
        
        if player.rapid_fire_timer > current_time:
            remaining = (player.rapid_fire_timer - current_time) / 1000
            self.draw_text(surface, f"RAPID FIRE: {remaining:.1f}s", 20, 
                          (20, y_offset), NEON_BLUE, "hud", glow=True)
            y_offset -= 25
        
        if player.damage_boost_timer > current_time:
            remaining = (player.damage_boost_timer - current_time) / 1000
            self.draw_text(surface, f"POWER SHOT: {remaining:.1f}s", 20, 
                          (20, y_offset), LASER_RED, "hud", glow=True)
            y_offset -= 25
            
        # Instructions (bottom right)
        instruction_y = screen_height - 100
        self.draw_text(surface, "SPACE: Shoot", 16, 
                      (screen_width - 150, instruction_y), WHITE, "ui")
        self.draw_text(surface, "F11: Fullscreen", 16, 
                      (screen_width - 150, instruction_y + 20), WHITE, "ui")
        self.draw_text(surface, "ESC: Pause", 16, 
                      (screen_width - 150, instruction_y + 40), WHITE, "ui")
    
    def draw_text(self, surface: pygame.Surface, text: str, size: int, 
                 position: Tuple[float, float], color: Tuple[int, int, int], 
                 font_type: str = "default", glow: bool = False, 
                 shadow: bool = False, pulse: bool = False):
        """Advanced text rendering with effects."""
        # Pulse animation
        if pulse:
            size = int(size * (1 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005)))
        
        # Get font from cache
        font = self.font.get_font(font_type, size)
        
        # Shadow effect
        if shadow:
            shadow_surf = font.render(text, True, UI_BLACK)
            surface.blit(shadow_surf, (position[0] + 2, position[1] + 2))
        
        # Glow effect
        if glow:
            for i in range(3, 0, -1):
                glow_surf = font.render(text, True, (*color, 30 * i))
                surface.blit(glow_surf, (position[0], position[1]))
        
        # Main text
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, position)

class Game:
    """Main game controller class."""
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Window setup with fullscreen support
        self.fullscreen = False
        self.setup_display()
        
        pygame.display.set_caption("Nebula Crusader: Ultimate Edition")
        self.clock = pygame.time.Clock()
        
        # Systems initialization
        self.state = GameState()
        self.ui = GameUI()
        self.sound = SoundSystem()
        self.particles = ParticleManager()
        self.post_processor = PostProcessor(self.screen_width, self.screen_height)
        
        # Game objects
        self.player = Player(self.sound)
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.asteroid_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        
        # Background layers
        self.starfield = AdvancedStarField(WIDTH, HEIGHT, star_count=300)
        self.nebula = NebulaBackground(WIDTH, HEIGHT)
        
        # Game setup
        self.reset_game()
    
    def setup_display(self):
        """Setup display with fullscreen toggle support"""
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get actual screen dimensions
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.screen_width = WIDTH
            self.screen_height = HEIGHT
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen
        self.setup_display()
        
        # Update post processor for new screen size
        self.post_processor.resize(self.screen_width, self.screen_height)
        
        # Update background systems
        self.starfield = AdvancedStarField(self.screen_width, self.screen_height, star_count=300)
        self.nebula = NebulaBackground(self.screen_width, self.screen_height)
        
    def reset_game(self):
        """Resets the game state for a new session."""
        self.all_sprites.empty()
        self.enemy_group.empty()
        self.bullet_group.empty()
        self.asteroid_group.empty()
        self.powerup_group.empty()
        
        self.state = GameState()
        self.player = Player(self.sound)
        self.all_sprites.add(self.player)
        
        # Initial spawns
        self.last_asteroid_spawn = 0
        self.last_enemy_spawn = 0
        self.last_powerup_spawn = 0
        self.spawn_initial_asteroids()
        
        # Start music
        self.sound.play_music("main_theme", loop=True)
    
    def spawn_initial_asteroids(self):
        """Creates starting asteroids."""
        sizes = ["small", "medium", "large"]
        for _ in range(5):
            size = random.choice(sizes)
            asteroid = Asteroid(size, self.state.difficulty)
            self.all_sprites.add(asteroid)
            self.asteroid_group.add(asteroid)
    
    def spawn_enemy(self):
        """Spawns an enemy based on current difficulty."""
        enemy_types = ["scout", "fighter", "cruiser"]
        weights = [
            0.6 - min(0.3, self.state.difficulty * 0.02),  # Scout weight decreases
            0.3 + min(0.25, self.state.difficulty * 0.01), # Fighter weight increases
            0.1 + min(0.15, self.state.difficulty * 0.005) # Cruiser weight increases
        ]
        
        # Boss spawn condition
        if not self.state.boss_active and self.state.difficulty >= 10 and random.random() < 0.05:
            boss = Boss(self.state.difficulty)
            self.all_sprites.add(boss, layer=2)
            self.enemy_group.add(boss)
            self.state.boss_active = True
            self.sound.play("boss_spawn")
        else:
            # Normal enemy spawn
            enemy_type = random.choices(enemy_types, weights=weights, k=1)[0]
            enemy = Enemy(enemy_type, self.state.difficulty)
            self.all_sprites.add(enemy, layer=1)
            self.enemy_group.add(enemy)
    
    def spawn_powerup(self, position: Optional[Tuple[float, float]] = None):
        """Spawns a power-up with weighted probabilities."""
        if position is None:
            position = (
                random.randint(100, WIDTH - 100),
                random.randint(100, HEIGHT - 100)
            )
        
        types = ["health", "attack", "shield", "rapid", "mega"]
        weights = [0.3, 0.25, 0.2, 0.2, 0.05]
        
        # Adjust weights based on player state
        if self.player.health < self.player.max_health * 0.5:
            weights[0] += 0.2  # Higher chance for health
        
        powerup_type = random.choices(types, weights=weights, k=1)[0]
        powerup = PowerUp(powerup_type, position)
        self.all_sprites.add(powerup, layer=1)
        self.powerup_group.add(powerup)
    
    def handle_events(self):
        """Processes all input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_game()
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_r and not self.player.alive():
                    self.reset_game()
    
    def handle_continuous_input(self):
        """Handle continuous input like shooting and movement"""
        keys = pygame.key.get_pressed()
        
        # Continuous shooting when spacebar is held
        if keys[pygame.K_SPACE]:
            self.player.shoot(self.bullet_group, self.all_sprites)
    
    def update(self, dt: float):
        """Updates all game systems."""
        # Update game state
        self.state.update(dt)
        
        # Update player
        keys = pygame.key.get_pressed()
        self.player.update(keys, dt)
        
        # Spawn system updates
        current_time = pygame.time.get_ticks()
        self.update_spawns(current_time, dt)
        
        # Update all game objects
        self.update_game_objects(dt)
        
        # Handle collisions
        self.handle_collisions(current_time)
        
        # Update effects
        self.particles.update(dt)
        self.post_processor.update(dt)
        
        # Check game over
        if not self.player.alive() and not self.particles.has_explosions():
            self.state.game_over = True
    
    def update_spawns(self, current_time: int, dt: float):
        """Handles all spawning logic."""
        # Asteroids
        asteroid_delay = max(500, 2000 - self.state.difficulty * 50)
        if current_time - self.last_asteroid_spawn > asteroid_delay:
            sizes = ["small", "medium", "large"]
            for _ in range(1 + int(self.state.difficulty // 3)):
                size = random.choice(sizes)
                asteroid = Asteroid(size, self.state.difficulty)
                self.all_sprites.add(asteroid, layer=1)
                self.asteroid_group.add(asteroid)
            self.last_asteroid_spawn = current_time
        
        # Enemies
        enemy_delay = max(10000, 30000 - self.state.difficulty * 1000)
        if current_time - self.last_enemy_spawn > enemy_delay:
            self.spawn_enemy()
            self.last_enemy_spawn = current_time
        
        # Power-ups
        if current_time - self.last_powerup_spawn > 15000:
            self.spawn_powerup()
            self.last_powerup_spawn = current_time
        
        # Difficulty progression
        if current_time % 10000 < dt * 60:  # Every ~10 seconds
            self.state.increase_difficulty()
    
    def update_game_objects(self, dt: float):
        """Updates all sprite groups."""
        self.bullet_group.update(dt, self.enemy_group)
        self.enemy_group.update(dt, self.player.position, self.bullet_group)
        self.asteroid_group.update(dt)
        self.powerup_group.update(dt)
        
        # Special boss updates
        if self.state.boss_active:
            for boss in [e for e in self.enemy_group if isinstance(e, Boss)]:
                boss.update_boss_behavior(dt, self.player.position, self.bullet_group)
    
    def handle_collisions(self, current_time: int):
        """Handles all collision detection and response."""
        # Bullets vs Asteroids
        bullet_hits = pygame.sprite.groupcollide(
            self.bullet_group, self.asteroid_group, True, False)
        
        for bullet, asteroids in bullet_hits.items():
            for asteroid in asteroids:
                if asteroid.take_damage(bullet.damage):
                    self.on_asteroid_destroyed(asteroid, current_time)
        
        # Bullets vs Enemies
        bullet_hits = pygame.sprite.groupcollide(
            self.bullet_group, self.enemy_group, True, False)
        
        for bullet, enemies in bullet_hits.items():
            for enemy in enemies:
                if enemy.take_damage(bullet.damage, bullet.position):
                    self.on_enemy_damaged(enemy, current_time)
        
        # Player vs Asteroids/Enemies
        for group in [self.asteroid_group, self.enemy_group]:
            hits = pygame.sprite.spritecollide(
                self.player, group, False, pygame.sprite.collide_mask)
            
            for entity in hits:
                if not self.player.invulnerable:
                    self.on_player_hit(entity)
        
        # Player vs Power-ups
        powerup_hits = pygame.sprite.spritecollide(
            self.player, self.powerup_group, True)
        
        for powerup in powerup_hits:
            powerup.apply(self.player)
            self.sound.play("powerup")
            self.particles.create_powerup_effect(powerup.rect.center)
    
    def on_asteroid_destroyed(self, asteroid: Asteroid, current_time: int):
        """Handles asteroid destruction effects."""
        self.state.add_score(asteroid.points)
        self.state.add_kill()
        
        # Visual effects
        self.particles.create_asteroid_explosion(
            asteroid.rect.center, asteroid.size)
        
        # Screen shake based on size
        shake = {"large": 10, "medium": 6, "small": 3}[asteroid.size]
        self.post_processor.add_screen_shake(shake)
        
        # Sound effect
        self.sound.play("explosion_large" if asteroid.size in ["large", "medium"] else "explosion_small")
        
        # Chance to spawn power-up
        if random.random() < 0.15:
            self.spawn_powerup(asteroid.rect.center)
    
    def on_enemy_damaged(self, enemy: Enemy, current_time: int):
        """Handles enemy damage effects."""
        if enemy.health <= 0:
            self.on_enemy_destroyed(enemy, current_time)
        else:
            self.sound.play("enemy_hit")
            self.particles.create_hit_effect(enemy.rect.center)
    
    def on_enemy_destroyed(self, enemy: Enemy, current_time: int):
        """Handles enemy destruction effects."""
        # Score and combo
        self.state.add_score(enemy.score_value)
        self.state.add_kill()
        
        # Special boss handling
        if isinstance(enemy, Boss):
            self.state.boss_active = False
            self.state.boss_defeated = True
            self.state.add_score(10000)
            self.particles.create_boss_explosion(enemy.rect.center)
            self.post_processor.add_screen_shake(20)
            self.sound.play("boss_explosion")
        else:
            # Normal enemy explosion
            self.particles.create_enemy_explosion(enemy.rect.center)
            self.post_processor.add_screen_shake(8)
            self.sound.play("explosion_medium")
        
        # Power-up chance
        if random.random() < 0.25:
            self.spawn_powerup(enemy.rect.center)
    
    def on_player_hit(self, entity):
        """Handles player damage effects."""
        self.player.take_damage(1)
        
        # Major screen effects
        self.post_processor.add_screen_shake(15)
        self.post_processor.add_flash(LASER_RED, 30)
        
        # Create explosion
        self.particles.create_player_hit_effect(self.player.rect.center)
        self.sound.play("player_hit")
        
        # Destroy the hitting entity if it's an asteroid
        if isinstance(entity, Asteroid):
            entity.kill()
            self.particles.create_asteroid_explosion(entity.rect.center, entity.size)
    
    def render(self):
        """Renders the entire game frame with post-processing."""
        # Start drawing to post-processing surface
        self.post_processor.start_capture()
        
        # Background layers
        self.nebula.draw(self.post_processor.surface)
        self.starfield.draw(self.post_processor.surface)
        
        # Game objects
        self.all_sprites.draw(self.post_processor.surface)
        
        # Particles (above most sprites)
        self.particles.render(self.post_processor.surface)
        
        # UI elements
        self.ui.draw_hud(self.post_processor.surface, self.state, self.player, 
                        self.screen_width, self.screen_height)
        
        # Apply post-processing effects
        self.post_processor.apply_effects()
        
        # Final render to screen with scaling if needed
        if self.fullscreen and (self.screen_width != WIDTH or self.screen_height != HEIGHT):
            # Scale the output to fit the screen
            scaled_surface = pygame.transform.scale(self.post_processor.output_surface, 
                                                   (self.screen_width, self.screen_height))
            self.screen.blit(scaled_surface, (0, 0))
        else:
            self.screen.blit(self.post_processor.output_surface, (0, 0))
        
        pygame.display.flip()
    
    def pause_game(self):
        """Shows the pause menu."""
        self.sound.play("menu_select")
        paused = True
        
        # Create overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        self.ui.draw_text(self.screen, "GAME PAUSED", 72, 
                         (self.screen_width//2 - 150, self.screen_height//2 - 100), NEON_BLUE, "title", 
                         glow=True, shadow=True)
        self.ui.draw_text(self.screen, "Press ESC to Resume", 36, 
                         (self.screen_width//2 - 120, self.screen_height//2 + 50), WHITE, "ui")
        
        pygame.display.flip()
        
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                        self.sound.play("menu_select")
                    elif event.key == pygame.K_q:
                        self.quit_game()
            
            self.clock.tick(FPS)
    
    def show_game_over(self):
        """Displays the game over screen."""
        # Update high score if needed
        if self.state.score > self.state.highscore:
            save_highscore(self.state.score)
            self.state.highscore = self.state.score
            new_highscore = True
        else:
            new_highscore = False
        
        # Create explosion effects
        for _ in range(3):
            self.particles.create_large_explosion(
                (random.randint(100, self.screen_width-100), 
                 random.randint(100, self.screen_height-100)))
        
        # Game over loop
        waiting = True
        while waiting:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Update effects
            self.particles.update(dt)
            self.post_processor.update(dt)
            
            # Background
            self.nebula.draw(self.screen)
            self.starfield.draw(self.screen)
            
            # Particles
            self.particles.render(self.screen)
            
            # Game over text
            self.ui.draw_text(self.screen, "GAME OVER", 96, 
                            (self.screen_width//2 - 200, self.screen_height//2 - 150), LASER_RED, "title", 
                            glow=True, shadow=True)
            
            # Score display
            self.ui.draw_text(self.screen, f"FINAL SCORE: {self.state.score:,}", 48, 
                            (self.screen_width//2 - 150, self.screen_height//2 - 50), NEON_YELLOW, "ui", 
                            glow=True)
            
            # High score celebration
            if new_highscore:
                self.ui.draw_text(self.screen, "NEW HIGH SCORE!", 42, 
                                (self.screen_width//2 - 120, self.screen_height//2 + 20), GOLD, "ui", 
                                glow=True, pulse=True)
            else:
                self.ui.draw_text(self.screen, f"HIGH SCORE: {self.state.highscore:,}", 36, 
                                (self.screen_width//2 - 100, self.screen_height//2 + 20), ELECTRIC_PURPLE, "ui")
            
            # Restart prompt
            self.ui.draw_text(self.screen, "Press R to Restart or Q to Quit", 36, 
                            (self.screen_width//2 - 180, self.screen_height//2 + 120), WHITE, "ui")
            
            pygame.display.flip()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        self.quit_game()
    
    def run(self):
        """Main game loop."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.handle_continuous_input()  # Handle continuous input like shooting
            
            if not self.state.game_over:
                self.update(dt)
                self.render()
            else:
                self.show_game_over()
    
    def quit_game(self):
        """Cleanly exits the game."""
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()