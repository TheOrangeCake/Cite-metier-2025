import pygame
import random

def input_zone(screen, width, height, label_font, input_font, user_input):
	zone = pygame.Rect(1300, 800, 620, height - 800)
	border_radius = 30
	pygame.draw.rect(screen, (139, 248, 106), zone, border_radius = border_radius)
	pygame.draw.rect(screen, (100, 155, 155), zone, width=8, border_radius=border_radius)
	marge_left = zone.x + 30
	blit_text(screen, "Entres tes modifications:", (marge_left, zone.y + 20), label_font, (60,60,60), zone.x + 530, 20)
	blit_text(screen, user_input, (marge_left, zone.y + 60), input_font, (0,0,0), zone.x + 530, height - 710)

def AI_zone(screen, width, height, label_font, output_font, AI_output):
	zone = pygame.Rect(0, 800, width - 630, height - 800)
	border_radius = 30
	pygame.draw.rect(screen, (248, 165, 106), zone, border_radius = border_radius)
	pygame.draw.rect(screen, (100, 155, 155), zone, width=8, border_radius=border_radius)
	blit_text(screen, AI_output, (320, 820), output_font, (0,0,0), 1290, 20)

def bot_zone(screen, images, state):
	if not hasattr(bot_zone, "last_state"):
		bot_zone.last_state = None
		bot_zone.current_image = None
		bot_zone.frame_timer = 0
		bot_zone.frame_threshold = random.randint(180, 300)

	shadow = pygame.Rect(25, 815, 275, 200)
	border_radius = 30
	pygame.draw.rect(screen, (100, 100, 100), shadow, border_radius = border_radius)
	background = pygame.Rect(20, 810, 275, 200)
	pygame.draw.rect(screen, (248, 236, 106), background, border_radius = border_radius)
	pos = (40, 820)
	if state != bot_zone.last_state:
		bot_zone.last_state = state
		bot_zone.frame_timer = 0
		bot_zone.frame_threshold = random.randint(180, 300)

		if state == "loading":
			bot_zone.current_image = images["loading"]
		elif state == "happy":
			bot_zone.current_image = random.choice([
				images["happy"],
				images["heart"],
				images["content"],
				images["eyes"],
			])
		elif state == "sad":
			bot_zone.current_image = random.choice([
				images["unhappy"],
				images["scare"],
			])
	else:
		bot_zone.frame_timer += 1
		if state == "happy" and bot_zone.frame_timer >= bot_zone.frame_threshold:
			bot_zone.frame_timer = 0
			bot_zone.frame_threshold = random.randint(180, 300)
			bot_zone.current_image = random.choice([
				images["happy"],
				images["heart"],
			])
	if bot_zone.current_image:
		screen.blit(bot_zone.current_image, pos)

def help_zone(screen, font):
	shadow = pygame.Rect(25, 1025, 275, 40)
	border_radius = 10
	pygame.draw.rect(screen, (100, 100, 100), shadow, border_radius = border_radius)
	background = pygame.Rect(20, 1020, 275, 40)
	pygame.draw.rect(screen, (248, 236, 255), background, border_radius = border_radius)
	# blit_text(screen, "TIPS", (30, 1025), font, (60,60,60), 275, 40)
	text = font.render("GUIDE et PAUSE", True, (60,60,60))
	text_rect = text.get_rect(center=background.center)
	screen.blit(text, text_rect)
	return background

def help_box(screen, width, height, button_font, input_font):
	overlay = pygame.Surface((width, height), pygame.SRCALPHA)
	overlay.fill((0, 0, 0, 180))
	screen.blit(overlay, (0, 0))

	box_rect = pygame.Rect(width//2 - 300, height//2 - 200, 600, 400)
	border_radius = 15
	pygame.draw.rect(screen, (255, 255, 255), box_rect, border_radius=border_radius)
	pygame.draw.rect(screen, (0, 0, 0), box_rect, 3, border_radius=border_radius)

	text_surface = button_font.render("Comment ça marche?", True, (0, 0, 0))
	screen.blit(text_surface, (box_rect.centerx - text_surface.get_width()//2, box_rect.top + 30))
	lines = [
		"Flèches = déplacer",
		"Entrée = lancer l'IA",
	]
	y = box_rect.top + 100
	for line in lines:
		surf = input_font.render(line, True, (0, 0, 0))
		screen.blit(surf, (box_rect.centerx - surf.get_width()//2, y))
		y += 40
	close = "Cliquez de nouveau sur le bouton ou ESC pour fermer"
	close_line = input_font.render(close, True, (0, 0, 0))
	y += 120
	screen.blit(close_line, (box_rect.centerx - close_line.get_width()//2, y))
		
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

def error_handler(screen, label_font, height, width, image):
	error_message = "Oh no!\n" \
			"\n" \
			"Désolé, j'ai fait des erreurs dans le code et le programme a été réinitialisé à l'état initial.\n" \
			"L'IA n'est pas omnipotente et peut faire des erreurs. J'ai besoin d'un humain pour corriger mes erreurs.\n" \
			"Les métiers de l'informatique ne sont pas remplaçables par l'IA."
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
