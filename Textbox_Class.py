import pygame
from just_playback import Playback
import tempfile
import magic
import mimetypes
import os
import pyperclip
import wave


class Textbox:
    def __init__(self, base_rect, border_size, text_padding, line_spacing, font, border_color, background_color, ui_manager=None):
        self.border_size = border_size
        self.text_padding = text_padding
        self.line_spacing = line_spacing
        self.border_color = border_color
        self.background_color = background_color
        self.ui_manager = ui_manager
        self.font = font

        self.border_rect = pygame.Rect(base_rect)
        self.background_rect = pygame.Rect(
            base_rect[0] + border_size,
            base_rect[1] + border_size,
            base_rect[2] - border_size * 2,
            base_rect[3] - border_size * 2
        )
        self.visible_text_rect = pygame.Rect(
            self.background_rect[0] + text_padding,
            self.background_rect[1] + text_padding,
            self.background_rect[2] - text_padding * 2 - 20,  # место под скроллбар
            self.background_rect[3] - text_padding * 2
        )

        self.scroll_y = 0
        self.messages = []
        self.content = []
        self.audio_players = []
        self.visible_messages = []
        self.total_height = 0
        self.line_height = font.get_linesize() + line_spacing

        self.i_beam_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_IBEAM)
        self.normal_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.pointy_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)

        self.scroll_bar = None
        self.mouse_position = (0, 0)
        self.scroll_bar_button_pressed = False
        self.pressed_mouse_position = (0, 0)

        # Атрибуты для выделения текста
        self.selection_active = False
        self.selection_start = None   # (index_in_content, char_offset)
        self.selection_end = None
        self.selection_rects = []

    def append_messages(self, messages):
        for message in messages:
            if 'color' in message:
                color = pygame.Color(message['color'])
            else:
                color = None
            self.messages.append({
                'type': message['type'],
                'value': message['value'],
                'position': len(self.messages) + 1
            })

            if message['type'] == 'text':
                # Подготовка токенов: список слов с цветами
                if isinstance(message['value'], str):
                    # Старый формат: строка + один цвет
                    words = message['value'].split()
                    tokens = [{'text': w, 'color': color} for w in words]
                else:
                    # Новый формат: список сегментов {'text': ..., 'color': ...}
                    tokens = []
                    for seg in message['value']:
                        c = pygame.Color(seg['color']) if 'color' in seg else color
                        # Разбиваем сегмент на слова (на случай, если в нём пробелы)
                        for w in seg['text'].split():
                            tokens.append({'text': w, 'color': c})

                # Перенос строк по ширине с использованием токенов
                line_tokens = []  # токены текущей строки
                current_width = 0
                for token in tokens:
                    word = token['text']
                    word_width = self.font.size(word)[0]
                    space_width = self.font.size(' ')[0] if line_tokens else 0

                    if current_width + space_width + word_width <= self.visible_text_rect.width:
                        line_tokens.append(token)
                        current_width += space_width + word_width
                    else:
                        # Строка заполнена, финализируем её
                        self._add_text_line(line_tokens)
                        # Начинаем новую строку с текущего слова
                        line_tokens = [token]
                        current_width = word_width

                # Последняя строка
                if line_tokens:
                    self._add_text_line(line_tokens)

            elif message['type'] == 'image':
                img_surface = message['value']
                height = img_surface.get_height()
                self.content.append({
                    'type': 'image',
                    'surface': img_surface,
                    'height': height,
                    'message_id': len(self.messages)
                })
                self.total_height += height

            elif message['type'] == 'audio':
                player_width = self.visible_text_rect.width
                player_height = 54
                if self.content:
                    last_element = self.content[-1]
                    last_visible = self.visible_messages[-1]
                    dest_y = self.visible_text_rect.y + last_element['height'] + last_visible['y']
                else:
                    dest_y = self.visible_text_rect.y

                player_rect = (self.visible_text_rect.x, dest_y, player_width, player_height)
                audio_player = AudioPlayer(player_rect, 2, self.border_color, self.background_color, self.font)
                audio_data = message['value']
                if isinstance(audio_data, str):
                    audio_player.load_audio(audio_path=audio_data)
                elif isinstance(audio_data, bytes):
                    audio_player.load_audio(audio_bytes=audio_data)

                self.audio_players.append(audio_player)
                self.content.append({
                    'type': 'audio',
                    'player': audio_player,
                    'height': player_height,
                    'message_id': len(self.messages)
                })
                self.total_height += player_height

        self.scroll_y = max(0, self.total_height - self.visible_text_rect.height)
        self.update_visible_elements()
        self.check_for_scroll_bar()
        if self.scroll_bar:
            self.scroll_bar.calculate_button_height(self.total_height, self.visible_text_rect.height)
            self.scroll_bar.set_scrolled_percentage(1)

    def _get_char_pos_at(self, x, y):
        """Возвращает (index_in_content, char_offset) или None, если позиция не над текстом."""
        if not self.visible_text_rect.collidepoint(x, y):
            return None
        rel_x = x - self.visible_text_rect.x
        rel_y = y - self.visible_text_rect.y + self.scroll_y

        current_y = 0
        for idx, element in enumerate(self.content):
            if element['type'] != 'text':
                current_y += element['height']
                continue
            if current_y <= rel_y < current_y + element['height']:
                text = element['text']
                char_offset = 0
                while char_offset < len(text):
                    width = self.font.size(text[:char_offset + 1])[0]
                    if width > rel_x:
                        break
                    char_offset += 1
                return idx, char_offset
            current_y += element['height']
        return None

    def _set_selection(self, start_idx, start_char, end_idx, end_char):
        # Нормализация порядка
        if (start_idx, start_char) > (end_idx, end_char):
            start_idx, end_idx = end_idx, start_idx
            start_char, end_char = end_char, start_char
        self.selection_start = (start_idx, start_char)
        self.selection_end = (end_idx, end_char)
        self._update_selection_rects()

    def _update_selection_rects(self):
        self.selection_rects.clear()
        if not self.selection_start or not self.selection_end:
            return
        start_idx, start_char = self.selection_start
        end_idx, end_char = self.selection_end

        for idx in range(start_idx, end_idx + 1):
            element = self.content[idx]
            if element['type'] != 'text':
                continue
            text = element['text']
            line_start_char = start_char if idx == start_idx else 0
            line_end_char = end_char if idx == end_idx else len(text)
            if line_start_char == line_end_char:
                continue

            x_start = self.visible_text_rect.x + self.font.size(text[:line_start_char])[0]
            x_end = self.visible_text_rect.x + self.font.size(text[:line_end_char])[0]

            # Вычисляем абсолютную Y-координату строки в content
            absolute_y = 0
            for i in range(idx):
                absolute_y += self.content[i]['height']
            screen_y = self.visible_text_rect.y + absolute_y - self.scroll_y

            # Добавляем прямоугольник только если он видим
            if screen_y + element['height'] > self.visible_text_rect.y and screen_y < self.visible_text_rect.bottom:
                rect = pygame.Rect(x_start, screen_y, x_end - x_start, element['height'])
                self.selection_rects.append(rect)

    def _add_text_line(self, line_tokens):
        if not line_tokens:
            return
        full_text = ' '.join(t['text'] for t in line_tokens)
        segments = []
        x = 0
        for token in line_tokens:
            word_surf = self.font.render(token['text'], False, token['color'])
            segments.append({
                'surface': word_surf,
                'x_offset': x,
                'text': token['text']
            })
            x += word_surf.get_width() + self.font.size(' ')[0]

        self.content.append({
            'type': 'text',
            'text': full_text,
            'segments': segments,
            'height': self.line_height,
            'message_id': len(self.messages)
        })
        # ✅ Увеличиваем общую высоту на высоту одной строки
        self.total_height += self.line_height

    def copy_selection(self):
        if not self.selection_start or not self.selection_end:
            return
        start_idx, start_char = self.selection_start
        end_idx, end_char = self.selection_end
        selected_parts = []
        for idx in range(start_idx, end_idx + 1):
            element = self.content[idx]
            if element['type'] != 'text':
                continue
            text = element['text']
            line_start = start_char if idx == start_idx else 0
            line_end = end_char if idx == end_idx else len(text)
            if line_start < line_end:
                selected_parts.append(text[line_start:line_end])
        if selected_parts:
            pyperclip.copy(' '.join(selected_parts))

    def render(self, screen: pygame.Surface):
        screen.fill(self.border_color, self.border_rect)
        screen.fill(self.background_color, self.background_rect)

        if self.visible_messages:
            old_clip = screen.get_clip()
            screen.set_clip(self.visible_text_rect)

            for rect in self.selection_rects:
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                s.fill((0, 84, 255, 204))
                screen.blit(s, rect)

            for msg in self.visible_messages:
                element = msg['element']
                dest_y = self.visible_text_rect.y + msg['y']

                if element['type'] == 'text':
                    if 'segments' in element:
                        # Разноцветная строка
                        for seg in element['segments']:
                            screen.blit(seg['surface'], (self.visible_text_rect.x + seg['x_offset'], dest_y))
                    else:
                        # Одноцветная строка (старый формат)
                        screen.blit(element['surface'], (self.visible_text_rect.x, dest_y))

                elif element['type'] == 'image':
                    screen.blit(element['surface'], (self.visible_text_rect.x, dest_y))

                elif element['type'] == 'audio':
                    player = element['player']
                    if self.visible_text_rect.colliderect(player.border_rect):
                        player.render(screen)
            screen.set_clip(old_clip)

        if self.scroll_bar:
            self.scroll_bar.render(screen)
            self.scroll_bar.button.render(screen)

        for player in self.audio_players:
            player.update()

    def check_for_scroll_bar(self):
        if not self.scroll_bar and self.total_height > self.visible_text_rect.height:
            scroll_rect = (
                self.background_rect.x + self.background_rect.width - 20,
                self.background_rect.y,
                20,
                self.background_rect.height
            )
            self.scroll_bar = ScrollBar(scroll_rect, 1, self.border_color, self.background_color)
            self.scroll_bar.calculate_button_height(self.total_height, self.visible_text_rect.height)

    def update_visible_elements(self):
        self.visible_messages.clear()
        current_y = 0
        visible_top = self.scroll_y
        visible_bottom = visible_top + self.visible_text_rect.height

        for element in self.content:
            element_top = current_y
            element_bottom = current_y + element['height']

            if element_bottom > visible_top and element_top < visible_bottom:
                offset_y = max(0, visible_top - element_top)
                visible_height = min(
                    element['height'] - offset_y,
                    visible_bottom - element_top
                )
                relative_y = element_top - self.scroll_y

                self.visible_messages.append({
                    'element': element,
                    'y': relative_y,
                    'offset': offset_y,
                    'visible_height': visible_height
                })

                if element['type'] == 'audio':
                    player = element['player']
                    player_screen_y = self.visible_text_rect.y + relative_y
                    player.set_absolute_y(player_screen_y)

            current_y += element['height']

        # После обновления видимых элементов пересчитываем прямоугольники выделения
        self._update_selection_rects()

    def _is_mouse_over_gui(self) -> bool:
        """Возвращает True, если мышь находится над любым элементом pygame-gui."""
        if self.ui_manager is None:
            return False
        # Используем публичный метод UIManager для проверки
        return self.ui_manager.get_hovering_any_element()

    def process_events(self, event: pygame.event.Event):
        collided_with_player = False
        for player in self.audio_players:
            if player.process_events(event):
                collided_with_player = True

        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if self.visible_text_rect.collidepoint(mouse_pos):
                max_scroll = max(0, self.total_height - self.visible_text_rect.height)
                if max_scroll > 0:
                    delta = -event.y * self.line_height
                    self.scroll_y = pygame.math.clamp(self.scroll_y + delta, 0, max_scroll)
                    self.update_visible_elements()
                    if self.scroll_bar:
                        percentage = self.scroll_y / max_scroll
                        self.scroll_bar.set_scrolled_percentage(percentage)



        # Обработка выделения текста
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed_mouse_position = event.pos
            if self.scroll_bar and self.scroll_bar.button.border_rect.collidepoint(event.pos):
                self.scroll_bar_button_pressed = True
                self.scroll_bar.button.relative_pressed_position = event.pos[1] - self.scroll_bar.button.border_rect.y
                # Сброс выделения при клике на скроллбар
                self.selection_active = False
                self.selection_start = self.selection_end = None
                self.selection_rects.clear()
            else:
                # Проверяем, кликнули ли по аудиоплееру
                clicked_on_player = any(p.border_rect.collidepoint(event.pos) for p in self.audio_players)
                if self.visible_text_rect.collidepoint(event.pos) and not clicked_on_player:
                    pos = self._get_char_pos_at(*event.pos)
                    if pos:
                        idx, char = pos
                        self.selection_active = True
                        self.selection_start = (idx, char)
                        self.selection_end = (idx, char)
                        self._update_selection_rects()
                    else:
                        # Клик вне текста (пустое место) – сброс выделения
                        self.selection_active = False
                        self.selection_start = self.selection_end = None
                        self.selection_rects.clear()
                else:
                    # Клик вне текстовой области или на плеере – сброс
                    self.selection_active = False
                    self.selection_start = self.selection_end = None
                    self.selection_rects.clear()


        elif event.type == pygame.MOUSEMOTION:

            self.mouse_position = event.pos

            # Расширение выделения при зажатой левой кнопке (без изменений)

            if self.selection_active and pygame.mouse.get_pressed()[0]:

                pos = self._get_char_pos_at(*event.pos)

                if pos:

                    idx, char = pos

                    if (idx, char) != self.selection_end:
                        self._set_selection(self.selection_start[0], self.selection_start[1], idx, char)

            # Обновление курсора ТОЛЬКО если мышь НЕ над pygame-gui

            if not self._is_mouse_over_gui():

                scroll_bar_collided = self.scroll_bar and self.scroll_bar.border_rect.collidepoint(self.mouse_position)

                current_cursor = pygame.mouse.get_cursor()

                if not collided_with_player:

                    if self.border_rect.collidepoint(self.mouse_position) and not scroll_bar_collided:

                        if current_cursor != self.i_beam_cursor:
                            pygame.mouse.set_cursor(self.i_beam_cursor)

                    else:

                        if current_cursor == self.i_beam_cursor:
                            pygame.mouse.set_cursor(self.normal_cursor)

                elif current_cursor != self.pointy_cursor:

                    pygame.mouse.set_cursor(self.pointy_cursor)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.scroll_bar_button_pressed = False
            if self.selection_active:
                self.selection_active = False
                # Выделение остаётся

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                self.copy_selection()

        # Перетаскивание скроллбара (как в оригинале)
        if self.scroll_bar_button_pressed:
            delta_y = self.mouse_position[1] - self.scroll_bar.button.border_rect.y
            button_y = self.scroll_bar.button.border_rect.y + delta_y - self.scroll_bar.button.relative_pressed_position
            min_y = self.scroll_bar.background_rect.top
            max_y = self.scroll_bar.background_rect.bottom - self.scroll_bar.button.border_rect.height
            button_y = pygame.math.clamp(button_y, min_y, max_y)
            self.scroll_bar.button.set_button_y_position(button_y)

            percentage = self.scroll_bar.get_scrolled_percentage()
            max_scroll = max(0, self.total_height - self.visible_text_rect.height)
            self.scroll_y = percentage * max_scroll
            self.update_visible_elements()


