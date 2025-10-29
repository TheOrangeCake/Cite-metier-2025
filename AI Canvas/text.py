import pygame
import random

def input_zone(screen, width, height, label_font, input_font, user_input):
	zone_x = int(width * 0.68)
	zone_y = int(height * 0.74)
	zone_w = int(width * 0.32)
	zone_h = int(height * 0.26)

	border_radius = int(width * 0.015)
	pygame.draw.rect(screen, (139, 248, 106), (zone_x, zone_y, zone_w, zone_h), border_radius=border_radius)
	pygame.draw.rect(screen, (100, 155, 155), (zone_x, zone_y, zone_w, zone_h), width=int(width * 0.004), border_radius=border_radius)

	margin_left = zone_x + int(width * 0.015)
	text_max_x = zone_x + zone_w - int(width * 0.05)
	text_max_y = zone_y + zone_h - int(height * 0.07)

	blit_text(screen, "Entres tes modifications:", (margin_left, zone_y + int(height * 0.02)), label_font, (60,60,60), text_max_x, 20)
	blit_text(screen, user_input, (margin_left, zone_y + int(height * 0.06)), input_font, (0,0,0), text_max_x, text_max_y)


def AI_zone(screen, width, height, label_font, output_font, AI_output):
	zone_x = 0
	zone_y = int(height * 0.74)
	zone_w = int(width * 0.68)
	zone_h = int(height * 0.26)

	border_radius = int(width * 0.015)
	pygame.draw.rect(screen, (248, 165, 106), (zone_x, zone_y, zone_w, zone_h), border_radius=border_radius)
	pygame.draw.rect(screen, (100, 155, 155), (zone_x, zone_y, zone_w, zone_h), width=int(width * 0.004), border_radius=border_radius)

	text_start_x = int(width * 0.17)
	text_start_y = zone_y + int(height * 0.02)
	text_max_x = zone_x + zone_w - int(width * 0.05)
	text_max_y = zone_y + zone_h - int(height * 0.07)

	blit_text(screen, AI_output, (text_start_x, text_start_y), output_font, (0,0,0), text_max_x, 20)

def bot_zone(screen, images, state, width, height):
	if not hasattr(bot_zone, "last_state"):
		bot_zone.last_state = None
		bot_zone.current_image = None
		bot_zone.frame_timer = 0
		bot_zone.frame_threshold = random.randint(180, 300)

	zone_w = int(width * 0.145)
	zone_h = int(height * 0.185)
	zone_x = int(width * 0.010)
	zone_y = int(height * 0.75)
	border_radius = int(width * 0.015)

	shadow = pygame.Rect(zone_x + 5, zone_y + 5, zone_w, zone_h)
	pygame.draw.rect(screen, (100, 100, 100), shadow, border_radius=border_radius)
	background = pygame.Rect(zone_x, zone_y, zone_w, zone_h)
	pygame.draw.rect(screen, (248, 236, 106), background, border_radius=border_radius)
	pos = (zone_x + int(width * 0.01), zone_y + int(height * 0.02))

	if state != bot_zone.last_state:
		bot_zone.last_state = state
		bot_zone.frame_timer = 0
		bot_zone.frame_threshold = random.randint(180, 300)
		if state == "loading":
			bot_zone.current_image = images["loading"]
		elif state == "happy":
			bot_zone.current_image = random.choice([
				images["happy"], images["heart"], images["content"], images["eyes"]
			])
		elif state == "sad":
			bot_zone.current_image = random.choice([
				images["unhappy"], images["scare"]
			])
	else:
		bot_zone.frame_timer += 1
		if state == "happy" and bot_zone.frame_timer >= bot_zone.frame_threshold:
			bot_zone.frame_timer = 0
			bot_zone.frame_threshold = random.randint(180, 300)
			bot_zone.current_image = random.choice([
				images["happy"], images["heart"]
			])
	if bot_zone.current_image:
		screen.blit(bot_zone.current_image, pos)


