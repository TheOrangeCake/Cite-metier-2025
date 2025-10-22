#--Start--

import pygame
import random

background_color = (10, 5, 30)

# Car class to manage position and movement
class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.randint(3, 7)
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        self.width = 60
        self.height = 30

    def update(self):
        self.x += self.speed
        # Reset car position when it goes off screen
        if self.x > 1300:
            self.x = -60
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )

    def draw(self, screen):
        # Draw car body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw wheels
        pygame.draw.circle(screen, (20, 20, 20), (self.x + 15, self.y + 30), 8)
        pygame.draw.circle(screen, (20, 20, 20), (self.x + 45, self.y + 30), 8)
        # Draw windows
        pygame.draw.rect(screen, (180, 220, 255), (self.x + 5, self.y + 5, 15, 15))
        pygame.draw.rect(screen, (180, 220, 255), (self.x + 40, self.y + 5, 15, 15))

# Initialize cars
cars = [Car(i * 150, 720) for i in range(6)]

# Precompute tree data to prevent movement
tree_data = []

def initialize_trees(screen):
    global tree_data
    if tree_data:
        return  # Already initialized
    
    # Main tree positions
    tree_positions = [100, 200, 300, 430, 530, 650, 760, 880, 1000, 1100, 1200]
    for pos in tree_positions:
        height_variation = random.uniform(0.7, 1.3)
        base_y = random.randint(620, 680)
        tree_data.append((pos, base_y, height_variation))
    
    # Additional trees
    additional_trees = [
        (150, random.randint(620, 680), random.uniform(0.8, 1.2)),
        (275, random.randint(620, 680), random.uniform(0.9, 1.1)),
        (350, random.randint(620, 680), random.uniform(0.7, 1.3)),
        (490, random.randint(620, 680), random.uniform(0.8, 1.2)),
        (620, random.randint(620, 680), random.uniform(0.9, 1.1)),
        (730, random.randint(620, 680), random.uniform(0.7, 1.3)),
        (850, random.randint(620, 680), random.uniform(0.8, 1.2)),
        (970, random.randint(620, 680), random.uniform(0.9, 1.1)),
        (1070, random.randint(620, 680), random.uniform(0.7, 1.3)),
        (1170, random.randint(620, 680), random.uniform(0.8, 1.2))
    ]
    for x, y, scale in additional_trees:
        tree_data.append((x, y, scale))

# Function to draw a tree using polygons
def draw_tree(screen, x, y, height_scale=1.0):
    trunk_height = int(40 * height_scale)
    # Trunk
    pygame.draw.rect(screen, (101, 67, 33), (x-5, y - trunk_height, 10, trunk_height))
    
    # Leaves (darker green)
    pygame.draw.polygon(screen, (34, 102, 34), [
        (x, y - trunk_height - 20),
        (x-25, y - trunk_height + 10),
        (x+25, y - trunk_height + 10)
    ])
    pygame.draw.polygon(screen, (34, 102, 34), [
        (x, y - trunk_height - 40),
        (x-20, y - trunk_height - 10),
        (x+20, y - trunk_height - 10)
    ])
    pygame.draw.polygon(screen, (34, 102, 34), [
        (x, y - trunk_height - 55),
        (x-15, y - trunk_height - 25),
        (x+15, y - trunk_height - 25)
    ])

def left_press(state, screen):
	pass
def right_press(state, screen):
	pass
def up_press(state, screen):
	pass
def down_press(state, screen):
	pass
def custom_draw(screen, state):
	# Draw sky
	screen.fill(background_color)
	
	# Draw stars (blinking randomly)
	for _ in range(100):
		x = random.randint(0, screen.get_width())
		y = random.randint(0, 500)
		brightness = random.randint(150, 255)
		if random.random() < 0.3:  # 30% chance to blink
			pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
	
	# Draw water
	water_rect = pygame.Rect(0, 600, screen.get_width(), 200)
	pygame.draw.rect(screen, (0, 10, 40), water_rect)
	
	# Draw buildings (moved lower)
	buildings = [
		(50, 450, 100, 150),
		(160, 350, 80, 250),
		(250, 400, 120, 200),
		(380, 300, 90, 300),
		(480, 430, 110, 170),
		(600, 370, 100, 230),
		(710, 450, 90, 150),
		(810, 390, 130, 210),
		(950, 420, 80, 180),
		(1040, 360, 100, 240),
		(1150, 410, 120, 190)
	]
	
	for x, y, width, height in buildings:
		# Draw building
		building_rect = pygame.Rect(x, y, width, height)
		pygame.draw.rect(screen, (40, 40, 60), building_rect)
		
		# Draw windows
		window_size = 8
		window_spacing = 15
		for win_y in range(y + 15, y + height - 10, window_spacing):
			for win_x in range(x + 10, x + width - 10, window_spacing):
				if (win_x + win_y) % 3 == 0:  # Some windows are lit
					color = (255, 255, 200)
				else:
					color = (30, 30, 50)
				pygame.draw.rect(screen, color, (win_x, win_y, window_size, window_size))
	
	# Initialize trees once
	initialize_trees(screen)
	
	# Draw all precomputed trees
	for x, y, scale in tree_data:
		draw_tree(screen, x, y, scale)
	
	# Draw moon (without reflection)
	moon_pos = (1100, 100)
	pygame.draw.circle(screen, (255, 255, 220), moon_pos, 40)
	
	# Draw road
	road_rect = pygame.Rect(0, 700, screen.get_width(), 100)
	pygame.draw.rect(screen, (50, 50, 50), road_rect)
	
	# Draw road markings
	for i in range(0, screen.get_width(), 40):
		pygame.draw.rect(screen, (200, 200, 200), (i, 745, 20, 10))
	
	# Draw street lamps
	for i in range(50, screen.get_width(), 150):
		# Lamp head (moved up)
		pygame.draw.circle(screen, (255, 255, 200), (i + 2, 600), 8)
		# Light beam (reduced to edge of road)
		light_points = [(i - 20, 700), (i + 25, 700), (i + 2, 600)]
		pygame.draw.polygon(screen, (255, 255, 180), light_points)
	
	# Update and draw cars
	for car in cars:
		car.update()
		car.draw(screen)
	
def custom_interaction(screen, state):
	pass
#--End--