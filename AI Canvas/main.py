import pygame
import sys
import traceback
from threading import Thread, Lock
from addons import addons_new
import context
import text
import utils
import change_logger

PROJECT_NAME = 'AI Canvas'
ADDON_PATH = 'addons/addons_new.py'
context_file = utils.load('context.py')
scenes = utils.set_scenes()
robot = utils.set_images()
lock = Lock()

observer, addon_handler = utils.start_watchdog(ADDON_PATH)
pygame.init()
desktop = pygame.display.Info()
width = desktop.current_w
height = desktop.current_h
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
# screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
pygame.display.set_caption(PROJECT_NAME)
pygame.key.set_repeat(300, 50)

label_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 28)
input_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 24)
output_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 24)
button_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 30)

reset = True
clock = pygame.time.Clock()
user_input = ''
AI_response = 'Salut, je suis Canva-Exe.\n' \
			'Ensemble, nous personalisons le canvas sans tapper une ligne de code !\n' \
			'\n' \
			'Tips: Plus la demande est détaillée, mieux la résultat !'
robot_state = "happy"
help_box = False
paused = False
error_mode = False
pending = None
parent = None

current_state = context.reset_game_state()
draw_zone_width = int(width * 0.68)
draw_zone_height = int(height * 0.74)
draw_zone = pygame.Rect(0, 0, draw_zone_width, draw_zone_height)
screen.fill((0, 0, 0))
zone_surface = screen.subsurface(draw_zone)

while True:
	if addon_handler.reload_pending:
		addon_handler.reload_pending = False
		error = utils.reload_addons(addons_new, lock)
		if error == True:
			print("Erreur de compilation avec AI code")
			utils.reset_addons(ADDON_PATH, scenes["f1"], observer, lock, pending)
			error_mode = True
			continue

		# CHANGER POUR MISE A JOUR LE CODE CHANGE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		change_logger.get_logger().on_file_modified()

	if error_mode:
		text.error_handler(screen, label_font, height, width, robot["warning"])
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				utils.clean_up(observer, parent, pending)
				sys.exit(0)
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
				error_mode = False
				current_state = context.reset_game_state()
				robot_state = "happy"
		clock.tick(30)
		continue

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			utils.clean_up(observer, parent, pending)
			## Uncomment in production
			# utils.reset_addons(ADDON_PATH, scene1, observer, lock, pending)
			sys.exit(0)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if pause_button.collidepoint(event.pos):
				help_box = not help_box
				paused = help_box
			elif quit_button.collidepoint(event.pos):
				utils.clean_up(observer, parent, pending)
				## Uncomment in production
				# utils.reset_addons(ADDON_PATH, scene1, observer, lock, pending)
				sys.exit(0)
		elif event.type == pygame.KEYDOWN:
			# todo: add "draw in pygame primitive" in prompt
			if event.key in (pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6, pygame.K_F7, pygame.K_F8, pygame.K_F9):
				current_state = utils.handle_scene_switch(event.key, current_state, observer, pending, scenes, ADDON_PATH, context.reset_game_state, lock)
			elif event.key in context.key_handlers:
				try:
					with lock:
						context.key_handlers[event.key](current_state, screen)
				except Exception as e:
					print("Erreur de runtime avec AI code")
					utils.reset_addons(ADDON_PATH, scenes["f1"], observer, lock, pending)
					error_mode = True
					continue
			elif event.key == pygame.K_BACKSPACE:
				user_input = user_input[:-1]
			elif event.key == pygame.K_ESCAPE:
				if help_box:
					help_box = False
					paused = False
				else:
					help_box = True
					paused = True
			elif event.key == pygame.K_RETURN:
				if reset == True:
					user_input = ''
					reset = False
					continue
				if pending is None:
					pending, parent = utils.start_ai_thread(user_input, context_file, ADDON_PATH, lock)
					AI_response = 'Génération de la réponse en cours...'
					reset = True
					robot_state = "loading"
				else:
					AI_response = 'Une génération est déjà en cours...'
					robot_state = "loading"
					reset = False
			else:
				if event.unicode.isalnum() or event.unicode in " .,!?'\"-":
					if reset == True:
						user_input = ''
						reset = False
					user_input += event.unicode
					AI_response = ("J'ai hâte de voir ton message!\n"
									"Tips: Plus ton message est détaillé, plus le rendu sera juste")

	done, result, status, pending, parent = utils.check_ai_thread(pending, parent)
	if done:
		AI_response = result
		robot_state = "happy"
		if status != "OK":
			robot_state = "sad"

	if not paused:
		try:
			with lock:
				context.code_inject(screen, zone_surface, current_state)
		except Exception as e:
			print("Erreur de runtime avec AI code")
			traceback.print_exc()
			utils.reset_addons(ADDON_PATH, scenes["f1"], observer, lock, pending)
			error_mode = True
			continue
	else:
		text.help_box(screen, width, height, button_font, input_font, robot["question"])

	# Code show zone
	code_zone = pygame.Rect(draw_zone_width, 0, width - draw_zone_width, draw_zone_height)
	pygame.draw.rect(screen, (0, 0, 0), code_zone)
	change_logger.draw_changes(screen)

	text.input_zone(screen, width, height, label_font, input_font, user_input)
	text.AI_zone(screen, width, height, label_font, output_font, AI_response)
	text.bot_zone(screen, robot, robot_state, width, height)
	pause_button = text.pause_zone(screen, button_font, width, height)
	quit_button = text.quit_zone(screen, button_font, width, height)

	pygame.display.flip()
	clock.tick(60)
