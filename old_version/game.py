import pygame
from bot_filter import response_analizer
from changes import addons
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import importlib
import change_logger

pygame.init()

def v(name):
    return getattr(addons, name)

with open('game.py', 'r', encoding='utf-8') as file:
    main_file = file.read()

with open('addons_base.py', 'r', encoding='utf-8') as file:
    base_addons = file.read()
def reset_addons():
    with open('changes/addons.py', 'w') as file:
        file.write(base_addons)

#Watcher
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        importlib.reload(addons)

        # to check
        change_logger.get_logger().on_file_modified()

        return super().on_modified(event)

path = Path("changes/addons.py")
observer = Observer()
handler = MyHandler()
observer.schedule(handler, path, recursive=True)
observer.start()

#Initializing the display window
size = (1400,600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("pong")

score = 0

#input box
input_rect = pygame.Rect(800, 80, 200, 0)
base_font = pygame.font.SysFont('Calibri', 24, False, False)
user_text = 'Entres un prompt pour modifier le jeu'
reset = True
message = ''

#draws the paddle. Also restricts its movement between the edges
#of the window.
def drawrect(screen,x,y):
    if x <= 0:
        x = 0
    if x >= 800 - v('rect_size_x'):
        x = 800 - v('rect_size_x') 
    pygame.draw.rect(screen,v('rect_color'),[x,y,v('rect_size_x'),v('rect_size_y')])
    
# https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame
def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.
    
#game's main loop    
done = False
clock=pygame.time.Clock()
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                addons.rect_change_x = v('rect_speed_y')
            elif event.key == pygame.K_RIGHT:
                addons.rect_change_x = v('rect_speed_x')
            elif event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            elif event.key == pygame.K_RETURN:
                if reset == True:
                    user_text = ''
                    reset = False
                    continue
                moderation = response_analizer(user_text, main_file)
                if isinstance(moderation, dict):
                    status = moderation.get("status", "error")
                    message = moderation.get("message", "")
                else:
                    status = "OK"
                    message = moderation
                print(user_text)
                # print(message)
                user_text = 'Entres un prompt'
                reset = True
            elif event.key == pygame.K_ESCAPE:
                user_text = ''
            elif event.key == pygame.K_RSHIFT:
                reset_addons()
                importlib.reload(addons)
                user_text = 'Entres un prompt pour modifier le jeu'
                reset = True
            else:
                if reset == True:
                    user_text = ''
                    reset = False
                user_text += event.unicode
                message = ''
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                addons.rect_change_x = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                addons.rect_change_y = 0            
    screen.fill(v('screen_color'))

    # right back ground in white
    pygame.draw.rect(screen, (255,255,255), (800, 0, 600, 600))

    # add custom addons
    addons.custom_draw()
    addons.custom_interaction()

    addons.rect_x += v('rect_change_x')
    if addons.rect_x > 800 - v('rect_size_x'):
        addons.rect_x = 800 - v('rect_size_x')
    if addons.rect_x < 0:
        addons.rect_x = 0
    addons.rect_y += v('rect_change_y')
    addons.ball_x += v('ball_change_x')
    addons.ball_y += v('ball_change_y')
    
    #handles the movement of the ball.
    if v('ball_x') < 0:
        addons.ball_x = 0
        addons.ball_change_x = v('ball_change_x') * -1
    elif v('ball_x') > 785:
        addons.ball_x = 785
        addons.ball_change_x = v('ball_change_x') * -1
    elif v('ball_y') < 0:
        addons.ball_y = 0
        addons.ball_change_y = v('ball_change_y') * -1
    elif v('ball_x')>v('rect_x') and v('ball_x')<v('rect_x')+v('rect_size_x') and v('ball_y')==(600 - v('ball_size_y')):
        addons.ball_change_y = v('ball_change_y') * -1
        score = score + 1
    elif v('ball_y') > 600:
        addons.ball_change_y = v('ball_change_y') * -1
        score = 0                        
    pygame.draw.rect(screen,v('ball_color'),[v('ball_x'),v('ball_y'),v('ball_size_x'),v('ball_size_y')])
    drawrect(screen,v('rect_x'),v('rect_y'))
    
    #text
    #promt box
    blit_text(screen, user_text, (input_rect.x+20, 40), base_font, (0,0,0))
    #AI response
    blit_text(screen, message, (input_rect.x+20, 80), base_font, (200,30,100))

    #score board
    font = pygame.font.SysFont('Calibri', 20, False, False)
    text = font.render("Score = " + str(score), True, (0,0,0))
    screen.blit(text,[820,10]) 
    
    # Afficher les modifications d'addons.py
    change_logger.draw_changes(screen)
       
    pygame.display.flip()         
    clock.tick(60)

observer.stop()
observer.join()
pygame.quit()  