class ScrollBar:
    def __init__(self, base_rect, border_size, border_color, background_color):
        self.border_size = border_size
        self.border_color = border_color
        self.background_color = background_color

        self.border_rect = pygame.Rect(base_rect)
        self.background_rect = pygame.Rect(
            base_rect[0] + border_size,
            base_rect[1] + border_size,
            base_rect[2] - border_size * 2,
            base_rect[3] - border_size * 2
        )
        self.minimal_button_height = 15
        self.button = SliderButton(
            (self.background_rect.x, self.background_rect.y, self.background_rect.width, 0),
            border_size, border_color, 'white'
        )

    def calculate_button_height(self, lines_height, visible_height):
        new_height = max(
            (visible_height / lines_height) * self.background_rect.height,
            self.minimal_button_height
        )
        self.button.set_button_height(new_height)

    def render(self, screen):
        screen.fill(self.border_color, self.border_rect)
        screen.fill(self.background_color, self.background_rect)

    def get_scrolled_percentage(self):
        track_y = self.background_rect.y
        track_h = self.background_rect.height
        button_h = self.button.border_rect.height
        return (self.button.border_rect.y - track_y) / (track_h - button_h)

    def set_scrolled_percentage(self, percentage):
        track_y = self.background_rect.y
        track_h = self.background_rect.height
        button_h = self.button.border_rect.height
        self.button.set_button_y_position(percentage * (track_h - button_h) + track_y)


