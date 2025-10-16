import pygame
import importlib
import traceback
import sys
from multiprocessing import Process, Pipe
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from addons import addons_new
import text
from bot_filter import response_analizer
import change_logger

WIDTH = 1920
HEIGHT = 1080
PROJECT_NAME = 'Vibe Kid'
ADDON_PATH = 'addons/addons_new.py'
BASE_PATH = 'addons_base.py'
MAIN_PATH = 'main.py'

# Clean up
def clean_up():
	observer.stop()
	observer.join()
	pygame.quit()
	if pending is not None:
		pending.terminate()
		pending.join()

try:
	with open(MAIN_PATH, 'r', encoding='utf-8') as file:
		main_file = file.read()
	with open(BASE_PATH, 'r', encoding='utf-8') as file:
		addons_base = file.read()
except Exception as e:
	print('Base files open error')
	sys.exit(1)

def reset_addons():
	try:
		with open(ADDON_PATH, 'w') as file:
			file.write(addons_base)
	except Exception as e:
		print('Reset base addons error')
		clean_up()
		sys.exit(1)

# Start the watcher
class MyHandler(FileSystemEventHandler):
	def on_modified(self, event):
		try:
			importlib.reload(addons_new)
		except Exception as e:
			# To remake later
			print('Bad AI code')
			traceback.print_exc()
			print('Reload base addons')
			reset_addons()

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

done = False
reset = True
clock = pygame.time.Clock()
user_input = ''
AI_response = ''
pending = None
parent = None
child = None
label_font = pygame.font.SysFont('Calibri', 18, False, False)
input_font = pygame.font.SysFont('Calibri', 24, False, False)
output_font = pygame.font.SysFont('Calibri', 24, False, False)

draw_zone = pygame.Rect(0, 0, 1300, 800)
zone_surface = screen.subsurface(draw_zone)

# Main loop
while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RSHIFT:
				reset_addons()
			elif event.key == pygame.K_BACKSPACE:
				user_input = user_input[:-1]
			elif event.key == pygame.K_ESCAPE:
				user_input = ''
			elif event.key == pygame.K_RETURN:
				if reset == True:
					user_input = ''
					reset = False
					continue

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
				user_input += event.unicode
				AI_response = ''

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

	screen.fill((255,255,255))
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

clean_up()