import pygame
import time
import random
from threading import Lock

class ChangeLogger:
    """
    Stream-friendly code-change visualizer with persistent diff highlighting.
    """
    def __init__(self, file_path="addons/addons_new.py"):
        self.file_path = file_path
        self._lock = Lock()
        self._streaming = False

        # lines: list of tuples (content:str, is_diff:bool)
        self.lines = [("En attend les modifications", False)]

        self._partial_buffer = ""
        self.previous_content = self._read_file()

        # scroll & UI state
        self.scroll_offset = 0
        self.is_dragging_scrollbar = False
        self.scrollbar_rect = None
        self.scrollbar_handle_rect = None
        self.auto_scroll = True

        # visual particles
        self.particles = []

        # fonts
        self._cached_zone = (0, 0, 0, 0)
        self._title_font = None
        self._line_font = None
        self._info_font = None
        self._line_height = 18

        pygame.font.init()

    # ----------------------------
    # File API
    # ----------------------------
    def _read_file(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception:
            return []

    def on_file_modified(self, external_lock):
        """Diff the current file with previous content and mark changed lines persistently"""
        with external_lock:
            current_content = self._read_file()

        # preserve previous highlights
        old_lines_dict = {line: is_diff for line, is_diff in self.lines}
        new_lines = []

        for line in current_content:
            clean_line = line.rstrip('\n')
            if clean_line not in old_lines_dict:
                new_lines.append((clean_line, True))  # new line -> highlight
            else:
                new_lines.append((clean_line, old_lines_dict[clean_line]))  # preserve highlight

        with self._lock:
            self.lines = new_lines
            self._partial_buffer = ""
            self.auto_scroll = True

        self.previous_content = current_content

    def get_previous_content(self):
        """Return previous file content as string"""
        return ''.join(self.previous_content)

    # ----------------------------
    # Streaming API
    # ----------------------------
    def stream_code(self, chunk: str):
        if not chunk:
            return

        with self._lock:
            self._streaming = True
            self._partial_buffer += chunk
            while '\n' in self._partial_buffer:
                line, rest = self._partial_buffer.split('\n', 1)
                self.lines.append((line.rstrip('\r'), False))
                While len(self.lines) > 2000:
                    self.lines.pop(0)
                self._partial_buffer = rest
                self.auto_scroll = True

                # optional particles
                if len(self.particles) < 100:
                    for _ in range(2):
                        self.particles.append({
                            'x': random.random(),
                            'y': random.random(),
                            'speed': random.uniform(0.5, 2.0),
                            'life': random.uniform(1.0, 2.0),
                            'created_at': time.time()
                        })

    def finalize_stream(self):
        with self._lock:
            if self._partial_buffer:
                self._streaming = False
                self.lines.append((self._partial_buffer.rstrip('\r\n'), False))
                self._partial_buffer = ""
                self.auto_scroll = True

    # ----------------------------
    # Drawing / layout
    # ----------------------------
    def _ensure_fonts(self, zone_w, zone_h):
        if (zone_w, zone_h) == (self._cached_zone[2], self._cached_zone[3]) and self._title_font:
            return
        base = max(12, int(zone_h * 0.025))
        title_size = max(18, int(zone_h * 0.035))
        info_size = max(14, int(zone_h * 0.028))

        self._line_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", base)
        self._title_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", title_size)
        self._info_font = pygame.font.Font("Sniglet/Sniglet-Regular.ttf", info_size)
        self._line_height = self._line_font.get_linesize() + 2

        self._cached_zone = (0, 0, zone_w, zone_h)

    def draw_matrix_particles(self, screen, zone_x, zone_y, zone_w, zone_h):
        now = time.time()
        i = 0
        while i < len(self.particles):
            p = self.particles[i]
            age = now - p['created_at']
            if age > p['life']:
                self.particles.pop(i)
                continue
            x = zone_x + int(p['x'] * zone_w)
            y = zone_y + int((p['y'] + age * p['speed'] * 0.2) * zone_h) % (zone_y + zone_h)
            alpha = int(255 * max(0.0, 1 - age / p['life']))
            pygame.draw.circle(screen, (0, min(255, alpha + 50), 0), (x, y), 2)
            i += 1

    def draw(self, screen, zone_x, zone_y, zone_w, zone_h):
        self._ensure_fonts(zone_w, zone_h)

        margin_x = max(8, int(zone_w * 0.03))
        margin_y = max(8, int(zone_h * 0.03))
        content_x = zone_x + margin_x
        content_y = zone_y + margin_y + self._title_font.get_linesize() + 6
        content_w = zone_w - 2 * margin_x
        content_h = zone_h - (content_y - zone_y) - margin_y

        clip_rect = pygame.Rect(content_x, content_y, content_w, content_h)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        self.draw_matrix_particles(screen, zone_x, zone_y, zone_w, zone_h)

        # title
        title_surface = self._title_font.render("Modifications du code", True, (0, 255, 0))
        screen.blit(title_surface, (zone_x + margin_x, zone_y + margin_y))

        # snapshot
        with self._lock:
            lines_snapshot = list(self.lines)
            partial = self._partial_buffer

        total_lines = len(lines_snapshot) + (1 if partial else 0)
        total_height = total_lines * self._line_height

        # auto scroll
        max_scroll = max(0, total_height - content_h)
        if self.auto_scroll:
            self.scroll_offset = max_scroll
        else:
            self.scroll_offset = min(max_scroll, max(0, self.scroll_offset))

        # draw lines
        y = content_y - self.scroll_offset
        for content, is_diff in lines_snapshot:
            content_render = content.replace('\t', '    ')
            color = (0, 255, 0) if is_diff else (255, 255, 255)
            text_surface = self._line_font.render(content_render, True, color)
            if y + self._line_height >= content_y and y <= content_y + content_h:
                screen.blit(text_surface, (content_x, y))
            y += self._line_height

        # partial buffer
        if partial:
            typing_text = partial + ("█" if int(time.time() * 2) % 2 == 0 else "")
            text_surface = self._line_font.render(typing_text.replace('\t', '    '), True, (255, 255, 255))
            if y + self._line_height >= content_y and y <= content_y + content_h:
                screen.blit(text_surface, (content_x, y))
            y += self._line_height

        screen.set_clip(old_clip)

        # draw scrollbar
        self._draw_scrollbar(screen, zone_x, zone_y, zone_w, zone_h, content_x, content_y, content_h, total_height)

    # ----------------------------
    # Scrollbar
    # ----------------------------
    def _draw_scrollbar(self, screen, zone_x, zone_y, zone_w, zone_h, content_x, content_y, content_h, total_height):
        scrollbar_width = max(10, int(zone_w * 0.02))
        scrollbar_x = zone_x + zone_w - scrollbar_width - int(zone_w * 0.01)
        scrollbar_y = content_y
        scrollbar_h = content_h

        self.scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_h)
        pygame.draw.rect(screen, (30, 30, 30), self.scrollbar_rect, border_radius=scrollbar_width // 2)
        pygame.draw.rect(screen, (0, 100, 0), self.scrollbar_rect, width=1, border_radius=scrollbar_width // 2)

        if total_height <= content_h or total_height == 0:
            handle_h = scrollbar_h
            handle_y = scrollbar_y
        else:
            handle_h = max(20, int(scrollbar_h * (content_h / total_height)))
            max_scroll = total_height - content_h
            ratio = self.scroll_offset / max_scroll if max_scroll > 0 else 0.0
            handle_y = scrollbar_y + int((scrollbar_h - handle_h) * ratio)

        self.scrollbar_handle_rect = pygame.Rect(scrollbar_x, handle_y, scrollbar_width, handle_h)
        is_hover = self.scrollbar_handle_rect.collidepoint(pygame.mouse.get_pos())
        handle_color = (0, 255, 0) if is_hover else (0, 180, 0)
        pygame.draw.rect(screen, handle_color, self.scrollbar_handle_rect, border_radius=scrollbar_width // 2)

    def handle_scroll_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.scrollbar_handle_rect and self.scrollbar_handle_rect.collidepoint(event.pos):
                self.is_dragging_scrollbar = True
                self.auto_scroll = False
            elif event.button == 4:
                self.auto_scroll = False
                self.scroll_offset = max(0, self.scroll_offset - self._line_height * 3)
            elif event.button == 5:
                self.auto_scroll = False
                self.scroll_offset = min(self.scroll_offset + self._line_height * 3, 1e6)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging_scrollbar = False
        elif event.type == pygame.MOUSEMOTION and self.is_dragging_scrollbar:
            if not self.scrollbar_rect or not self.scrollbar_handle_rect:
                return
            handle_h = self.scrollbar_handle_rect.height
            max_scroll_area = self.scrollbar_rect.height - handle_h
            if max_scroll_area <= 0:
                return
            rel_y = event.pos[1] - self.scrollbar_rect.y - handle_h // 2
            rel_y = max(0, min(rel_y, max_scroll_area))
            ratio = rel_y / max_scroll_area
            with self._lock:
                total_lines = len(self.lines) + (1 if self._partial_buffer else 0)
            total_height = total_lines * self._line_height
            max_scroll = max(0, total_height - self.scrollbar_rect.height)
            self.scroll_offset = int(ratio * max_scroll)
            self.auto_scroll = False


# ----------------------------
# Singleton access
# ----------------------------
_logger_instance = None
def get_logger():
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ChangeLogger()
    return _logger_instance

def draw_changes(screen, zone_x, zone_y, zone_w, zone_h):
    get_logger().draw(screen, zone_x, zone_y, zone_w, zone_h)
