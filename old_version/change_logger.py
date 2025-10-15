import pygame
import difflib
from pathlib import Path

class ChangeLogger:
    """Surveille et affiche les modifications du fichier addons.py"""

    def __init__(self, file_path="changes/addons.py"):
        self.file_path = file_path
        self.changes = []
        self.max_lines = 20
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

        # Garde seulement les dernières lignes
        if len(self.changes) > self.max_lines:
            self.changes = self.changes[-self.max_lines:]

        self.previous_content = current_content

    def draw(self, screen):
        """Affiche les modifications dans une fenêtre en bas à droite"""
        box_x = 820
        box_y = 400
        box_width = 560
        box_height = 180

        surface = pygame.Surface((box_width, box_height))
        surface.set_alpha(230)
        surface.fill((240, 240, 240))
        screen.blit(surface, (box_x, box_y))

        pygame.draw.rect(screen, (100, 100, 100), (box_x, box_y, box_width, box_height), 2)

        title_font = pygame.font.SysFont('Calibri', 16, True, False)
        title = title_font.render("Modifications addons.py:", True, (0, 0, 0))
        screen.blit(title, (box_x + 10, box_y + 5))

        y_offset = 30
        line_height = 16

        for change_type, line_content in self.changes[-10:]:
            color = (0, 150, 0) if change_type == 'add' else (200, 0, 0)
            prefix = "+ " if change_type == 'add' else "- "
            display_text = prefix + line_content[:65]
            text_surface = self.font.render(display_text, True, color)
            screen.blit(text_surface, (box_x + 10, box_y + y_offset))
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
