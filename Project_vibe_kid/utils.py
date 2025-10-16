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
	observer.stop()
	observer.join()
	pygame.quit()
	if pending is not None:
		pending.terminate()
		pending.join()

def reset_addons(path, addons_base, observer, pending=None):
	try:
		with open(path, 'w') as file:
			file.write(addons_base)
	except Exception as e:
		print('Reset base addons error')
		clean_up(observer)
		sys.exit(1)