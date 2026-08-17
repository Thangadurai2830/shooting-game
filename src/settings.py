"""
ULTIMATE SPACE SHOOTER - PROFESSIONAL SETTINGS
This configuration file contains all game parameters with advanced organization.
"""

import os
import pygame

# ==================== PATHS CONFIGURATION ====================
# Get the project root directory (one level up from src)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# Asset paths
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
DATA_DIR = os.path.join(ASSETS_DIR, "data")

# ==================== ENGINE CONFIGURATION ====================
class Engine:
    # Display settings
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    FPS = 144  # High refresh rate support
    VSYNC = True
    FULLSCREEN = False
    WINDOW_TITLE = "Nebula Crusader DX"
    
    # Rendering quality
    PARTICLE_QUALITY = 3  # 1-3 (Low-High)
    LIGHTING_QUALITY = 2  # 0-2 (Off-High)
    POST_PROCESSING = True
    
    # Performance
    MAX_PARTICLES = 2000
    ENTITY_POOL_SIZE = 100
    STARFIELD_DENSITY = 300

# ==================== VISUAL DESIGN SYSTEM ====================
class Colors:
    # Core palette
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DEEP_SPACE = (5, 5, 15)
    NEBULA_BASE = (15, 10, 30)
    
    # UI Colors
    UI_BACKGROUND = (10, 10, 20, 200)
    UI_ACCENT = (0, 150, 255)
    UI_TEXT = (230, 240, 255)
    UI_WARNING = (255, 100, 50)
    UI_BLACK = (0, 0, 0)
    UI_WHITE = (255, 255, 255)
    UI_GRAY = (128, 128, 128)
    UI_GREEN = (0, 255, 0)
    UI_YELLOW = (255, 255, 0)
    UI_PURPLE = (128, 0, 128)
    UI_DARK_PURPLE = (64, 0, 64)
    
    # Player colors
    PLAYER_SHIP = (0, 180, 255)
    PLAYER_ENGINE = (255, 100, 0)
    PLAYER_SHIELD = (0, 200, 255, 100)
    
    # Enemy colors
    ENEMY_BASE = (200, 50, 50)
    ENEMY_ELITE = (180, 80, 220)
    BOSS_CORE = (255, 50, 50)
    
    # Weapon colors
    PLASMA_BLUE = (0, 100, 255)
    LASER_RED = (255, 50, 50)
    ELECTRIC_PURPLE = (180, 0, 255)
    QUANTUM_GREEN = (50, 255, 100)
    
    # Power-up colors
    HEALTH = (255, 50, 80)
    DAMAGE_BOOST = (255, 150, 0)
    SHIELD = (0, 150, 255)
    RAPID_FIRE = (0, 255, 150)
    ULTIMATE = (255, 215, 0)
    
    # Effect colors
    EXPLOSION_ORANGE = (255, 100, 0)
    EXPLOSION_YELLOW = (255, 200, 0)
    SHIELD_HIT = (0, 200, 255)
    AFTERIMAGE = (100, 200, 255, 100)

# ==================== GAMEPLAY BALANCE ====================
class Gameplay:
    # Player configuration
    PLAYER_SPEED = 8
    PLAYER_ACCELERATION = 0.5
    PLAYER_FRICTION = 0.92
    PLAYER_LIVES = 3
    PLAYER_INVULNERABILITY_DURATION = 2.0  # seconds
    
    # Weapon systems
    BASE_FIRE_RATE = 0.3  # seconds
    RAPID_FIRE_RATE = 0.1
    BULLET_SPEED = 1200
    BULLET_LIFETIME = 1.5  # seconds
    
    # Power-ups
    POWERUP_SPAWN_RATE = 0.02  # chance per frame
    POWERUP_DURATIONS = {
        'health': 0,      # instant
        'attack': 8.0,
        'shield': 12.0,
        'rapid': 10.0,
        'ultimate': 15.0
    }
    
    # Difficulty scaling
    DIFFICULTY_INCREASE_INTERVAL = 30.0  # seconds
    DIFFICULTY_SCALING = {
        'spawn_rate': 1.1,
        'enemy_speed': 1.05,
        'enemy_health': 1.15,
        'boss_interval': 0.9
    }

