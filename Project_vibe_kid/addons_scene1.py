#--Start--

import pygame
import random

background_color = (135, 169, 219)  # Light blue sky

# Generate random stars for the background
stars = [(random.randint(0, 1300), random.randint(0, 800), random.randint(1, 3)) for _ in range(100)]

# Generate raindrops
raindrops = [(random.randint(0, 1300), random.randint(-800, 0)) for _ in range(200)]

# Dark clouds positions and sizes
clouds = [(random.randint(0, 1300), random.randint(50, 200), random.randint(80, 150)) for _ in range(15)]

# Lightning effect timer
lightning_timer = 0

def custom_draw(screen):
	global lightning_timer, clouds
	
	# Draw stars on the background
	for x, y, size in stars:
		pygame.draw.circle(screen, (255, 255, 255), (x, y), size)
	
	# Draw more realistic dark clouds using multiple ellipses
	cloud_rects = []
	for i in range(len(clouds)):
		x, y, width = clouds[i]
		# Base cloud ellipse
		rect1 = pygame.draw.ellipse(screen, (70, 70, 70), (x, y, width, width//2))
		# Additional overlapping ellipses for realism
		rect2 = pygame.draw.ellipse(screen, (70, 70, 70), (x + width//3, y - 10, width//2, width//3))
		rect3 = pygame.draw.ellipse(screen, (70, 70, 70), (x + width//2, y, width//1.5, width//4))
		rect4 = pygame.draw.ellipse(screen, (70, 70, 70), (x + width//4, y + 10, width//1.8, width//5))
		
		# Store cloud rectangles for collision detection
		cloud_rects.append(rect1.unionall([rect2, rect3, rect4]))
		
		# Move clouds to the left
		x -= 1
		if x < -width:
			x = 1300
		clouds[i] = (x, y, width)

	# Draw lightning randomly
	lightning_timer -= 1
	if lightning_timer <= 0:
		if random.randint(0, 3) == 0:  # More frequent lightning (6 -> 3)
			lightning_timer = 5  # Faster strikes
			# Randomize first lightning bolt position
			bolt1_x = random.randint(400, 800)
			points1 = [(bolt1_x, 100), (bolt1_x+40, 200), (bolt1_x, 200), (bolt1_x+60, 300)]
			# Check collision with clouds
			bolt1_rect = pygame.draw.lines(screen, (255, 255, 200), False, points1, 18)
			collided = any(bolt1_rect.colliderect(cloud) for cloud in cloud_rects)
			if collided:
				pygame.draw.lines(screen, (255, 0, 0), False, points1, 18)
			
			# Randomize second lightning bolt position
			bolt2_x = random.randint(700, 900)
			points2 = [(bolt2_x, 50), (bolt2_x+20, 150), (bolt2_x, 180), (bolt2_x+40, 250)]
			# Check collision with clouds
			bolt2_rect = pygame.draw.lines(screen, (200, 220, 255), False, points2, 12)
			collided = any(bolt2_rect.colliderect(cloud) for cloud in cloud_rects)
			if collided:
				pygame.draw.lines(screen, (255, 0, 0), False, points2, 12)
			
			# Additional 8 lightning bolts
			for i in range(8):
				bolt_x = random.randint(100, 1200)
				bolt_y = random.randint(50, 300)
				size_factor = random.uniform(0.5, 1.5)
				points = [
					(bolt_x, bolt_y),
					(bolt_x + int(20*size_factor), bolt_y + int(50*size_factor)),
					(bolt_x, bolt_y + int(60*size_factor)),
					(bolt_x + int(30*size_factor), bolt_y + int(100*size_factor))
				]
				color = (
					random.randint(200, 255),
					random.randint(200, 255),
					random.randint(200, 255)
				)
				width = random.randint(4, 12)
				# Draw and check collision
				bolt_rect = pygame.draw.lines(screen, color, False, points, width)
				collided = any(bolt_rect.colliderect(cloud) for cloud in cloud_rects)
				if collided:
					pygame.draw.lines(screen, (255, 0, 0), False, points, width)
	
	# Draw blue rain
	for i in range(len(raindrops)):
		x, y = raindrops[i]
		pygame.draw.line(screen, (0, 0, 255), (x, y), (x, y + 5), 1)
		raindrops[i] = (x, y + 5)  # Move down
		if y > 800:
			raindrops[i] = (x, random.randint(-20, 0))  # Reset to top

	# Draw river at the bottom
	pygame.draw.rect(screen, (0, 100, 200), (0, 700, 1300, 100))

	# Draw pretty boat using polygons
	# Hull
	hull_points = [(500, 700), (650, 690), (750, 700), (600, 720)]
	pygame.draw.polygon(screen, (139, 69, 19), hull_points)
	# Sail
	sail_points = [(600, 690), (630, 620), (660, 690)]
	pygame.draw.polygon(screen, (255, 255, 255), sail_points)
	# Mast
	pygame.draw.line(screen, (101, 67, 33), (630, 690), (630, 620), 3)

def left_press(screen):
	pass
def right_press(screen):
	pass
def up_press(screen):
	pass
def down_press(screen):
	pass
def custom_interaction(screen):
	pass
#--End--