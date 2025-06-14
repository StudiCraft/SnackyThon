import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# --- Constants ---
# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Should be defined after pygame.init()
pygame.display.set_caption("Marathon Snack Collector")

# Colors
BACKGROUND_COLOR = (30, 30, 40)    # Dark bluish-gray
PLAYER_COLOR = (70, 170, 255)      # Sky blue
SNACK_COLOR = (255, 190, 0)        # Amber/Orange
TEXT_COLOR = (220, 220, 220)       # Light gray / Off-white
HUD_BACKGROUND_COLOR = (50, 50, 70, 200) # Semi-transparent darker gray for HUD (alpha for Surface)
FINISH_LINE_COLOR = (255, 60, 60)      # Bright red for finish line
WIN_TEXT_COLOR = (100, 255, 100)     # Bright green for win messages
LOSE_TEXT_COLOR = (255, 80, 80)      # Bright red for lose messages
HELP_TITLE_COLOR = (180, 180, 255)   # Light blue for help title
HELP_INFO_COLOR = TEXT_COLOR         # Standard text color for help info lines
OVERLAY_COLOR_DARK = (0, 0, 0, 180)  # Semi-transparent black for full-screen message backgrounds

# Player
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_INITIAL_X = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
PLAYER_INITIAL_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
PLAYER_SPEED = 1 # Reduced player speed for slower game flow

# Snack
SNACK_SIZE = 20
SNACK_SPAWN_INTERVAL = 60  # frames

# Game Mechanics
TIMER_DURATION = 20  # seconds
FINISH_LINE_SPEED_FACTOR = 0.0001 # Small addition to make finish line slightly faster than snacks if needed
TARGET_SCORE = 20

# Fonts
FONT_SIZE_NORMAL = 36
FONT_SIZE_LARGE = 72
font = pygame.font.Font(None, FONT_SIZE_NORMAL)
large_font = pygame.font.Font(None, FONT_SIZE_LARGE)

# Game States
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_HELP = "help"
STATE_PAUSED = "paused"

# --- Game Variables (will be initialized/reset in a function) ---
player_x = 0
player_y = 0
snacks = []
score = 0
start_time = 0
game_over = False
finish_line_active = False
finish_line_y = 0
game_outcome_text = ""
game_outcome_details = ""
game_outcome_color = TEXT_COLOR
frame_count = 0
current_game_state = STATE_PLAYING # Initial state

