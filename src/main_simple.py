import pygame
import sys
import random
import math
from settings import Engine, Colors
from player import Player
from bullet import Bullet
from asteroid import Asteroid
from powerup import PowerUp
from utils import asset_manager, initialize_assets, load_highscore, save_highscore

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Get display info for fullscreen
        self.display_info = pygame.display.Info()
        self.fullscreen = True
        
        # Initialize display - start in fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Update engine constants to match screen size
            Engine.SCREEN_WIDTH = self.screen.get_width()
            Engine.SCREEN_HEIGHT = self.screen.get_height()
        else:
            self.screen = pygame.display.set_mode((Engine.SCREEN_WIDTH, Engine.SCREEN_HEIGHT))
            
        pygame.display.set_caption(Engine.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        # Initialize assets
        print(">> Initializing game assets...")
        self.asset_manager = initialize_assets()
        
        # Game state
        self.running = True
        self.score = 0
        self.highscore = load_highscore()
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        
        # Create player
        self.player = Player(self.asset_manager)
        self.all_sprites.add(self.player)
        
        # Verify player initialization
        print(f"Player initialized: Lives={self.player.lives}/3, Health={self.player.health}/{self.player.max_health}")
        
        # Game variables
        self.last_asteroid_spawn = 0
        self.last_powerup_spawn = 0
        self.asteroid_spawn_delay = 1000
        self.difficulty_level = 1
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Player shoots (no score for shooting, only for hitting)
                    self.player.shoot(self.bullets, self.all_sprites)
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    self.toggle_fullscreen()
        return True
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            Engine.SCREEN_WIDTH = self.screen.get_width()
            Engine.SCREEN_HEIGHT = self.screen.get_height()
        else:
            # Return to default window size
            Engine.SCREEN_WIDTH = 1200
            Engine.SCREEN_HEIGHT = 800
            self.screen = pygame.display.set_mode((Engine.SCREEN_WIDTH, Engine.SCREEN_HEIGHT))
    
    def update(self):
        keys = pygame.key.get_pressed()
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        
        # Handle continuous shooting
        if keys[pygame.K_SPACE]:
            # Player shoots (no score for shooting, only for hitting asteroids)
            self.player.shoot(self.bullets, self.all_sprites)
        
        # Update player
        self.player.update(keys, dt)
        
        # Update other sprites
        self.bullets.update(dt, self.asteroids)
        self.asteroids.update(dt)
        self.powerups.update(dt)
        self.explosions.update()
        
        # Spawn asteroids
        current_time = pygame.time.get_ticks()
        if current_time - self.last_asteroid_spawn > self.asteroid_spawn_delay:
            asteroid = Asteroid()
            self.all_sprites.add(asteroid)
            self.asteroids.add(asteroid)
            self.last_asteroid_spawn = current_time
        
        # Spawn power-ups occasionally
        if current_time - self.last_powerup_spawn > 15000:
            powerup_type = random.choice(['health', 'attack', 'shield', 'mega'])
            powerup = PowerUp(powerup_type)
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)
            self.last_powerup_spawn = current_time
        
        # Handle collisions
        self.handle_collisions()
    
    def handle_collisions(self):
        # Bullets vs Asteroids
        hits = pygame.sprite.groupcollide(self.bullets, self.asteroids, True, False)
        for bullet in hits:
            for asteroid in hits[bullet]:
                asteroid.take_damage(bullet.damage)
                if asteroid.health <= 0:
                    # Calculate score for destroying asteroid
                    base_score = asteroid.points
                    
                    # Add bonus points based on player health (reward staying healthy)
                    health_bonus = int(base_score * (self.player.health / self.player.max_health * 0.5))
                    
                    # Add life bonus (more lives = higher bonus, but reasonable amount)
                    life_bonus = base_score * self.player.lives
                    
                    total_score = base_score + health_bonus + life_bonus
                    self.score += total_score
                    
                    asteroid.kill()
                    
                    # Play explosion sound
                    sound = asset_manager.get_sound("explosion_small")
                    sound.play()
                    
                    # Show score popup (optional visual feedback)
                    print(f"Destroyed asteroid! +{total_score} points (base: {base_score}, health bonus: {health_bonus}, life bonus: {life_bonus})")
        
        # Player vs Asteroids
        hits = pygame.sprite.spritecollide(self.player, self.asteroids, False)
        for asteroid in hits:
            if not self.player.invulnerable:
                # Player takes damage - this handles the life system internally
                player_died = self.player.take_damage(1)
                asteroid.kill()
                
                # Play explosion sound
                sound = asset_manager.get_sound("explosion_large")
                sound.play()
                
                # Lose some points when hit (penalty for taking damage)
                penalty = min(100, self.score // 10)  # Lose 10% of score or 100 points, whichever is less
                self.score = max(0, self.score - penalty)
                print(f"Hit by asteroid! -{penalty} points")
                
                # Check if player died (lives <= 0)
                if player_died or self.player.lives <= 0:
                    return self.game_over()
        
        # Player vs PowerUps
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in hits:
            # Apply powerup effects and get any score bonus
            result = powerup.apply(self.player)
            
            # Give bonus points for collecting power-ups
            powerup_bonus = 50 * powerup.rarity  # Rarer power-ups give more points
            
            # Check if there's an additional score bonus (like from mega powerup at max lives)
            if result and isinstance(result, dict) and "score_bonus" in result:
                powerup_bonus += result["score_bonus"]
                print(f"Collected {powerup.type} power-up! +{powerup_bonus} points (including bonus: {result['score_bonus']})")
            else:
                print(f"Collected {powerup.type} power-up! +{powerup_bonus} points")
            
            self.score += powerup_bonus
            
            # Play collection sound
            sound = asset_manager.get_sound("powerup_collect")
            sound.play()
    
    def draw(self):
        # Clear screen with space background
        self.screen.fill(Colors.DEEP_SPACE)
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw the user interface with proper layout to avoid overlapping."""
        # UI positioning based on screen size
        margin = 20
        top_y = margin
        
        # === LEFT SIDE: SCORE ===
        font_large = asset_manager.get_font("hud_large", 36)
        score_text = font_large.render(f"SCORE: {self.score:,}", True, Colors.UI_TEXT)
        score_shadow = font_large.render(f"SCORE: {self.score:,}", True, (0, 0, 0))
        
        # Draw score with shadow effect
        self.screen.blit(score_shadow, (margin + 2, top_y + 2))
        self.screen.blit(score_text, (margin, top_y))
        
        # === CENTER TOP: HIGH SCORE ===
        font_medium = asset_manager.get_font("hud_medium", 30)
        highscore_text = font_medium.render(f"HIGH SCORE: {self.highscore:,}", True, Colors.UI_ACCENT)
        highscore_shadow = font_medium.render(f"HIGH SCORE: {self.highscore:,}", True, (0, 0, 0))
        
        highscore_rect = highscore_text.get_rect()
        highscore_rect.centerx = Engine.SCREEN_WIDTH // 2
        highscore_rect.top = top_y
        
        # Draw with shadow
        shadow_rect = highscore_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        self.screen.blit(highscore_shadow, shadow_rect)
        self.screen.blit(highscore_text, highscore_rect)
        
        # === RIGHT TOP: LIVES DISPLAY ===
        # Hearts display with proper spacing and text positioning
        heart_size = 35
        heart_spacing = 40
        
        # Calculate hearts area - ensure enough space for "LIVES" text
        lives_text_width = 80  # Reserve space for "LIVES" text
        total_hearts_width = 3 * heart_spacing
        hearts_area_width = max(total_hearts_width, lives_text_width)
        hearts_start_x = Engine.SCREEN_WIDTH - margin - hearts_area_width
        hearts_y = top_y + 30  # Move down to make room for text
        
        # Lives label (above hearts) - properly centered over all hearts
        lives_label = font_medium.render("LIVES", True, Colors.UI_TEXT)
        lives_label_rect = lives_label.get_rect()
        lives_label_rect.centerx = hearts_start_x + (hearts_area_width // 2)
        lives_label_rect.bottom = hearts_y - 5
        self.screen.blit(lives_label, lives_label_rect)
        
        # Draw 3 hearts for lives
        for i in range(3):
            heart_x = hearts_start_x + (i * heart_spacing)
            
            if i < self.player.lives:
                # Determine heart color based on health when this is the current life
                if i == self.player.lives - 1:  # Current active life
                    # Color changes based on health: 4=green, 3=yellow, 2=orange, 1=red
                    if self.player.health == 4:
                        heart_color = (0, 255, 0)  # Green - full health
                    elif self.player.health == 3:
                        heart_color = (255, 255, 0)  # Yellow - 3/4 health
                    elif self.player.health == 2:
                        heart_color = (255, 165, 0)  # Orange - 2/4 health  
                    else:  # health == 1
                        heart_color = (255, 0, 0)  # Red - 1/4 health
                else:
                    # Other lives are full health (green)
                    heart_color = (0, 255, 0)  # Green
                
                self.draw_heart(heart_x, hearts_y, heart_size, heart_color, True)
            else:
                # Empty heart (lost life)
                self.draw_heart(heart_x, hearts_y, heart_size, (100, 100, 100), False)
        
        # === RIGHT MIDDLE: HEALTH BAR (Below hearts) ===
        health_section_y = hearts_y + heart_size + 25  # Position below hearts with more spacing
        health_bar_width = 180  # Slightly smaller to fit better
        health_bar_height = 16
        health_bar_x = Engine.SCREEN_WIDTH - margin - health_bar_width
        
        # Health text (above health bar) - properly positioned
        font_health = asset_manager.get_font("hud_medium", 22)
        health_text = font_health.render(f"HEALTH: {self.player.health}/{self.player.max_health}", True, Colors.UI_TEXT)
        health_text_rect = health_text.get_rect()
        health_text_rect.topright = (Engine.SCREEN_WIDTH - margin, health_section_y)
        self.screen.blit(health_text, health_text_rect)
        
        # Health bar background (dark red)
        health_bar_y = health_section_y + 30  # Position below health text
        pygame.draw.rect(self.screen, (60, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health bar fill (gradient from green to red based on health)
        health_percentage = self.player.health / self.player.max_health
        fill_width = health_bar_width * health_percentage
        
        if health_percentage > 0.6:
            health_color = (0, 255, 0)  # Green
        elif health_percentage > 0.3:
            health_color = (255, 255, 0)  # Yellow
        else:
            health_color = (255, 0, 0)  # Red
            
        if fill_width > 0:
            pygame.draw.rect(self.screen, health_color, (health_bar_x, health_bar_y, fill_width, health_bar_height))
        
        # Health bar border with glow effect
        pygame.draw.rect(self.screen, (255, 255, 255), (health_bar_x - 2, health_bar_y - 2, health_bar_width + 4, health_bar_height + 4), 2)
        pygame.draw.rect(self.screen, Colors.UI_TEXT, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
        
        # === BOTTOM RIGHT: CONTROLS INFO ===
        font_controls = asset_manager.get_font("hud_small", 16)
        controls_y = Engine.SCREEN_HEIGHT - 100
        
        controls_info = [
            "ARROW KEYS: Move",
            "SPACE: Shoot", 
            "F11: Fullscreen",
            "ESC: Quit"
        ]
        
        # Controls title - properly positioned
        controls_title = font_controls.render("CONTROLS:", True, Colors.UI_ACCENT)
        title_rect = controls_title.get_rect()
        title_rect.topright = (Engine.SCREEN_WIDTH - margin, controls_y - 25)
        self.screen.blit(controls_title, title_rect)
        
        # Controls list - ensure all text fits on screen
        for i, control in enumerate(controls_info):
            control_text = font_controls.render(control, True, (150, 150, 150))
            control_rect = control_text.get_rect()
            control_rect.topright = (Engine.SCREEN_WIDTH - margin, controls_y + (i * 16))
            self.screen.blit(control_text, control_rect)
    
    def draw_heart(self, x, y, size, color, filled=True):
        """Draw a heart shape at the specified position."""
        # Heart shape using polygons
        heart_points = []
        center_x, center_y = x + size // 2, y + size // 2
        
        # Generate heart shape points
        for i in range(360):
            angle = math.radians(i)
            # Heart equation: x = 16sin³(t), y = 13cos(t) - 5cos(2t) - 2cos(3t) - cos(4t)
            heart_x = 16 * (math.sin(angle) ** 3)
            heart_y = -(13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))
            
            # Scale and position
            scaled_x = center_x + heart_x * (size / 40)
            scaled_y = center_y + heart_y * (size / 40)
            heart_points.append((scaled_x, scaled_y))
        
        if filled:
            # Draw filled heart
            pygame.draw.polygon(self.screen, color, heart_points)
            # Add highlight
            highlight_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
            pygame.draw.polygon(self.screen, highlight_color, heart_points[:len(heart_points)//3])
        else:
            # Draw outline only
            pygame.draw.polygon(self.screen, color, heart_points, 3)
    
    def game_over(self):
        # Update high score
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)
        
        # Game over screen
        self.show_game_over()
        return False
    
    def show_game_over(self):
        overlay = pygame.Surface((Engine.SCREEN_WIDTH, Engine.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        font_large = asset_manager.get_font("title_large", 72)
        game_over_text = font_large.render("GAME OVER", True, Colors.ENEMY_BASE)
        game_over_rect = game_over_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score
        font_medium = asset_manager.get_font("hud_large", 36)
        score_text = font_medium.render(f"Final Score: {self.score:,}", True, Colors.UI_TEXT)
        score_rect = score_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(score_text, score_rect)
        
        # High score
        if self.score == self.highscore and self.score > 0:
            new_high_text = font_medium.render("🏆 NEW HIGH SCORE! 🏆", True, Colors.UI_ACCENT)
            new_high_rect = new_high_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(new_high_text, new_high_rect)
        else:
            high_text = font_medium.render(f"High Score: {self.highscore:,}", True, Colors.UI_ACCENT)
            high_rect = high_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(high_text, high_rect)
        
        # Instructions
        font_small = asset_manager.get_font("ui_medium", 30)
        restart_text = font_small.render("Press [R] to Restart or [Q] to Quit", True, Colors.UI_TEXT)
        restart_rect = restart_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        
        # Wait for input
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False
                        return True  # Restart
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
        return False
    
    def show_main_menu(self):
        self.screen.fill(Colors.DEEP_SPACE)
        
        # Title
        font_title = asset_manager.get_font("title_large", 96)
        title_text = font_title.render("ULTIMATE", True, Colors.UI_ACCENT)
        title_rect = title_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT // 2 - 120))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = font_title.render("SPACE SHOOTER", True, Colors.PLAYER_SHIP)
        subtitle_rect = subtitle_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions
        font_medium = asset_manager.get_font("ui_large", 42)
        start_text = font_medium.render("Press [SPACE] to Start", True, Colors.UI_TEXT)
        start_rect = start_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(start_text, start_rect)
        
        quit_text = font_medium.render("Press [Q] to Quit", True, Colors.UI_WARNING)
        quit_rect = quit_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(quit_text, quit_rect)
        
        # Controls
        font_small = asset_manager.get_font("ui_small", 22)
        controls_text = font_small.render("Controls: Arrow Keys + SPACE", True, Colors.UI_TEXT)
        controls_rect = controls_text.get_rect(center=(Engine.SCREEN_WIDTH // 2, Engine.SCREEN_HEIGHT - 100))
        self.screen.blit(controls_text, controls_rect)
        
        pygame.display.flip()
        
        # Wait for input
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                        return True
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
        return False
    
    def run(self):
        while self.running:
            # Show main menu
            if not self.show_main_menu():
                break
            
            # Reset game state
            self.score = 0
            self.player.lives = 3  # Proper 3-life system
            self.player.health = 4  # Start with full health (4 points)
            self.player.invulnerable_time = 0
            
            # Clear all sprites except player
            for group in [self.bullets, self.asteroids, self.powerups, self.explosions]:
                group.empty()
            
            # Game loop
            game_running = True
            while game_running and self.running:
                # Handle events
                if not self.handle_events():
                    self.running = False
                    break
                
                # Update game
                self.update()
                
                # Draw everything
                self.draw()
                
                # Check game over
                if self.player.lives <= 0:
                    if self.show_game_over():
                        game_running = False  # Restart
                    else:
                        self.running = False  # Quit
                
                self.clock.tick(Engine.FPS)
        
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