def quit_zone(screen, font, width, height):
	total_w = int(width * 0.145)
	total_h = int(height * 0.037)
	total_x = int(width * 0.010)
	total_y = int(height * 0.945)
	border_radius = int(width * 0.007)

	margin = int(total_w * 0.03)
	zone_w = (total_w - margin) // 2

	zone_x = total_x
	shadow = pygame.Rect(zone_x + 5, total_y + 5, zone_w, total_h)
	pygame.draw.rect(screen, (100, 100, 100), shadow, border_radius=border_radius)
	background = pygame.Rect(zone_x, total_y, zone_w, total_h)
	pygame.draw.rect(screen, (248, 236, 255), background, border_radius=border_radius)

	text = font.render("QUIT", True, (60, 60, 60))
	text_rect = text.get_rect(center=background.center)
	screen.blit(text, text_rect)
	return background


def pause_zone(screen, font, width, height):
	total_w = int(width * 0.145)
	total_h = int(height * 0.037)
	total_x = int(width * 0.010)
	total_y = int(height * 0.945)
	border_radius = int(width * 0.007)

	margin = int(total_w * 0.03)
	zone_w = (total_w - margin) // 2

	zone_x = total_x + zone_w + margin
	shadow = pygame.Rect(zone_x + 5, total_y + 5, zone_w, total_h)
	pygame.draw.rect(screen, (100, 100, 100), shadow, border_radius=border_radius)
	background = pygame.Rect(zone_x, total_y, zone_w, total_h)
	pygame.draw.rect(screen, (248, 236, 255), background, border_radius=border_radius)

	text = font.render("PAUSE", True, (60, 60, 60))
	text_rect = text.get_rect(center=background.center)
	screen.blit(text, text_rect)
	return background


def help_box(screen, width, height, button_font, input_font, robot, pause_message):
	overlay = pygame.Surface((width, height), pygame.SRCALPHA)
	overlay.fill((0, 0, 0, 180))
	screen.blit(overlay, (0, 0))

	box_w = int(width * 0.5)
	box_h = int(height * 0.6)
	box_x = width // 3 - box_w // 2
	box_y = height // 3 - box_h // 2
	border_radius = int(width * 0.008)

	pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_w, box_h), border_radius=border_radius)
	pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_w, box_h), width=int(width * 0.002), border_radius=border_radius)
	robot_rect = robot.get_rect(center=(box_x + box_w // 2, box_y + box_h // 5))
	screen.blit(robot, robot_rect)
	text_surface = button_font.render("Comment ça marche?", True, (0, 0, 0))
	text_x = box_x + (box_w - text_surface.get_width()) // 2
	text_y = box_y + int(height * 0.23)
	screen.blit(text_surface, (text_x, text_y))

	y = box_y + int(height * 0.27)
	for line in pause_message:
		surf = input_font.render(line, True, (0, 0, 0))
		line_x = box_x + (box_w - surf.get_width()) // 2
		screen.blit(surf, (line_x, y))
		y += int(height * 0.03)

	close = "Cliquez sur PAUSE ou presses ESC pour fermer"
	close_line = input_font.render(close, True, (0, 0, 0))
	close_x = box_x + (box_w - close_line.get_width()) // 2
	y = box_y + box_h - int(height * 0.1)
	screen.blit(close_line, (close_x, y))
		
# https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame
def blit_text(surface, text, pos, font, color, max_width, max_height):
	words = [word.split(' ') for word in text.splitlines()]
	space = font.size(' ')[0]
	x, y = pos
	for line in words:
		for word in line:
			word_surface = font.render(word, 0, color)
			word_width, word_height = word_surface.get_size()
			if x + word_width >= max_width:
				x = pos[0]
				y += word_height
			surface.blit(word_surface, (x, y))
			x += word_width + space
		x = pos[0]
		y += word_height

def error_handler(screen, label_font, height, width, image, error_message):
	screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
	screen.fill((0, 0, 0))
	img_rect = image.get_rect()
	img_rect.center = (width // 2, height // 3)
	screen.blit(image, img_rect)
	lines = error_message.split('\n')
	y_start = img_rect.bottom + 40
	for i, line in enumerate(lines):
		text_surface = label_font.render(line, True, (255, 255, 255))
		text_rect = text_surface.get_rect(center=(width // 2, y_start + i * 40))
		screen.blit(text_surface, text_rect)
	prompt = label_font.render("Appuie sur Entrée pour revenir au jeu", True, (200, 200, 200))
	prompt_rect = prompt.get_rect(center=(width // 2, height - 100))
	screen.blit(prompt, prompt_rect)
	pygame.display.flip()
