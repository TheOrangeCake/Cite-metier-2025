import pygame
import difflib
from pathlib import Path

class ChangeLogger:
    """Surveille et affiche les modifications du fichier addons.py"""

    def __init__(self, file_path="addons/addons_new.py"):
        self.file_path = file_path
        self.changes = []
        self.font = pygame.font.SysFont('Courier', 14, False, False)
        self.previous_content = self._read_file()

    def _read_file(self):
        """Lit le contenu actuel du fichier"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except:
            return []

    def on_file_modified(self):
        """Appelé quand le fichier est modifié"""
        current_content = self._read_file()

        # Calcule les différences
        diff = difflib.unified_diff(
            self.previous_content,
            current_content,
            lineterm='',
            n=0
        )

        # Parse les modifications
        for line in diff:
            if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                continue
            if line.startswith('+'):
                self.changes.append(('add', line[1:].rstrip()))
            elif line.startswith('-'):
                self.changes.append(('del', line[1:].rstrip()))

        self.previous_content = current_content

    def draw(self, screen):
        """Affiche les modifications dans une fenêtre en bas à droite"""
        box_x = 1300
        box_y = 0
        box_width = 620
        box_height = 800

        title_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 32)
        title = title_font.render("Modifications du code:", True, (255, 255, 255))
        screen.blit(title, (box_x + 20, box_y + 15))

        y_offset = 70
        line_height = 30

        line_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 24)
        for change_type, line_content in self.changes[-10:]:
            color = (255, 255, 255) if change_type == 'add' else (255, 0, 0)
            prefix = "+ " if change_type == 'add' else "- "
            display_text = prefix + line_content[:65]
            text_surface = line_font.render(display_text, True, color)
            screen.blit(text_surface, (box_x + 20, box_y + y_offset))
            y_offset += line_height
            if y_offset > box_height - 20:
                break
    
    def get_previous_content(self):
        """Retourne le contenu précédent du fichier addons.py sous forme de chaîne"""
        return ''.join(self.previous_content)

_logger_instance = None

def get_logger():
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ChangeLogger()
    return _logger_instance

def draw_changes(screen):
    logger = get_logger()
    logger.draw(screen)
