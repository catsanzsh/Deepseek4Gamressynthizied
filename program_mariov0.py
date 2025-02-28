import pygame
import sys
from math import sin

# Initialize Pygame
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)

# Screen settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mario Forever Worlds")

# Colors
COLORS = {
    "sky": (135, 206, 235),
    "ground": (139, 69, 19),
    "pipe": (0, 128, 0),
    "castle": (105, 105, 105),
    "lava": (255, 0, 0),
    "ice": (173, 216, 230),
    "sand": (244, 164, 96),
    "night": (25, 25, 112)
}

# Additional color constants
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)

# Platform class
class Platform:
    def __init__(self, x, y, width, height, ptype):
        self.rect = pygame.Rect(x, y, width, height)
        self.ptype = ptype

# Level class
class Level:
    def __init__(self, theme, platforms, enemies, goal, hazard=None):
        self.theme = theme
        self.platforms = platforms
        self.enemies = enemies
        self.goal = goal  # (x, y, width, height)
        self.hazard = hazard  # (type, rect, damage)

# Enemy class
class Enemy:
    def __init__(self, x, y, etype):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.direction = 1
        self.speed = 2
        self.etype = etype  # "goomba", "koopa", "spiny"
        
    def move(self, platforms):
        self.rect.x += self.direction * self.speed
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.direction == 1:
                    self.rect.right = platform.rect.left
                else:
                    self.rect.left = platform.rect.right
                self.direction *= -1

# Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 300, 30, 45)
        self.velocity_y = 0
        self.on_ground = False
        self.facing_right = True
        self.lives = 3
        self.score = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
            self.facing_right = True
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = -12
            self.on_ground = False

    def apply_gravity(self):
        self.velocity_y += 0.5  # Gravity acceleration
        self.rect.y += int(self.velocity_y)

    def check_platform_collisions(self, platforms):
        # Basic collision detection: adjust if falling onto a platform
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity_y = 0

    def update(self, platforms):
        self.handle_input()
        self.apply_gravity()
        self.check_platform_collisions(platforms)

# Create worlds/levels
def create_worlds():
    return [
        # World 1-1 (Grassland)
        Level(
            theme="sky",
            platforms=[
                Platform(0, 360, 600, 40, "ground"),
                Platform(100, 300, 100, 20, "ground"),
                Platform(400, 240, 100, 20, "ground")
            ],
            enemies=[
                Enemy(200, 300, "goomba"),
                Enemy(450, 240, "goomba")
            ],
            goal=(550, 200, 30, 160)
        ),
        # World 1-2 (Underground)
        Level(
            theme="night",
            platforms=[
                Platform(0, 360, 600, 40, "ground"),
                Platform(200, 280, 100, 20, "ground"),
                Platform(50, 200, 100, 20, "ground")
            ],
            enemies=[
                Enemy(300, 280, "koopa")
            ],
            goal=(550, 160, 30, 200)
        ),
        # World 1-3 (Sky with Pit Hazard)
        Level(
            theme="sky",
            platforms=[
                Platform(0, 360, 200, 20, "ground"),
                Platform(300, 360, 300, 20, "ground"),
                Platform(400, 280, 100, 20, "ground")
            ],
            enemies=[
                Enemy(250, 360, "goomba")
            ],
            goal=(550, 220, 30, 140),
            hazard=("pit", pygame.Rect(200, 0, 100, 400), 1)
        )
        # Additional worlds can be added here...
    ]

# Draw the game environment
def draw_environment(level):
    # Draw background
    screen.fill(COLORS[level.theme])
    
    # Draw platforms
    for platform in level.platforms:
        color = COLORS[platform.ptype] if platform.ptype in COLORS else GREEN
        pygame.draw.rect(screen, color, platform.rect)
    
    # Draw goal (flag pole)
    pygame.draw.rect(screen, RED, pygame.Rect(*level.goal))
    
    # Draw hazards
    if level.hazard:
        hazard_type, hazard_rect, _ = level.hazard
        if hazard_type == "lava":
            pygame.draw.rect(screen, COLORS["lava"], hazard_rect)
        elif hazard_type == "pit":
            pygame.draw.rect(screen, BLACK, hazard_rect)

# Draw enemy
def draw_enemy(enemy):
    color = BROWN if enemy.etype == "goomba" else GREEN
    pygame.draw.ellipse(screen, color, enemy.rect)

# Main game loop
def game_loop():
    worlds = create_worlds()
    current_world = 0
    player = Player()
    clock = pygame.time.Clock()
    
    while player.lives > 0 and current_world < len(worlds):
        level = worlds[current_world]
        running = True
        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            player.update(level.platforms)
            
            # Update enemies and check collisions with player
            for enemy in level.enemies:
                enemy.move(level.platforms)
                if player.rect.colliderect(enemy.rect):
                    player.lives -= 1
                    player.rect.topleft = (50, 300)
                    player.velocity_y = 0
            
            # Check hazard collisions
            if level.hazard:
                hazard_type, hazard_rect, damage = level.hazard
                if player.rect.colliderect(hazard_rect):
                    player.lives -= damage
                    player.rect.topleft = (50, 300)
                    player.velocity_y = 0
            
            # Check if player reached the goal
            if player.rect.colliderect(pygame.Rect(*level.goal)):
                current_world += 1
                running = False
                break
            
            # Draw all game elements
            draw_environment(level)
            for enemy in level.enemies:
                draw_enemy(enemy)
            pygame.draw.rect(screen, (0, 0, 255), player.rect)  # Draw player as a blue rectangle
            
            # HUD: Display lives
            lives_text = font.render(f'Lives: {player.lives}', True, (0, 0, 0))
            screen.blit(lives_text, (10, 10))
            
            pygame.display.flip()
    
    # End of game: Show victory or game over screen
    screen.fill(BLACK)
    if player.lives <= 0:
        message = "Game Over!"
    else:
        message = "You Win!"
    message_text = font.render(message, True, (255, 255, 255))
    screen.blit(
        message_text,
        ((SCREEN_WIDTH - message_text.get_width()) // 2, (SCREEN_HEIGHT - message_text.get_height()) // 2)
    )
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
