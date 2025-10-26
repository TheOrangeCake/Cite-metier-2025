# The code below is used for context, do not modify this code.
# Use pygame
import pygame
# addons_new is the game to modify, all codes below are used to inject into the main game loop
from addons import addons_new

# This function give the game its initial state,
# these variable can be updated in addons_new to change the game
# Pygame’s origin (0,0) is top-left; y increases downward
def reset_game_state():
	return {
		"x": 50,
		"y": 0,
		"width": 0,
		"height": 0,
		"velocity": 0,
		"is_jumping": False,
		"is_ducking": False,
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

# The game supports injection of arrows keys by default,
# update those functions in addons_new file to change functionalities
key_handlers = {
	pygame.K_LEFT: addons_new.left_press,
	pygame.K_RIGHT: addons_new.right_press,
	pygame.K_UP: addons_new.up_press,
	pygame.K_DOWN: addons_new.down_press
}

# This fucntion injects behavior changes to the main game loop,
# update those functions in addons_new file to change behavior.
# This function is called every frame
def code_inject(screen, zone_surface, current_state):
	zone_surface.fill(addons_new.background_color)
	addons_new.custom_draw(zone_surface, current_state)
	addons_new.custom_interaction(screen, current_state)

# This function allows adding new keys to the game state dynamically.
# AI-generated code should call this when it needs to introduce new keys
# that are not present in the default game state.
# Example: add_state_keys(state, {"is_ducking": False})
def add_state_keys(state, new_keys=None):
	if new_keys is None:
		new_keys = {}
	for key, val in new_keys.items():
		state.setdefault(key, val)
