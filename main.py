import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Marathon Snack Collector")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player properties
player_width = 50
player_height = 50
player_x = SCREEN_WIDTH // 2 - player_width // 2
player_y = SCREEN_HEIGHT - player_height - 10
player_speed = 1 # Reduced player speed for slower game flow

# Snack properties
snack_size = 20
snacks = []
snack_spawn_interval = 60  # frames

# Game variables
score = 0
timer_duration = 20  # 1 minute 30 seconds
start_time = time.time()
game_over = False
finish_line_active = False
finish_line_y = 0  # Initial position of the finish line (will be set to player_y when activated)
finish_line_speed = 0.0001 # Speed at which the finish line moves

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Helper function to display text
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    SCREEN.blit(text_surface, text_rect)

# Game loop
running = True
frame_count = 0
help_visible = False # Global flag for help menu

while running:
    # Event handling needs to be at the top of the loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                help_visible = not help_visible # Toggle help visibility
            # Handle restart/quit only when game is over
            if game_over and event.key == pygame.K_r:
                # Reset game variables
                score = 0
                start_time = time.time()
                game_over = False
                finish_line_active = False
                finish_line_y = 0 # Reset finish line position
                player_x = SCREEN_WIDTH // 2 - player_width // 2
                player_y = SCREEN_HEIGHT - player_height - 10
                snacks = []
                frame_count = 0
                help_visible = False # Reset help menu visibility on restart
            if game_over and event.key == pygame.K_q:
                running = False

    if help_visible:
        SCREEN.fill(BLACK) # Clear screen for help menu
        draw_text("Help:", large_font, WHITE, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 100)
        draw_text("Collect at least 20 snacks.", font, WHITE, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20)
        draw_text("Reach the finish line before the timer ends.", font, WHITE, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 20)
        draw_text("Press H to close help.", font, WHITE, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 100)
        pygame.display.flip()
        continue # Skip game logic if help is visible

    if not game_over:
        keys = pygame.key.get_pressed()
        
        # Player movement is now only sideways. The illusion of moving forward
        # is created by moving the snacks downwards faster.

        # Handle left movement (QWERTY A, AZERTY Q, or Arrow Left)
        if keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_q]:
            player_x -= player_speed
        # Handle right movement (QWERTY D, AZERTY D, or Arrow Right)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_x += player_speed

        # Keep player on screen
        if player_x < 0: player_x = 0
        if player_x > SCREEN_WIDTH - player_width: player_x = SCREEN_WIDTH - player_width

        # Snack spawning
        frame_count += 1
        if frame_count % snack_spawn_interval == 0:
            snack_x = random.randint(0, SCREEN_WIDTH - snack_size)
            snack_y = random.randint(-100, -20) # Spawn above screen
            snacks.append(pygame.Rect(snack_x, snack_y, snack_size, snack_size))

        # Move snacks and check for collision
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for snack in snacks[:]:
            snack.y += player_speed + 0.0001 # Further slow down snack movement
            if player_rect.colliderect(snack):
                snacks.remove(snack)
                if score < 20: # Only increase score if less than 20
                    score += 1
            if snack.y > SCREEN_HEIGHT: # Remove snacks that go off screen
                snacks.remove(snack)

        # Timer logic
        elapsed_time = time.time() - start_time
        remaining_time = max(0, timer_duration - elapsed_time)

        if remaining_time <= 0 and not finish_line_active:
            finish_line_active = True
            finish_line_y = 0 # Start finish

        # Clear screen
        SCREEN.fill(BLACK)

        # Draw player
        pygame.draw.rect(SCREEN, BLUE, player_rect)

        # Draw snacks
        for snack in snacks:
            pygame.draw.rect(SCREEN, GREEN, snack)

        # Draw score and timer
        draw_text(f"Snacks: {score}/20", font, WHITE, 10, 10)
        draw_text(f"Time: {int(remaining_time)}s", font, WHITE, 10, 50)

        # Movement instructions and help prompt
        draw_text("Movement: A/D or Q/D or Arrow Keys", font, WHITE, 10, 90)
        draw_text("Press H for Help", font, WHITE, 10, 130)

        # Finish line logic
        if finish_line_active:
            # Move finish line towards the bottom of the screen, similar to snacks
            finish_line_y += player_speed + 0.0001 # Use the same speed as snacks for consistent movement
            pygame.draw.line(SCREEN, RED, (0, finish_line_y), (SCREEN_WIDTH, finish_line_y), 5)
            
            # Player crosses finish line (or passes it)
            if player_y <= finish_line_y:
                if score >= 20:
                    draw_text("YOU WIN!", large_font, GREEN, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
                else:
                    draw_text("GAME OVER!", large_font, RED, SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2)
                    draw_text("Not enough snacks!", large_font, RED, SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 3)
                game_over = True
        
        # Game over if timer runs out AND not enough snacks AND player hasn't crossed finish line
        #if remaining_time <= 0 and not game_over and score < 20 and player_y > finish_line_y:
        #    draw_text("TIME'S UP! GAME OVER!", large_font, RED, SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2)
        #    game_over = True

    else: # Game is over
        draw_text("Press R to Restart or Q to Quit", font, WHITE, SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 100)
        # No need for separate event handling here, it's done in the main loop

    pygame.display.flip()

pygame.quit()
sys.exit()