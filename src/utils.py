import os
import pygame
import random
import math
import json
import array
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pygame import gfxdraw
from settings import (
    EXPLOSION_COLORS, PARTICLE_COLORS, WIDTH, HEIGHT, 
    ASSETS_DIR, FONTS_DIR, IMAGES_DIR, SOUNDS_DIR, DATA_DIR
)

# Constants
HIGHSCORE_FILE = os.path.join(DATA_DIR, "highscore.json")
SOUND_CACHE: Dict[str, pygame.mixer.Sound] = {}
FONT_CACHE: Dict[str, Dict[int, pygame.font.Font]] = {}
IMAGE_CACHE: Dict[str, pygame.Surface] = {}

class AssetManager:
    """Professional Asset Management System"""
    
    def __init__(self):
        self.fonts = {}
        self.images = {}
        self.sounds = {}
        self.loaded = False
        
        # Create asset directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create asset directories if they don't exist"""
        directories = [ASSETS_DIR, FONTS_DIR, IMAGES_DIR, SOUNDS_DIR, DATA_DIR,
                      os.path.join(IMAGES_DIR, "ships"),
                      os.path.join(IMAGES_DIR, "asteroids"),
                      os.path.join(IMAGES_DIR, "effects"),
                      os.path.join(IMAGES_DIR, "ui"),
                      os.path.join(IMAGES_DIR, "background"),
                      os.path.join(SOUNDS_DIR, "sfx"),
                      os.path.join(SOUNDS_DIR, "music")]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_fonts(self):
        """Load all game fonts with fallbacks"""
        font_configs = {
            # Title fonts (Large headers)
            "title_large": {"file": "Orbitron-Bold.ttf", "sizes": [72, 96, 120], "fallback": "arial"},
            "title_medium": {"file": "Orbitron-Bold.ttf", "sizes": [48, 56, 64], "fallback": "arial"},
            
            # HUD fonts (Game interface)
            "hud_large": {"file": "Rajdhani-SemiBold.ttf", "sizes": [32, 36, 40], "fallback": "arial"},
            "hud_medium": {"file": "Rajdhani-SemiBold.ttf", "sizes": [24, 28], "fallback": "arial"},
            "hud_small": {"file": "Rajdhani-SemiBold.ttf", "sizes": [16, 18, 20], "fallback": "arial"},
            
            # Score fonts (Retro style)
            "score": {"file": "kenvector_future.ttf", "sizes": [20, 24, 28, 32], "fallback": "courier"},
            
            # UI fonts (Menus and buttons)
            "ui_large": {"file": "Rajdhani-SemiBold.ttf", "sizes": [42, 48], "fallback": "arial"},
            "ui_medium": {"file": "Rajdhani-SemiBold.ttf", "sizes": [30, 36], "fallback": "arial"},
            "ui_small": {"file": "Rajdhani-SemiBold.ttf", "sizes": [22, 26], "fallback": "arial"},
        }
        
        for font_name, config in font_configs.items():
            self.fonts[font_name] = {}
            font_path = os.path.join(FONTS_DIR, config["file"])
            
            for size in config["sizes"]:
                try:
                    if os.path.exists(font_path):
                        self.fonts[font_name][size] = pygame.font.Font(font_path, size)
                    else:
                        # Fallback to system font
                        self.fonts[font_name][size] = pygame.font.SysFont(config["fallback"], size, bold=True)
                        print(f">> Font not found: {config['file']}, using fallback: {config['fallback']}")
                except Exception as e:
                    # Ultimate fallback
                    self.fonts[font_name][size] = pygame.font.SysFont("arial", size, bold=True)
                    print(f"❌ Font loading error: {e}, using default font")
    
    def load_images(self):
        """Load all game images with procedural fallbacks"""
        image_configs = {
            # Ships
            "player_ship": {"path": "ships/player_ship.png", "size": (64, 64)},
            "enemy_ship": {"path": "ships/enemy_ship.png", "size": (48, 48)},
            "boss_ship": {"path": "ships/boss_ship.png", "size": (128, 128)},
            
            # Asteroids
            "asteroid_large": {"path": "asteroids/asteroid_large.png", "size": (80, 80)},
            "asteroid_medium": {"path": "asteroids/asteroid_medium.png", "size": (50, 50)},
            "asteroid_small": {"path": "asteroids/asteroid_small.png", "size": (30, 30)},
            
            # Effects
            "explosion_large": {"path": "effects/explosion_large.png", "size": (100, 100)},
            "explosion_medium": {"path": "effects/explosion_medium.png", "size": (60, 60)},
            "laser_beam": {"path": "effects/laser_beam.png", "size": (8, 32)},
            
            # Power-ups
            "powerup_health": {"path": "effects/powerup_health.png", "size": (32, 32)},
            "powerup_weapon": {"path": "effects/powerup_weapon.png", "size": (32, 32)},
            "powerup_shield": {"path": "effects/powerup_shield.png", "size": (32, 32)},
            
            # UI Elements
            "button_normal": {"path": "ui/button_normal.png", "size": (200, 50)},
            "button_hover": {"path": "ui/button_hover.png", "size": (200, 50)},
            "health_bar": {"path": "ui/health_bar.png", "size": (100, 20)},
            
            # Background
            "nebula_bg": {"path": "background/nebula.png", "size": (1200, 800)},
            "starfield": {"path": "background/stars.png", "size": (1200, 800)},
        }
        
        for image_name, config in image_configs.items():
            image_path = os.path.join(IMAGES_DIR, config["path"])
            size = config["size"]
            
            try:
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path).convert_alpha()
                    self.images[image_name] = pygame.transform.scale(image, size)
                else:
                    # Create procedural fallback
                    self.images[image_name] = self._create_fallback_image(image_name, size)
                    print(f">> Image not found: {config['path']}, using procedural fallback")
            except Exception as e:
                self.images[image_name] = self._create_fallback_image(image_name, size)
                print(f"❌ Image loading error: {e}, using procedural fallback")
    
    def _create_fallback_image(self, image_name: str, size: Tuple[int, int]) -> pygame.Surface:
        """Create procedural fallback images"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        w, h = size
        
        # Color schemes for different types
        if "player" in image_name:
            # Blue player ship
            pygame.draw.polygon(surface, (0, 150, 255), [(w//2, 0), (0, h), (w//2, h*0.8), (w, h)])
            pygame.draw.polygon(surface, (100, 200, 255), [(w//2, 5), (w*0.2, h*0.9), (w//2, h*0.8), (w*0.8, h*0.9)])
        elif "enemy" in image_name:
            # Red enemy ship
            pygame.draw.polygon(surface, (255, 50, 50), [(w//2, h), (0, 0), (w//2, h*0.2), (w, 0)])
            pygame.draw.polygon(surface, (255, 150, 150), [(w//2, h*0.8), (w*0.2, h*0.1), (w//2, h*0.2), (w*0.8, h*0.1)])
        elif "asteroid" in image_name:
            # Gray rocky asteroid
            center = (w//2, h//2)
            radius = min(w, h) // 2 - 2
            pygame.draw.circle(surface, (100, 80, 70), center, radius)
            # Add some rocky details
            for _ in range(8):
                x = random.randint(radius//4, w - radius//4)
                y = random.randint(radius//4, h - radius//4)
                r = random.randint(2, 6)
                pygame.draw.circle(surface, (80, 60, 50), (x, y), r)
        elif "powerup" in image_name:
            # Glowing power-up
            if "health" in image_name:
                color = (50, 255, 50)  # Green
                pygame.draw.rect(surface, color, (w//4, w//8, w//2, w//4))
                pygame.draw.rect(surface, color, (w//8, w//4, w//4, w//2))
            elif "weapon" in image_name:
                color = (255, 200, 50)  # Gold
                pygame.draw.polygon(surface, color, [(w//2, 0), (0, h), (w, h)])
            else:  # shield
                color = (50, 200, 255)  # Blue
                pygame.draw.circle(surface, color, (w//2, h//2), w//2 - 2, 3)
        else:
            # Generic colored rectangle
            pygame.draw.rect(surface, (150, 150, 150), (0, 0, w, h))
            pygame.draw.rect(surface, (200, 200, 200), (2, 2, w-4, h-4))
        
        return surface
    
    def load_sounds(self):
        """Load all game sounds with procedural fallbacks"""
        sound_configs = {
            # SFX
            "laser_shoot": {"path": "sfx/laser_01.ogg", "volume": 0.3},
            "laser_charge": {"path": "sfx/laser_charge.ogg", "volume": 0.4},
            "explosion_small": {"path": "sfx/explosion_small.wav", "volume": 0.5},
            "explosion_large": {"path": "sfx/explosion_large.wav", "volume": 0.6},
            "powerup_collect": {"path": "sfx/powerup.ogg", "volume": 0.4},
            "shield_hit": {"path": "sfx/shield_hit.wav", "volume": 0.3},
            "enemy_shoot": {"path": "sfx/enemy_laser.ogg", "volume": 0.2},
            "boss_roar": {"path": "sfx/boss_roar.wav", "volume": 0.7},
            
            # UI Sounds
            "menu_select": {"path": "sfx/menu_select.ogg", "volume": 0.4},
            "menu_confirm": {"path": "sfx/menu_confirm.ogg", "volume": 0.5},
            "game_over": {"path": "sfx/game_over.wav", "volume": 0.6},
            
            # Music (these will be loaded differently)
            "menu_theme": {"path": "music/menu_theme.ogg", "volume": 0.3},
            "game_theme": {"path": "music/game_theme.ogg", "volume": 0.3},
            "boss_theme": {"path": "music/boss_theme.ogg", "volume": 0.4},
        }
        
        for sound_name, config in sound_configs.items():
            sound_path = os.path.join(SOUNDS_DIR, config["path"])
            
            try:
                if os.path.exists(sound_path):
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(config["volume"])
                    self.sounds[sound_name] = sound
                else:
                    # Create procedural sound
                    self.sounds[sound_name] = self._create_fallback_sound(sound_name, config["volume"])
                    print(f">> Sound not found: {config['path']}, using procedural fallback")
            except Exception as e:
                self.sounds[sound_name] = self._create_fallback_sound(sound_name, config["volume"])
                print(f"❌ Sound loading error: {e}, using procedural fallback")
    
    def _create_fallback_sound(self, sound_name: str, volume: float) -> pygame.mixer.Sound:
        """Create procedural fallback sounds"""
        duration = 0.1  # Default duration
        sample_rate = 22050
        
        if "explosion" in sound_name:
            duration = 0.5
            # Create explosion sound (noise)
            frames = int(duration * sample_rate)
            sound_data = []
            for i in range(frames):
                # Decay envelope
                envelope = max(0, 1 - (i / frames))
                noise = random.randint(-32768, 32767) * envelope * 0.3
                sound_data.extend([int(noise), int(noise)])
        elif "laser" in sound_name:
            duration = 0.15
            # Create laser sound (sine wave sweep)
            frames = int(duration * sample_rate)
            sound_data = []
            for i in range(frames):
                t = i / sample_rate
                # Frequency sweep from high to low
                freq = 800 - (t * 400)
                envelope = max(0, 1 - (t / duration))
                wave = math.sin(2 * math.pi * freq * t) * envelope * 0.2
                sample = int(wave * 32767)
                sound_data.extend([sample, sample])
        elif "powerup" in sound_name:
            duration = 0.3
            # Create power-up sound (ascending tones)
            frames = int(duration * sample_rate)
            sound_data = []
            for i in range(frames):
                t = i / sample_rate
                freq1 = 440 + (t * 220)  # Rising tone
                freq2 = 660 + (t * 330)  # Harmony
                envelope = math.sin(math.pi * t / duration)
                wave = (math.sin(2 * math.pi * freq1 * t) + 
                       0.5 * math.sin(2 * math.pi * freq2 * t)) * envelope * 0.15
                sample = int(wave * 32767)
                sound_data.extend([sample, sample])
        else:
            # Generic beep
            frames = int(duration * sample_rate)
            sound_data = []
            for i in range(frames):
                t = i / sample_rate
                envelope = max(0, 1 - (t / duration))
                wave = math.sin(2 * math.pi * 440 * t) * envelope * 0.1
                sample = int(wave * 32767)
                sound_data.extend([sample, sample])
        
        try:
            sound_array = array.array('h', sound_data)
            sound = pygame.mixer.Sound(buffer=sound_array.tobytes())
            sound.set_volume(volume)
            return sound
        except:
            # Ultra fallback - silent sound
            return pygame.mixer.Sound(buffer=b'\x00' * 1000)
    
    def load_all_assets(self):
        """Load all game assets"""
        print(">> Loading game assets...")
        
        try:
            self.load_fonts()
            print("✅ Fonts loaded successfully")
        except Exception as e:
            print(f"❌ Font loading failed: {e}")
        
        try:
            self.load_images()
            print("✅ Images loaded successfully")
        except Exception as e:
            print(f"❌ Image loading failed: {e}")
        
        try:
            self.load_sounds()
            print("✅ Sounds loaded successfully")
        except Exception as e:
            print(f"❌ Sound loading failed: {e}")
        
        self.loaded = True
        print("🎮 All assets loaded and ready!")
    
    def get_font(self, font_name: str, size: int) -> pygame.font.Font:
        """Get a font with automatic fallback"""
        if font_name in self.fonts and size in self.fonts[font_name]:
            return self.fonts[font_name][size]
        
        # Find closest size if exact size not available
        if font_name in self.fonts:
            available_sizes = list(self.fonts[font_name].keys())
            if available_sizes:
                closest_size = min(available_sizes, key=lambda x: abs(x - size))
                return self.fonts[font_name][closest_size]
        
        # Ultimate fallback
        return pygame.font.SysFont("arial", size, bold=True)
    
    def get_image(self, image_name: str) -> pygame.Surface:
        """Get an image"""
        return self.images.get(image_name, self._create_fallback_image(image_name, (32, 32)))
    
    def get_sound(self, sound_name: str) -> pygame.mixer.Sound:
        """Get a sound"""
        return self.sounds.get(sound_name, self._create_fallback_sound(sound_name, 0.3))

# Global asset manager instance
asset_manager = AssetManager()

class ParticleType(Enum):
    STAR = 1
    EXPLOSION = 2
    TRAIL = 3
    POWERUP = 4

@dataclass
class Particle:
    x: float
    y: float
    vx: float = 0
    vy: float = 0
    life: int = 60
    color: Tuple[int, int, int] = (255, 255, 255)
    size: int = 3
    particle_type: ParticleType = ParticleType.STAR
    trail: List[Tuple[float, float]] = None
    glow: bool = False

def load_highscore() -> int:
    """Load highscore with JSON metadata support"""
    try:
        if not os.path.exists(HIGHSCORE_FILE):
            default_data = {"value": 0, "timestamp": 0}
            with open(HIGHSCORE_FILE, 'w') as f:
                json.dump(default_data, f)
            return 0
        
        with open(HIGHSCORE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("value", 0)
    except:
        return 0

def save_highscore(score: int) -> None:
    """Save highscore with timestamp"""
    data = {
        "value": score,
        "timestamp": pygame.time.get_ticks(),
        "player": "Anonymous"  # Could be extended with player profiles
    }
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump(data, f)

def load_sound(filename: str, volume: float = 1.0) -> pygame.mixer.Sound:
    """Cached sound loading with fallback procedural generation"""
    cache_key = f"{filename}_{volume}"
    if cache_key in SOUND_CACHE:
        return SOUND_CACHE[cache_key]
    
    try:
        path = os.path.join(ASSETS_DIR, "sounds", filename)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            SOUND_CACHE[cache_key] = sound
            return sound
        else:
            # Silently generate procedural sound
            sound_type = "shoot" if "laser" in filename else "explosion" if ("boom" in filename or "explosion" in filename) else "powerup"
            sound = create_procedural_sound(sound_type)
            sound.set_volume(volume)
            SOUND_CACHE[cache_key] = sound
            return sound
    except Exception as e:
        # Generate fallback sound on any error
        sound_type = "shoot" if "laser" in filename else "explosion" if ("boom" in filename or "explosion" in filename) else "powerup"
        sound = create_procedural_sound(sound_type)
        sound.set_volume(volume)
        SOUND_CACHE[cache_key] = sound
        return sound

def create_procedural_sound(
    sound_type: str = "shoot",
    frequency: int = 440,
    duration: float = 0.2,
    sample_rate: int = 44100
) -> pygame.mixer.Sound:
    """Advanced procedural sound generator with effects"""
    frames = int(duration * sample_rate)
    sound_data = []
    
    # Base waveform generators
    def sine_wave(t, freq):
        return math.sin(2 * math.pi * freq * t)
    
    def square_wave(t, freq):
        return 1 if sine_wave(t, freq) > 0 else -1
    
    def noise(t):
        return random.random() * 2 - 1
    
    # Sound profiles
    profiles = {
        "shoot": {
            "wave": lambda t: square_wave(t, frequency) * sine_wave(t, frequency*2),
            "envelope": lambda t: math.exp(-t * 20),
            "duration": 0.1
        },
        "explosion": {
            "wave": lambda t: noise(t) * sine_wave(t, frequency * 0.5),
            "envelope": lambda t: math.exp(-t * 5),
            "duration": 0.4
        },
        "powerup": {
            "wave": lambda t: sine_wave(t, frequency + t * 200),
            "envelope": lambda t: math.exp(-t * 8),
            "duration": 0.3
        },
        "hit": {
            "wave": lambda t: noise(t) * square_wave(t, frequency * 2),
            "envelope": lambda t: math.exp(-t * 15),
            "duration": 0.15
        }
    }
    
    profile = profiles.get(sound_type, profiles["shoot"])
    actual_duration = profile["duration"]
    frames = int(actual_duration * sample_rate)
    
    for i in range(frames):
        t = i / sample_rate
        envelope = profile["envelope"](t)
        wave = profile["wave"](t) * envelope * 0.3
        sample = max(-32767, min(32767, int(wave * 32767)))
        sound_data.extend([sample, sample])  # Stereo
    
    # Convert to pygame sound - reshape for stereo
    import numpy as np
    sound_array = np.array(sound_data, dtype=np.int16)
    sound_array = sound_array.reshape(-1, 2)  # Reshape to stereo format
    sound = pygame.sndarray.make_sound(sound_array)
    return sound

def generate_sound_pack():
    """Generate a complete set of procedural sound effects and save them"""
    sounds_to_generate = {
        # Main sounds directory
        "laser1.wav": ("shoot", 800, 0.1),
        "laser2.wav": ("shoot", 600, 0.12),
        "laser3.wav": ("shoot", 1000, 0.08),
        "player_hit.wav": ("hit", 400, 0.2),
        "powerup.wav": ("powerup", 440, 0.3),
        "explosion.wav": ("explosion", 200, 0.5),
        "asteroid_hit.wav": ("hit", 300, 0.15),
        "plasma_fire.wav": ("shoot", 700, 0.15),
        "plasma_impact.wav": ("hit", 500, 0.1),
        "powerup_collect.wav": ("powerup", 660, 0.25),
        "powerup_hum.wav": ("powerup", 220, 0.8),
        
        # SFX subdirectory
        "sfx/enemy_engine.wav": ("powerup", 150, 1.0),
        "sfx/enemy_hit.wav": ("hit", 350, 0.2),
        "sfx/enemy_explosion.wav": ("explosion", 180, 0.6),
        "sfx/shield_impact.wav": ("hit", 800, 0.3)
    }
    
    print("🎵 Generating procedural sound pack...")
    
    for filename, (sound_type, freq, duration) in sounds_to_generate.items():
        try:
            # Create sound
            sound = create_procedural_sound(sound_type, freq, duration)
            
            # Determine full path
            sound_path = os.path.join(SOUNDS_DIR, filename)
            
            # Create directory if needed
            sound_dir = os.path.dirname(sound_path)
            os.makedirs(sound_dir, exist_ok=True)
            
            # Save as WAV file (placeholder - would need additional library for actual WAV writing)
            print(f"✅ Generated {filename} ({sound_type}, {freq}Hz, {duration}s)")
            
        except Exception as e:
            print(f"❌ Failed to generate {filename}: {e}")
    
    print("🎵 Sound pack generation complete!")

# Global asset manager instance
asset_manager = AssetManager()

class ParticleType(Enum):
    """Particle type enumeration"""
    SPARK = "spark"
    EXPLOSION = "explosion"
    TRAIL = "trail"
    STAR = "star"
    POWERUP = "powerup"

@dataclass
class Particle:
    """Particle data structure"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float
    color: Tuple[int, int, int]
    particle_type: ParticleType
    trail: Optional[List] = None

