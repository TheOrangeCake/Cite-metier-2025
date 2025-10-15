import pygame

def input_zone(screen, width, height, label_font, user_input):
	zone = pygame.Rect(0, 800, 560, height - 800)
	border_radius = 20
	pygame.draw.rect(screen, (30,30,90), zone, border_radius = border_radius)
	input_font = pygame.font.SysFont('Calibri', 24, False, False)
	marge_left = zone.x + 30
	blit_text(screen, "Entres tes modifications:", (marge_left, zone.y + 30), label_font, (255,255,255), zone.x + 530, 20)
	blit_text(screen, user_input, (marge_left, zone.y + 60), input_font, (255,255,255), zone.x + 530, height - 710)

def AI_zone(screen, width, height, label_font, AI_output):
	zone = pygame.Rect(570, 800, width - 570, height - 800)
	border_radius = 20
	pygame.draw.rect(screen, (30,30,90), zone, border_radius = border_radius)
	output_font = pygame.font.SysFont('Calibri', 24, False, False)
	marge_left = zone.x + 30
	blit_text(screen, "La réponse du IA:", (marge_left, zone.y + 30), label_font, (255,255,255), width - 630, 20)
	blit_text(screen, AI_output, (marge_left, zone.y + 60), output_font, (255,255,255), width - 630, height - 710)

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
