import pygame
import sys
import traceback
from addons import addons_new
import text
import utils
import change_logger

WIDTH = 1920
HEIGHT = 1080
PROJECT_NAME = 'AI Canvas'
ADDON_PATH = 'addons/addons_new.py'
main_file = utils.load('main.py')
scenes = utils.set_scenes()
robot = utils.set_images()

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
		"obstacle_frequency": 80,
		"scroll_speed": 7,
		"score": 0,
		"game_over": False,
		"GROUND_Y": 0,
		"GAME_WIDTH": 0,
		"GAME_HEIGHT": 0,
	}

key_handlers = {
	pygame.K_LEFT: addons_new.left_press,
	pygame.K_RIGHT: addons_new.right_press,
	pygame.K_UP: addons_new.up_press,
	pygame.K_DOWN: addons_new.down_press
}

observer, addon_handler = utils.start_watchdog(ADDON_PATH)
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
AI_response = 'Salut, je suis CanvaEXE.\nOn formera une belle équipe!'
robot_state = "happy"
error_mode = False
pending = None
parent = None

current_state = reset_game_state()
draw_zone = pygame.Rect(0, 0, 1300, 800)
zone_surface = screen.subsurface(draw_zone)

while True:
	if addon_handler.reload_pending:
		addon_handler.reload_pending = False
		error = utils.reload_addons(addons_new, ADDON_PATH, observer, scenes["f1"])
		if error == True:
			print("Erreur de compilation avec AI code")
			utils.reset_addons(ADDON_PATH, scenes["f1"], observer, pending)
			error_mode = True
			continue

		# CHANGER POUR MISE A JOUR LE CODE CHANGE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		change_logger.get_logger().on_file_modified()

	if error_mode:
		text.error_handler(screen, label_font, HEIGHT, WIDTH, robot["warning"])
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				utils.clean_up(observer, parent, pending)
				sys.exit(0)
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
				error_mode = False
				current_state = reset_game_state()
				utils.reset_addons(ADDON_PATH, scenes["f1"], observer, pending)
				robot_state = "happy"
		clock.tick(30)
		continue

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			utils.clean_up(observer, parent, pending)
			## Uncomment in production
			# utils.reset_addons(ADDON_PATH, scene1, observer, pending)
			sys.exit(0)
		elif event.type == pygame.KEYDOWN:
			# todo: add "draw in pygame primitive" in prompt
			if event.key in (pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6, pygame.K_F7, pygame.K_F8, pygame.K_F9):
				current_state = utils.handle_scene_switch(event.key, current_state, observer, pending, scenes, ADDON_PATH, reset_game_state)
			elif event.key in key_handlers:
				try:
					key_handlers[event.key](current_state, screen)
				except Exception as e:
					print("Erreur de runtime avec AI code")
					utils.reset_addons(ADDON_PATH, scenes["f1"], observer, pending)
					error_mode = True
					continue
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
					pending, parent = utils.start_ai_thread(user_input, main_file, ADDON_PATH)
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

	# check if bad prompt to display sad robot here
	done, result, status, pending, parent = utils.check_ai_thread(pending, parent)
	if done:
		AI_response = result
		robot_state = "happy"
		if status != "OK":
			robot_state = "sad"

	screen.fill(addons_new.background_color)

	# Custom addons for injection
	try:
		addons_new.custom_draw(zone_surface, current_state)
		addons_new.custom_interaction(screen, current_state)
	except Exception as e:
		print("Erreur de runtime avec AI code")
		utils.reset_addons(ADDON_PATH, scenes["f1"], observer, pending)
		error_mode = True
		continue
	
	# Code show zone
	pygame.draw.rect(screen, (0,0,0), pygame.Rect(1300, 0, WIDTH - 1300, 800))
	change_logger.draw_changes(screen)

	text.input_zone(screen, WIDTH, HEIGHT, label_font, input_font, user_input)
	text.AI_zone(screen, WIDTH, HEIGHT, label_font, output_font, AI_response)
	text.bot_zone(screen, robot, robot_state)

	pygame.display.flip()
	clock.tick(60)
