import sys
import pygame
import traceback
import importlib
from threading import Thread
from queue import Queue
from bot_filter import response_analizer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
		pending.join(timeout=0.1)
		if pending.is_alive():
			pending.terminate()
			pending.join()
		if parent is not None:
			parent.close()
		pending = None
		parent = None
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

def reload_addons(addons_module, addon_path, observer, fallback_scene):
	try:
		importlib.reload(addons_module)
		return False
	except Exception:
		return True

def start_ai_thread(user_input, main_file, addon_path):
	q = Queue()

	def worker(q, user_input, main_file, addon_path):
		try:
			result = response_analizer(user_input, main_file, addon_path)
			q.put(result)
		except Exception as e:
			traceback.print_exc()
			q.put({"status": "error", "message": str(e)})

	thread = Thread(target=worker, args=(q, user_input, main_file, addon_path), daemon=True)
	thread.start()
	return thread, q


def check_ai_thread(thread, queue):
	# Returns (is_done, AI_response, status, thread, queue)
	if thread is None:
		return False, None, None, None, None

	if not thread.is_alive():
		AI_response = ''
		status = 'OK'
		if not queue.empty():
			output = queue.get()
			if isinstance(output, dict):
				status = output.get("status", "error")
				AI_response = output.get("message", "")
			else:
				AI_response = str(output)
		return True, AI_response, status, None, None

	return False, None, None, thread, queue

def handle_scene_switch(event_key, current_state, observer, pending, scenes, addon_path, reset_game_state):
	new_state = current_state
	if event_key == pygame.K_F1:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f1"], observer, pending)
		print("Load f1")
	elif event_key == pygame.K_F2:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f2"], observer, pending)
		print("Load f2")
	elif event_key == pygame.K_F3:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f3"], observer, pending)
		print("Load f3")
	elif event_key == pygame.K_F4:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f4"], observer, pending)
		print("Load f4")
	elif event_key == pygame.K_F5:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f5"], observer, pending)
		print("Load f5")
	elif event_key == pygame.K_F6:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f6"], observer, pending)
		print("Load f6")
	elif event_key == pygame.K_F7:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f7"], observer, pending)
		print("Load f7")
	elif event_key == pygame.K_F8:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f8"], observer, pending)
		print("Load f8")
	elif event_key == pygame.K_F9:
		new_state = reset_game_state()
		reset_addons(addon_path, scenes["f9"], observer, pending)
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
	observer.schedule(handler, path, recursive=False)
	observer.start()
	return observer, handler
