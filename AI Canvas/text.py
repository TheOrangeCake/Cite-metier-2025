import pygame

def input_zone(screen, width, height, label_font, input_font, user_input):
	zone = pygame.Rect(0, 800, 560, height - 800)
	border_radius = 30
	pygame.draw.rect(screen, (139, 248, 106), zone, border_radius = border_radius)
	pygame.draw.rect(screen, (100, 155, 155), zone, width=8, border_radius=border_radius)
	marge_left = zone.x + 30
	blit_text(screen, "Entres tes modifications:", (marge_left, zone.y + 20), label_font, (60,60,60), zone.x + 530, 20)
	blit_text(screen, user_input, (marge_left, zone.y + 60), input_font, (0,0,0), zone.x + 530, height - 710)

def AI_zone(screen, width, height, label_font, output_font, AI_output):
	zone = pygame.Rect(570, 800, width - 570, height - 800)
	border_radius = 30
	pygame.draw.rect(screen, (248, 165, 106), zone, border_radius = border_radius)
	pygame.draw.rect(screen, (100, 155, 155), zone, width=8, border_radius=border_radius)
	marge_left = zone.x + 30
	blit_text(screen, "La réponse de l'IA:", (marge_left, zone.y + 20), label_font, (60,60,60), width, 20)
	blit_text(screen, AI_output, (marge_left, zone.y + 60), output_font, (0,0,0), width, height - 710)

def error_handler(screen, label_font, height, width):
	error_message = "Oh no!\n" \
			"\n" \
			"Désolé, j'ai fait des erreurs dans le code et le programme a été réinitialisé à l'état initial.\n" \
			"L'IA n'est pas omnipotente et peut faire des erreurs. J'ai besoin d'un humain pour corriger mes erreurs.\n" \
			"Les métiers de l'informatique ne sont pas remplaçables par l'IA."
	screen.fill((0, 0, 0))
	lines = error_message.split('\n')
	y_start = height // 2 - len(lines) * 20
	for i, line in enumerate(lines):
		text_surface = label_font.render(line, True, (255, 255, 255))
		text_rect = text_surface.get_rect(center=(width // 2, y_start + i * 40))
		screen.blit(text_surface, text_rect)
	prompt = label_font.render("Appuie sur Entrée pour revenir au jeu", True, (200, 200, 200))
	prompt_rect = prompt.get_rect(center=(width // 2, height - 100))
	screen.blit(prompt, prompt_rect)
	pygame.display.flip()

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