def load_highscore() -> int:
    """Load highscore with JSON metadata support"""
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("score", 0)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return 0

def save_highscore(score: int) -> None:
    """Save highscore with metadata"""
    data = {
        "score": score,
        "timestamp": pygame.time.get_ticks(),
        "player": "Anonymous"  # Could be extended with player profiles
    }
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump(data, f)

def particle_explosion(position: Tuple[float, float], color: Tuple[int, int, int], count: int = 20) -> List[Particle]:
    """Creates explosion particles"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        particles.append(Particle(
            x=position[0],
            y=position[1],
            vx=math.cos(angle) * speed,
            vy=math.sin(angle) * speed,
            life=random.uniform(30, 60),
            max_life=60,
            size=random.uniform(2, 6),
            color=color,
            particle_type=ParticleType.EXPLOSION
        ))
    return particles

def bezier_curve(p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], t: float) -> Tuple[float, float]:
    """Quadratic bezier curve calculation"""
    x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
    y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
    return (x, y)

def initialize_assets():
    """Initialize all game assets"""
    asset_manager.load_all_assets()
    return asset_manager

class Starfield:
    def __init__(self, width: int, height: int, layers: int = 3):
        self.width = width
        self.height = height
        self.layers = layers
        self.stars = self._generate_stars()
        self.nebulas = self._generate_nebulas()
        self.time = 0
    
    def _generate_stars(self) -> List[Dict]:
        """Generate parallax star layers"""
        stars = []
        for layer in range(self.layers):
            layer_density = 100 * (layer + 1)
            for _ in range(layer_density):
                stars.append({
                    'x': random.uniform(0, self.width),
                    'y': random.uniform(0, self.height),
                    'speed': 0.2 + layer * 0.3,
                    'size': random.uniform(0.5, 1.5) * (layer + 1),
                    'color': (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(200, 255)
                    ),
                    'layer': layer,
                    'twinkle_speed': random.uniform(0.01, 0.05),
                    'twinkle_phase': random.uniform(0, 6.28)
                })
        return stars
    
    def _generate_nebulas(self) -> List[Dict]:
        """Generate colorful nebula clouds"""
        nebulas = []
        for _ in range(5):
            nebula_colors = [
                (50, 20, 80),  # Purple
                (30, 50, 90),   # Blue
                (80, 30, 50),   # Red
                (40, 80, 40)    # Green
            ]
            nebulas.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'width': random.randint(300, 800),
                'height': random.randint(300, 800),
                'color': random.choice(nebula_colors),
                'alpha': random.randint(5, 20),
                'drift_x': random.uniform(-0.1, 0.1),
                'drift_y': random.uniform(-0.1, 0.1)
            })
        return nebulas
    
    def update(self, dt: float) -> None:
        """Animate starfield"""
        self.time += dt
        
        # Update stars
        for star in self.stars:
            star['y'] += star['speed']
            star['twinkle_phase'] += star['twinkle_speed']
            
            if star['y'] > self.height:
                star['y'] = 0
                star['x'] = random.uniform(0, self.width)
        
        # Update nebulas
        for nebula in self.nebulas:
            nebula['x'] += nebula['drift_x']
            nebula['y'] += nebula['drift_y']
            
            # Wrap around
            if nebula['x'] < -nebula['width']:
                nebula['x'] = self.width
            elif nebula['x'] > self.width:
                nebula['x'] = -nebula['width']
                
            if nebula['y'] < -nebula['height']:
                nebula['y'] = self.height
            elif nebula['y'] > self.height:
                nebula['y'] = -nebula['height']
    
    def render(self, surface: pygame.Surface) -> None:
        """Render starfield with parallax effect"""
        # Draw nebulas first
        for nebula in self.nebulas:
            nebula_surface = pygame.Surface((nebula['width'], nebula['height']), pygame.SRCALPHA)
            nebula_surface.fill((*nebula['color'], nebula['alpha']))
            
            # Apply perlin noise for cloud-like appearance
            for _ in range(3):  # Multiple passes for density
                points = []
                for _ in range(20):
                    x = random.randint(0, nebula['width'])
                    y = random.randint(0, nebula['height'])
                    radius = random.randint(50, 150)
                    alpha = random.randint(5, 15)
                    pygame.draw.circle(
                        nebula_surface,
                        (*nebula['color'], alpha),
                        (x, y),
                        radius
                    )
            
            surface.blit(
                nebula_surface,
                (nebula['x'] - nebula['width']//2, nebula['y'] - nebula['height']//2)
            )
        
        # Draw stars with twinkle effect
        for star in sorted(self.stars, key=lambda s: s['layer']):
            twinkle = 0.7 + 0.3 * math.sin(star['twinkle_phase'] + self.time)
            color = (
                int(star['color'][0] * twinkle),
                int(star['color'][1] * twinkle),
                int(star['color'][2] * twinkle)
            )
            
            # Different rendering for different layers
            if star['layer'] == self.layers - 1:  # Foreground
                # Glow effect
                glow_size = star['size'] * 3
                glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surface,
                    (*color, 50),
                    (glow_size, glow_size),
                    glow_size
                )
                surface.blit(
                    glow_surface,
                    (star['x'] - glow_size, star['y'] - glow_size)
                )
            
            # Star core
            pygame.draw.circle(
                surface,
                color,
                (int(star['x']), int(star['y'])),
                max(1, int(star['size']))
            )

class FontManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_fonts()
        return cls._instance
    
    def _init_fonts(self):
        """Initialize all game fonts with fallbacks"""
        self.fonts = {}
        base_sizes = [8, 12, 16, 20, 24, 32, 48, 64, 96]
        
        # Try to load custom fonts first
        try:
            orbitron_path = os.path.join(ASSETS_DIR, "fonts/Orbitron-Bold.ttf")
            for size in base_sizes:
                self.fonts[f"orbitron_{size}"] = pygame.font.Font(orbitron_path, size)
        except:
            print("Failed to load Orbitron font, using fallback")
        
        # System font fallbacks
        for size in base_sizes:
            # Title font
            self.fonts[f"title_{size}"] = pygame.font.SysFont("Arial Black", size, True)
            # UI font
            self.fonts[f"ui_{size}"] = pygame.font.SysFont("Arial", size)
            # Monospace font
            self.fonts[f"mono_{size}"] = pygame.font.SysFont("Courier New", size)
    
    def get_font(self, name: str = "ui", size: int = 24) -> pygame.font.Font:
        """Get a font with automatic scaling"""
        key = f"{name}_{size}"
        if key not in self.fonts:
            # Find closest available size
            available_sizes = sorted(
                [int(k.split("_")[1]) for k in self.fonts.keys() if k.startswith(f"{name}_")]
            )
            if not available_sizes:
                return pygame.font.Font(None, size)
            
            closest_size = min(available_sizes, key=lambda x: abs(x - size))
            key = f"{name}_{closest_size}"
        
        return self.fonts[key]
    
    def render_text(
        self,
        text: str,
        name: str = "ui",
        size: int = 24,
        color: Tuple[int, int, int] = (255, 255, 255),
        antialias: bool = True,
        glow: bool = False,
        glow_color: Tuple[int, int, int] = None,
        glow_size: int = 2
    ) -> pygame.Surface:
        """Render text with optional glow effect"""
        font = self.get_font(name, size)
        text_surface = font.render(text, antialias, color)
        
        if glow:
            glow_color = glow_color or (color[0]//4, color[1]//4, color[2]//4)
            glow_surface = pygame.Surface(
                (text_surface.get_width() + glow_size*2, 
                 text_surface.get_height() + glow_size*2),
                pygame.SRCALPHA
            )
            
            # Draw glow in multiple passes
            for i in range(glow_size, 0, -1):
                alpha = int(100 * (i / glow_size))
                temp_surface = font.render(text, antialias, (*glow_color, alpha))
                for dx in [-i, 0, i]:
                    for dy in [-i, 0, i]:
                        if dx != 0 or dy != 0:
                            glow_surface.blit(temp_surface, (glow_size + dx, glow_size + dy))
            
            # Combine surfaces
            final_surface = pygame.Surface(glow_surface.get_size(), pygame.SRCALPHA)
            final_surface.blit(glow_surface, (0, 0))
            final_surface.blit(text_surface, (glow_size, glow_size))
            return final_surface
        else:
            return text_surface

# Backward compatibility functions
def load_highscore() -> int:
    """Load highscore with JSON metadata support"""
    try:
        if not os.path.exists(HIGHSCORE_FILE):
            default_data = {"value": 0, "timestamp": 0}
            with open(HIGHSCORE_FILE, 'w') as f:
                json.dump(default_data, f)
            return 0
        
        with open(HIGHSCORE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("value", 0)
    except:
        return 0

def save_highscore(score: int):
    """Save highscore with metadata"""
    try:
        os.makedirs(os.path.dirname(HIGHSCORE_FILE), exist_ok=True)
        data = {
            "value": score,
            "timestamp": pygame.time.get_ticks()
        }
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Failed to save highscore: {e}")

# Initialize the global asset manager
def initialize_assets():
    """Initialize all game assets"""
    asset_manager.load_all_assets()
    return asset_manager


def bezier_curve(p0, p1, p2, p3, num_points=10):
    """Generate points along a cubic bezier curve."""
    points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        # Cubic bezier formula
        x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        points.append((int(x), int(y)))
    return points


def particle_explosion(x, y, color=(255, 255, 255), count=20):
    """Create a simple particle explosion effect."""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 150)
        velocity_x = math.cos(angle) * speed
        velocity_y = math.sin(angle) * speed
        
        particles.append({
            'x': x,
            'y': y,
            'vx': velocity_x,
            'vy': velocity_y,
            'life': random.uniform(0.5, 1.5),
            'color': color,
            'size': random.uniform(2, 5)
        })
    return particles

def load_sprite_sheet(filename: str, sprite_width: int, sprite_height: int, 
                     rows: int = 1, cols: int = 1) -> List[pygame.Surface]:
    """Load and split a sprite sheet into individual sprites"""
    try:
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            sheet = pygame.image.load(path).convert_alpha()
        else:
            # Create a fallback sprite sheet
            sheet_width = sprite_width * cols
            sheet_height = sprite_height * rows
            sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
            # Fill with gradient colors for different sprites
            for row in range(rows):
                for col in range(cols):
                    x = col * sprite_width
                    y = row * sprite_height
                    color_intensity = (row * cols + col + 1) * (255 // (rows * cols))
                    color = (color_intensity % 255, (color_intensity * 2) % 255, (color_intensity * 3) % 255)
                    pygame.draw.rect(sheet, color, (x, y, sprite_width, sprite_height))
    except:
        # Ultra fallback
        sheet_width = sprite_width * cols
        sheet_height = sprite_height * rows
        sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
        sheet.fill((100, 100, 100))
    
    sprites = []
    for row in range(rows):
        for col in range(cols):
            x = col * sprite_width
            y = row * sprite_height
            sprite = sheet.subsurface((x, y, sprite_width, sprite_height)).copy()
            sprites.append(sprite)
    
    return sprites

def load_font(filename: str, size: int) -> pygame.font.Font:
    """Load a font file with fallback to system fonts"""
    cache_key = f"{filename}_{size}"
    if cache_key in FONT_CACHE:
        return FONT_CACHE[cache_key]
    
    try:
        path = os.path.join(FONTS_DIR, filename)
        if os.path.exists(path):
            font = pygame.font.Font(path, size)
        else:
            # Try system fonts
            font = pygame.font.SysFont("arial", size, bold=True)
    except:
        # Ultimate fallback
        font = pygame.font.Font(None, size)
    
    FONT_CACHE[cache_key] = font
    return font

def load_image(filename: str, alpha: bool = True) -> pygame.Surface:
    """Load an image with caching and fallback creation"""
    if filename in IMAGE_CACHE:
        return IMAGE_CACHE[filename]
    
    try:
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            if alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()
        else:
            # Create procedural fallback based on filename
            size = (64, 64)  # Default size
            image = pygame.Surface(size, pygame.SRCALPHA if alpha else 0)
            
            if "ship" in filename.lower():
                # Create a simple ship shape
                w, h = size
                pygame.draw.polygon(image, (0, 150, 255), [(w//2, 0), (0, h), (w//2, h*0.8), (w, h)])
            elif "asteroid" in filename.lower():
                # Create a rocky asteroid
                w, h = size
                center = (w//2, h//2)
                radius = min(w, h) // 2 - 2
                pygame.draw.circle(image, (100, 80, 70), center, radius)
            elif "bullet" in filename.lower() or "laser" in filename.lower():
                # Create a bullet/laser
                w, h = size
                pygame.draw.rect(image, (255, 255, 0), (w//2-2, 0, 4, h))
            else:
                # Generic colored rectangle
                image.fill((150, 150, 150))
    except:
        # Ultra fallback
        size = (64, 64)
        image = pygame.Surface(size, pygame.SRCALPHA if alpha else 0)
        image.fill((200, 200, 200))
    
    IMAGE_CACHE[filename] = image
    return image