# Helper function to display text
def draw_text(text, font, color, surface, x, y, center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def reset_game():
    global player_x, player_y, snacks, score, start_time, game_over
    global finish_line_active, finish_line_y, frame_count
    global game_outcome_text, game_outcome_details, game_outcome_color, current_game_state

    player_x = PLAYER_INITIAL_X
    player_y = PLAYER_INITIAL_Y
    snacks = []
    score = 0
    start_time = time.time()
    game_over = False # This variable is still useful for internal logic before switching state
    finish_line_active = False
    finish_line_y = 0
    frame_count = 0
    game_outcome_text = ""
    game_outcome_details = ""
    game_outcome_color = TEXT_COLOR
    current_game_state = STATE_PLAYING

reset_game() # Initialize game variables for the first run

# Game loop
running = True

while running:
    # Event handling needs to be at the top of the loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                if current_game_state == STATE_HELP:
                    current_game_state = STATE_PLAYING # Or previous state if we store it
                elif current_game_state == STATE_PLAYING or current_game_state == STATE_PAUSED:
                    current_game_state = STATE_HELP

            if event.key == pygame.K_p:
                if current_game_state == STATE_PLAYING:
                    current_game_state = STATE_PAUSED
                elif current_game_state == STATE_PAUSED:
                    current_game_state = STATE_PLAYING

            if current_game_state == STATE_GAME_OVER:
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_q:
                    running = False
            elif current_game_state == STATE_HELP: # Allow quitting from help screen
                 if event.key == pygame.K_q:
                    running = False

    # --- Game State Logic & Drawing ---

    if current_game_state == STATE_HELP:
        SCREEN.fill(BACKGROUND_COLOR)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR_DARK)
        SCREEN.blit(overlay, (0, 0))

        draw_text("Help Menu", large_font, HELP_TITLE_COLOR, SCREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True)

        help_lines_content = [
            f"Collect at least {TARGET_SCORE} snacks to win.",
            "Reach the finish line after it appears (timer ends).",
            "Movement: A/D or Q/D or Arrow Keys.",
            "Press P to Pause/Resume game.",
            "Press H to close this help menu.",
            "Press Q to Quit at any time from Help or Game Over."
        ]
        line_y_start = SCREEN_HEIGHT // 2 - 40
        for i, line in enumerate(help_lines_content):
            draw_text(line, font, HELP_INFO_COLOR, SCREEN, SCREEN_WIDTH // 2, line_y_start + i * 40, center=True)

    elif current_game_state == STATE_PAUSED:
        SCREEN.fill(BACKGROUND_COLOR) # Or draw the game state underneath and overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR_DARK)
        SCREEN.blit(overlay, (0,0))
        draw_text("PAUSED", large_font, TEXT_COLOR, SCREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, center=True)
        draw_text("Press P to Resume", font, TEXT_COLOR, SCREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, center=True)

    elif current_game_state == STATE_PLAYING:
        # --- Game Logic (only if playing) ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_q]: # Q for AZERTY left
            player_x -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_x += PLAYER_SPEED

        player_x = max(0, min(player_x, SCREEN_WIDTH - PLAYER_WIDTH)) # Keep player on screen

        frame_count += 1
        if frame_count % SNACK_SPAWN_INTERVAL == 0:
            snack_x = random.randint(0, SCREEN_WIDTH - SNACK_SIZE)
            snack_y = random.randint(-100, -20)
            snacks.append(pygame.Rect(snack_x, snack_y, SNACK_SIZE, SNACK_SIZE))

        player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        for snack in snacks[:]:
            snack.y += PLAYER_SPEED + FINISH_LINE_SPEED_FACTOR # Snacks move slightly faster than player's base speed
            if player_rect.colliderect(snack):
                snacks.remove(snack)
                if score < TARGET_SCORE:
                    score += 1
            elif snack.y > SCREEN_HEIGHT:
                snacks.remove(snack)

        elapsed_time = time.time() - start_time
        remaining_time = max(0, TIMER_DURATION - elapsed_time)

        if remaining_time <= 0 and not finish_line_active:
            finish_line_active = True
            finish_line_y = 0 # Start finish line from the top

        # --- Drawing (only if playing) ---
        SCREEN.fill(BACKGROUND_COLOR)
        pygame.draw.rect(SCREEN, PLAYER_COLOR, player_rect)
        for snack in snacks:
            pygame.draw.ellipse(SCREEN, SNACK_COLOR, snack)

        hud_height = 70
        hud_surface = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
        hud_surface.fill(HUD_BACKGROUND_COLOR)
        SCREEN.blit(hud_surface, (0, 0))

        draw_text(f"Snacks: {score}/{TARGET_SCORE}", font, TEXT_COLOR, SCREEN, 20, 5)
        draw_text(f"Time: {int(remaining_time)}s", font, TEXT_COLOR, SCREEN, 20, 35)

        instructions_y_start = SCREEN_HEIGHT - 70
        draw_text("Movement: A/D or Q/D or Arrow Keys", font, TEXT_COLOR, SCREEN, 10, instructions_y_start)
        draw_text("Press H for Help | P to Pause", font, TEXT_COLOR, SCREEN, 10, instructions_y_start + 35)

        if finish_line_active:
            finish_line_y += PLAYER_SPEED + FINISH_LINE_SPEED_FACTOR
            pygame.draw.line(SCREEN, FINISH_LINE_COLOR, (0, finish_line_y), (SCREEN_WIDTH, finish_line_y), 7)

            if player_y <= finish_line_y and not game_over: # Player crosses
                if score >= TARGET_SCORE:
                    game_outcome_text = "YOU WIN!"
                    game_outcome_details = f"You collected {score} snacks!"
                    game_outcome_color = WIN_TEXT_COLOR
                else:
                    game_outcome_text = "GAME OVER!"
                    game_outcome_details = "Not enough snacks!"
                    game_outcome_color = LOSE_TEXT_COLOR
                game_over = True
                current_game_state = STATE_GAME_OVER
            elif finish_line_y > SCREEN_HEIGHT and not game_over: # Finish line scrolled off screen
                game_outcome_text = "GAME OVER!"
                game_outcome_details = "The finish line passed you!"
                game_outcome_color = LOSE_TEXT_COLOR
                game_over = True
                current_game_state = STATE_GAME_OVER

    elif current_game_state == STATE_GAME_OVER:
        SCREEN.fill(BACKGROUND_COLOR)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR_DARK)
        SCREEN.blit(overlay, (0,0))

        if game_outcome_text:
            draw_text(game_outcome_text, large_font, game_outcome_color, SCREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, center=True)
        if game_outcome_details:
            draw_text(game_outcome_details, font, game_outcome_color, SCREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)

        draw_text("Press R to Restart or Q to Quit", font, TEXT_COLOR, SCREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, center=True)

    pygame.display.flip() # Update the full display

