import pygame
import os
from pygame import gfxdraw
from utils import load_font, load_image

class UI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fonts = self._load_fonts()
        self.colors = self._define_colors()
        self.images = self._load_images()
        self.particles = []

    def _load_fonts(self):
        """Load custom fonts with fallbacks."""
        return {
            "title": load_font("Orbitron-Bold.ttf", 72),
            "hud": load_font("Orbitron-Medium.ttf", 24),
            "button": load_font("Rajdhani-SemiBold.ttf", 32),
        }

    def _define_colors(self):
        """Cyberpunk color palette."""
        return {
            "neon_blue": (0, 240, 255),
            "neon_pink": (255, 0, 128),
            "dark_bg": (10, 10, 20),
            "health_green": (0, 255, 100),
            "health_red": (255, 40, 0),
        }

    def _load_images(self):
        """Load UI assets (e.g., buttons, icons)."""
        return {
            "button_bg": load_image("ui/button_bg.png"),
            "powerup_icon": load_image("ui/powerup.png"),
        }

    def draw_health_bar(self, surface, current_health, max_health):
        """Animated health bar with glow."""
        bar_width = 300
        bar_height = 20
        x, y = 50, self.screen_height - 40
        ratio = current_health / max_health

        # Background
        pygame.draw.rect(surface, self.colors["dark_bg"], (x, y, bar_width, bar_height), border_radius=10)

        # Health fill (glow effect)
        health_width = int(bar_width * ratio)
        if ratio > 0.6:
            color = self.colors["health_green"]
        else:
            color = self.colors["health_red"]

        # Gradient fill
        for i in range(health_width):
            alpha = int(255 * (i / health_width))
            temp_surface = pygame.Surface((1, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (*color, alpha), (0, 0, 1, bar_height))
            surface.blit(temp_surface, (x + i, y))

        # Border
        pygame.draw.rect(surface, self.colors["neon_blue"], (x, y, bar_width, bar_height), 2, border_radius=10)

    def draw_score(self, surface, score):
        """Score display with pulsing animation."""
        text = f"SCORE: {score}"
        text_surface = self.fonts["hud"].render(text, True, self.colors["neon_blue"])
        glow_surface = text_surface.copy()
        glow_surface.fill((*self.colors["neon_blue"], 50), special_flags=pygame.BLEND_RGBA_ADD)
        
        # Position (top-right)
        x = self.screen_width - text_surface.get_width() - 20
        y = 20
        
        # Draw glow (3x offset for blur effect)
        for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            surface.blit(glow_surface, (x + offset[0], y + offset[1]))
        
        surface.blit(text_surface, (x, y))

    def draw_button(self, surface, text, rect, hovered=False):
        """Interactive button with particle effects."""
        button_color = self.colors["neon_pink"] if hovered else self.colors["neon_blue"]
        
        # Button background (with rounded corners)
        pygame.draw.rect(surface, (30, 30, 50), rect, border_radius=12)
        pygame.draw.rect(surface, button_color, rect, 3, border_radius=12)
        
        # Text
        text_surface = self.fonts["button"].render(text, True, button_color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
        
        # Hover effects
        if hovered:
            self._emit_button_particles(rect.center)

    def _emit_button_particles(self, pos):
        """Create sparkle particles on button hover."""
        for _ in range(5):
            self.particles.append({
                "pos": list(pos),
                "velocity": [pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() % 360) * 0.5],
                "lifetime": 30,
                "color": self.colors["neon_blue"],
            })

    def update_particles(self):
        """Update and draw particles."""
        for particle in self.particles[:]:
            particle["lifetime"] -= 1
            if particle["lifetime"] <= 0:
                self.particles.remove(particle)
            else:
                particle["pos"][0] += particle["velocity"][0]
                particle["pos"][1] += particle["velocity"][1]
                pygame.draw.circle(
                    pygame.display.get_surface(),
                    particle["color"],
                    (int(particle["pos"][0]), int(particle["pos"][1])),
                    max(1, particle["lifetime"] // 10),
                )

    def draw_game_over(self, surface, score, high_score):
        """Stylish game-over screen."""
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Title
        title = self.fonts["title"].render("GAME OVER", True, self.colors["neon_pink"])
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))
        
        # Scores
        score_text = self.fonts["hud"].render(f"FINAL SCORE: {score}", True, self.colors["neon_blue"])
        high_text = self.fonts["hud"].render(f"HIGH SCORE: {high_score}", True, self.colors["neon_blue"])
        surface.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, 250))
        surface.blit(high_text, (self.screen_width // 2 - high_text.get_width() // 2, 300))