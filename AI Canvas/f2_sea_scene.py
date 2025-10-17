#--Start--

import pygame
import random
import math

background_color = (135, 206, 235)  # Sky blue

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

def draw_boat(screen, boat_x, boat_y, boat_w, boat_h):
	hull_color = (139, 69, 19)
	sail_color = (255, 255, 255)
	mast_color = (105, 105, 105)

	hull_height = boat_h // 2
	hull_bottom_y = boat_y + boat_h       # bottom aligned with boat rect
	hull_top_y = hull_bottom_y - hull_height

	# Hull trapezoid
	hull_points = [
		(boat_x, hull_top_y),
		(boat_x + boat_w, hull_top_y),
		(boat_x + 3*boat_w//4, hull_bottom_y),
		(boat_x + boat_w//4, hull_bottom_y)
	]
	pygame.draw.polygon(screen, hull_color, hull_points)

	# Optional bottom curve
	bottom_rect = pygame.Rect(boat_x + boat_w//4, hull_bottom_y - hull_height//6, boat_w//2, hull_height//6)
	pygame.draw.arc(screen, hull_color, bottom_rect, 3.14, 0, 3)

	# Mast
	mast_height = int(boat_h * 1.5)  # Increased mast height
	mast_x = boat_x + boat_w // 2
	mast_base_y = hull_top_y
	mast_top_y = mast_base_y - mast_height//2
	pygame.draw.line(screen, mast_color, (mast_x, mast_base_y), (mast_x, mast_top_y), 3)

	# Sail
	sail_points = [
		(mast_x, mast_top_y),
		(mast_x, mast_base_y),
		(mast_x + boat_w//3, mast_base_y)
	]
	pygame.draw.polygon(screen, sail_color, sail_points)

	# Flag (flipped to opposite direction)
	pygame.draw.polygon(screen, (255,0,0), [
		(mast_x, mast_top_y),
		(mast_x - 12, mast_top_y + 6),
		(mast_x, mast_top_y + 12)
	])


def custom_draw(screen, state):
	# Update screen-dependent values
	state["GAME_WIDTH"], state["GAME_HEIGHT"] = screen.get_size()
	state["GROUND_Y"] = int(state["GAME_HEIGHT"] * 0.75)
	state["width"] = int(state["GAME_WIDTH"] * 0.04)
	state["height"] = int(state["GAME_HEIGHT"] * 0.12)

	# Initialize clouds if not present
	if "clouds" not in state:
		state["clouds"] = []
		spacing = state["GAME_WIDTH"] // 8  # Space clouds evenly across screen
		for i in range(8):
			state["clouds"].append([
				i * spacing + random.randint(-50, 50),  # Add some randomness to positions
				random.randint(30, 150)
			])

	if not state["game_over"]:
		# Boat physics
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
			# Darker colors
			color = random.choice([
				(180, 40, 40), (40, 180, 40),
				(40, 40, 180), (180, 180, 40)
			])
			# Random shape type
			shape_type = random.choice(["triangle", "diamond", "pentagon"])
			state["obstacles"].append([
				state["GAME_WIDTH"], y_pos,
				int(state["GAME_WIDTH"] * 0.03), height, color, shape_type
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

		# Slowly move clouds
		for cloud in state["clouds"]:
			cloud[0] -= 0.2  # Slower movement
			if cloud[0] < -50:
				cloud[0] = state["GAME_WIDTH"] + 50
				cloud[1] = random.randint(30, 150)

	# --- Drawing ---
	screen.fill(background_color)

	# Draw fixed sun
	sun_color = (255, 255, 0)
	sun_radius = 50
	sun_x = state["GAME_WIDTH"] - 100
	sun_y = 80
	pygame.draw.circle(screen, sun_color, (int(sun_x), int(sun_y)), sun_radius)

	# Draw moving clouds
	cloud_color = (255, 255, 255)
	for cloud_x, cloud_y in state["clouds"]:
		# Fluffy cloud using multiple overlapping circles
		pygame.draw.circle(screen, cloud_color, (int(cloud_x), int(cloud_y)), 25)
		pygame.draw.circle(screen, cloud_color, (int(cloud_x + 20), int(cloud_y - 15)), 20)
		pygame.draw.circle(screen, cloud_color, (int(cloud_x + 40), int(cloud_y)), 25)
		pygame.draw.circle(screen, cloud_color, (int(cloud_x + 20), int(cloud_y + 15)), 20)
		pygame.draw.circle(screen, cloud_color, (int(cloud_x + 10), int(cloud_y)), 22)
		pygame.draw.circle(screen, cloud_color, (int(cloud_x + 30), int(cloud_y)), 22)

	# Draw sea water
	wave_y = state["GROUND_Y"] + state["height"]
	water_rect = pygame.Rect(
		0, wave_y,
		state["GAME_WIDTH"], state["GAME_HEIGHT"]
	)
	pygame.draw.rect(screen, (0, 100, 200), water_rect)

	# Draw wavy blue line like the sea
	wave_color = (30, 144, 255)  # Deep sky blue
	wave_amplitude = 8
	wave_frequency = 0.02
	wave_speed = 2
	points = []
	for x in range(0, state["GAME_WIDTH"] + 5, 5):
		y = wave_y + wave_amplitude * math.sin(x * wave_frequency + state["obstacle_timer"] * wave_speed / 10)
		points.append((x, y))
	if len(points) > 1:
		pygame.draw.lines(screen, wave_color, False, points, 4)

	# Draw boat instead of rectangle
	boat_x = state["x"]
	boat_y = state["y"]
	boat_w = state["width"]
	boat_h = state["height"]

	draw_boat(screen, boat_x, boat_y, boat_w, boat_h)

	# Mast (vertical line) - removed since it's now part of draw_boat

	for obs in state["obstacles"]:
		# Draw different shapes based on type
		x, y, w, h, color, shape_type = obs[0], obs[1], obs[2], obs[3], obs[4], obs[5]
		
		if shape_type == "triangle":
			points = [
				(x + w//2, y),      # Top point
				(x, y + h),         # Bottom left
				(x + w, y + h)      # Bottom right
			]
			pygame.draw.polygon(screen, color, points)
		elif shape_type == "diamond":
			points = [
				(x, y),             # Top left
				(x + w, y),         # Top right
				(x + w, y + h),     # Bottom right
				(x, y + h)          # Bottom left
			]
			pygame.draw.polygon(screen, color, points)
		elif shape_type == "pentagon":
			points = [
				(x + w//2, y),           # Top point
				(x + w, y),              # Top right
				(x + w, y + h),          # Bottom right
				(x, y + h),              # Bottom left
				(x, y)                   # Top left
			]
			pygame.draw.polygon(screen, color, points)

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