# ==================== AUDIO CONFIGURATION ====================
class Audio:
    MASTER_VOLUME = 0.8
    VOLUME_LEVELS = {
        'music': 0.6,
        'sfx': 0.7,
        'ui': 0.8,
        'voice': 1.0
    }
    
    # Sound priorities
    MAX_CHANNELS = 32
    CHANNEL_ALLOCATION = {
        'player': 8,
        'enemies': 12,
        'environment': 6,
        'ui': 6
    }

# ==================== UI/UX SETTINGS ====================
class UI:
    # Font system
    FONT_PRIMARY = "assets/fonts/Orbitron-Bold.ttf"
    FONT_SECONDARY = "assets/fonts/Rajdhani-Medium.ttf"
    FONT_SPECIAL = "assets/fonts/Audiowide-Regular.ttf"
    
    # Sizing
    FONT_SIZES = {
        'title': 72,
        'heading': 48,
        'subheading': 36,
        'body': 24,
        'small': 18
    }
    
    # Animations
    MENU_TRANSITION_SPEED = 0.5
    TOOLTIP_FADE_TIME = 0.3
    NOTIFICATION_DURATION = 3.0

# ==================== PARTICLE SYSTEM ====================
class Particles:
    # Engine effects
    ENGINE_SPAWN_RATE = 0.8
    ENGINE_COLORS = [
        (255, 100, 0),  # Orange
        (255, 200, 0),  # Yellow
        (0, 150, 255)   # Blue
    ]
    
    # Explosion presets
    EXPLOSION_PRESETS = {
        'small': {
            'count': 30,
            'speed': 400,
            'size': 5,
            'colors': [Colors.EXPLOSION_ORANGE, Colors.EXPLOSION_YELLOW]
        },
        'large': {
            'count': 100,
            'speed': 600,
            'size': 8,
            'colors': [Colors.EXPLOSION_ORANGE, Colors.EXPLOSION_YELLOW, Colors.WHITE]
        }
    }

# ==================== DEBUG SETTINGS ====================
class Debug:
    SHOW_HITBOXES = False
    SHOW_FPS = True
    INVULNERABLE = False
    UNLIMITED_AMMO = False
    SPAWN_BOSS_KEY = pygame.K_F2
    
    # Logging levels
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_FILE = "game.log"

# ==================== ASSET PATHS ====================
class Paths:
    # Graphics
    IMAGES = "assets/images/"
    TEXTURES = "assets/textures/"
    PARTICLE_TEXTURES = "assets/particles/"
    
    # Audio
    MUSIC = "assets/audio/music/"
    SFX = "assets/audio/sfx/"
    VOICE = "assets/audio/voice/"
    
    # Fonts
    FONTS = "assets/fonts/"
    
    # Data
    SAVES = "saves/"
    CONFIGS = "config/"

# ==================== DEPRECATION WARNINGS ====================
"""
LEGACY COLOR DEFINITIONS (Maintained for compatibility)
These will be removed in v3.0 - Use Colors class instead
"""
NEON_BLUE = Colors.PLAYER_SHIP
ELECTRIC_CYAN = (0, 255, 255)
NEON_GREEN = Colors.QUANTUM_GREEN
LASER_RED = Colors.LASER_RED
GOLD = Colors.ULTIMATE
ELECTRIC_PURPLE = Colors.ELECTRIC_PURPLE
ASTEROID_BROWN = (139, 69, 19)
ASTEROID_GRAY = (105, 105, 105)
SILVER = (192, 192, 192)

# ==================== RUNTIME CALCULATIONS ====================
# Calculate derived values
PLAYER_SPEED_PIXELS = Gameplay.PLAYER_SPEED * 100
BULLET_SPEED_PIXELS = Gameplay.BULLET_SPEED * 100

