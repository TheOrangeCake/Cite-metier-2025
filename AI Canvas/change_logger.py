import pygame
import difflib
from pathlib import Path
import time
import math
import random

class ChangeLogger:
    """Surveille et affiche les modifications du fichier addons.py"""

    def __init__(self, file_path="addons/addons_new.py"):
        self.file_path = file_path
        self.changes = []  # Lignes terminées
        self.pending_changes = []  # Lignes en attente d'être écrites
        self.current_writing_line = None  # Ligne en cours d'écriture
        self.line_states = []  # État de chaque ligne (writing, sliding, done)
        self.line_positions = []  # Position Y de chaque ligne
        self.font = pygame.font.SysFont('Courier', 14, False, False)
        self.previous_content = self._read_file()
        self.char_write_speed = 0.015  # Vitesse d'écriture par caractère
        self.line_slide_duration = 0.3  # Durée de l'animation de descente
        self.start_time = time.time()
        self.current_line_start_time = 0  # Début de l'écriture de la ligne actuelle
        self.current_line_chars = 0  # Nombre de caractères écrits
        self.scroll_offset = 0  # Offset pour le scroll manuel
        self.scrollbar_rect = None  # Rectangle de la barre de scroll
        self.scrollbar_handle_rect = None  # Rectangle du curseur de scroll
        self.is_dragging_scrollbar = False  # État du drag de la barre
        self.total_modifications = 0  # Compteur total de modifications
        self.particles = []  # Particules pour effet Matrix
        
        # Cache des polices pour performance
        self.title_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 28)
        self.line_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 18)
        self.info_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 22)
        
        # Cache pour les calculs répétitifs
        self.last_zone_width = 0
        self.last_zone_height = 0
        self.cached_dimensions = None

    def _read_file(self):
        """Lit le contenu actuel du fichier"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except:
            return []

    def _clean_text(self, text):
        """Nettoie le texte pour n'afficher que des caractères supportés par la police"""
        # Caractères autorisés : lettres, chiffres, ponctuation basique, espaces
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:!?()[]{}+-*/<>=_"\'\n\t')
        # Garder seulement les caractères supportés
        cleaned = ''.join(c if c in allowed_chars else '' for c in text)
        # Simplifier les espaces multiples
        cleaned = ' '.join(cleaned.split())
        return cleaned

    # def stream_code(self, code_chunk):
    #     """
    #     Accepté un bout de code
    #     """
    #     lines = code_chunk.split("\n")
    #     for line in lines:
    #         cleaned = self._clean_text(line)
    #         if cleaned.strip():
    #             self.pending_changes.append(('add', cleaned))
    #             self.total_modifications += 1

    def on_file_modified(self, lock):
        """Appelé quand le fichier est modifié"""
        with lock:
            current_content = self._read_file()

        # Calcule les différences
        diff = difflib.unified_diff(
            self.previous_content,
            current_content,
            lineterm='',
            n=0
        )

        # Parse les modifications
        new_changes = []
        for line in diff:
            if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                continue
            
            # Filtrer les commentaires
            if line.startswith('+'):
                content = line[1:].rstrip()
                # Vérifier si c'est un commentaire (après suppression des espaces)
                if content.strip() and not content.strip().startswith('#'):
                    # Nettoyer le texte pour éviter les caractères non supportés
                    cleaned_content = self._clean_text(content)
                    if cleaned_content:  # Seulement si il reste du contenu
                        new_changes.append(('add', cleaned_content))
            elif line.startswith('-'):
                content = line[1:].rstrip()
                # Vérifier si c'est un commentaire (après suppression des espaces)
                if content.strip() and not content.strip().startswith('#'):
                    # Nettoyer le texte pour éviter les caractères non supportés
                    cleaned_content = self._clean_text(content)
                    if cleaned_content:  # Seulement si il reste du contenu
                        new_changes.append(('del', cleaned_content))

        if new_changes:
            # Ajouter les nouvelles modifications à la file d'attente
            self.pending_changes.extend(new_changes)
            self.total_modifications += len(new_changes)
            
            # Créer moins de particules Matrix pour la performance (2 par ligne au lieu de 3)
            for i in range(min(len(new_changes) * 2, 10)):  # Max 10 particules par batch
                self.particles.append({
                    'x': random.randint(0, 100),
                    'y': random.randint(0, 100),
                    'speed': random.uniform(1.5, 2.5),
                    'life': random.uniform(2.0, 3.0),
                    'created_at': time.time()
                })

        self.previous_content = current_content

    def draw(self, screen, zone_x, zone_y, zone_width, zone_height):
        """Affiche les modifications avec style Matrix + effets visuels (optimisé)"""
        current_time = time.time() - self.start_time
        
        # Cache des dimensions si elles n'ont pas changé
        if zone_width != self.last_zone_width or zone_height != self.last_zone_height:
            self.last_zone_width = zone_width
            self.last_zone_height = zone_height
            self.cached_dimensions = {
                'margin_x': int(zone_width * 0.03),
                'margin_y': int(zone_height * 0.02),
                'scrollbar_width': int(zone_width * 0.02),
                'content_y_start': zone_y + int(zone_height * 0.09),  # Réduit pour remonter le contenu
                'content_height': zone_height - int(zone_height * 0.11),
                'line_height': int(zone_height * 0.05),  # Réduit de 0.06 à 0.05 pour encore moins d'espace
                'line_h': int(zone_height * 0.05 * 0.9),
                'border_radius': int(zone_height * 0.05 * 0.3)
            }
        
        dims = self.cached_dimensions
        margin_x = dims['margin_x']
        margin_y = dims['margin_y']
        scrollbar_width = dims['scrollbar_width']
        
        # Dessiner les particules Matrix en arrière-plan
        self.draw_matrix_particles(screen, zone_x, zone_y, zone_width, zone_height)
        
        # Titre avec effet glow Matrix (optimisé) - utiliser le cache
        title_text = "Modifications du code"
        
        # Effet de pulsation pour le titre (simplifié)
        pulse = abs(math.sin(current_time * 2)) * 0.3 + 0.7
        title_color = (0, int(255 * pulse), 0)
        
        # Glow réduit (2 passes au lieu de 4)
        title_x = zone_x + margin_x
        title_y = zone_y + margin_y
        for offset in [(1, 1), (-1, -1)]:
            glow_surface = self.title_font.render(title_text, True, (0, 100, 0))
            screen.blit(glow_surface, (title_x + offset[0], title_y + offset[1]))
        
        title = self.title_font.render(title_text, True, title_color)
        screen.blit(title, (title_x, title_y))
        
        # Ligne de séparation avec effet néon simplifié
        line_y = zone_y + int(zone_height * 0.07)
        line_start_x = zone_x + margin_x
        line_end_x = zone_x + zone_width - margin_x - scrollbar_width
        
        # Glow simplifié (1 passe au lieu de 3)
        pygame.draw.line(screen, (0, 150, 0), (line_start_x, line_y), (line_end_x, line_y), 5)
        pygame.draw.line(screen, (0, 255, 0), (line_start_x, line_y), (line_end_x, line_y), 3)
        
        # Zone de contenu (utiliser le cache)
        content_y_start = dims['content_y_start']
        content_height = dims['content_height']
        line_height = dims['line_height']
        line_h = dims['line_h']
        border_radius = dims['border_radius']
        
        x_start = zone_x + margin_x
        max_width = zone_width - 2 * margin_x - scrollbar_width
        
        # Pas de scroll automatique - l'utilisateur contrôle
        # Clipping pour ne pas dépasser la zone
        clip_rect = pygame.Rect(x_start, content_y_start, max_width, content_height)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)
        
        # Gérer la file d'attente et démarrer la prochaine ligne si besoin
        if self.current_writing_line is None and self.pending_changes:
            self.current_writing_line = self.pending_changes.pop(0)
            self.current_line_start_time = current_time
            self.current_line_chars = 0
        
        # Zone d'écriture réservée en haut
        writing_zone_height = 50
        writing_y = content_y_start + 10
        
        # Afficher la ligne en cours d'écriture (TOUJOURS visible en haut)
        if self.current_writing_line is not None:
            change_type, line_content = self.current_writing_line
            
            # Ignorer les commentaires
            if not line_content.strip().startswith('#'):
                # Calcul de l'animation d'écriture
                time_since_start = current_time - self.current_line_start_time
                write_duration = len(line_content) * self.char_write_speed
                
                # Calculer le nombre de caractères visibles
                visible_chars = int(time_since_start / self.char_write_speed)
                is_writing = visible_chars < len(line_content)
                
                # Effet bounce pendant l'écriture (réduit)
                if is_writing:
                    bounce_progress = time_since_start / max(0.01, write_duration)
                    bounce_offset = abs(math.sin(bounce_progress * math.pi * 2)) * 3  # Réduit de 8 à 3
                elif time_since_start < write_duration + 0.5:
                    # Bounce après écriture (réduit)
                    bounce_progress = (time_since_start - write_duration) / 0.5
                    bounce_offset = abs(math.sin(bounce_progress * math.pi)) * 6 * (1 - bounce_progress)  # Réduit de 15 à 6
                else:
                    # Ligne terminée, l'ajouter aux changes et passer à la suivante
                    self.changes.insert(0, self.current_writing_line)
                    self.line_states.insert(0, 'completed')
                    self.line_positions.insert(0, writing_y + writing_zone_height)  # Position initiale pour le slide
                    self.current_writing_line = None
                    self.current_line_start_time = None
                    self.current_line_chars = 0
                    bounce_offset = 0
                
                if self.current_writing_line is not None:  # Toujours afficher si pas encore terminée
                    # Couleurs style Matrix (minimaliste)
                    if change_type == 'add':
                        color = (0, 255, 0)
                        prefix = "+ "
                    else:
                        color = (255, 0, 100)
                        prefix = "- "
                    
                    # Texte à afficher (tronqué pour performance)
                    max_content_length = 60
                    display_content = line_content[:max_content_length]
                    
                    if is_writing:
                        display_text = prefix + display_content[:visible_chars] + "█"
                    else:
                        display_text = prefix + display_content
                    
                    # Décalage pour centrer le texte
                    text_offset_x = int(max_width * 0.1)
                    
                    # Texte direct sans fond (minimaliste)
                    # Glow léger pour le relief
                    for offset in [(1, 1), (-1, -1)]:
                        glow_text = self.line_font.render(display_text, True, (0, 50, 0) if change_type == 'add' else (50, 0, 0))
                        screen.blit(glow_text, (x_start + text_offset_x + offset[0], writing_y - bounce_offset + offset[1]))
                    
                    text_surface = self.line_font.render(display_text, True, color)
                    screen.blit(text_surface, (x_start + text_offset_x, writing_y - bounce_offset))
            else:
                # Ignorer le commentaire et passer au suivant
                self.current_writing_line = None
                self.current_line_start_time = None
        
        # Afficher les lignes complétées avec animation de slide
        y_offset = writing_y + writing_zone_height
        
        for line_idx, (change_type, line_content) in enumerate(self.changes):
            # Ignorer les commentaires
            if line_content.strip().startswith('#'):
                continue
            
            # Gérer l'animation de slide
            if line_idx < len(self.line_positions):
                target_y = y_offset - self.scroll_offset
                current_pos_y = self.line_positions[line_idx]
                
                # Interpolation fluide vers la position cible
                if abs(current_pos_y - target_y) > 1:
                    self.line_positions[line_idx] += (target_y - current_pos_y) * 0.2
                else:
                    self.line_positions[line_idx] = target_y
                
                display_y = self.line_positions[line_idx]
            else:
                # Nouvelle ligne, initialiser sa position
                self.line_positions.append(y_offset - self.scroll_offset)
                display_y = self.line_positions[line_idx]
            
            # Vérifier si visible (optimisation: ne pas dessiner hors écran)
            if display_y + line_height < content_y_start or display_y > content_y_start + content_height:
                y_offset += line_height
                continue
            
            # Couleurs minimalistes
            if change_type == 'add':
                color = (0, 255, 0)
                prefix = "+ "
            else:
                color = (255, 0, 100)
                prefix = "- "
            
            # Texte (tronqué)
            max_content_length = 60
            display_content = line_content[:max_content_length]
            display_text = prefix + display_content
            
            # Décalage pour centrer le texte
            text_offset_x = int(max_width * 0.1)
            
            # Texte direct sans fond (minimaliste)
            # Glow léger pour le relief
            for offset in [(1, 1), (-1, -1)]:
                glow_text = self.line_font.render(display_text, True, (0, 50, 0) if change_type == 'add' else (50, 0, 0))
                screen.blit(glow_text, (x_start + text_offset_x + offset[0], display_y + offset[1]))
            
            text_surface = self.line_font.render(display_text, True, color)
            screen.blit(text_surface, (x_start + text_offset_x, display_y))
            
            y_offset += line_height
        
        # Restaurer le clip
        screen.set_clip(old_clip)
        
        # Message d'info si aucune modification
        if not self.changes and not self.current_writing_line:
            message = ">>> Waiting for code changes..."
            # Effet typing pour le message
            typing_progress = int((current_time * 5) % (len(message) + 10))
            display_message = message[:min(typing_progress, len(message))]
            if typing_progress <= len(message):
                display_message += "█"
            
            info_text = self.info_font.render(display_message, True, (0, 200, 0))
            screen.blit(info_text, (x_start, content_y_start + int(line_height)))
        
        # Dessiner la barre de scroll style Matrix
        self.draw_scrollbar(screen, zone_x, zone_y, zone_width, zone_height, content_y_start, content_height)
    
    def draw_matrix_particles(self, screen, zone_x, zone_y, zone_width, zone_height):
        """Dessine les particules tombantes style Matrix (optimisé)"""
        current_time = time.time()
        
        # Limiter le nombre de particules pour la performance
        if len(self.particles) > 50:
            self.particles = self.particles[:50]
        
        # Dessiner et nettoyer les particules en une seule passe
        i = 0
        while i < len(self.particles):
            particle = self.particles[i]
            age = current_time - particle['created_at']
            
            if age > particle['life']:
                self.particles.pop(i)
                continue
            
            # Position de la particule
            x = zone_x + int(particle['x'] * zone_width * 0.01)
            y = zone_y + int((particle['y'] + age * particle['speed'] * 30) % zone_height)
            
            # Alpha basé sur la durée de vie (optimisé)
            alpha = int(255 * (1 - age / particle['life']))
            
            # Dessiner directement avec pygame.draw pour performance
            pygame.draw.circle(screen, (0, min(255, alpha + 50), 0), (x, y), 2)
            
            i += 1
    
    def draw_progress_bar(self, screen, zone_x, progress_y, zone_width, scrollbar_width, margin_x):
        """Dessine la barre de progression des modifications"""
        bar_width = zone_width - 2 * margin_x - scrollbar_width
        bar_height = 12
        bar_x = zone_x + margin_x
        
        # Fond de la barre
        pygame.draw.rect(screen, (0, 20, 0), (bar_x, progress_y, bar_width, bar_height), border_radius=6)
        
        # Bordure
        pygame.draw.rect(screen, (0, 150, 0), (bar_x, progress_y, bar_width, bar_height), width=2, border_radius=6)
        
        # Progression (basée sur le nombre de modifications)
        if self.total_modifications > 0:
            progress_ratio = min(1.0, self.total_modifications / 50)  # Max à 50 modifs pour une barre pleine
            fill_width = int((bar_width - 4) * progress_ratio)
            
            # Effet de gradient
            for i in range(fill_width):
                ratio = i / fill_width if fill_width > 0 else 0
                color_val = int(100 + 155 * ratio)
                color = (0, color_val, 0)
                pygame.draw.line(screen, color, 
                               (bar_x + 2 + i, progress_y + 2), 
                               (bar_x + 2 + i, progress_y + bar_height - 2))
            
            # Glow sur la barre de progression
            if fill_width > 0:
                glow_surface = pygame.Surface((fill_width + 10, bar_height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (0, 255, 0, 30), (0, 0, fill_width + 10, bar_height + 10), border_radius=8)
                screen.blit(glow_surface, (bar_x - 3, progress_y - 3))
        
        # Afficher le compteur
        counter_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", 14)
        counter_text = f"{self.total_modifications} MODIF{'S' if self.total_modifications > 1 else ''}"
        counter_surface = counter_font.render(counter_text, True, (0, 255, 0))
        counter_x = bar_x + bar_width + 10
        screen.blit(counter_surface, (counter_x, progress_y - 2))
    
    def draw_scrollbar(self, screen, zone_x, zone_y, zone_width, zone_height, content_y_start, content_height):
        """Dessine la barre de scroll style Matrix"""
        # Paramètres de la barre de scroll
        scrollbar_width = int(zone_width * 0.02)
        scrollbar_x = zone_x + zone_width - scrollbar_width - int(zone_width * 0.01)
        scrollbar_y = content_y_start
        scrollbar_height = content_height
        
        # Sauvegarder les rectangles pour les interactions
        self.scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        
        # Fond de la barre avec effet néon
        pygame.draw.rect(screen, (0, 20, 0), self.scrollbar_rect, border_radius=int(scrollbar_width // 2))
        pygame.draw.rect(screen, (0, 100, 0), self.scrollbar_rect, width=1, border_radius=int(scrollbar_width // 2))
        
        # Calculer la hauteur du curseur
        line_height = int(zone_height * 0.11)
        total_height = len(self.changes) * line_height
        visible_height = content_height
        
        if total_height > visible_height:
            handle_height = max(int(scrollbar_height * visible_height / total_height), 20)
            handle_ratio = self.scroll_offset / (total_height - visible_height) if (total_height - visible_height) > 0 else 0
            handle_y = scrollbar_y + int((scrollbar_height - handle_height) * handle_ratio)
        else:
            handle_height = scrollbar_height
            handle_y = scrollbar_y
        
        self.scrollbar_handle_rect = pygame.Rect(scrollbar_x, handle_y, scrollbar_width, handle_height)
        
        # Curseur avec glow
        is_hover = self.scrollbar_handle_rect.collidepoint(pygame.mouse.get_pos())
        handle_color = (0, 255, 0) if is_hover else (0, 200, 0)
        
        # Glow autour du curseur
        if is_hover:
            glow_surface = pygame.Surface((scrollbar_width + 8, handle_height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (0, 255, 0, 50), (0, 0, scrollbar_width + 8, handle_height + 8), border_radius=int(scrollbar_width // 2))
            screen.blit(glow_surface, (scrollbar_x - 4, handle_y - 4))
        
        pygame.draw.rect(screen, handle_color, self.scrollbar_handle_rect, border_radius=int(scrollbar_width // 2))
    
    def handle_scroll_input(self, event):
        """Gère les entrées souris pour la barre de scroll"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.scrollbar_handle_rect and self.scrollbar_handle_rect.collidepoint(event.pos):
                self.is_dragging_scrollbar = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging_scrollbar = False
        
        elif event.type == pygame.MOUSEMOTION and self.is_dragging_scrollbar:
            if self.scrollbar_rect:
                # Calculer la position du scroll en fonction de la souris
                handle_height = self.scrollbar_handle_rect.height
                max_scroll_area = self.scrollbar_rect.height - handle_height
                
                if max_scroll_area > 0:
                    line_height = int(pygame.display.get_surface().get_height() * 0.11)
                    total_height = len(self.changes) * line_height
                    visible_height = self.scrollbar_rect.height
                    
                    # Position relative dans la barre
                    relative_y = event.pos[1] - self.scrollbar_rect.y - (handle_height // 2)
                    relative_y = max(0, min(relative_y, max_scroll_area))
                    
                    # Convertir en scroll offset
                    scroll_ratio = relative_y / max_scroll_area if max_scroll_area > 0 else 0
                    self.scroll_offset = int(scroll_ratio * (total_height - visible_height))
    
    def get_previous_content(self):
        """Retourne le contenu précédent du fichier addons.py sous forme de chaîne"""
        return ''.join(self.previous_content)

_logger_instance = None

def get_logger():
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ChangeLogger()
    return _logger_instance

def draw_changes(screen, zone_x, zone_y, zone_width, zone_height):
    logger = get_logger()
    logger.draw(screen, zone_x, zone_y, zone_width, zone_height)