class SliderButton:
    def __init__(self, base_rect, border_size, border_color, background_color):
        self.border_size = border_size
        self.border_color = border_color
        self.background_color = background_color
        self.relative_pressed_position = 0

        self.border_rect = pygame.Rect(base_rect)
        self.background_rect = pygame.Rect(
            self.border_rect.x + border_size,
            self.border_rect.y + border_size,
            self.border_rect.width - border_size * 2,
            self.border_rect.height - border_size * 2
        )

    def set_button_height(self, height):
        self.border_rect.height = height
        self.background_rect = pygame.Rect(
            self.border_rect.x + self.border_size,
            self.border_rect.y + self.border_size,
            self.border_rect.width - self.border_size * 2,
            height - self.border_size * 2
        )

    def set_button_y_position(self, y):
        self.border_rect.y = y
        self.background_rect.y = y + self.border_size

    def render(self, screen):
        screen.fill(self.border_color, self.border_rect)
        screen.fill(self.background_color, self.background_rect)


class AudioPlayer:
    def __init__(self, base_rect, border_size, border_color, background_color, font):
        self.playback = Playback()
        self.border_color = border_color
        self.background_color = background_color
        self.border_size = border_size
        self.font = font

        self.border_radius = base_rect[3] // 2
        self.border_rect = pygame.Rect(base_rect)
        self.background_rect = pygame.Rect(
            base_rect[0] + border_size,
            base_rect[1] + border_size,
            base_rect[2] - border_size * 2,
            base_rect[3] - border_size * 2
        )
        self.button_radius = int(self.border_radius / 1.6875)
        self.scale_factor = 54 / self.border_rect.height

        # Play button
        self.play_button_center = (self.border_rect.x + self.border_radius, self.border_rect.centery)
        self.play_button_color = [int(c * 0.8) for c in background_color]
        self.play_button_rect = pygame.Rect(
            self.play_button_center[0] - self.button_radius,
            self.play_button_center[1] - self.button_radius,
            self.button_radius * 2,
            self.button_radius * 2
        )
        self.play_symbol_play = font.render('▶', True, border_color)
        self.play_symbol_pause = font.render('⏸', True, border_color)
        self.play_symbol_rect = self.play_symbol_play.get_rect(
            center=(self.play_button_center[0] + 1 * self.scale_factor,
                    self.play_button_center[1] - 2 * self.scale_factor)
        )

        # Sound button
        self.sound_button_center = (self.border_rect.right - self.border_radius, self.border_rect.centery)
        self.sound_button_rect = pygame.Rect(
            self.sound_button_center[0] - self.button_radius,
            self.sound_button_center[1] - self.button_radius,
            self.button_radius * 2,
            self.button_radius * 2
        )
        self.sound_area_color = [int(c * 0.8) for c in background_color]
        self.sound_area_rect = pygame.Rect(
            self.sound_button_center[0] - 100 * self.scale_factor + self.button_radius,
            self.sound_button_center[1] - self.button_radius,
            100 * self.scale_factor,
            self.button_radius * 2
        )
        self.sound_slider_bar = SliderBar(
            (self.sound_area_rect.x + self.button_radius,
             self.sound_area_rect.centery - 3 * self.scale_factor / 2,
             self.sound_area_rect.width - self.button_radius * 3,
             3 * self.scale_factor),
            self.scale_factor,
            border_color
        )

        self.sound_symbol_muted = font.render('🔇', True, border_color)
        self.sound_symbol_low = font.render('🔈', True, border_color)
        self.sound_symbol_mid = font.render('🔉', True, border_color)
        self.sound_symbol_high = font.render('🔊', True, border_color)
        self.sound_symbol_rect = self.play_symbol_play.get_rect(
            center=(self.sound_button_center[0] + 1 * self.scale_factor,
                    self.sound_button_center[1] - 3 * self.scale_factor)
        )
        self.volume = 1.0

        self.duration_area_color = [int(c * 0.8) for c in background_color]
        self.duration_area_rect = pygame.Rect(
            self.play_button_rect.right,
            self.play_button_rect.y,
            self.sound_button_rect.left - self.play_button_rect.right,
            self.button_radius * 2
        )
        self.duration_slider_bar_squeezed = self.sound_area_rect.left - self.play_button_rect.right - self.button_radius * 2
        self.duration_slider_bar_unsqueezed = self.duration_area_rect.width - self.button_radius * 2
        self.duration_slider_bar = SliderBar(
            (self.duration_area_rect.x + self.button_radius,
             self.duration_area_rect.centery - 3 * self.scale_factor / 2,
             self.duration_slider_bar_unsqueezed,
             3 * self.scale_factor),
            self.scale_factor,
            border_color
        )

        self.mouse_position = (0, 0)
        self.pressed_mouse_position = (0, 0)
        self.mouse_pressed_button = None
        self.duration_rect_collided = False
        self.play_button_collided = False
        self.paused = False
        self.playing = False
        self.sound_slider_visible = False

        self.pointy_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)
        self.normal_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)

    def set_absolute_y(self, y):
        self.border_rect.y = y
        self.background_rect.y = y + self.border_size
        self._update_rects_y()

    def _update_rects_y(self):
        self.play_button_center = (self.play_button_center[0], self.border_rect.centery)
        self.play_button_rect.y = self.play_button_center[1] - self.button_radius
        self.play_symbol_rect.centery = self.play_button_center[1] - 2 * self.scale_factor

        self.sound_button_center = (self.sound_button_center[0], self.border_rect.centery)
        self.sound_button_rect.y = self.sound_button_center[1] - self.button_radius
        self.sound_area_rect.y = self.sound_button_center[1] - self.button_radius
        self.sound_slider_bar.main_rect.centery = self.sound_area_rect.centery
        self.sound_symbol_rect.centery = self.sound_button_center[1] - 3 * self.scale_factor

        self.duration_area_rect.y = self.play_button_rect.y
        self.duration_slider_bar.main_rect.centery = self.duration_area_rect.centery

    def get_height(self):
        return self.border_rect.height

    def update(self):
        if self.playing and not self.paused:
            self.playing = self.playback.active
            if self.playback.duration > 0:
                self.duration_slider_bar.set_percentage(self.playback.curr_pos / self.playback.duration)

    def load_audio(self, audio_path=None, audio_bytes=None):
        if audio_path:
            self.playback.load_file(audio_path)
        elif audio_bytes:
            os.makedirs('resources/temp/audios', exist_ok=True)
            mimetype = magic.from_buffer(audio_bytes, mime=True)
            extension = mimetypes.guess_extension(mimetype) or ''
            if extension != '.bin':
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir='resources/temp/audios') as temp_file:
                    temp_file.write(audio_bytes)
                    temp_audio_path = temp_file.name
            else:
                channels = 2  # Моно
                sampwidth = 2  # 2 байта (16 бит)
                framerate = 44100  # 44.1 кГц
                audio_number = len(os.listdir('resources/temp/audios'))
                temp_audio_path = f'resources/temp/audios/{audio_number}.wav'

                with wave.open(temp_audio_path, 'wb') as wav_file:
                    wav_file.setnchannels(channels)
                    wav_file.setsampwidth(sampwidth)
                    wav_file.setframerate(framerate)
                    wav_file.writeframes(audio_bytes)  # Запись пустых байтов

            self.playback.load_file(temp_audio_path)

    def set_volume_exponential(self, volume):
        self.playback.set_volume(pygame.math.clamp(volume, 0, 1) ** 2)

    def set_duration(self, duration_percentage):
        clamped = pygame.math.clamp(duration_percentage, 0, 1)
        self.playback.seek(self.playback.duration * clamped)

    def render(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.background_color, self.background_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.border_color, self.border_rect, width=self.border_size, border_radius=self.border_radius)

        # Play button
        if self.play_button_collided or self.mouse_pressed_button == 'play':
            pygame.draw.circle(screen, self.play_button_color, self.play_button_center, self.button_radius)
        symbol = self.play_symbol_pause if (self.playing and not self.paused) else self.play_symbol_play
        screen.blit(symbol, self.play_symbol_rect)

        # Sound slider (if visible)
        if self.sound_slider_visible or self.mouse_pressed_button == 'sound bar':
            pygame.draw.rect(screen, self.sound_area_color, self.sound_area_rect, border_radius=self.button_radius)
            self.sound_slider_bar.render(screen)

        # Volume icon
        if self.volume == 0:
            icon = self.sound_symbol_muted
        elif self.volume <= 0.25:
            icon = self.sound_symbol_low
        elif self.volume <= 0.5:
            icon = self.sound_symbol_mid
        else:
            icon = self.sound_symbol_high
        screen.blit(icon, self.sound_symbol_rect)

        # Duration slider highlight
        if (self.duration_rect_collided or self.mouse_pressed_button == 'duration bar') and not self.sound_slider_visible:
            pygame.draw.rect(screen, self.duration_area_color, self.duration_area_rect, border_radius=self.button_radius)

        self.duration_slider_bar.render(screen)

    def process_events(self, event: pygame.event.Event):
        collided = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed_mouse_position = event.pos
            if self.play_button_rect.collidepoint(self.mouse_position):
                collided = True
                self.mouse_pressed_button = 'play'
            elif self.sound_area_rect.collidepoint(self.mouse_position) and self.sound_slider_visible:
                collided = True
                self.mouse_pressed_button = 'sound bar'
            elif self.duration_area_rect.collidepoint(self.mouse_position) and not self.sound_slider_visible:
                collided = True
                self.mouse_pressed_button = 'duration bar'

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.play_button_rect.collidepoint(self.mouse_position):
                if self.paused:
                    self.playback.resume()
                elif not self.playing:
                    self.playback.play()
                else:
                    self.playback.pause()
                self.paused = not self.playback.playing
                self.playing = self.playback.active
            self.mouse_pressed_button = None

        if event.type == pygame.MOUSEMOTION:
            self.mouse_position = event.pos
            if pygame.mouse.get_cursor() == self.pointy_cursor:
                pygame.mouse.set_cursor(self.normal_cursor)

            # Определение видимости слайдера громкости
            on_sound_icon = self.sound_button_rect.collidepoint(self.mouse_position)
            on_sound_area = self.sound_area_rect.collidepoint(self.mouse_position)
            self.sound_slider_visible = (
                on_sound_icon or
                (self.sound_slider_visible and on_sound_area) or
                self.mouse_pressed_button == 'sound bar'
            )
            if self.sound_slider_visible:
                collided = True

            # Сжатие слайдера длительности
            target_width = self.duration_slider_bar_squeezed if self.sound_slider_visible else self.duration_slider_bar_unsqueezed
            if self.duration_slider_bar.main_rect.width != target_width:
                self.duration_slider_bar.squeeze(target_width)

            self.duration_rect_collided = (
                not self.sound_slider_visible and
                self.duration_area_rect.collidepoint(self.mouse_position)
            )

            # Смена курсора
            self.play_button_collided = False
            show_hand = False
            if self.play_button_rect.collidepoint(self.mouse_position):
                show_hand = True
                self.play_button_collided = True
            elif self.sound_button_rect.collidepoint(self.mouse_position) and not self.duration_rect_collided:
                show_hand = True
            elif self.sound_slider_visible and self.sound_area_rect.collidepoint(self.mouse_position):
                show_hand = True
            elif not self.sound_slider_visible and self.duration_rect_collided:
                show_hand = True

            if show_hand:
                pygame.mouse.set_cursor(self.pointy_cursor)
                collided = True
            else:
                pygame.mouse.set_cursor(self.normal_cursor)

            # Перетаскивание слайдеров
            if self.mouse_pressed_button == 'sound bar' and self.sound_slider_visible:
                self.sound_slider_bar.set_circle_x_position(self.mouse_position[0])
                self.volume = self.sound_slider_bar.get_percentage()
                self.set_volume_exponential(self.volume)
                collided = True
            elif self.mouse_pressed_button == 'duration bar' and not self.sound_slider_visible:
                self.duration_slider_bar.set_circle_x_position(self.mouse_position[0])
                self.set_duration(self.duration_slider_bar.get_percentage())
                collided = True

        return collided


class SliderBar:
    def __init__(self, main_rect, scale_factor, color):
        self.main_rect = pygame.Rect(main_rect)
        self.border_radius = self.main_rect.height // 2
        self.circle_x = self.main_rect.right
        self.circle_radius = 3 * scale_factor
        self.color = color
        self.hidden = False

    def get_percentage(self):
        return (self.circle_x - self.main_rect.x) / self.main_rect.width

    def set_percentage(self, percentage):
        self.circle_x = percentage * self.main_rect.width + self.main_rect.x

    def set_circle_x_position(self, x):
        self.circle_x = pygame.math.clamp(x, self.main_rect.left, self.main_rect.right)

    def squeeze(self, width):
        percentage = self.get_percentage()
        self.main_rect.width = width
        self.set_percentage(percentage)

    def render(self, screen):
        if not self.hidden:
            pygame.draw.rect(screen, self.color, self.main_rect, border_radius=self.border_radius)
            pygame.draw.circle(screen, self.color, (self.circle_x, self.main_rect.centery), self.circle_radius)

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False