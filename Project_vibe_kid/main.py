import pygame
import importlib
import traceback
from multiprocessing import Process, Pipe
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from addons import addons_new
import text
import utils
from bot_filter import response_analizer
import change_logger

WIDTH = 1920
HEIGHT = 1080
PROJECT_NAME = 'Vibe Kid'
ADDON_PATH = 'addons/addons_new.py'
BASE_PATH = 'addons_base.py'
SCENE1_PATH = 'addons_scene1.py'
SCENE2_PATH = 'addons_scene2.py'
SCENE3_PATH = 'addons_scene3.py'
SCENE4_PATH = 'addons_scene4.py'
SCENE5_PATH = 'addons_scene5.py'
MAIN_PATH = 'main.py'

main_file = utils.load(MAIN_PATH)
addons_base = utils.load(BASE_PATH)
addons_scene1 = utils.load(SCENE1_PATH)
addons_scene2 = utils.load(SCENE2_PATH)
addons_scene3 = utils.load(SCENE3_PATH)
addons_scene4 = utils.load(SCENE4_PATH)
addons_scene5 = utils.load(SCENE5_PATH)

class MyHandler(FileSystemEventHandler):
	def on_modified(self, event):
		try:
			importlib.reload(addons_new)
		except Exception as e:
			# To remake later
			print('Bad AI code')
			traceback.print_exc()
			print('Reload base addons')
			utils.reset_addons(ADDON_PATH, addons_base, observer)

		# Add code change display trigger here !!!!!!!!!!!!!!
		change_logger.get_logger().on_file_modified()

		return super().on_modified(event)
path = Path(ADDON_PATH)
observer = Observer()
handler = MyHandler()
observer.schedule(handler, path, recursive=False)
observer.start()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(PROJECT_NAME)
pygame.key.set_repeat(300, 50)

label_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 28)
input_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 24)
output_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 24)

done = False
reset = True
clock = pygame.time.Clock()
user_input = ''
AI_response = ''
pending = None
parent = None
child = None

draw_zone = pygame.Rect(0, 0, 1300, 800)
zone_surface = screen.subsurface(draw_zone)

while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RSHIFT:
				utils.reset_addons(ADDON_PATH, addons_base, observer, pending)
			elif event.key == pygame.K_F1:
				utils.reset_addons(ADDON_PATH, addons_scene1, observer, pending)
			elif event.key == pygame.K_F2:
				utils.reset_addons(ADDON_PATH, addons_scene2, observer, pending)
			elif event.key == pygame.K_F3:
				utils.reset_addons(ADDON_PATH, addons_scene3, observer, pending)
			elif event.key == pygame.K_F4:
				utils.reset_addons(ADDON_PATH, addons_scene4, observer, pending)
			elif event.key == pygame.K_F5:
				utils.reset_addons(ADDON_PATH, addons_scene5, observer, pending)
			elif event.key == pygame.K_BACKSPACE:
				user_input = user_input[:-1]
			elif event.key == pygame.K_ESCAPE:
				user_input = ''
			elif event.key == pygame.K_LEFT:
				addons_new.left_press(screen)
			elif event.key == pygame.K_RIGHT:
				addons_new.right_press(screen)
			elif event.key == pygame.K_UP:
				addons_new.up_press(screen)
			elif event.key == pygame.K_DOWN:
				addons_new.down_press(screen)
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
					AI_response = 'Génération de la réponse en cours...'
					reset = True
				else:
					AI_response = 'Une génération est déjà en cours...'

			else:
				if reset == True:
					user_input = ''
					reset = False
				if event.unicode.isalnum() or event.unicode in " .,!?'\"-":
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
			pending = None

	screen.fill(addons_new.background_color)

	# Custom addons for injection
	addons_new.custom_draw(zone_surface)
	addons_new.custom_interaction(screen)
	
	# Code show zone
	pygame.draw.rect(screen, (0,0,0), pygame.Rect(1300, 0, WIDTH - 1300, HEIGHT))
	change_logger.draw_changes(screen)

	# Text zone
	text.input_zone(screen, WIDTH, HEIGHT, label_font, input_font, user_input)
	text.AI_zone(screen, WIDTH, HEIGHT, label_font, output_font, AI_response)

	pygame.display.flip()
	clock.tick(60)

utils.clean_up(observer, pending)