# ==================== GLOBAL CONSTANTS FOR COMPATIBILITY ====================
# Screen dimensions
WIDTH = Engine.SCREEN_WIDTH
HEIGHT = Engine.SCREEN_HEIGHT

# Player constants
PLAYER_SPEED = Gameplay.PLAYER_SPEED
PLAYER_ACCELERATION = Gameplay.PLAYER_ACCELERATION
PLAYER_LIVES = Gameplay.PLAYER_LIVES
SHIELD_DURATION = Gameplay.POWERUP_DURATIONS.get('shield', 5.0)

# Color constants
SHIELD_BLUE = Colors.PLAYER_SHIELD
ENGINE_ORANGE = Colors.PLAYER_ENGINE
ENGINE_YELLOW = (255, 200, 0)
ENGINE_BLUE = (0, 150, 255)
ENGINE_RED = (255, 50, 50)
ENGINE_GRAY = (100, 100, 100)
DAMAGE_RED = (255, 100, 100)
WHITE = Colors.WHITE
PLASMA_BLUE = Colors.PLASMA_BLUE
QUANTUM_PURPLE = Colors.ELECTRIC_PURPLE

# Ship colors
SHIP_BLUE = Colors.PLAYER_SHIP
CORE_BLUE = (100, 200, 255)
CORE_WHITE = (255, 255, 255)
WING_ENERGY = (150, 255, 200)

# Power-up colors
POWER_GOLD = Colors.ULTIMATE
POWER_RED = (255, 100, 100)
HEALTH_COLOR = (0, 200, 0)
HEALTH_GLOW = (0, 255, 0)
SHIELD_COLOR = (0, 100, 200)
SHIELD_GLOW = (0, 150, 255)
WEAPON_COLOR = (200, 150, 0)  
WEAPON_GLOW = (255, 200, 0)

# Effect colors
MUZZLE_FLASH = (255, 255, 100)
DAMAGE_ORANGE = (255, 150, 0)
DAMAGE_YELLOW = (255, 255, 0)

# Additional colors for asteroid effects
NEON_YELLOW = (255, 255, 0)
ORANGE_RED = (255, 100, 0)

# Power-up specific colors
HEALTH_HIGHLIGHT = (0, 255, 0)
HEALTH_CORE = (0, 200, 0)
SHIELD_HIGHLIGHT = (0, 150, 255)
SHIELD_CORE = (0, 100, 200)
WEAPON_HIGHLIGHT = (255, 200, 0)
WEAPON_CORE = (200, 150, 0)
ATTACK_COLOR = (255, 150, 0)
ATTACK_GLOW = (255, 100, 0)
ATTACK_CORE = (200, 80, 0)
ATTACK_HIGHLIGHT = (255, 255, 100)
RAPID_COLOR = (0, 255, 150)
RAPID_GLOW = (0, 255, 150)
RAPID_CORE = (0, 200, 100)
RAPID_HIGHLIGHT = (150, 255, 200)
MEGA_COLOR = (255, 50, 255)
MEGA_GLOW = (255, 50, 255)
MEGA_CORE = (200, 50, 200)
MEGA_COLORS = [(255, 50, 255), (255, 100, 255), (200, 50, 200)]
MEGA_COLOR = (255, 50, 255)
MEGA_GLOW = (255, 50, 255)
MEGA_CORE = (200, 50, 200)

# Effect colors
EXPLOSION_COLORS = [Colors.EXPLOSION_ORANGE, Colors.EXPLOSION_YELLOW, (255, 255, 255)]
PARTICLE_COLORS = [Colors.PLASMA_BLUE, Colors.ELECTRIC_PURPLE, Colors.QUANTUM_GREEN, Colors.EXPLOSION_ORANGE]

# Create color gradients
def create_gradient(color1, color2, steps):
    return [
        tuple(
            int(color1[i] + (color2[i] - color1[i]) * t / (steps - 1))
            for i in range(3)
        )
        for t in range(steps)
    ]

# Nebula background gradient
NEBULA_GRADIENT = create_gradient(Colors.DEEP_SPACE, Colors.NEBULA_BASE, 256)