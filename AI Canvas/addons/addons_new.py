#--Start--

import pygame
import random

background_color = (180, 180, 180)  # Darker grey
raindrops = []
lightning_timer = 0
lightning_duration = 0

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

def draw_car(screen, state):
	car_x = state["x"]
	car_y = state["y"] + state["height"]
	car_width = state["width"]
	car_height = state["height"] * 0.45  # Lower profile

	# Wheels
	wheel_radius = int(car_height * 0.25)
	wheel_y = int(car_y)
	wheel_color = (30, 30, 30)
	hub_color = (180, 180, 180)

	for offset in [0.25, 0.75]:
		center_x = int(car_x + car_width * offset)
		pygame.draw.circle(screen, wheel_color, (center_x, wheel_y), wheel_radius)
		pygame.draw.circle(screen, hub_color, (center_x, wheel_y), wheel_radius // 2)

	# Body
	body_bottom = wheel_y - wheel_radius
	body_top = body_bottom - car_height
	body_color = (200, 0, 0)
	body_rect = pygame.Rect(car_x, body_top, car_width, car_height)
	pygame.draw.rect(screen, body_color, body_rect)

	# Roof
	roof_height = car_height * 0.3
	roof_top = body_top - roof_height
	roof_rect = pygame.Rect(car_x + car_width * 0.25, roof_top, car_width * 0.5, roof_height)
	pygame.draw.rect(screen, body_color, roof_rect)

	# Windows
	window_color = (173, 216, 230)
	window_border = (100, 100, 100)
	window_rect = pygame.Rect(car_x + car_width * 0.3, roof_top + 4, car_width * 0.4, roof_height - 8)
	pygame.draw.rect(screen, window_color, window_rect)
	pygame.draw.rect(screen, window_border, window_rect, 2)

	# Outline
	pygame.draw.rect(screen, (0, 0, 0), body_rect, 2)
	pygame.draw.rect(screen, (0, 0, 0), roof_rect, 2)

def point_in_triangle(px, py, x1, y1, x2, y2, x3, y3):
	# Compute barycentric coordinates
	denom = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
	if denom == 0:
		return False
	a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / denom
	b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / denom
	c = 1 - a - b
	# Check if point is inside triangle
	return 0 <= a <= 1 and 0 <= b <= 1 and 0 <= c <= 1

def custom_draw(screen, state):
	global raindrops, lightning_timer, lightning_duration
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
			obstacle_type = random.choice(["triangle", "rock", "log", "cone", "barrier", "sign"])
			height = random.choice([
				int(state["GAME_HEIGHT"] * 0.04),
				int(state["GAME_HEIGHT"] * 0.06)
			])
			y_pos = state["GROUND_Y"] + state["height"] - height
			color = random.choice([
				(255, 50, 50), (50, 255, 50),
				(50, 50, 255), (255, 255, 50)
			])
			# Store obstacle as [x, y, width, height, color, type]
			state["obstacles"].append([
				state["GAME_WIDTH"], y_pos,
				int(state["GAME_WIDTH"] * 0.03), height, color, obstacle_type
			])

		# Move & collision
		for obs in state["obstacles"][:]:
			obs[0] -= state["scroll_speed"]
			if obs[0] < -50:
				state["obstacles"].remove(obs)
				state["score"] += 1
			
			# Collision check using bounding box
			x, y, w, h = obs[0], obs[1], obs[2], obs[3]
			car_left = state["x"]
			car_right = state["x"] + state["width"]
			car_top = state["y"]
			car_bottom = state["y"] + state["height"]
			
			if (car_right > x and car_left < x + w and 
				car_bottom > y and car_top < y + h):
				state["game_over"] = True

	# --- Drawing ---
	# Handle lightning
	lightning_timer -= 1
	lightning_duration -= 1

	if lightning_timer <= 0:
		lightning_timer = random.randint(60, 180)  # More frequent lightning
		lightning_duration = random.randint(10, 25)  # Longer duration

	if lightning_duration > 0:
		background_color_current = (255, 255, 255)
		bolt_x = random.randint(50, state["GAME_WIDTH"] - 50)
		bolt_y = 30
		points = [(bolt_x, bolt_y)]
		for _ in range(5):
			bolt_x += random.randint(-20, 20)
			bolt_y += random.randint(20, 40)
			points.append((bolt_x, bolt_y))
		if len(points) > 1:
			pygame.draw.lines(screen, (200, 200, 255), False, points, 4)  # Brighter bolt

		thunder_points = [
			(bolt_x - 50, bolt_y + 60),
			(bolt_x, bolt_y + 30),
			(bolt_x + 30, bolt_y + 45),
			(bolt_x - 15, bolt_y + 90),
			(bolt_x + 45, bolt_y + 75),
			(bolt_x, bolt_y + 120)
		]
		pygame.draw.polygon(screen, (255, 255, 100), thunder_points)  # Brighter thunder
	else:
		background_color_current = background_color

	screen.fill(background_color_current)

	# Moon
	moon_x = state["GAME_WIDTH"] - 100
	moon_y = 80
	pygame.draw.circle(screen, (255, 255, 255), (moon_x, moon_y), 40)

	# Clouds
	cloud_base_y = 120  # Changed from 30 to 120 to place below moon
	for i in range(6):
		base_x = i * 200 + 100
		base_y = cloud_base_y
		offset1 = random.randint(-20, 20)
		offset2 = random.randint(-15, 15)
		size_variation = random.uniform(0.8, 1.2)

		pygame.draw.ellipse(screen, (100, 100, 100),
							(base_x + offset1, base_y,
							int(150 * size_variation), int(60 * size_variation)))
		pygame.draw.ellipse(screen, (100, 100, 100),
							(base_x + 50 + offset2, base_y - 20 + offset1,
							int(130 * size_variation), int(60 * size_variation)))
		pygame.draw.ellipse(screen, (100, 100, 100),
							(base_x + 100 + offset1, base_y + offset2,
							int(140 * size_variation), int(60 * size_variation)))

	# Rain
	for drop in raindrops[:]:
		drop[1] += 10
		pygame.draw.line(screen, (50, 50, 255), (drop[0], drop[1]), (drop[0], drop[1]+10), 2)
		if drop[1] > state["GAME_HEIGHT"]:
			raindrops.remove(drop)

	if len(raindrops) < 150:
		for _ in range(10):
			x = random.randint(0, state["GAME_WIDTH"])
			y = random.randint(cloud_base_y, cloud_base_y + 60)  # Start from cloud bottom
			raindrops.append([x, y])

	# Ground (same height as before)
	ground_rect = pygame.Rect(
		0, state["GROUND_Y"] + state["height"],
		state["GAME_WIDTH"], state["GAME_HEIGHT"] - (state["GROUND_Y"] + state["height"])
	)
	pygame.draw.rect(screen, (139, 69, 19), ground_rect)

	# Ground texture
	for _ in range(100):
		x = random.randint(0, state["GAME_WIDTH"])
		y = random.randint(state["GROUND_Y"] + state["height"], state["GAME_HEIGHT"])
		width = random.randint(2, 6)
		height = random.randint(2, 6)
		pygame.draw.ellipse(screen, (101, 67, 33), (x, y, width, height))

	pygame.draw.line(screen, (101, 67, 33),
					(0, state["GROUND_Y"] + state["height"]),
					(state["GAME_WIDTH"], state["GROUND_Y"] + state["height"]), 4)

	# Draw car
	draw_car(screen, state)

	# Draw obstacles
	for obs in state["obstacles"]:
		x, y, w, h, color, obs_type = obs
		if obs_type == "triangle":
			points = [
				(x, y + h),      # bottom-left
				(x + w, y + h),  # bottom-right
				(x + w/2, y)     # top-middle
			]
			pygame.draw.polygon(screen, color, points)
		elif obs_type == "rock":
			pygame.draw.circle(screen, color, (x + w//2, y + h//2), w//2)
		elif obs_type == "log":
			log_rect = pygame.Rect(x, y, w, h)
			pygame.draw.rect(screen, color, log_rect)
		elif obs_type == "cone":
			points = [
				(x + w/2, y),          # top
				(x, y + h),            # bottom-left
				(x + w, y + h)         # bottom-right
			]
			pygame.draw.polygon(screen, (255, 165, 0), points)  # Orange cone
			# Stripes
			for i in range(1, 4):
				strip_y = y + (h * i // 4)
				pygame.draw.line(screen, (255, 255, 255), 
							   (x + w*0.2, strip_y), 
							   (x + w*0.8, strip_y), 2)
		elif obs_type == "barrier":
			barrier_rect = pygame.Rect(x, y, w, h)
			pygame.draw.rect(screen, (255, 0, 0), barrier_rect)  # Red barrier
			# White stripes
			stripe_height = h // 3
			for i in range(3):
				if i % 2 == 0:
					stripe = pygame.Rect(x, y + i * stripe_height, w, stripe_height)
					pygame.draw.rect(screen, (255, 255, 255), stripe)
		elif obs_type == "sign":
			# Sign post
			pygame.draw.rect(screen, (105, 105, 105), (x + w//2 - 2, y + h//3, 4, h*2//3))
			# Sign board (diamond shape)
			sign_points = [
				(x + w//2, y),           # top
				(x + w, y + h//3),       # right
				(x + w//2, y + 2*h//3),  # bottom
				(x, y + h//3)            # left
			]
			pygame.draw.polygon(screen, (255, 0, 0), sign_points)  # Red diamond
			# White cross
			pygame.draw.rect(screen, (255, 255, 255), (x + w//2 - 3, y + h//6, 6, h//3))
			pygame.draw.rect(screen, (255, 255, 255), (x + w//4, y + h//3 - 3, w//2, 6))

	# Score
	font = pygame.font.SysFont(None, int(state["GAME_HEIGHT"] * 0.05))
	score_text = font.render(f'Score: {state["score"]}', True, (0, 0, 0))
	screen.blit(score_text, (20, 20))

	# Game over
	if state["game_over"]:
		over_text = font.render(
			'Game Over! Presses Tab pour recommencer',
			True, (0, 0, 0)
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