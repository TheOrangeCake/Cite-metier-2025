#--Start--

import pygame
import random

# Colors
background_color = (0, 0, 0)

# Game variables (these will adapt later)
dino_x = 50
dino_y = 0
dino_width = 0
dino_height = 0
dino_velocity = 0
is_jumping = False
gravity = 1
jump_power = -18

obstacles = []
obstacle_timer = 0
obstacle_frequency = 60
scroll_speed = 7
score = 0
game_over = False

# These will be updated dynamically from screen
GROUND_Y = 0
GAME_WIDTH = 0
GAME_HEIGHT = 0


def left_press(screen):
	pass


def right_press(screen):
	pass


def up_press(screen):
	global dino_velocity, is_jumping
	if not is_jumping:
		dino_velocity = jump_power
		is_jumping = True


def down_press(screen):
	pass


def reset_game():
	global dino_y, dino_velocity, is_jumping, obstacles, score, game_over
	dino_y = GROUND_Y
	dino_velocity = 0
	is_jumping = False
	obstacles = []
	score = 0
	game_over = False


def custom_draw(screen):
	global dino_y, dino_velocity, is_jumping, obstacles, obstacle_timer, score, game_over
	global GROUND_Y, GAME_WIDTH, GAME_HEIGHT, dino_width, dino_height

	# Dynamically get size of play area
	GAME_WIDTH, GAME_HEIGHT = screen.get_size()
	GROUND_Y = int(GAME_HEIGHT * 0.75)

	# Set Dino size proportional to area
	dino_width = int(GAME_WIDTH * 0.04)
	dino_height = int(GAME_HEIGHT * 0.12)

	if not game_over:
		# Update dino position
		dino_velocity += gravity
		dino_y += dino_velocity

		if dino_y >= GROUND_Y:
			dino_y = GROUND_Y
			is_jumping = False

		# Generate obstacles
		obstacle_timer += 1
		if obstacle_timer >= obstacle_frequency:
			obstacle_timer = 0
			# Randomly pick shape and height
			height = random.choice([int(GAME_HEIGHT * 0.04), int(GAME_HEIGHT * 0.06)])
			y_pos = GROUND_Y + dino_height - height
			obstacles.append([GAME_WIDTH, y_pos, int(GAME_WIDTH * 0.03), height])

		# Move obstacles and check collisions
		for obs in obstacles[:]:
			obs[0] -= scroll_speed
			if obs[0] < -50:
				obstacles.remove(obs)
				score += 1
			if (
				dino_x + dino_width > obs[0]
				and dino_x < obs[0] + obs[2]
				and dino_y + dino_height > obs[1]
				and dino_y < obs[1] + obs[3]
			):
				game_over = True

	# Draw background
	screen.fill(background_color)

	# Draw ground line
	pygame.draw.line(screen, (150, 150, 150), (0, GROUND_Y + dino_height), (GAME_WIDTH, GROUND_Y + dino_height), 4)

	# Draw Dino
	pygame.draw.rect(screen, (255, 255, 255), (dino_x, dino_y, dino_width, dino_height))

	# Draw obstacles
	for obs in obstacles:
		pygame.draw.rect(screen, (255, 50, 50), obs)

	# Display score
	font = pygame.font.SysFont(None, int(GAME_HEIGHT * 0.05))
	score_text = font.render(f'Score: {score}', True, (255, 255, 255))
	screen.blit(score_text, (20, 20))

	if game_over:
		over_text = font.render('Game Over! Press Tab pour recommencer', True, (255, 255, 255))
		text_rect = over_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))
		screen.blit(over_text, text_rect)


def custom_interaction(screen):
	keys = pygame.key.get_pressed()
	if keys[pygame.K_TAB]:
		reset_game()

#--End--
