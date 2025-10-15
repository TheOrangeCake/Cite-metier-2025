import pygame
import importlib
import traceback
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

try:
	# Save main file to pass to AI later
	with open(MAIN_PATH, 'r', encoding='utf-8') as file:
		main_file = file.read()
	# Save default addon file to reset later
	with open(BASE_PATH, 'r', encoding='utf-8') as file:
		addons_base = file.read()
except Exception as e:
	print('Base files open error')
	sys.exit(1)

# Reset addons.py to default state
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
	# If file is modified
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
observer.schedule(handler, path, recursive=True)
observer.start()

# Start pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(PROJECT_NAME)

done = False
clock = pygame.time.Clock()
user_input = ''
AI_response = ''
reset = True

# Main loop
while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		elif event.type == pygame.KEYDOWN:
			# Reset to base game
			if event.key == pygame.K_RSHIFT:
				reset_addons()
			# Manage input
			elif event.key == pygame.K_BACKSPACE:
				user_input = user_input[:-1]
			elif event.key == pygame.K_ESCAPE:
				user_input = ''
			# Submit input
			elif event.key == pygame.K_RETURN:
				if reset == True:
					user_input = ''
					reset = False
					continue
				moderation = response_analizer(user_input, main_file, ADDON_PATH)
				if isinstance(moderation, dict):
					status = moderation.get("status", "error")
					AI_response = moderation.get("message", "")
				else:
					status = "OK"
					AI_response = moderation
				print(AI_response)
				reset = True
			# Get input
			else:
				if reset == True:
					user_input = ''
					reset = False
				user_input += event.unicode
				AI_response = ''
	screen.fill((255,255,255))

	# Custom addons for injection
	addons_new.custom_draw(screen)
	addons_new.custom_interaction(screen)
	
	# Code show zone
	pygame.draw.rect(screen, (0,0,0), pygame.Rect(1300, 0, WIDTH - 1300, HEIGHT))
	change_logger.draw_changes(screen)

	# Text zone
	label_font = pygame.font.SysFont('Calibri', 18, False, False)
	text.input_zone(screen, WIDTH, HEIGHT, label_font, user_input)
	text.AI_zone(screen, WIDTH, HEIGHT, label_font, AI_response)

	pygame.display.flip()
	clock.tick(60)

clean_up()