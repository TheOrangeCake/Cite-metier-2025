import sys
import pygame

def load(path):
	try:
		with open(path, 'r', encoding='utf-8') as file:
			scene = file.read()
			return scene
	except Exception as e:
		print('Base files open error')
		sys.exit(1)

def clean_up(observer, pending = None):
	if pending is not None:
		if pending.is_alive():
			pending.terminate()
		pending.join()
	if observer is not None:
		observer.stop()
		observer.join()
	pygame.quit()

def reset_addons(path, addons_base, observer, pending=None):
	try:
		with open(path, 'w') as file:
			file.write(addons_base)
	except Exception as e:
		print('Reset base addons error')
		clean_up(observer)
		sys.exit(1)

