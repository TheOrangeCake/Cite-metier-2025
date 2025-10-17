#--Start--

import random

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
SKY_BLUE = (135, 206, 235)
RIVER_BLUE = (64, 164, 223)  # New river color

# Paddle
# paddle color
rect_color = BLUE
#Starting coordinates of the paddle
rect_x = 400
rect_y = 580
#initial speed of the paddle
rect_change_x = 0
rect_change_y = 0
#speed of the paddle
rect_speed_x = 6
rect_speed_y = -6
#paddle size
rect_size_x = 200
rect_size_y = 20

# Ball
#initial position of the ball
ball_x = 50
ball_y = 50
#speed of the ball
ball_change_x = 5
ball_change_y = 5
#ball size
ball_size_x = 15
ball_size_y = 15
#ball color
ball_color = BLACK

# Screen
screen_color = BLACK

# Clouds
class Cloud:
    def __init__(self):
        self.x = random.randint(0, 800)
        self.y = random.randint(50, 200)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(30, 70)
    
    def update(self):
        self.x += self.speed
        if self.x > 850:
            self.x = -50
            self.y = random.randint(50, 200)
    
    def draw(self, screen):
        import pygame
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x + self.size*0.8), int(self.y - self.size*0.2)), int(self.size*0.8))
        pygame.draw.circle(screen, WHITE, (int(self.x + self.size*1.5), int(self.y)), int(self.size*0.9))
        pygame.draw.circle(screen, WHITE, (int(self.x + self.size*0.8), int(self.y + self.size*0.2)), int(self.size*0.7))

# Mountains
class Mountain:
    def __init__(self):
        self.x = random.randint(-100, 900)
        self.y = random.randint(400, 550)
        self.width = random.randint(200, 400)
        self.height = random.randint(100, 250)
        self.color = (random.randint(50, 100), random.randint(50, 100), random.randint(50, 100))
    
    def draw(self, screen):
        import pygame
        points = [
            (self.x, self.y),
            (self.x + self.width//2, self.y - self.height),
            (self.x + self.width, self.y)
        ]
        pygame.draw.polygon(screen, self.color, points)

# Trees
class Tree:
    def __init__(self):
        self.x = random.randint(0, 800)
        self.y = random.randint(450, 550)
        self.trunk_width = 15
        self.trunk_height = random.randint(30, 50)
        self.leaves_size = random.randint(25, 40)
        self.trunk_color = (101, 67, 33)
        self.leaves_color = (random.randint(0, 50), random.randint(100, 150), random.randint(0, 50))
    
    def draw(self, screen):
        import pygame
        # Draw trunk
        pygame.draw.rect(screen, self.trunk_color, 
                        (self.x - self.trunk_width//2, self.y, self.trunk_width, self.trunk_height))
        # Draw leaves
        pygame.draw.circle(screen, self.leaves_color, 
                          (self.x, self.y - self.leaves_size//2), self.leaves_size)

# River
class River:
    def __init__(self):
        self.y = 550  # Position of the river
        self.width = 800  # Full width of screen
        self.height = 50  # Height of river
        self.wave_offset = 0
    
    def update(self):
        self.wave_offset += 0.1
    
    def draw(self, screen):
        import pygame
        # Draw main river body
        pygame.draw.rect(screen, RIVER_BLUE, (0, self.y, self.width, self.height))
        
        # Draw wave patterns
        for i in range(0, self.width, 20):
            wave_height = 3 * pygame.math.Vector2(1, 0).rotate(self.wave_offset * 50 + i).y
            pygame.draw.arc(screen, (100, 180, 255), 
                           (i, self.y - 2, 20, 10), 0, 3.14, 2)

# Boat
class Boat:
    def __init__(self):
        self.x = 0
        self.y = 530  # Position on the river
        self.speed = 2
        self.width = 60
        self.height = 30
    
    def update(self):
        self.x += self.speed
        if self.x > 850:
            self.x = -50
    
    def draw(self, screen):
        import pygame
        # Draw boat hull
        pygame.draw.ellipse(screen, (139, 69, 19), (self.x, self.y, self.width, self.height))
        # Draw mast
        pygame.draw.line(screen, (139, 69, 19), (self.x + self.width//2, self.y), (self.x + self.width//2, self.y - 40), 3)
        # Draw sail
        pygame.draw.polygon(screen, WHITE, [
            (self.x + self.width//2, self.y - 5),
            (self.x + self.width//2 + 25, self.y - 20),
            (self.x + self.width//2, self.y - 35)
        ])

clouds = [Cloud() for _ in range(5)]
mountains = [Mountain() for _ in range(3)]
trees = [Tree() for _ in range(8)]
river = River()  # Create river instance
boat = Boat()    # Create boat instance

def custom_draw():
    # Draw sky background
    import pygame
    screen = pygame.display.get_surface()
    screen.fill(SKY_BLUE)
    
    # Draw mountains
    for mountain in mountains:
        mountain.draw(screen)
    
    # Draw clouds
    for cloud in clouds:
        cloud.draw(screen)
    
    # Draw river
    river.draw(screen)
    
    # Draw boat
    boat.draw(screen)
    
    # Draw trees
    for tree in trees:
        tree.draw(screen)
	
def custom_interaction():
    # Update clouds
    for cloud in clouds:
        cloud.update()
    
    # Update river
    river.update()
    
    # Update boat
    boat.update()

#--End--