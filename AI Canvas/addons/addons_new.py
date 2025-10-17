#--Start--

import pygame
import random

background_color = (0, 0, 0)

def left_press(state, screen):
	pass

def right_press(state, screen):
	pass

def up_press(state, screen):
	if not state["is_jumping"]:
		state["velocity"] = state["jump_power"]
		state["is_jumping"] = True

def down_press(state, screen):
	pass

def reset_game(state):
	state["y"] = state["GROUND_Y"]
	state["velocity"] = 0
	state["is_jumping"] = False
	state["obstacles"] = []
	state["score"] = 0
	state["game_over"] = False

def custom_draw(screen, state):
	# Update screen-dependent values
	state["GAME_WIDTH"], state["GAME_HEIGHT"] = screen.get_size()
	state["GROUND_Y"] = int(state["GAME_HEIGHT"] * 0.75)
	state["width"] = int(state["GAME_WIDTH"] * 0.04)
	state["height"] = int(state["GAME_HEIGHT"] * 0.12)

	if not state["game_over"]:
		# Dino physics
		state["velocity"] += state["gravity"]
		state["y"] += state["velocity"]

		if state["y"] >= state["GROUND_Y"]:
			state["y"] = state["GROUND_Y"]
			state["is_jumping"] = False

		# Obstacles
		state["obstacle_timer"] += 1
		if state["obstacle_timer"] >= state["obstacle_frequency"]:
			state["obstacle_timer"] = 0
			height = random.choice([
				int(state["GAME_HEIGHT"] * 0.04),
				int(state["GAME_HEIGHT"] * 0.06)
			])
			y_pos = state["GROUND_Y"] + state["height"] - height
			color = random.choice([
				(255, 50, 50), (50, 255, 50),
				(50, 50, 255), (255, 255, 50)
			])
			state["obstacles"].append([
				state["GAME_WIDTH"], y_pos,
				int(state["GAME_WIDTH"] * 0.03), height, color
			])

		# Move & collision
		for obs in state["obstacles"][:]:
			obs[0] -= state["scroll_speed"]
			if obs[0] < -50:
				state["obstacles"].remove(obs)
				state["score"] += 1
			if (
				state["x"] + state["width"] > obs[0]
				and state["x"] < obs[0] + obs[2]
				and state["y"] + state["height"] > obs[1]
				and state["y"] < obs[1] + obs[3]
			):
				state["game_over"] = True

	# --- Drawing ---
	screen.fill(background_color)

	pygame.draw.line(
		screen, (150, 150, 150),
		(0, state["GROUND_Y"] + state["height"]),
		(state["GAME_WIDTH"], state["GROUND_Y"] + state["height"]),
		4
	)

	pygame.draw.rect(
		screen, (255, 255, 255),
		(state["x"], state["y"], state["width"], state["height"])
	)

	for obs in state["obstacles"]:
		pygame.draw.rect(screen, obs[4], obs[:4])

	font = pygame.font.SysFont(None, int(state["GAME_HEIGHT"] * 0.05))
	score_text = font.render(f'Score: {state["score"]}', True, (255, 255, 255))
	screen.blit(score_text, (20, 20))

	if state["game_over"]:
		over_text = font.render(
			'Game Over! Press Tab pour recommencer',
			True, (255, 255, 255)
		)
		text_rect = over_text.get_rect(
			center=(state["GAME_WIDTH"] // 2, state["GAME_HEIGHT"] // 2)
		)
		screen.blit(over_text, text_rect)

def custom_interaction(screen, state):
	keys = pygame.key.get_pressed()
	if keys[pygame.K_TAB]:
		reset_game(state)

#--End--