import pygame
import sys
import importlib
import traceback
from multiprocessing import Process, Pipe
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from addons import addons_new
import text
import utils
from bot_filter import response_analizer
import change_logger

WIDTH = 1920
HEIGHT = 1080
PROJECT_NAME = 'AI Canvas'
ADDON_PATH = 'addons/addons_new.py'

main_file = utils.load('main.py')
scene1 = utils.load('f1_base_game.py')
scene2 = utils.load('f2_sea_scene.py')
scene3 = utils.load('addons_scene3.py')
scene4 = utils.load('addons_scene4.py')
scene5 = utils.load('addons_scene5.py')
scene6 = utils.load('f6_blank.py')


class MyHandler(FileSystemEventHandler):
	def on_modified(self, event):
		try:
			importlib.reload(addons_new)
		except Exception as e:
			# To remake later
			print('Bad AI code')
			traceback.print_exc()
			print('Reload base addons')
			utils.reset_addons(ADDON_PATH, scene1, observer, pending)

		# Add code change display trigger here !!!!!!!!!!!!!!
		change_logger.get_logger().on_file_modified()

		return super().on_modified(event)
observer = Observer()
handler = MyHandler()
observer.schedule(handler, ADDON_PATH, recursive=False)
observer.start()

def reset_game_state():
	return {
		"x": 50,
		"y": 0,
		"width": 0,
		"height": 0,
		"velocity": 0,
		"is_jumping": False,
		"gravity": 1,
		"jump_power": -18,
		"obstacles": [],
		"obstacle_timer": 0,
		"obstacle_frequency": 60,
		"scroll_speed": 7,
		"score": 0,
		"game_over": False,
		"GROUND_Y": 0,
		"GAME_WIDTH": 0,
		"GAME_HEIGHT": 0,
	}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(PROJECT_NAME)
pygame.key.set_repeat(300, 50)

label_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 28)
input_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 24)
output_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 24)

reset = True
clock = pygame.time.Clock()
user_input = ''
AI_response = ''
pending = None
parent = None
child = None

draw_zone = pygame.Rect(0, 0, 1300, 800)
zone_surface = screen.subsurface(draw_zone)

game = "f2"
current_state = reset_game_state()

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			utils.clean_up(observer, pending)
			utils.reset_addons(ADDON_PATH, scene1, observer, pending)
			sys.exit(0)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_F1:
				game = "f1"
				current_state = reset_game_state()
				utils.reset_addons(ADDON_PATH, scene1, observer, pending)
				print("Load f1")
			elif event.key == pygame.K_F2:
				game = "f2"
				current_state = reset_game_state()
				utils.reset_addons(ADDON_PATH, scene2, observer, pending)
				print("Load f2")
			elif event.key == pygame.K_F3:
				game = "f3"
				current_state = reset_game_state()
				utils.reset_addons(ADDON_PATH, scene3, observer, pending)
				print("Load f3")
			elif event.key == pygame.K_F4:
				game = "f4"
				current_state = reset_game_state()
				utils.reset_addons(ADDON_PATH, scene4, observer, pending)
				print("Load f4")
			elif event.key == pygame.K_F5:
				game = "f5"
				current_state = reset_game_state()
				utils.reset_addons(ADDON_PATH, scene5, observer, pending)
				print("Load f5")
			elif event.key == pygame.K_F6:
				game = "f6"
				current_state = reset_game_state()
				utils.reset_addons(ADDON_PATH, scene6, observer, pending)
				print("Load f6")
			elif event.key == pygame.K_BACKSPACE:
				user_input = user_input[:-1]
			elif event.key == pygame.K_ESCAPE:
				user_input = ''
			elif event.key == pygame.K_LEFT:
				addons_new.left_press(current_state, screen)
			elif event.key == pygame.K_RIGHT:
				addons_new.right_press(current_state, screen)
			elif event.key == pygame.K_UP:
				addons_new.up_press(current_state, screen)
			elif event.key == pygame.K_DOWN:
				addons_new.down_press(current_state, screen)
			elif event.key == pygame.K_RETURN:
				if reset == True:
					user_input = ''
					reset = False
					continue
				
				# Threading for API call
				if pending is None:
					parent, child = Pipe(duplex = False)
					def worker(conn, user_input, main_file, addon_path):
						try:
							result = response_analizer(user_input, main_file, addon_path)
							conn.send(result)
						except Exception as e:
							conn.send({"status": "error", "message": str(e)})
						finally:
							conn.close()
					pending = Process(target=worker, args=(child, user_input, main_file, ADDON_PATH))
					pending.start()
					child.close()
					AI_response = 'Génération de la réponse en cours...'
					reset = True
				else:
					AI_response = 'Une génération est déjà en cours...'

			else:
				if event.unicode.isalnum() or event.unicode in " .,!?'\"-":
					if reset == True:
						user_input = ''
						reset = False
					user_input += event.unicode
					AI_response = ''

	# Reap API call output
	if pending is not None:
		if not pending.is_alive():
			if parent.poll():
				output = parent.recv()
				if isinstance(output, dict):
						status = output.get("status", "error")
						AI_response = output.get("message", "")
				else:
					status = "OK"
					AI_response = str(output)
			parent.close()
			pending.join()
			pending.terminate() 
			pending = None

	screen.fill(addons_new.background_color)

	# Custom addons for injection
	addons_new.custom_draw(zone_surface, current_state)
	addons_new.custom_interaction(screen, current_state)
	
	# Code show zone
	pygame.draw.rect(screen, (0,0,0), pygame.Rect(1300, 0, WIDTH - 1300, HEIGHT))
	change_logger.draw_changes(screen)

	# Text zone
	text.input_zone(screen, WIDTH, HEIGHT, label_font, input_font, user_input)
	text.AI_zone(screen, WIDTH, HEIGHT, label_font, output_font, AI_response)

	pygame.display.flip()
	clock.tick(60)
