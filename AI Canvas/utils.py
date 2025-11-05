import sys
import pygame
import traceback
import importlib
from threading import Thread, Lock
from queue import Queue
from bot_filter import response_analizer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from new_bot import AI_call

def load(path):
	try:
		with open(path, 'r', encoding='utf-8') as file:
			scene = file.read()
			return scene
	except Exception as e:
		traceback.print_exc()
		sys.exit(1)

def clean_up(observer, parent = None, pending = None):
	if pending is not None:
		pending.join(timeout=0.1)
		if pending.is_alive():
			pending.join()
		if parent is not None:
			if hasattr(parent, "close"):
				parent.close()
			elif hasattr(parent, "cancel_join_thread"):
				parent.cancel_join_thread()
		pending = None
		parent = None
	if observer is not None:
		observer.stop()
		observer.join()
	pygame.quit()

def reset_addons(path, last_state, observer, lock):
	try:
		with lock:
			with open(path, 'w', encoding='utf-8') as file:
				file.write(last_state)
	except Exception as e:
		print('Reset state error')
		clean_up(observer)
		sys.exit(1)

def reload_addons(addons_module, lock):
	try:
		with lock:
			importlib.reload(addons_module)
		return False
	except Exception:
		traceback.print_exc()
		return True

def start_ai_thread(user_input, main_file, addon_path, lock):
	q = Queue()

	def worker(q, user_input, main_file, addon_path, lock):
		try:
<<<<<<< HEAD
			result = AI_call(user_input, main_file, addon_path)
=======
			result = response_analizer(user_input, main_file, addon_path, lock)
>>>>>>> bf6c934 (add mutex for race condition)
			q.put(result)
		except Exception as e:
			traceback.print_exc()
			q.put({"status": "error", "message": str(e)})

	thread = Thread(target=worker, args=(q, user_input, main_file, addon_path, lock), daemon=True)
	thread.start()
	return thread, q


def check_ai_thread(thread, queue):
	# Returns (is_done, AI_response, status, code, thread, queue)
	if thread is None:
		return False, None, None, None, None, None

	if not thread.is_alive():
		AI_response = ''
		status = 'OK'
		if not queue.empty():
			output = queue.get()
			if isinstance(output, dict):
				status = output.get("status", "error")
				AI_response = output.get("message", "")
				code = output.get("output", "")
			else:
				AI_response = str(output)
		return True, AI_response, status, code, None, None

	return False, None, None, None, thread, queue

def handle_scene_switch(event_key, current_state, observer, scenes, addon_path, reset_game_state, lock, last_state):
	new_state = current_state
	if event_key == pygame.K_F1:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f1"], observer, lock)
		last_state = scenes["f1"]
		print("Load f1")
	elif event_key == pygame.K_F2:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f2"], observer, lock)
		last_state = scenes["f2"]
		print("Load f2")
	elif event_key == pygame.K_F3:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f3"], observer, lock)
		last_state = scenes["f3"]
		print("Load f3")
	elif event_key == pygame.K_F4:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f4"], observer, lock)
		last_state = scenes["f4"]
		print("Load f4")
	elif event_key == pygame.K_F5:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f5"], observer, lock)
		last_state = scenes["f5"]
		print("Load f5")
	elif event_key == pygame.K_F6:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f6"], observer, lock)
		last_state = scenes["f6"]
		print("Load f6")
	elif event_key == pygame.K_F7:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f7"], observer, lock)
		last_state = scenes["f7"]
		print("Load f7")
	elif event_key == pygame.K_F8:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f8"], observer, lock)
		last_state = scenes["f8"]
		print("Load f8")
	elif event_key == pygame.K_F9:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f9"], observer, lock)
		last_state = scenes["f9"]
		print("Load f9")
	return new_state

class Handler(FileSystemEventHandler):
	def __init__(self):
		super().__init__()
		self.reload_pending = False

	def on_modified(self, event):
		self.reload_pending = True
		return super().on_modified(event)

def start_watchdog(path):
	handler = Handler()
	observer = Observer()
	observer.schedule(handler, path, recursive=True)
	observer.start()
	return observer, handler

def set_scenes():
	scenes = {
		"f1": load('f1_base_game.py'),
		"f2": load('f2_sea_scene.py'),
		"f3": load('f3_rain_scene.py'),
		"f4": load('f4_to_add.py'),
		"f5": load('f5_to_add.py'),
		"f6": load('f6_blank.py'),
		"f7": load('f7_blank_city.py'),
		"f8": load('f8_blank_to_add.py'),
		"f9": load('f9_blank_to_add.py')
	}
	return scenes

import pygame

# original design resolution
DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1280

def set_images(screen_width, screen_height):
	scale_w = screen_width / 1920
	scale_h = screen_height / 1080
	scale = min(scale_w, scale_h)

	original_sizes = {
		"happy": (235, 180),
		"heart": (235, 180),
		"eyes": (235, 180),
		"content": (235, 180),
		"loading": (235, 180),
		"scare": (235, 180),
		"unhappy": (235, 180),
		"warning": (235, 180),
		"question": (261, 200),
	}

	images = {}
	for name, (w, h) in original_sizes.items():
		new_size = (int(w * scale), int(h * scale))
		try:
			images[name] = pygame.transform.scale(
				pygame.image.load(f"images/{name}.png"), new_size
			)
		except Exception:
				traceback.print_exc()
				pygame.quit()
				sys.exit(1)
	return images