pygame.quit()
sys.exit()
                running = False

    if help_visible:
        SCREEN.fill(BLACK) # Clear screen for help menu
        draw_text("Help:", large_font, WHITE, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 100)
        draw_text("Collect at least 20 snacks.", font, WHITE, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20)
    if help_visible:
        SCREEN.fill(BACKGROUND_COLOR) # Fill with main background

        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR_DARK)
        SCREEN.blit(overlay, (0, 0))

        title_text = "Help Menu"
        title_surf = large_font.render(title_text, True, HELP_TITLE_COLOR)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        SCREEN.blit(title_surf, title_rect)

        help_lines = [
            ("Collect at least 20 snacks to win.", SCREEN_HEIGHT // 2 - 20),
            ("Reach the finish line after it appears (timer ends).", SCREEN_HEIGHT // 2 + 20),
            ("Movement: A/D or Q/D or Arrow Keys.", SCREEN_HEIGHT // 2 + 60),
            ("Press H to close this help menu.", SCREEN_HEIGHT // 2 + 120)
        ]
        for line, y_pos in help_lines:
            line_surf = font.render(line, True, HELP_INFO_COLOR)
            line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            SCREEN.blit(line_surf, line_rect)

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
        SCREEN.fill(BACKGROUND_COLOR)

        # Draw player
        pygame.draw.rect(SCREEN, PLAYER_COLOR, player_rect)

        # Draw snacks
        for snack in snacks:
            pygame.draw.ellipse(SCREEN, SNACK_COLOR, snack) # Draw snacks as ellipses

        # HUD for Score and Timer
        hud_height = 70
        hud_surface = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
        hud_surface.fill(HUD_BACKGROUND_COLOR)
        SCREEN.blit(hud_surface, (0, 0))

        draw_text(f"Snacks: {score}/20", font, TEXT_COLOR, 20, 5)
        draw_text(f"Time: {int(remaining_time)}s", font, TEXT_COLOR, 20, 35)

        # Movement instructions and help prompt at the bottom
        instructions_y_start = SCREEN_HEIGHT - 70
        draw_text("Movement: A/D or Q/D or Arrow Keys", font, TEXT_COLOR, 10, instructions_y_start)
        draw_text("Press H for Help", font, TEXT_COLOR, 10, instructions_y_start + 35)

        # Finish line logic
        if finish_line_active:
            # Move finish line towards the bottom of the screen, similar to snacks
            finish_line_y += player_speed + 0.0001 # Use the same speed as snacks for consistent movement
            pygame.draw.line(SCREEN, FINISH_LINE_COLOR, (0, finish_line_y), (SCREEN_WIDTH, finish_line_y), 7) # Thicker line
            
            # Player crosses finish line (or passes it)
            if player_y <= finish_line_y:
                if score >= 20:
                    game_outcome_text = "YOU WIN!"
                    game_outcome_details = f"You collected {score} snacks!"
                    game_outcome_color = WIN_TEXT_COLOR
                else:
                    game_outcome_text = "GAME OVER!"
                    game_outcome_details = "Not enough snacks!"
                    game_outcome_color = LOSE_TEXT_COLOR
                game_over = True
        
        # Game over if timer runs out AND not enough snacks AND player hasn't crossed finish line
        #if remaining_time <= 0 and not game_over and score < 20 and player_y > finish_line_y:
        #    draw_text("TIME'S UP! GAME OVER!", large_font, RED, SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2)
        #    game_over = True
    else: # Game is over
        SCREEN.fill(BACKGROUND_COLOR) # Clear with background

        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR_DARK)
        SCREEN.blit(overlay, (0,0))

        # Draw the final game outcome message
        if game_outcome_text:
            outcome_surf = large_font.render(game_outcome_text, True, game_outcome_color)
            outcome_rect = outcome_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            SCREEN.blit(outcome_surf, outcome_rect)

            if game_outcome_details:
                details_surf = font.render(game_outcome_details, True, game_outcome_color) # Can use TEXT_COLOR for details if preferred
                details_rect = details_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                SCREEN.blit(details_surf, details_rect)

        # Draw Restart/Quit prompt
        restart_prompt_text = "Press R to Restart or Q to Quit"
        prompt_surf = font.render(restart_prompt_text, True, TEXT_COLOR)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        SCREEN.blit(prompt_surf, prompt_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()