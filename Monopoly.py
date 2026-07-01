# для прочего
import time
import os
import traceback
import gc
import pprint
import json
import datetime
import sys
import subprocess

# import cProfile, pstats
# profiler = cProfile.Profile()
# profiler.enable()

os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (0, 31) # (0, 31)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# для функционала игры
import pygame as pg
import socket as sck
import threading
import math

# для отправки файлов
import io
from PIL import Image, UnidentifiedImageError
import base64
import tkinter
import tkinter.filedialog
import zlib
import mimetypes

# для интерфейса
import pygame_gui

# классы
from classes.Players_Class_Client_side import Player
from classes.Recorder_Class import AudioRecorder
from classes.ProgressBar_Class import ProgressBar
from classes.CurrencyDrawingButton_Class import CurrencyDrawingButton
from classes.Settings_Class import Settings

# функции
from functions.all_tiles_extraction import all_tiles_get, all_tiles_change_resolution
from functions.colored_output import thread_open, information_sent, information_received, new_connection
from functions.resolution_choice import resolution_definition
from functions.character_checks import forbidden_characters_check, allowed_characters_check
from functions.bmcf import write_bmcf, read_bmcf, change_currency_character


def settings_buttons():
    global start_game_button, dropdown, fps_textbox, minimize_window_fps_optimization_checkbox, minimize_window_fps_optimization_textbox, inactivity_fps_optimization_checkbox, inactivity_fps_optimization_textbox, debug_checkbox, pick_color_button, color_picker, fullscreen_checkbox, scale_checkbox, apply_button, currency_draw_button

    if settings.resolution_index == 1:
        resolution_ = '1280x720'
    elif settings.resolution_index == 2:
        resolution_ = '1920x1080'
    elif settings.resolution_index == 3:
        resolution_ = '2560x1440'

    dropdown = pygame_gui.elements.UIDropDownMenu(
        relative_rect=pg.Rect(settings_buttons_coordinates['dropdown']),
        starting_option=resolution_,
        options_list=['1280x720', '1920x1080', '2560x1440'],
        manager=manager)

    fps_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['fps_textbox']),
        placeholder_text='',
        initial_text=str(settings.max_fps),
        object_id='#settings_font',
        manager=manager)

    minimize_window_fps_optimization_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['minimize_window_fps_optimization_checkbox']),
        text='',
        initial_state=settings.minimize_fps_optimize,
        manager=manager)

    minimize_window_fps_optimization_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['minimize_window_fps_optimization_textbox']),
        placeholder_text='',
        initial_text=str(settings.minimize_fps),
        object_id='#settings_font',
        manager=manager)

    inactivity_fps_optimization_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['inactivity_fps_optimization_checkbox']),
        text='',
        initial_state=settings.inactive_fps_optimize,
        manager=manager)

    inactivity_fps_optimization_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['inactivity_fps_optimization_textbox']),
        placeholder_text='',
        initial_text=str(settings.inactive_fps),
        object_id='#settings_font',
        manager=manager)

    debug_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['debug_checkbox']),
        text='',
        initial_state=settings.debug,
        manager=manager)

    fullscreen_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['fullscreen_checkbox']),
        text='',
        initial_state=settings.fullscreen,
        manager=manager)

    scale_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['scale_checkbox']),
        text='',
        initial_state=settings.scaled,
        manager=manager)
    if not fullscreen_checkbox.get_state():
        scale_checkbox.disable()

    pick_color_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(settings_buttons_coordinates['pick_color_button']),
        text='Выбрать цвет фона',
        object_id='#settings_font',
        manager=manager)

    apply_button = pygame_gui.elements.UIButton(
        relative_rect=settings_buttons_coordinates['apply_button'],
        text='Применить',
        object_id='#settings_font',
        manager=manager)

    currency_draw_button = pygame_gui.elements.UIButton(
        relative_rect=settings_buttons_coordinates['currency_draw_button'],
        text='Изменить ¤',
        object_id='#settings_font',
        manager=manager)

    color_picker = pygame_gui.windows.UIColourPickerDialog(
        rect=pg.Rect(settings_buttons_coordinates['color_picker']),
        initial_colour=settings.background_color_converted,
        manager=manager,
        visible=False)

    start_game_button = pygame_gui.elements.UIButton(
        relative_rect=settings_buttons_coordinates['start_game_button'],
        text='Начать игру',
        object_id='#settings_font',
        manager=manager)

    screen_widgets['settings start'] = [
        [dropdown, dropdown.visible],
        [fps_textbox, fps_textbox.visible],
        [minimize_window_fps_optimization_checkbox, minimize_window_fps_optimization_checkbox.visible],
        [minimize_window_fps_optimization_textbox, minimize_window_fps_optimization_textbox.visible],
        [inactivity_fps_optimization_checkbox, inactivity_fps_optimization_checkbox.visible],
        [inactivity_fps_optimization_textbox, inactivity_fps_optimization_textbox.visible],
        [debug_checkbox, debug_checkbox.visible],
        [fullscreen_checkbox, fullscreen_checkbox.visible],
        [scale_checkbox, scale_checkbox.visible],
        [pick_color_button, pick_color_button.visible],
        [currency_draw_button, currency_draw_button.visible],
        [apply_button, apply_button.visible],
        [color_picker, color_picker.visible],
        [start_game_button, start_game_button.visible]
    ]


def monopoly_init():
    # замена файлов библиотек на модифицированные
    if os.path.exists('lib/modified_library_files/magic/__init__.py'):
        os.replace('lib/modified_library_files/magic/__init__.py', '.venv/Lib/site-packages/magic/__init__.py')
    if os.path.exists('lib/modified_library_files/pygame-gui/html_parser.py'):
        os.replace('lib/modified_library_files/pygame-gui/html_parser.py', '.venv/Lib/site-packages/pygame_gui/core/text/html_parser.py')
    if os.path.exists('lib/modified_library_files/pygame-gui/ui_font_dictionary.py'):
        os.replace('lib/modified_library_files/pygame-gui/ui_font_dictionary.py', '.venv/Lib/site-packages/pygame_gui/core/ui_font_dictionary.py')
    if os.path.exists('lib/modified_library_files/pygame-gui/ui_appearance_theme.py'):
        os.replace('lib/modified_library_files/pygame-gui/ui_appearance_theme.py', '.venv/Lib/site-packages/pygame_gui/core/ui_appearance_theme.py')

    global all_tiles, players, player_dict, exchange_value, exchange_color, state, recorder, log_textbox

    gc.enable()
    pg.init()
    pg.mixer.init(frequency=44100, size=16, channels=1)  # для звука
    mimetypes.init()

    players = []
    all_tiles = []
    player_dict = {}

    exchange_value = -100
    exchange_color = ''
    log_textbox = None

    recorder = AudioRecorder()

    state = {'throw_cubes_btn_active': False,
             'buy_btn_active': [False, None],
             'pay_btn_active': [False, None],
             'penis_build_btn_active': False,
             'penis_remove_btn_active': False,
             'mortgage_btn_active': False,
             'redeem_btn_active': False,
             'auction_btn_active': False,
             'exchange_btn_active': False,
             'surrender_btn_active': False,

             'bonus_buttons': [],
             'all_penises_build_btns_active': False,
             'all_penises_remove_btns_active': False,
             'mortgage_tile_btn_active': False,
             'redeem_tile_btn_active': False,
             'exchange_player_btn_active': False,
             'exchange_tile_btn_active': False,
             'show_exchange_screen': False,
             'show_exchange_request_screen': [False],
             'is_game_started': False,
             'ready': False,
             'connected': False,
             'double': False,
             'paid': False,
             'refused_to_buy': False,
             'avatar_chosen': False,
             'cube_animation_playing': False,
             'tile_debug': False,
             'show_auction_screen': [False],
             'show_egg_panel': False,
             'tile_info_show': [False],
             'audio_recording': False,
             'messages_count': 0,
             'screen': 'settings start', # / 'board' / 'settings ingame' / 'currency drawing'
             'currency_drawing_action': None, # / 'blacking' / 'whitening'
             }

    global screen_widgets
    screen_widgets = {
        'settings start': [],
        'board': [],
        'settings ingame': [],
        'currency drawing': []
    }

    global settings, screen, clock

    settings = Settings()
    settings.load_settings()

    global resolution, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, auction_coordinates, tile_size, offset_horizontal, offset_vertical, fps_coordinates, font_path, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_card_text_width, egg_btns_coordinates, log_textbox_coordinates, tile_info_coordinates, settings_buttons_coordinates, max_log_image_size, default_offsets, currency_drawing_tile_size, currency_drawing_coordinates
    resolution, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, auction_coordinates, tile_size, offset_horizontal, offset_vertical, fps_coordinates, font_path, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_card_text_width, egg_btns_coordinates, log_textbox_coordinates, tile_info_coordinates, settings_buttons_coordinates, max_log_image_size, default_offsets, currency_drawing_tile_size, currency_drawing_coordinates = resolution_definition(settings)

    flags = pg.HWSURFACE
    if settings.fullscreen:
        flags = flags | pg.FULLSCREEN
        flags = flags | pg.SCALED

    screen = pg.display.set_mode(resolution, flags)
    TITLE = 'Monopoly v1.4'
    icon = pg.image.load(f'resources/icon.png')
    pg.display.set_icon(icon)
    pg.display.set_caption(TITLE)
    clock = pg.time.Clock()

    global inactive_window, chosen_bmcf_to_set
    inactive_window = True
    chosen_bmcf_to_set = 'default'

    global font, settings_font, manager, prev_time
    font = pg.font.Font(font_path)
    manager = pygame_gui.UIManager(resolution, theme_path=f'resources/{settings.resolution_folder}/gui_theme.json', enable_live_theme_updates=False, starting_language='ru')

    settings_buttons()

    theme = manager.create_new_theme(f'resources/{settings.resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)
    manager.add_font_paths('BulBulPoly', font_path)
    manager.preload_fonts([{'name': 'BulBulPoly', 'point_size': '1', 'style': 'regular', 'antialiased': '0'}])

    global settings_layout
    settings_layout = [
        [(dropdown,)],
        [('Максимальный FPS:', fps_textbox)],
        [('Уменьшать FPS при сворачивании:', minimize_window_fps_optimization_checkbox),
         ('до:', minimize_window_fps_optimization_textbox)],
        [('Уменьшать FPS при бездействии:', inactivity_fps_optimization_checkbox),
         ('до:', inactivity_fps_optimization_textbox)],
        [('Полноэкранный режим:', fullscreen_checkbox)],
        [('Растяжение экрана:', scale_checkbox)],
        [('Режим отладки:', debug_checkbox)],
        [(currency_draw_button,)],
        [(pick_color_button,)],
        [(apply_button,)]
    ]
    update_settings_positions()

    if settings.debug:
        global command_counter, unknown_commands
        command_counter = {}
        for command in ['color main', 'avatar', 'move', 'move diagonally', 'playersData', 'property', 'money',
                        'playerDeleted', 'gameStarted', 'onMove', 'error',
                        'imprisoned', 'unimprisoned', 'penis built', 'penis removed', 'imprisoned double failed',
                        'all property', 'exchange request', 'auction bid',
                        'mortgaged', 'redeemed', 'late to redeem', 'need to pay to player', 'pulled card position',
                        'show cubes', 'free prison escape card',
                        'message', 'mortgaged_moves_count', 'sound message', 'voice message', 'image message',
                        'receive size', 'player state', 'd/n card', 'pay multiplier', 'ping', 'ping by player',
                        'timer', 'surrender', 'value']:
            command_counter[command] = 0
        unknown_commands = []

    prev_time = time.time()


def load_assets():
    settings.load_settings()
    global resolution, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, auction_coordinates, tile_size, offset_horizontal, offset_vertical, fps_coordinates, font_path, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_card_text_width, egg_btns_coordinates, log_textbox_coordinates, tile_info_coordinates, settings_buttons_coordinates, max_log_image_size, default_offsets, currency_drawing_tile_size, currency_drawing_coordinates
    resolution, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, auction_coordinates, tile_size, offset_horizontal, offset_vertical, fps_coordinates, font_path, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_card_text_width, egg_btns_coordinates, log_textbox_coordinates, tile_info_coordinates, settings_buttons_coordinates, max_log_image_size, default_offsets, currency_drawing_tile_size, currency_drawing_coordinates = resolution_definition(settings)

    global exchange_screen, auction_screen, darkening_full, darkening_tile, profile_picture, bars, player_bars, mortgaged_tile, font, eggs_card_uncovered, board_image, bankrupt_picture
    exchange_screen = pg.image.load(f'resources/{settings.resolution_folder}/exchange.png').convert_alpha()
    auction_screen = pg.image.load(f'resources/{settings.resolution_folder}/auction.png').convert_alpha()
    darkening_full = pg.image.load(f'resources/{settings.resolution_folder}/darkening all.png').convert_alpha()
    darkening_tile = pg.image.load(f'resources/{settings.resolution_folder}/darkening tile.png').convert_alpha()
    profile_picture = pg.image.load(f'resources/{settings.resolution_folder}/profile/profile.png').convert_alpha()
    bankrupt_picture = pg.image.load(f'resources/{settings.resolution_folder}/profile/bankrupt.png').convert_alpha()
    bars = pg.image.load(f'resources/{settings.resolution_folder}/bars.png').convert_alpha()
    player_bars = pg.image.load(f'resources/{settings.resolution_folder}/profile/profile_bars.png').convert_alpha()
    mortgaged_tile = pg.image.load(f'resources/{settings.resolution_folder}/mortgaged.png').convert_alpha()
    eggs_card_uncovered = pg.image.load(f'resources/{settings.resolution_folder}/egg-s_card_uncovered.png').convert()
    font = pg.font.Font(font_path)

    for penis in range(5):
        globals()[f'{penis + 1}_penises_image'] = pg.image.load(f'resources/{settings.resolution_folder}/white penises/{penis + 1}.png').convert_alpha()

    global all_tiles, all_players, all_egg, all_eggs, screen, player_dict, all_question
    if not all_tiles:
        all_tiles, all_egg, all_eggs, all_question = all_tiles_get(settings.resolution_folder, tile_size)
        for tile in all_tiles:
            tile.text_defining(font)
    else: # изменяем разрешение отдельно, не перезаписывая данные
        all_tiles_change_resolution(all_tiles, settings.resolution_folder, tile_size)
        for tile in all_tiles:
            tile.text_defining(font)

    board_image = pg.image.load(f'resources/temp/images/{settings.resolution_folder}/board image.png').convert()

    all_players = [Player('red',    (all_tiles[0].x_center, all_tiles[0].y_center), settings.resolution_folder, font),
                   Player('blue',   (all_tiles[0].x_center, all_tiles[0].y_center), settings.resolution_folder, font),
                   Player('yellow', (all_tiles[0].x_center, all_tiles[0].y_center), settings.resolution_folder, font),
                   Player('green',  (all_tiles[0].x_center, all_tiles[0].y_center), settings.resolution_folder, font)]

    if not player_dict:
        for player in all_players:
            player_dict[player.color] = player
    else: # изменяем разрешение отдельно, не перезаписывая данные
        for player in player_dict:
            player_dict[player].change_resolution((all_tiles[player_dict[player].piece_position].x_center, all_tiles[player_dict[player].piece_position].y_center), settings.resolution_folder, (avatar_side_size, avatar_side_size), font)

    for player in players:
        player.change_resolution((all_tiles[player.piece_position].x_center, all_tiles[player.piece_position].y_center), settings.resolution_folder, (avatar_side_size, avatar_side_size), font)
        globals()[f'{player.color}_profile'] = pg.image.load(
            f'resources/{settings.resolution_folder}/profile/{player.color}_profile.png').convert_alpha()
        globals()[f'{player.color}_property_image'] = pg.image.load(
            f'resources/{settings.resolution_folder}/property/{player.color}_property.png').convert_alpha()

        if player.color == 'red':
            color_value = (255, 0, 0)
        elif player.color == 'blue':
            color_value = (0, 0, 255)
        elif player.color == 'yellow':
            color_value = (255, 255, 0)
        elif player.color == 'green':
            color_value = (10, 160, 10)

        player.timer_bar = ProgressBar(profile_coordinates[len(players) - 1]['timer_bar'], color_value, 1)

        player.rendered_name = font.render(f'{player.name}', False, 'black')
        player.rendered_money = font.render(f'{player.money}¤', False, 'black')
        player.rendered_value = font.render(f'{player.value}¤', False, 'black')
        position_update()

    flags = pg.HWSURFACE
    if settings.fullscreen:
        flags = flags | pg.FULLSCREEN
        flags = flags | pg.SCALED

    screen = pg.display.set_mode(resolution, flags)
    manager.set_window_resolution(resolution)

    start_game_button.kill()
    dropdown.kill()
    fps_textbox.kill()
    minimize_window_fps_optimization_checkbox.kill()
    minimize_window_fps_optimization_textbox.kill()
    inactivity_fps_optimization_checkbox.kill()
    inactivity_fps_optimization_textbox.kill()
    debug_checkbox.kill()
    pick_color_button.kill()
    color_picker.kill()
    fullscreen_checkbox.kill()
    scale_checkbox.kill()
    apply_button.kill()
    currency_draw_button.kill()

    global theme
    theme = manager.create_new_theme(f'resources/{settings.resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)
    # manager.add_font_paths('BulBulPoly', "resources/fonts/bulbulpoly-4.ttf")
    # manager.preload_fonts([{'name': 'BulBulPoly', 'point_size': f'{font_size}', 'style': 'regular', 'antialiased': '0'}])

    update_settings_positions()

    settings_buttons()
    start_game_button.rebuild()
    dropdown.rebuild()
    fps_textbox.rebuild()
    minimize_window_fps_optimization_checkbox.rebuild()
    minimize_window_fps_optimization_textbox.rebuild()
    inactivity_fps_optimization_checkbox.rebuild()
    inactivity_fps_optimization_textbox.rebuild()
    debug_checkbox.rebuild()
    pick_color_button.rebuild()
    color_picker.rebuild()
    fullscreen_checkbox.rebuild()
    scale_checkbox.rebuild()
    apply_button.rebuild()
    currency_draw_button.rebuild()

    global settings_layout
    settings_layout = [
        [(dropdown,)],
        [('Максимальный FPS:', fps_textbox)],
        [('Уменьшать FPS при сворачивании:', minimize_window_fps_optimization_checkbox),
         ('до:', minimize_window_fps_optimization_textbox)],
        [('Уменьшать FPS при бездействии:', inactivity_fps_optimization_checkbox),
         ('до:', inactivity_fps_optimization_textbox)],
        [('Полноэкранный режим:', fullscreen_checkbox)],
        [('Растяжение экрана:', scale_checkbox)],
        [('Режим отладки:', debug_checkbox)],
        [(currency_draw_button,)],
        [(pick_color_button,)],
        [(apply_button,)]
    ]

    update_settings_positions()

    theme = manager.create_new_theme(f'resources/{settings.resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)


def load_game():
    from classes.Textbox_Class import Textbox, AudioPlayer

    global sock, CLEAR_UPDATE_LIST, log_textbox, test_audio_player
    change_screen('board')

    if not state['connected']:
        sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)
        sock.settimeout(0)
        sock.setblocking(True)

    buttons()
    test_audio_player = AudioPlayer((-100, -100, 1, 1), 0, (0, 0, 0), (0, 0, 0), font, 'resources/temp/audios/client')
    log_textbox = Textbox(log_textbox_coordinates['main_box'], 2, 6, 1, font, (0, 0, 0), (200, 200, 200), 'resources/temp/audios/client', manager)

    theme = manager.create_new_theme(f'resources/{settings.resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)
    manager.add_font_paths('BulBulPoly', font_path)
    manager.preload_fonts([{'name': 'BulBulPoly', 'point_size': '1', 'style': 'regular', 'antialiased': '0'}])
    active_buttons_check()

    update_static_layer()


def throw_cubes():
    exchange_screen_reset()
    if state['throw_cubes_btn_active'] and state['is_game_started']:
        move_command = 'move¥'
        sock.send(move_command.encode())
        information_sent('Команда отправлена', move_command)
        player_dict['main'].timer_bar.set_percentage(1)


def buy():
    if state['is_game_started'] and state['buy_btn_active'][0]:
        buy_command = f'buy¦{state['buy_btn_active'][1]}¥'
        sock.send(buy_command.encode())
        information_sent('Команда отправлена', buy_command)
        player_dict['main'].timer_bar.set_percentage(1)


def pay():
    if state['is_game_started']:
        if state['pay_btn_active'][1] == 'minus':
            player = player_dict['main']
            pay_command = f'pay¦{player.piece_position}¥'
            sock.send(pay_command.encode())
            information_sent('Команда отправлена', pay_command)
            player_dict['main'].timer_bar.set_percentage(1)

        elif state['pay_btn_active'][1] == 'pay sum':
            pay_command = f'pay sum¦{state['pay_btn_active'][2]}¥'
            sock.send(pay_command.encode())
            information_sent('Команда отправлена', pay_command)
            player_dict['main'].timer_bar.set_percentage(1)

        elif state['pay_btn_active'][1] == 'color':
            player = player_dict['main']
            pay_command = f'payToColor¦{player.piece_position}¦{state['pay_btn_active'][2]}¥'
            sock.send(pay_command.encode())
            information_sent('Команда отправлена', pay_command)
            player_dict['main'].timer_bar.set_percentage(1)

        elif state['pay_btn_active'][1] == 'player':
            player = player_dict['main']
            if player.money >= state['pay_btn_active'][3] * player.pay_multiplier:
                pay_command = f'pay to player¦{state['pay_btn_active'][2]}¦{state['pay_btn_active'][3]}¥' # 'pay to player¦{color}¦{sum}¥'
                sock.send(pay_command.encode())
                information_sent('Команда отправлена', pay_command)
            player_dict['main'].timer_bar.set_percentage(1)

        elif state['pay_btn_active'][1] == 'players':
            player = player_dict['main']
            if player.money >= state['pay_btn_active'][2] * (len(players) - 1) * player.pay_multiplier:
                pay_command = f'pay to players¦{state['pay_btn_active'][2]}¥' # 'pay to players¦{sum}¥'
                sock.send(pay_command.encode())
                information_sent('Команда отправлена', pay_command)
            player_dict['main'].timer_bar.set_percentage(1)

        elif state['pay_btn_active'][1] == 'prison':
            pay_command = f'pay for prison¥'
            sock.send(pay_command.encode())
            information_sent('Команда отправлена', pay_command)
            player_dict['main'].timer_bar.set_percentage(1)


def debug_output():
    state['tile_debug'] = not state['tile_debug']
    for player in players:
        print(f'       piece_position: {player.piece_position}\n'
              f'       name: {player.name}\n'
              f'       color: {player.color}\n'
              f'       money: {player.money}\n'
              f'       main: {player.main}\n'
              f'       x: {player.x}\n'
              f'       y: {player.y}\n'
              f'       imprisoned: {player.imprisoned}\n'
              f'       time_left: {player.time_left}\n'
              f'       max_time: {player.max_time}\n')

    pprint.pp(state)
    pprint.pp(screen_widgets)
    # objgraph.show_most_common_types(limit=15)


def connect():
    if not state['is_game_started'] and not state['connected']:
        try:
            ip_ = ip_textbox.get_text()
            port_ = port_textbox.get_text()
            port_ = int(port_)
            name_ = name_textbox.get_text()
            if '¥' not in name_ and '¦' not in name_:
                if name_:
                    sock.connect((ip_, port_))
                    sock.send(f'name¦{name_}¥'.encode())
                    state['connected'] = True

                    settings.address = ip_
                    settings.name = name_
                    settings.port = str(port_)
                    settings.save_settings()

                    active_buttons_check()

                    connection_handler = threading.Thread(target=handle_connection, name='connection_handler', daemon=True)
                    connection_handler.start()
                    thread_open('Поток открыт', connection_handler.name)

                    new_connection('Подключено к', f'{ip_}:{port_}')
                    active_buttons_check()
                else:
                    print(f'{"\033[31m{}".format('Ваше имя не должно быть пустым')}{'\033[0m'}')
                    log_textbox.append_messages([{'type': 'text',
                                                  'value': f'Ваше имя не должно быть пустым',
                                                  'color': (208, 57, 42)}])
            else:
                print(f'{"\033[31m{}".format('Ваше имя не должно содержать символов "¦" и "¥"')}{'\033[0m'}')
                log_textbox.append_messages([{'type': 'text',
                                              'value': f'Ваше имя не должно содержать символов "¦" и "¥"',
                                              'color': (208, 57, 42)}])
        except:
            log_textbox.append_messages([{'type': 'text',
                                          'value': f'Не удалось подключиться',
                                          'color': (208, 57, 42)}])
            print(f'{"\033[31m{}".format('Не удалось подключиться')}{'\033[0m'}')  # красный
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def tile_button(tile_position):
    if state['tile_debug']:
        tile = all_tiles[tile_position]
        print(f'{tile.position = }\n'
              f'{tile.buyable = }\n'
              f'{tile.type = }\n'
              f'{tile.family = }\n'
              f'{tile.name = }\n'
              f'{tile.price = }\n'
              f'{tile.color = }\n'
              f'{tile.angle = }\n'
              f'{tile.max_family_members = }\n'
              f'{tile.rect = }\n'
              f'{tile.xText = }\n'
              f'{tile.yText = }\n'
              f'{tile.x_center = }\n'
              f'{tile.y_center = }\n'
              f'{tile.family_members = }\n'
              f'{tile.penis_price = }\n'
              f'{tile.penises = }\n'
              f'{tile.penised_family = }\n'
              f'{tile.recently_built = }\n'
              f'{tile.income = }\n'
              f'{tile.owned = }\n'
              f'{tile.owner = }\n'
              f'{tile.full_family = }\n'
              f'{tile.mortgaged = }\n'
              f'{tile.mortgaged_moves_count = }\n')

    if state['is_game_started'] and state['all_penises_build_btns_active']:
        player = player_dict['main']
        if (all_tiles[tile_position].full_family and
                all_tiles[tile_position].penises < 5 and
                player.money >= all_tiles[tile_position].penis_price and
                all_tiles[tile_position].type == 'buildable' and
                all_tiles[tile_position].owner == player.color):
            state['all_penises_build_btns_active'] = False
            penis_command = f'penis build¦{tile_position}¥'
            sock.send(penis_command.encode())
            information_sent('Информация отправлена', penis_command)
            active_buttons_check()

    elif state['is_game_started'] and state['all_penises_remove_btns_active']:
        player = player_dict['main']
        if (all_tiles[tile_position].full_family and
                1 <= all_tiles[tile_position].penises <= 5 and
                all_tiles[tile_position].type == 'buildable' and
                all_tiles[tile_position].owner == player.color):
            state['all_penises_remove_btns_active'] = False
            penis_command = f'penis remove¦{tile_position}¥'
            sock.send(penis_command.encode())
            information_sent('Информация отправлена', penis_command)

    elif state['is_game_started'] and state['exchange_tile_btn_active']:
        global exchange_give, exchange_get
        if tile_position in available_tiles_for_exchange:
            if (tile_position not in exchange_give and
                    tile_position not in exchange_get):
                player = player_dict['main']
                if player.color == all_tiles[tile_position].owner:
                    exchange_give.append(tile_position)
                else:
                    exchange_get.append(tile_position)
            else:
                player = player_dict['main']
                if player.color == all_tiles[tile_position].owner:
                    exchange_give.remove(tile_position)
                else:
                    exchange_get.remove(tile_position)
            exchange_value_calculation()

    elif state['is_game_started'] and state['mortgage_tile_btn_active']:
        if not all_tiles[tile_position].mortgaged and not all_tiles[tile_position].penised_family:
            mortgage_command = f'mortgage¦{tile_position}¥'
            sock.send(mortgage_command.encode())
            information_sent('Команда отправлена', mortgage_command)
            state['mortgage_tile_btn_active'] = False

    elif state['is_game_started'] and state['redeem_tile_btn_active']:
        player = player_dict['main']
        if all_tiles[tile_position].mortgaged and player.money >= all_tiles[tile_position].price / 2 * 1.1:
            redeem_command = f'redeem¦{tile_position}¥'
            sock.send(redeem_command.encode())
            information_sent('Команда отправлена', redeem_command)
            state['redeem_tile_btn_active'] = False

    elif not state['redeem_tile_btn_active'] and not state['all_penises_build_btns_active'] and not state['all_penises_remove_btns_active'] and not state['exchange_tile_btn_active'] and not state['mortgage_tile_btn_active'] and not state['redeem_tile_btn_active']:
        tile = all_tiles[tile_position]
        if tile.type == 'nonbuildable':
            message = [f'{tile.name}:',
                       f'Про это поле мне нечего сказать']
        elif tile.type == 'buildable':
            if tile.special_price:
                coef = 6.4
                coef2 = 2
            else:
                coef = 8
                coef2 = 2
            message = [f'{tile.name}:',
                       f'Базовая стоимость: {            math.ceil(tile.price / coef * (coef2 ** -1))}¤',
                       f'Стоимость при полной семье: {   math.ceil(tile.price / coef * (coef2 ** 0))}¤',
                       f'Стоимость при 1 белом пЭнисе: { math.ceil(tile.price / coef * (coef2 ** 1))}¤',
                       f'Стоимость при 2 белых пЭнисах: {math.ceil(tile.price / coef * (coef2 ** 2))}¤',
                       f'Стоимость при 3 белых пЭнисах: {math.ceil(tile.price / coef * (coef2 ** 3))}¤',
                       f'Стоимость при 4 белых пЭнисах: {math.ceil(tile.price / coef * (coef2 ** 4))}¤',
                       f'Стоимость при 5 белых пЭнисах: {math.ceil(tile.price / coef * (coef2 ** 5))}¤',
                       f'Стоимость белого пЭниса: {      tile.penis_price}¤']
        elif tile.type == 'train':
            coef = 8
            coef2 = 2
            message = [f'{tile.name}:',
                       f'Стоимость при 1 поле: { math.ceil(tile.price / coef * (coef2 ** 0))}¤',
                       f'Стоимость при 2 полях: {math.ceil(tile.price / coef * (coef2 ** 1))}¤',
                       f'Стоимость при 3 полях: {math.ceil(tile.price / coef * (coef2 ** 2))}¤',
                       f'Стоимость при 4 полях: {math.ceil(tile.price / coef * (coef2 ** 3))}¤']
        elif tile.type == 'infrastructure':
            message = [f'{tile.name}:',
                       f'Стоимость при 1 поле: сумма кубов * 4',
                       f'Стоимость при 2 полях: сумма кубов * 10']
        elif tile.type == 'minus':
            message = [f'{tile.name}:',
                       f'Это {tile.family}, он украдёт ваши {-tile.price}¤, хе-хе',]
        else:
            message = [f'{tile.name}:',
                       f'Не знаю, что тут пошло не так,',
                       f'но описания тут нет']


        strings_widths = []
        for string in message:
            strings_widths.append(font.size(string)[0] + 20)
        rect_dimensions = (max(strings_widths), font.get_linesize() * (len(message) + 1))
        message_panel.set_dimensions(rect_dimensions)
        message_panel.rebuild()
        message_panel.show()

        state['tile_info_show'] = [True, message]


def player_button(color):
    global available_tiles_for_exchange, exchange_color, exchange_give, exchange_get
    if state['is_game_started'] and state['exchange_player_btn_active']:
        player2 = player_dict[color]
        if not player2.main:
            available_tiles_for_exchange = []
            player = player_dict['main']
            for tile in all_tiles:
                if not tile.penised_family:
                    if tile.owner == player.color:
                        available_tiles_for_exchange.append(tile.position)
                    elif tile.owner == color:
                        available_tiles_for_exchange.append(tile.position)

                    exchange_give = []
                    exchange_get = []
                    state['exchange_tile_btn_active'] = True
                    state['exchange_player_btn_active'] = False
                    state['mortgage_tile_btn_active'] = False
                    state['redeem_tile_btn_active'] = False
                    state['all_penises_build_btns_active'] = False
                    state['all_penises_remove_btns_active'] = False
                    state['show_exchange_screen'] = True
                    exchange_color = str(color)
                    exchange_commit_button.show()
                    exchange_cancel_button.show()
                    exchange_give_textbox.show()
                    exchange_get_textbox.show()
                    log_textbox.hide()
                    log_text_send_button.hide()
                    log_audio_send_button.hide()
                    log_voice_message_send_button.hide()
                    log_image_send_button.hide()
                    log_entry_textbox.hide()
                    active_buttons_check()


def shove_penis_activation():
    exchange_screen_reset()
    if state['is_game_started'] and state['penis_build_btn_active']:
        for tile in all_tiles:
            if tile.full_family:
                player = player_dict['main']
                if tile.owner == player.color:
                    state['all_penises_build_btns_active'] = True
                    state['all_penises_remove_btns_active'] = False
                    state['mortgage_tile_btn_active'] = False
                    state['redeem_tile_btn_active'] = False
                    state['exchange_tile_btn_active'] = False
                    active_buttons_check()


def remove_penis_activation():
    exchange_screen_reset()
    if state['is_game_started'] and state['penis_remove_btn_active']:
        for tile in all_tiles:
            if tile.full_family:
                if 1 <= tile.penises <= 5:
                    player = player_dict['main']
                    if tile.owner == player.color:
                        state['all_penises_remove_btns_active'] = True
                        state['all_penises_build_btns_active'] = False
                        state['mortgage_tile_btn_active'] = False
                        state['redeem_tile_btn_active'] = False
                        state['exchange_tile_btn_active'] = False
                        active_buttons_check()


def exchange():
    exchange_screen_reset()
    if state['is_game_started'] and state['exchange_btn_active']:
        state['exchange_player_btn_active'] = True
        log_textbox.append_messages([{'type': 'text',
                                      'value': f'Нажмите на аватар человека, с которым хотите обменяться',
                                      'color': (0, 0, 0)}])
        active_buttons_check()


def exchange_commit():
    if state['is_game_started'] and state['exchange_tile_btn_active']:
        exchange_money_give_sum = exchange_give_textbox.get_text()
        exchange_money_get_sum = exchange_get_textbox.get_text()
        incorrect_values = False
        if exchange_money_get_sum == '' and not incorrect_values:
            exchange_money_get_sum = 0
        else:
            try:
                exchange_money_get_sum = int(exchange_money_get_sum)
            except:
                exchange_get_textbox.set_text(exchange_money_get_sum[:-1])
                incorrect_values = True

        if exchange_money_give_sum == '' and not incorrect_values:
            exchange_money_give_sum = 0
        else:
            try:
                exchange_money_give_sum = int(exchange_money_give_sum)
            except:
                exchange_give_textbox.set_text(exchange_money_give_sum[:-1])
                incorrect_values = True

        for player in players:
            if player.main:
                if player.money <= exchange_money_give_sum:
                    incorrect_values = True
            elif player.color == exchange_color:
                if player.money <= exchange_money_get_sum:
                    incorrect_values = True

        if -50 <= exchange_value <= 50 and not incorrect_values and (exchange_give or exchange_get):
            exchange_command = f'exchange request¦{exchange_money_give_sum}_'

            for give_tile in exchange_give:
                exchange_command += f'{all_tiles[give_tile].position}-'
            if exchange_give:
                exchange_command = exchange_command[:-1]
            exchange_command = exchange_command + f'¦{exchange_money_get_sum}_'

            for get_tile in exchange_get:
                exchange_command += f'{all_tiles[get_tile].position}-'
            if exchange_get:
                exchange_command = exchange_command[:-1]
            exchange_command = exchange_command + f'¦{exchange_color}¥'

            sock.send(exchange_command.encode())
            information_sent('Команда отправлена', exchange_command)
            player_dict['main'].timer_bar.set_percentage(1)
            state['exchange_tile_btn_active'] = False
            state['exchange_player_btn_active'] = False
            state['show_exchange_screen'] = False
            # del available_tiles_for_exchange, exchange_color, exchange_give, exchange_get\

            exchange_commit_button.hide()
            exchange_cancel_button.hide()
            exchange_give_textbox.set_text('')
            exchange_give_textbox.hide()
            exchange_get_textbox.set_text('')
            exchange_get_textbox.hide()
            log_textbox.show()
            log_text_send_button.show()
            log_audio_send_button.show()
            log_voice_message_send_button.show()
            log_image_send_button.show()
            log_entry_textbox.show()

            active_buttons_check()


def exchange_value_calculation():
    global exchange_value
    incorrect_values = False
    value_give = 0
    value_get = 0

    exchange_money_give_sum_old = exchange_give_textbox.get_text()
    exchange_money_get_sum_old = exchange_get_textbox.get_text()
    exchange_money_give_sum = allowed_characters_check(exchange_money_give_sum_old, '0123456789')
    exchange_money_get_sum = allowed_characters_check(exchange_money_get_sum_old, '0123456789')
    if exchange_money_get_sum_old != exchange_money_get_sum:
        exchange_get_textbox.set_text(exchange_money_get_sum)
    if exchange_money_give_sum_old != exchange_money_give_sum:
        exchange_give_textbox.set_text(exchange_money_give_sum)

    if exchange_money_get_sum == '' and not incorrect_values:
        exchange_money_get_sum = 0
    else:
        try:
            exchange_money_get_sum = int(exchange_money_get_sum)
        except:
            incorrect_values = True

    if exchange_money_give_sum == '' and not incorrect_values:
        exchange_money_give_sum = 0
    else:
        try:
            exchange_money_give_sum = int(exchange_money_give_sum)
        except:
            incorrect_values = True

    if not incorrect_values:
        for give_tile in exchange_give:
            value_give += int(all_tiles[give_tile].price) / 2
        value_give += exchange_money_give_sum

        for get_tile in exchange_get:
            value_get += int(all_tiles[get_tile].price) / 2
        value_get += exchange_money_get_sum

        if value_give or value_get:
            exchange_value = round((value_get - value_give) * 100 / max(value_give, value_get))
        else:
            exchange_value = -100
    else:
        exchange_value = -100
    active_buttons_check()


def exchange_request_confirm():
    if state['is_game_started'] and state['show_exchange_request_screen'][0]:
        if -50 <= exchange_value <= 50:
            give_money = state['show_exchange_request_screen'][1]
            give_property = state['show_exchange_request_screen'][2]
            get_money = state['show_exchange_request_screen'][3]
            get_property = state['show_exchange_request_screen'][4]
            color = state['show_exchange_request_screen'][5]

            exchange_command = f'exchange¦{give_money}_'
            for give_tile in give_property:
                try:
                    exchange_command += f'{all_tiles[int(give_tile)].position}-'
                except:
                    pass
            if give_property:
                exchange_command = exchange_command[:-1]
            exchange_command = exchange_command + f'¦{get_money}_'

            for get_tile in get_property:
                try:
                    exchange_command += f'{all_tiles[int(get_tile)].position}-'
                except:
                    pass
            if get_property:
                exchange_command = exchange_command[:-1]
            exchange_command = exchange_command + f'¦{color}¥'

            sock.send(exchange_command.encode())
            information_sent('Команда отправлена', exchange_command)
            state['show_exchange_request_screen'] = [False]
            exchange_request_confirm_button.hide()
            exchange_request_reject_button.hide()
            log_textbox.show()
            log_text_send_button.show()
            log_audio_send_button.show()
            log_voice_message_send_button.show()
            log_image_send_button.show()
            log_entry_textbox.show()
            active_buttons_check()
            player_dict['main'].timer_bar.set_percentage(1)


def exchange_request_reject():
    if state['is_game_started'] and state['show_exchange_request_screen'][0]:
        reject_command = 'exchange request rejected¥'
        sock.send(reject_command.encode())
        information_sent('Информация отправлена', reject_command)
        state['show_exchange_request_screen'] = [False]
        exchange_request_confirm_button.hide()
        exchange_request_reject_button.hide()
        log_textbox.show()
        log_text_send_button.show()
        log_audio_send_button.show()
        log_voice_message_send_button.show()
        log_image_send_button.show()
        log_entry_textbox.show()
        active_buttons_check()
        player_dict['main'].timer_bar.set_percentage(1)


def choose_avatar():
    if not state['avatar_chosen'] and state['is_game_started']:
        top = tkinter.Tk()
        top.withdraw()
        file_name = tkinter.filedialog.askopenfilename(parent=top, filetypes=[('Изображения',
                                                                               ('*.png', '*.apng', '*.jpg', '*.jpeg',
                                                                                '*.jfif', '*.jpe', '*.bmp', '*.gif',
                                                                                '*.ico', '*.tiff', '*.tif', '*.webp',
                                                                                '*.avif', '*.avifs', '*.cur', '*.dds',
                                                                                '*.jxr', '*.ppm', '*.psd', '*.tga',
                                                                                '*.xbm'))])
        top.destroy()
        if file_name != '' and not state['avatar_chosen']:
            state['avatar_chosen'] = True
            active_buttons_check()
            try:
                image = Image.open(file_name)
            except UnidentifiedImageError:
                print('Выбран неподдерживаемый формат изображения')
                log_textbox.append_messages([{'type': 'text',
                                             'value': f'Выбран неподдерживаемый формат изображения. Попробуйте выбрать другой файл',
                                             'color': (208, 57, 42)}])
                return

            width, height = image.size
            if width <= height:
                new_side_size = width
            else:
                new_side_size = height
            image = image.crop(((width - new_side_size) // 2, (height - new_side_size) // 2, (width + new_side_size) // 2, (height + new_side_size) // 2))
            image = image.resize([203, 203])

            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()

            image_bytes_encoded_bytes_base64 = base64.b64encode(image_bytes)
            sendable_data = 'avatar¦'.encode() + image_bytes_encoded_bytes_base64 + '¥'.encode()
            file_sock.send(sendable_data)


def auction():
    if state['is_game_started'] and state['auction_btn_active']:
        player = player_dict['main']
        if all_tiles[player.piece_position].buyable:
            auction_command = f'auction initiate¦{player.piece_position}¥'
            sock.send(auction_command.encode())
            information_sent('Команда отправлена', auction_command)
            player_dict['main'].timer_bar.set_percentage(1)


def auction_buy():
    if state['show_auction_screen'][0]:
        player = player_dict['main']
        if player.money >= int(state['show_auction_screen'][2]) + 20:
            auction_command = f'auction accept¦{state['show_auction_screen'][1]}¦{int(state['show_auction_screen'][2]) + 20}¥'
            sock.send(auction_command.encode())
            information_sent('Команда отправлена', auction_command)
            state['show_auction_screen'] = [False]
            auction_buy_button.hide()
            auction_reject_button.hide()
            log_textbox.show()
            log_text_send_button.show()
            log_audio_send_button.show()
            log_voice_message_send_button.show()
            log_image_send_button.show()
            log_entry_textbox.show()
        player_dict['main'].timer_bar.set_percentage(1)


def auction_reject():
    if state['show_auction_screen'][0]:
        auction_command = f'auction reject¥'
        sock.send(auction_command.encode())
        information_sent('Команда отправлена', auction_command)
        state['show_auction_screen'] = [False]
        auction_buy_button.hide()
        auction_reject_button.hide()
        log_textbox.show()
        log_text_send_button.show()
        log_audio_send_button.show()
        log_voice_message_send_button.show()
        log_image_send_button.show()
        log_entry_textbox.show()
        player_dict['main'].timer_bar.set_percentage(1)


def mortgage():  # заложить
    exchange_screen_reset()
    if state['mortgage_btn_active']:
        state['mortgage_tile_btn_active'] = True
        state['redeem_tile_btn_active'] = False
        state['exchange_tile_btn_active'] = False
        state['all_penises_build_btns_active'] = False
        state['all_penises_remove_btns_active'] = False
        active_buttons_check()
        log_textbox.append_messages([{'type': 'text',
                                      'value': f'Нажмите на поле, которое хотите заложить',
                                      'color': (0, 0, 0)}])


def redeem():  # выкупить
    exchange_screen_reset()
    if state['redeem_btn_active']:
        state['redeem_tile_btn_active'] = True
        state['mortgage_tile_btn_active'] = False
        state['exchange_tile_btn_active'] = False
        state['all_penises_build_btns_active'] = False
        state['all_penises_remove_btns_active'] = False
        active_buttons_check()
        log_textbox.append_messages([{'type': 'text',
                                      'value': f'Нажмите на поле, которое хотите выкупить',
                                      'color': (0, 0, 0)}])


def surrender():
    if state['is_game_started'] and state['surrender_btn_active']:
        surrender_command = f'surrender¥'
        sock.send(surrender_command.encode())
        information_sent('Команда отправлена', surrender_command)


def exit_prison_by_egg_s(egg_type):
    prison_exit_information = ''
    player = player_dict['main']
    if player.imprisoned:
        state['bonus_buttons'].remove(egg_type)
        if player.egg_prison_exit_card and egg_type == 'Яйцо':
            prison_exit_information = f'prison exit by eggs¦Яйцо¥'
            player.egg_prison_exit_card = False
            exit_prison_egg_btn.hide()
        elif player.eggs_prison_exit_card and egg_type == 'Яйца':
            prison_exit_information = f'prison exit by eggs¦Яйца¥'
            player.eggs_prison_exit_card = False
            exit_prison_eggs_btn.hide()
        sock.send(prison_exit_information.encode())
        information_sent('Команда отправлена', prison_exit_information)


def dn_activate():
    player = player_dict['main']
    if state['pay_btn_active'][1]:
        state['bonus_buttons'].remove('dn')
        if player.dn_card:
            dn_information = f'double or nothing¥'
            player.dn_card = False
            dn_btn.hide()

            sock.send(dn_information.encode())
            information_sent('Команда отправлена', dn_information)


def egg_s_reset():
    state['show_egg_panel'] = False
    active_buttons_check()


def exchange_screen_reset():
    if state['show_exchange_screen']:
        state['exchange_tile_btn_active'] = False
        state['show_exchange_screen'] = False
        exchange_commit_button.hide()
        exchange_cancel_button.hide()
        exchange_give_textbox.hide()
        exchange_get_textbox.hide()
        log_textbox.show()
        log_text_send_button.show()
        log_audio_send_button.show()
        log_voice_message_send_button.show()
        log_image_send_button.show()
        log_entry_textbox.show()
        active_buttons_check()


def tile_info_reset():
    if state['tile_info_show'][0]:
        state['tile_info_show'] = [False]
        message_panel.hide()


def send_message():
    if state['connected']:
        message = log_entry_textbox.get_text()
        if message:
            message_information = f'message¦{message}¥'
            log_entry_textbox.set_text('')
            sock.send(message_information.encode())
            information_sent('Команда отправлена', message_information)


def send_audio():
    if state['connected']:

        top = tkinter.Tk()
        top.withdraw()
        top.attributes('-topmost', True)
        file_name = tkinter.filedialog.askopenfilename(parent=top, filetypes=[('Аудио файлы',
                                                                               ('*.aiff', '*.flac', '*.iff', '*.mp3',
                                                                                '*.oga', '*.opus', '*.wav'))])
        top.destroy()
        if file_name:
            audio_bytes = open(file_name, 'rb').read()
            try:
                test_audio_player.load_audio(audio_bytes=audio_bytes)
            except:
                print('Выбран неподдерживаемый формат аудио')
                log_textbox.append_messages([{'type': 'text',
                                             'value': f'Выбран неподдерживаемый формат аудио. Попробуйте отправить другой файл',
                                             'color': (208, 57, 42)}])
                return
            encoding = zlib.compress(audio_bytes, level=9)
            audio_bytes_encoded_base64 = base64.b64encode(encoding)
            sendable_data = 'sound message¦'.encode() + audio_bytes_encoded_base64 + '¥'.encode()

            file_sock.send(sendable_data)
            information_sent('Информация отправлена', 'sound message')


def send_voice_message(button: str):
    if state['connected']:
        if button == 'left':
            state['audio_recording'] = not state['audio_recording']
            if state['audio_recording']:
                log_textbox.append_messages([{'type': 'text',
                                              'value': f'Началась запись голоса. Чтобы остановить и отправить запись, нажмите на кнопку ещё раз. Чтобы остановить запись без отправки нажмите на кнопку правой кнопкой мыши',
                                              'color': (0, 0, 0)}])
                recorder.start_recording()
            else:
                audio_bytes = recorder.stop_recording()
                encoding = zlib.compress(audio_bytes, level=9)
                audio_bytes_encoded_base64 = base64.b64encode(encoding)
                sendable_data = 'voice message¦'.encode() + audio_bytes_encoded_base64 + '¥'.encode()

                file_sock.send(sendable_data)
        elif button == 'right':
            if state['audio_recording']:
                state['audio_recording'] = False
                recorder.stop_recording()
                log_textbox.append_messages([{'type': 'text',
                                              'value': f'Запись голоса остановлена',
                                              'color': (0, 0, 0)}])


def send_image():
    top = tkinter.Tk()
    top.withdraw()
    file_name = tkinter.filedialog.askopenfilename(parent=top, filetypes=[('Изображения',
                                                                           ('*.png', '*.apng', '*.jpg', '*.jpeg',
                                                                            '*.jfif', '*.jpe', '*.bmp', '*.gif',
                                                                            '*.ico', '*.tiff', '*.tif', '*.webp',
                                                                            '*.avif', '*.avifs', '*.cur', '*.dds',
                                                                            '*.jxr', '*.ppm', '*.psd', '*.tga',
                                                                            '*.xbm'))])
    top.destroy()
    if file_name != '':
        try:
            image = Image.open(file_name)
        except UnidentifiedImageError:
            print('Выбран неподдерживаемый формат изображения')
            log_textbox.append_messages([{'type': 'text',
                                          'value': f'Выбран неподдерживаемый формат изображения. Попробуйте отправить другой файл',
                                          'color': (208, 57, 42)}])
            return
        width, height = image.size
        if height > 462:
            width = round(462 * width / height)
            height = 462
        if width > 925:
            height = round(925 * height / width)
            width = 925
        image = image.resize((width, height))

        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()
        image_bytes_encoded_bytes_base64 = base64.b64encode(image_bytes)

        sendable_data = 'image message¦'.encode() + image_bytes_encoded_bytes_base64 + '¥'.encode()
        file_sock.send(sendable_data)


# ^
# |
# Функционал кнопок и текст боксов


def update_static_layer():
    global board_static
    board_static = board_image.copy()
    board_static.blit(board_image, (0,0))

    for tile in all_tiles:
        if tile.owned:
            board_static.blit(globals()[f'{tile.owner}_property_image'], tile.rect)

        if 1 <= tile.penises <= 5:
            board_static.blit(globals()[f'{tile.penises}_penises_image'], tile.rect)

        if tile.mortgaged:
            board_static.blit(mortgaged_tile, tile.rect)
            text = font.render(str(tile.mortgaged_moves_count), False, 'white')
            text_rect = text.get_rect(center=(tile.x_center, tile.y_center))
            board_static.blit(text, text_rect)

        if tile.prerendered_text:
            board_static.blit(tile.prerendered_text, tile.text_rect)


def render_multiline_text(text, x, y, font_, line_height, align):
    lines = text
    for i, line in enumerate(lines):
        line_surface = font_.render(line, False, 'black').convert_alpha()
        if align == 'topleft':
            line_rect = line_surface.get_rect(topleft=(x, y + i * line_height))
        elif align == 'center':
            line_rect = line_surface.get_rect(center=(x, y + (i - len(lines) / 2 + 0.5) * line_height))
        screen.blit(line_surface, line_rect)


def blit_board():
    screen.blit(board_static)

    if state['cube_animation_playing']:
        screen.blit(cube_1_picture, cubes_coordinates[0])
        screen.blit(cube_2_picture, cubes_coordinates[1])


def blit_board_above_prices():
    if state['show_exchange_screen']:
        screen.blit(darkening_full, (0, 0))
        for tile in all_tiles:
            if tile.position not in available_tiles_for_exchange and tile.buyable:
                screen.blit(darkening_tile, tile.rect)

        screen.blit(exchange_screen, exchange_coordinates['exchange_screen'])

        give_text = []
        get_text = []
        for i in exchange_give:
            give_text.append(str(all_tiles[i].name))
        for i in exchange_get:
            get_text.append(str(all_tiles[i].name))

        render_multiline_text(give_text,
                              exchange_coordinates['text_give'][0],
                              exchange_coordinates['text_give'][1],
                              font,
                              font.get_linesize(),
                              'topleft')

        render_multiline_text(get_text,
                              exchange_coordinates['text_get'][0],
                              exchange_coordinates['text_get'][1],
                              font,
                              font.get_linesize(),
                              'topleft')

        value_text = font.render(str(exchange_value), False, 'black')
        value_text_rect = value_text.get_rect(center=exchange_coordinates['value'])
        screen.blit(value_text, value_text_rect)

    elif state['show_exchange_request_screen'][0]:
        give_money = state['show_exchange_request_screen'][1]
        give_property = state['show_exchange_request_screen'][2]
        get_money = state['show_exchange_request_screen'][3]
        get_property = state['show_exchange_request_screen'][4]
        exchange_property = give_property + get_property

        screen.blit(darkening_full, (0, 0))
        for tile in all_tiles:
            if tile.position not in exchange_property and tile.buyable:
                screen.blit(darkening_tile, tile.rect)

        screen.blit(exchange_screen, exchange_coordinates['exchange_screen'])

        give_text = []
        get_text = []
        for i in give_property:
            try:
                give_text.append(str(all_tiles[i].name))
            except:
                pass
        for i in get_property:
            try:
                get_text.append(str(all_tiles[i].name))
            except:
                pass

        render_multiline_text(give_text,
                              exchange_coordinates['text_give'][0],
                              exchange_coordinates['text_give'][1],
                              font,
                              font.get_linesize(),
                              'topleft')

        render_multiline_text(get_text,
                              exchange_coordinates['text_get'][0],
                              exchange_coordinates['text_get'][1],
                              font,
                              font.get_linesize(),
                              'topleft')

        value_text = font.render(str(exchange_value), False, 'black')
        value_text_rect = value_text.get_rect(center=exchange_coordinates['value'])
        screen.blit(value_text, value_text_rect)

        give_money_text = font.render(f'{give_money}¤', False, 'black')
        give_money_text_rect = give_money_text.get_rect(
            center=(exchange_coordinates['textbox_give'][0] + round(exchange_coordinates['textbox_give'][2] / 2),
                    exchange_coordinates['textbox_give'][1] + round(exchange_coordinates['textbox_give'][3] / 2)))
        screen.blit(give_money_text, give_money_text_rect)

        get_money_text = font.render(f'{get_money}¤', False, 'black')
        get_money_text_rect = get_money_text.get_rect(
            center=(exchange_coordinates['textbox_get'][0] + round(exchange_coordinates['textbox_get'][2] / 2),
                    exchange_coordinates['textbox_get'][1] + round(exchange_coordinates['textbox_get'][3] / 2)))
        screen.blit(get_money_text, get_money_text_rect)

    elif state['show_auction_screen'][0]:
        tile_position = int(state['show_auction_screen'][1])
        price = int(state['show_auction_screen'][2])
        tile = all_tiles[tile_position]
        text = f'{price} + 20¤'
        screen.blit(darkening_full, (0, 0))
        for tile_ in all_tiles:
            if tile_.buyable and tile_ != tile:
                screen.blit(darkening_tile, tile_.rect)
        screen.blit(auction_screen, auction_coordinates['auction_screen'])
        screen.blit(font.render(tile.name, False, 'black'), auction_coordinates['company_text'])
        screen.blit(font.render(text, False, 'black'), auction_coordinates['price_text'])


def blit_board_above_interface():
    if state['connected']:
        for player in players:
            player_index = players.index(player)
            player.timer_bar.render(screen, (profile_coordinates[player_index]['timer_bar'][0],
                                             profile_coordinates[player_index]['timer_bar'][1]))
            screen.blit(profile_picture, profile_coordinates[player_index]['profile'])
            screen.blit(player.avatar, profile_coordinates[player_index]['avatar'])
            if player.imprisoned:
                screen.blit(player_bars, profile_coordinates[player_index]['avatar'])
            screen.blit(globals()[f'{player.color}_profile'], profile_coordinates[player_index]['avatar'])
            screen.blit(player.rendered_money, profile_coordinates[player_index]['money'])
            screen.blit(player.rendered_value, profile_coordinates[player_index]['value'])
            screen.blit(player.rendered_name, profile_coordinates[player_index]['name'])
            if player.bankrupt:
                screen.blit(bankrupt_picture, profile_coordinates[player_index]['profile'])
            else:
                screen.blit(player.player_piece, player.player_piece_rect)


    screen.blit(bars, all_tiles[10].rect)

    if state['show_egg_panel']:
        screen.blit(eggs_card_uncovered, egg_card_coordinates)
        screen.blit(pulled_card_title, pulled_card_title_rect)
        render_multiline_text(pulled_card_strings, egg_card_text_center[0], egg_card_text_center[1], font, font.get_linesize(), 'center')

    if state['tile_info_show'][0]:
        tile_info = state['tile_info_show'][1]
        render_multiline_text(tile_info, tile_info_coordinates[0] + 10, tile_info_coordinates[1], font, font.get_linesize(), 'topleft')


def position_update():
    global players
    for player in players:
        players_on_tile = []
        for player2 in players:
            if player2.piece_position == player.piece_position:
                players_on_tile.append(player2)
        if len(players_on_tile) > 1:
            end_positions = []
            for player3 in players_on_tile:
                if player.piece_position in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29):
                    end_positions.append((all_tiles[player3.piece_position].x_center + offset_horizontal[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                          all_tiles[player3.piece_position].y_center + offset_horizontal[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))
                else:
                    end_positions.append((all_tiles[player3.piece_position].x_center + offset_vertical[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                          all_tiles[player3.piece_position].y_center + offset_vertical[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))
            move(players_on_tile, end_positions, 4)


def move_by_cubes(cube1, cube2, color):
    if cube1 >= 0:
        show_cubes(cube1, cube2)
    player = player_dict[color]
    # aver_time = []
    for i in range(abs(cube1 + cube2)):
        # now = time.time()
        players_on_tile = []

        if cube1 > 0:
            player.piece_position += 1
            if player.piece_position >= 40:
                player.piece_position -= 40
        else:
            player.piece_position -= 1
            if player.piece_position < 0:
                player.piece_position += 40

        for player2 in players:
            if player2.piece_position == player.piece_position:
                players_on_tile.append(player2)
        end_positions = []
        for player3 in players_on_tile:
            if player.piece_position in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29):
                end_positions.append((all_tiles[player3.piece_position].x_center + offset_horizontal[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                      all_tiles[player3.piece_position].y_center + offset_horizontal[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))
            else:
                end_positions.append((all_tiles[player3.piece_position].x_center + offset_vertical[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                      all_tiles[player3.piece_position].y_center + offset_vertical[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))
        move(players_on_tile, end_positions, cube1 + cube2)

        position_update()



    if player.main:
        sock.send('moved¦cubes¥'.encode())
        information_sent('Информация отправлена', 'moved¦cubes¥')


def move(players_on_tile, end_positions, cube_sum, mode='linear'):
    if settings.inactive_fps_optimize:
        global inactive_window
        settings.FPS = settings.max_fps
        inactive_window = False
    if not players_on_tile:
        return

    start_positions = []
    for player in players_on_tile:
        start_positions.append((player.x, player.y))

    first_player = players_on_tile[0]
    diff_x = end_positions[0][0] - first_player.x
    diff_y = end_positions[0][1] - first_player.y
    cube_speed = math.sqrt(abs(7 / cube_sum))
    distance = math.hypot(diff_x, diff_y)

    step_amount = round(distance * cube_speed * 10 * speed)
    sleep_seconds = cube_speed * 25 * speed

    total_time = step_amount * sleep_seconds
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed >= total_time:
            for i, player in enumerate(players_on_tile):
                player.x = end_positions[i][0]
                player.y = end_positions[i][1]
                player.player_piece_rect = player.player_piece.get_rect(center=(player.x, player.y))
            break

        if total_time > 0:
            t = elapsed / total_time
        else:
            t = 1

        for i, player in enumerate(players_on_tile):
            sx, sy = start_positions[i]
            ex, ey = end_positions[i]
            if mode == 'smoothstep':
                t_smooth = t * t * (3 - 2 * t)
            elif mode == 'linear':
                t_smooth = t
            player.x = sx + (ex - sx) * t_smooth
            player.y = sy + (ey - sy) * t_smooth
            player.player_piece_rect = player.player_piece.get_rect(center=(player.x, player.y))

        time.sleep(0.01)
    if settings.inactive_fps_optimize:
        settings.FPS = settings.inactive_fps
        inactive_window = True


def handle_connection():
    global players, all_tiles, cube_1_picture, cube_2_picture, list_for_file_handler

    def price_update(tile):
        tile_family_members = 0
        for tile_ in all_tiles:
            if tile_.family == tile.family:
                if tile_.owner == tile.owner and not tile_.mortgaged:
                    tile_family_members += 1

        for tile_ in all_tiles:
            if tile_.family == tile.family:
                if tile_.owner == tile.owner and not tile_.mortgaged:
                    tile_.family_members = tile_family_members
                    tile_.text_defining(font)

    buffer = b''
    encoded_separator = '¥'.encode('utf-8')
    while running:
        time.sleep(0.01)
        if state['connected']:
            try:
                data_undecoded = sock.recv(1024)
                buffer += data_undecoded

                while encoded_separator in buffer:
                    part, buffer = buffer.split(encoded_separator, 1)
                    single_command = part.decode('utf-8')
                    data = single_command.split('¦')

                    if data[0] != '':

                        if data[0] not in ('avatar', 'sound message', 'voice message', 'image message', 'timer', 'ping', 'ping by player'):
                            information_received('Информация получена', data)

                        if data[0] == 'ping by player':
                            player = player_dict[data[1]]
                            player.ping = int(data[2])

                        elif data[0] == 'ping':
                            time_server = float(data[1])
                            time_now = time.time()
                            ping = int((time_now - time_server) * 1000)
                            sock.send(f'pong¦{ping}¥'.encode())

                        elif data[0] == 'color main':
                            allPlayer = player_dict[data[1]]

                            allPlayer.main_color(data[1])
                            player_dict['main'] = allPlayer
                            connect_file_socket(data[1])

                        elif data[0] == 'move':
                            move_by_cubes(int(data[2]), int(data[3]), data[1])

                        elif data[0] == 'move diagonally':
                            player = player_dict[data[1]]
                            new_position = int(data[2])
                            player.piece_position = new_position
                            players_on_tile = []
                            for player2 in players:
                                if player2.piece_position == new_position:
                                    players_on_tile.append(player2)
                            end_positions = []
                            for player3 in players_on_tile:
                                if player.piece_position in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29): # только горизонтальные
                                    end_positions.append((all_tiles[player3.piece_position].x_center + offset_horizontal[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                                          all_tiles[player3.piece_position].y_center + offset_horizontal[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))
                                else:
                                    end_positions.append((all_tiles[player3.piece_position].x_center + offset_vertical[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                                          all_tiles[player3.piece_position].y_center + offset_vertical[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))

                            move([player], end_positions, 10, mode='smoothstep')

                            position_update()

                        elif data[0] == 'playersData':
                            globals()[f'{data[1]}_profile'] = pg.image.load(f'resources/{settings.resolution_folder}/profile/{data[1]}_profile.png').convert_alpha()
                            globals()[f'{data[1]}_property_image'] = pg.image.load(f'resources/{settings.resolution_folder}/property/{data[1]}_property.png').convert_alpha()
                            player = player_dict[data[1]]
                            if player not in players:
                                if data[1] == 'red':
                                    color_value = (255, 0, 0)
                                elif data[1] == 'blue':
                                    color_value = (0, 0, 255)
                                elif data[1] == 'yellow':
                                    color_value = (255, 255, 0)
                                elif data[1] == 'green':
                                    color_value = (10, 160, 10)

                                player.timer_bar = ProgressBar(profile_coordinates[len(players) - 1]['timer_bar'], color_value, 1)
                                players.append(player)

                            player.money = int(data[2])
                            player.piece_position = int(data[3])
                            player.name = data[4]
                            player.rendered_name = font.render(f'{player.name}', False, 'black')
                            player.rendered_money = font.render(f'{player.money}¤', False, 'black')
                            position_update()

                        elif data[0] == 'property':
                            for player in players:
                                if data[1] == player.color:
                                    tile_position = int(data[2])
                                    all_tiles[tile_position].owner = data[1]
                                    all_tiles[tile_position].owned = True
                                    all_tiles[tile_position].family_members += 1
                                    price_update(all_tiles[tile_position])

                        elif data[0] == 'money':
                            for i, player in enumerate(players):
                                if data[1] == player.color:
                                    player.money = int(data[2])
                                    player.rendered_money = font.render(f'{player.money}¤', False, 'black')

                        elif data[0] == 'playerDeleted':
                            player = player_dict[data[1]]
                            players.remove(player)

                        elif data[0] == 'gameStarted':
                            state['is_game_started'] = True
                            players_queue = data[1].split('_')
                            players_temp = []
                            for new_color in players_queue:
                                player = player_dict[new_color]
                                players_temp.append(player)
                            players = players_temp

                            for player in players:
                                globals()[f'{player.color}_player_button'] = pygame_gui.elements.UIButton(
                                    relative_rect=pg.Rect(profile_coordinates[players.index(player)]['avatar'], (avatar_side_size, avatar_side_size)),
                                    text='',
                                    manager=manager,
                                    object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons'))

                        elif data[0] == 'error':
                            print(f'Ошибка: {"\033[31m{}".format(data[1])}{'\033[0m'}')
                            state['avatar_chosen'] = False

                        elif data[0] == 'imprisoned':
                            for i, player in enumerate(players):
                                if data[1] == player.color:
                                    player.imprisoned = True
                                    player.piece_position = 10

                        elif data[0] == 'unimprisoned':
                            for i, player in enumerate(players):
                                if data[1] == player.color:
                                    player.imprisoned = False
                            if len(data) > 2:
                                move_by_cubes(int(data[2]), int(data[3]), data[1])

                        elif data[0] == 'penis built':
                            tile_position = int(data[1])
                            all_tiles[tile_position].penises += 1
                            all_tiles[tile_position].text_defining(font)
                            for tile in all_tiles:
                                if tile.family == all_tiles[tile_position].family:
                                    tile.penised_family = True

                        elif data[0] == 'penis removed':
                            tile_position = int(data[1])
                            all_tiles[tile_position].penises -= 1
                            all_tiles[tile_position].text_defining(font)
                            penised = False
                            for tile in all_tiles:
                                if tile.family == all_tiles[tile_position].family:
                                    if tile.penises:
                                        penised = True
                            for tile in all_tiles:
                                if tile.family == all_tiles[tile_position].family:
                                    tile.penised_family = penised

                        elif data[0] == 'imprisoned double failed':
                            show_cubes(data[2], data[3])

                            print(f'У игрока {data[1]} осталось {3 - int(data[4])} попытки чтобы выйти из тюрьмы')

                        elif data[0] == 'all property':
                            if data[2]:
                                new_property = data[2].split('_')
                                for i in new_property:
                                    tile = int(i)
                                    all_tiles[tile].owner = data[1]
                                    price_update(all_tiles[tile])

                        elif data[0] == 'exchange request':
                            global exchange_value
                            get_data = data[1].split('_')
                            give_data = data[2].split('_')
                            give_money = int(give_data[0])
                            get_money = int(get_data[0])
                            give_property_temp = give_data[1].split('-')
                            get_property_temp = get_data[1].split('-')
                            give_property = []
                            get_property = []
                            color = data[3]

                            value_give = 0
                            value_get = 0
                            for give_tile in give_property_temp:
                                if give_tile:
                                    give_property.append(int(give_tile))
                                    value_give += all_tiles[int(give_tile)].price / 2
                            value_give += give_money

                            for get_tile in get_property_temp:
                                if get_tile:
                                    get_property.append(int(get_tile))
                                    value_get += all_tiles[int(get_tile)].price / 2
                            value_get += get_money

                            exchange_value = round((value_get - value_give) * 100 / max(value_give, value_get))
                            print(exchange_value, value_give, value_get)
                            state['show_exchange_request_screen'] = [True, give_money, give_property, get_money,
                                                                     get_property, color]
                            print(state['show_exchange_request_screen'])
                            log_textbox.hide()
                            log_text_send_button.hide()
                            log_audio_send_button.hide()
                            log_voice_message_send_button.hide()
                            log_image_send_button.hide()
                            log_entry_textbox.hide()
                            exchange_request_confirm_button.show()
                            exchange_request_reject_button.show()

                        elif data[0] == 'auction bid':
                            state['show_auction_screen'] = [True, int(data[1]), int(data[2])]
                            log_textbox.hide()
                            log_text_send_button.hide()
                            log_audio_send_button.hide()
                            log_voice_message_send_button.hide()
                            log_image_send_button.hide()
                            log_entry_textbox.hide()
                            auction_buy_button.show()
                            auction_reject_button.show()

                        elif data[0] == 'mortgaged':
                            tile = all_tiles[int(data[1])]
                            tile.mortgaged = True
                            tile.mortgaged_moves_count = 15
                            for tile_ in all_tiles:
                                if tile_.family == tile.family:
                                    if tile_.owner == tile.owner:
                                        tile_.family_members -= 1
                                        tile_.text_defining(font)

                        elif data[0] == 'redeemed':
                            all_tiles[int(data[1])].mortgaged = False
                            for tile in all_tiles:
                                if tile.family == all_tiles[int(data[1])].family:
                                    tile.family_members += 1
                                    tile.text_defining(font)

                        elif data[0] == 'late to redeem':
                            for tile in all_tiles:
                                if tile.position == int(data[1]):
                                    tile.mortgaged = False
                                    tile.owned = False
                                    tile.owner = ''
                                    tile.family_members = 0
                                if tile.family == all_tiles[int(data[1])].family:
                                    tile.family_members -= 1
                                tile.text_defining(font)

                        elif data[0] == 'need to pay to player':
                            global pulled_card_strings
                            if state['show_egg_panel']:
                                player = player_dict[data[1]]
                                for i in pulled_card_strings:
                                    i.replace('{player_name}', player.name)

                        elif data[0] == 'pulled card position':
                            global pulled_card_text,  pulled_card_title, pulled_card_title_rect
                            state['show_egg_panel'] = True
                            if data[2] == 'Яйцо':
                                pulled_card_title = font.render('Вопросительное яйцо', False, 'black')
                                pulled_card_title_rect = pulled_card_title.get_rect(center=egg_card_title_center)
                                egg_card_position = int(data[3])
                                pulled_card_strings = []
                                text = all_egg[egg_card_position].description
                                if '{value}' in text:
                                    text = text.replace('{value}', f'{all_egg[egg_card_position].value}')
                                if '{tile_name}' in text:
                                    text = text.replace('{tile_name}', all_tiles[all_egg[egg_card_position].value].name)
                                if '{player_name}' in text:
                                    player = player_dict[data[1]]
                                    text = text.replace('{player_name}', player.name)
                                text = text.split(' ')

                            elif data[2] == 'Яйца':
                                pulled_card_title = font.render('Груда вопросительных яиц', False, 'black')
                                pulled_card_title_rect = pulled_card_title.get_rect(center=egg_card_title_center)
                                egg_card_position = int(data[3])
                                pulled_card_strings = []
                                text = all_eggs[egg_card_position].description
                                if '{value}' in text:
                                    text = text.replace('{value}', f'{all_eggs[egg_card_position].value}')
                                if '{tile_name}' in text:
                                    text = text.replace('{tile_name}', all_tiles[all_eggs[egg_card_position].value].name)
                                if '{player_name}' in text:
                                    player = player_dict[data[1]]
                                    text = text.replace('{player_name}', player.name)
                                text = text.split(' ')

                            while text:
                                text_new = []
                                while font.size(' '.join(text_new))[0] <= egg_card_text_width and text:
                                    text_new.append(text[0])
                                    text.pop(0)
                                text.insert(0, text_new[-1])
                                text_new.pop(-1)
                                pulled_card_strings.append(' '.join(text_new))
                                if font.size(' '.join(text))[0] <= egg_card_text_width:
                                    pulled_card_strings.append(' '.join(text))
                                    text.clear()

                        elif data[0] == 'show cubes':
                            show_cubes(data[1], data[2])

                        elif data[0] == 'free prison escape card':
                            player = player_dict['main']
                            state['bonus_buttons'].append(data[1])
                            if data[1] == 'Яйцо':
                                player.egg_prison_exit_card = True
                                exit_prison_egg_btn.rect = egg_btns_coordinates[state['bonus_buttons'].index('Яйцо')]
                                exit_prison_egg_btn.show()
                            else:
                                player.eggs_prison_exit_card = True
                                exit_prison_eggs_btn.rect = egg_btns_coordinates[state['bonus_buttons'].index('Яйца')]
                                exit_prison_eggs_btn.show()

                        elif data[0] == 'message':
                            message = json.loads(data[1])
                            log_textbox.append_messages(message)

                        elif data[0] == 'mortgaged_moves_count':
                            all_tiles[int(data[1])].mortgaged_moves_count = int(data[2])

                        elif data[0] == 'player state':
                            player_state = json.loads(data[1])
                            for player_state_key in player_state:
                                state[player_state_key] = player_state[player_state_key]

                        elif data[0] == 'd/n card':
                            player = player_dict['main']
                            state['bonus_buttons'].append('dn')
                            player.dn_card = True
                            dn_btn.rect = egg_btns_coordinates[state['bonus_buttons'].index('dn')]
                            dn_btn.show()

                        elif data[0] == 'pay multiplier':
                            player = player_dict[data[1]]
                            player.pay_multiplier = float(data[2])

                        elif data[0] == 'surrendered':
                            player = player_dict[data[1]]
                            player.bankrupt = True
                            player.timer_bar.set_percentage(1)

                            for tile in all_tiles:
                                if tile.owner == player.color:
                                    tile.reset_tile()

                        elif data[0] == 'value':
                            player = player_dict[data[1]]
                            player.value = int(data[2])
                            player.rendered_value = font.render(f'{player.value}¤', False, 'black')

                        elif data[0] == 'timer':
                            player = player_dict[data[1]]
                            player.time_left = int(data[2])
                            player.max_time = int(data[3])
                            player.timer_bar.set_percentage(player.time_left / player.max_time)

                        else:
                            print(f'Ошибка: {"\033[31m{}".format(f'Незарегистрированная команда на стороне клиента: {data[0]}')}{'\033[0m'}')

                        active_buttons_check()
                        update_static_layer()
                        if settings.debug:
                            # подсчёт команд по релевантности
                            try:
                                command_counter[data[0]] += 1
                            except KeyError:
                                unknown_commands.append(data[0])

                    if not running:
                        break
            except OSError:
                pass
            except UnicodeDecodeError:
                print(data_undecoded)
            except:
                print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def connect_file_socket(color):
    global file_sock
    try:
        ip_ = ip_textbox.get_text()
        file_port = int(settings.port) + 1
        file_sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        file_sock.connect((ip_, file_port))
        # Отправляем привязку
        bind_cmd = f"file_bind¦{color}¥".encode()
        file_sock.send(bind_cmd)
        # Запускаем поток для приёма файлов от сервера (если нужно)
        threading.Thread(target=file_receiver, daemon=True).start()
    except Exception as e:
        print("Не удалось подключить файловый канал:", e)
        print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def file_receiver():
    global running
    buffer = ''
    while running and file_sock:
        try:
            data = file_sock.recv(65536).decode()
            if not data:
                break  # соединение закрыто сервером
            buffer += data
            while '¥' in buffer:
                cmd, buffer = buffer.split('¥', 1)
                process_file_command(cmd)
        except BlockingIOError:#, socket.timeout):
            time.sleep(0.01)
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')

            break
    if file_sock:
        file_sock.close()


def process_file_command(cmd):
    parts = cmd.split('¦')
    if parts[0] == 'avatar':
        state['avatar_chosen'] = True
        avatar = parts[2]
        image_bytes_ascii_decoded = avatar.encode("ascii")
        image_bytes_decoded = base64.b64decode(image_bytes_ascii_decoded)
        image_decoded = Image.open(io.BytesIO(image_bytes_decoded))
        image_decoded = image_decoded.resize((avatar_side_size, avatar_side_size))
        image_bytes = io.BytesIO()
        image_decoded.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        try:
            for i, player in enumerate(players):
                if player.color == parts[1]:
                    player.avatar = pg.image.load(image_bytes).convert_alpha()
                    state['avatar_chosen'] = False
        except:
            image_decoded.save('error.png')
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')
            print('an error has occurred. avatar image saved inside main folder')

    if parts[0] == 'sound message':
        audio_bytes_ascii_decoded = parts[1]
        audio_bytes_decoded_base64 = base64.b64decode(audio_bytes_ascii_decoded)
        audio_bytes_decoded = zlib.decompress(audio_bytes_decoded_base64)
        log_textbox.append_messages([{'type': 'audio',
                                      'value': audio_bytes_decoded,
                                      'color': (0, 0, 0)}])

    elif parts[0] == 'voice message':
        audio_bytes_ascii_decoded = parts[1]
        audio_bytes_decoded_base64 = base64.b64decode(audio_bytes_ascii_decoded)
        audio_bytes_decoded = zlib.decompress(audio_bytes_decoded_base64)
        log_textbox.append_messages([{'type': 'audio',
                                      'value': audio_bytes_decoded,
                                      'color': (0, 0, 0)}])

    elif parts[0] == 'image message':
        image_bytes_decoded = base64.b64decode(parts[1])
        image_decoded = Image.open(io.BytesIO(image_bytes_decoded))

        width, height = image_decoded.size
        if height > max_log_image_size[1]:
            width = round(max_log_image_size[1] * width / height)
            height = max_log_image_size[1]
        if width > max_log_image_size[0]:
            height = round(max_log_image_size[0] * height / width)
            width = max_log_image_size[0]
        image_decoded = image_decoded.resize((width, height))

        image_bytes = io.BytesIO()
        image_decoded.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        image = pg.image.load(image_bytes).convert_alpha()
        message = [{'type': 'image', 'value': image}]
        log_textbox.append_messages(message)

    elif parts[0] == 'message':
        message = json.loads(parts[1])
        log_textbox.append_messages(message)


def delta_time(old_time):
    now = time.time()
    dt = now - old_time
    old_time = now
    return dt, old_time


def event_handler():
    global color_picker, chosen_bmcf_to_set

    events = pg.event.get()
    for event in events:
        if settings.minimize_fps_optimize:
            if event.type in (pg.WINDOWHIDDEN, pg.WINDOWFOCUSLOST):
                settings.FPS = settings.minimize_fps
            elif event.type in (pg.WINDOWRESTORED, pg.WINDOWFOCUSGAINED):
                if settings.inactive_fps_optimize:
                    if inactive_window:
                        settings.FPS = settings.inactive_fps
                    else:
                        settings.FPS = settings.max_fps
                else:
                    settings.FPS = settings.max_fps

        manager_initiated = False
        while not manager_initiated:
            try:
                manager.process_events(event)
                manager_initiated = True
            except:
                print(f'{"\033[32m{}".format(f'Не беспокойтесь. Эта ошибка не вредит игре:\n{traceback.format_exc()}')}{'\033[0m'}')

        if event.type == pg.QUIT:
            global running
            running = False

        if event.type == pg.KEYUP:
            if event.key == pg.K_d:
                debug_output()

        if state['screen'] == 'board':
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if state['show_egg_panel']:
                    egg_s_reset()
                elif state['tile_info_show'][0]:
                    tile_info_reset()
                for i, tile in enumerate(all_tiles):
                    if tile.rect.collidepoint(event.pos):
                        tile_button(i)
                        break

            elif event.type == pg.KEYUP :
                if settings.debug and not ip_textbox.is_focused and not port_textbox.is_focused and not name_textbox.is_focused and not exchange_give_textbox.is_focused and not exchange_get_textbox.is_focused and not log_entry_textbox.is_focused:
                    if event.key == pg.K_c:
                        connect()
                    elif event.key == pg.K_t:
                        throw_cubes()
                    elif event.key == pg.K_s:
                        change_screen('settings start')
                    elif event.key == pg.K_d:
                        debug_output()
                elif name_textbox.is_focused:
                    if event.key == pg.K_RETURN:
                        connect()
                elif log_entry_textbox.is_focused:
                    if event.key == pg.K_RETURN:
                        send_message()

            log_textbox.process_events(event)
            match event.type:
                case pygame_gui.UI_BUTTON_PRESSED:
                    event_type = event.ui_element
                    if event_type == cube_button:
                        throw_cubes()
                    elif event_type == buy_button:
                        buy()
                    elif event_type == pay_button:
                        pay()
                    elif event_type == shove_penis_button:
                        shove_penis_activation()
                    elif event_type == remove_penis_button:
                        remove_penis_activation()
                    elif event_type == exchange_button:
                        exchange()
                    elif event_type == auction_button:
                        auction()
                    elif event_type == mortgage_button:
                        mortgage()
                    elif event_type == redeem_button:
                        redeem()
                    elif event_type == avatar_choose_button:
                        threading.Thread(target=choose_avatar, daemon=True).start()
                    elif event_type == connect_button:
                        connect()
                    elif event_type == settings_button:
                        change_screen('settings start')
                    elif event_type == exchange_commit_button:
                        exchange_commit()
                    elif event_type == exchange_cancel_button:
                        exchange_screen_reset()
                    elif event_type == exchange_request_confirm_button:
                        exchange_request_confirm()
                    elif event_type == exchange_request_reject_button:
                        exchange_request_reject()
                    elif event_type == auction_buy_button:
                        auction_buy()
                    elif event_type == auction_reject_button:
                        auction_reject()
                    elif event_type == exit_prison_egg_btn:
                        exit_prison_by_egg_s('Яйцо')
                    elif event_type == exit_prison_eggs_btn:
                        exit_prison_by_egg_s('Яйца')
                    elif event_type == log_text_send_button:
                        send_message()
                    elif event_type == log_audio_send_button:
                        threading.Thread(target=send_audio, daemon=True).start()
                    elif event_type == log_voice_message_send_button:
                        print(event)
                        if event.mouse_button == 1:
                            send_voice_message('left')
                        elif event.mouse_button == 3:
                            send_voice_message('right')
                    elif event_type == log_image_send_button:
                        threading.Thread(target=send_image, daemon=True).start()
                    elif event_type == dn_btn:
                        dn_activate()
                    elif event_type == surrender_button:
                        surrender()
                    else:
                        if state['is_game_started']:
                            for player in players:
                                if event_type == globals()[f'{player.color}_player_button']:
                                    player_button(player.color)

                case pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    event_type = event.ui_element
                    if event_type == name_textbox:
                        name_check()
                    elif event_type == log_entry_textbox:
                        log_entry_check()
                    elif event_type == ip_textbox:
                        ip_ = ip_textbox.get_text()
                        ip_ = allowed_characters_check(ip_, '0123456789.')
                        if ip_textbox.get_text() != ip_:
                            ip_textbox.set_text(ip_)
                    elif event_type == port_textbox:
                        port_ = port_textbox.get_text()
                        port_ = allowed_characters_check(port_, '0123456789')
                        if port_textbox.get_text() != port_:
                            port_textbox.set_text(port_)
                    elif event_type == exchange_give_textbox or event_type == exchange_get_textbox:
                        exchange_value_calculation()
    
        elif state['screen'] == 'settings start':
            match event.type:
                case pygame_gui.UI_BUTTON_PRESSED:

                    if event.ui_element == start_game_button:
                        settings.minimize_fps_optimize = minimize_window_fps_optimization_checkbox.get_state()
                        settings.inactive_fps_optimize = inactivity_fps_optimization_checkbox.get_state()
                        settings.debug = debug_checkbox.get_state()
                        settings.fullscreen = fullscreen_checkbox.get_state()
                        settings.scaled = scale_checkbox.get_state()

                        settings.save_settings()
                        load_assets()
                        load_game()
                    elif event.ui_element == pick_color_button:
                        color_picker.show()
                    elif event.ui_element == apply_button:
                        settings.minimize_fps_optimize = minimize_window_fps_optimization_checkbox.get_state()
                        settings.inactive_fps_optimize = inactivity_fps_optimization_checkbox.get_state()
                        settings.debug = debug_checkbox.get_state()
                        settings.fullscreen = fullscreen_checkbox.get_state()
                        settings.scaled = scale_checkbox.get_state()

                        settings.save_settings()
                        load_assets()
                    elif event.ui_element == currency_draw_button:
                        change_screen_to_draw_currency()

                case pygame_gui.UI_CHECK_BOX_CHECKED:
                    if event.ui_element == fullscreen_checkbox:
                        scale_checkbox.enable()

                case pygame_gui.UI_CHECK_BOX_UNCHECKED:
                    if event.ui_element == fullscreen_checkbox:
                        scale_checkbox.disable()
                        scale_checkbox.set_state(False)

                case pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    resolution_to_index = {'1280x720': 1,
                                           '1920x1080': 2,
                                           '2560x1440': 3}
                    settings.resolution_index = resolution_to_index[event.text]

                case pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                    if event.ui_element == color_picker:
                        settings.background_color_converted = event.colour
                        settings.background_color = list(event.colour)
                        color_picker.kill()
                        color_picker = pygame_gui.windows.UIColourPickerDialog(
                            rect=pg.Rect(60, 120, 390, 390),
                            initial_colour=settings.background_color_converted,
                            manager=manager,
                            visible=0)

                case pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    if event.ui_element == fps_textbox:
                        fps_check(fps_textbox)
                        str_fps = fps_textbox.get_text()
                        if ',' in str_fps:
                            str_fps.replace(',', '.')
                        if '.' in str_fps:
                            settings.max_fps = float(str_fps)
                        else:
                            settings.max_fps = int(str_fps)

                    elif event.ui_element == minimize_window_fps_optimization_textbox:
                        fps_check(minimize_window_fps_optimization_textbox)
                        str_fps = minimize_window_fps_optimization_textbox.get_text()
                        if ',' in str_fps:
                            str_fps.replace(',', '.')
                        if '.' in str_fps:
                            settings.minimize_fps = float(str_fps)
                        else:
                            settings.minimize_fps = int(str_fps)

                    elif event.ui_element == inactivity_fps_optimization_textbox:
                        fps_check(inactivity_fps_optimization_textbox)
                        str_fps = inactivity_fps_optimization_textbox.get_text()
                        if ',' in str_fps:
                            str_fps.replace(',', '.')
                        if '.' in str_fps:
                            settings.inactive_fps = float(str_fps)
                        else:
                            settings.inactive_fps = int(str_fps)

        elif state['screen'] == 'currency drawing':
            for row in currency_drawing_widget_list:
                for button in row:
                    state['currency_drawing_action'] = button.process_events(event, state['currency_drawing_action'])

            match event.type:
                case pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == save_button:
                        save_character()
                    elif event.ui_element == back_button:
                        change_screen('settings start')
                    elif event.ui_element == set_char_button:
                        change_currency_character(font_path, f'resources/currency/{settings.resolution_folder}/{chosen_bmcf_to_set}.bmcf')
                        settings.save_settings()
                    elif event.ui_element == restart_button:
                        restart_game()

                case pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == dropdown_load:
                        load_bmcf(f'resources/currency/{settings.resolution_folder}/{event.text}.bmcf')
                    elif event.ui_element == dropdown_save:
                        chosen_bmcf_to_set = event.text
                        settings.currency = chosen_bmcf_to_set


def buttons():
    global cube_button, buy_button, pay_button, name_textbox, ip_textbox, port_textbox, connect_button, settings_button, avatar_choose_button, shove_penis_button, remove_penis_button, exchange_button, exchange_commit_button, exchange_cancel_button, exchange_give_textbox, exchange_get_textbox, exchange_request_confirm_button, exchange_request_reject_button, auction_button, auction_buy_button, auction_reject_button, mortgage_button, redeem_button, surrender_button, exit_prison_egg_btn, exit_prison_eggs_btn, log_entry_textbox, log_text_send_button, log_audio_send_button, log_voice_message_send_button, log_image_send_button, message_panel, dn_btn

    for element_list in screen_widgets['board']:
        element_list[0].kill()

    cube_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['throw_cubes']),
        text='Бросить кубы',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Просто бросить кубы</font>')

    buy_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['buy']),
        text='Купить',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Купить поле</font>')

    pay_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['pay']),
        text='Оплатить',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Оплатить свой долг</font>')

    shove_penis_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['shove_penis']),
        text='Сунуть пЭнис',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Сувание пЭнисов повышает ценность поля</font>')

    remove_penis_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['remove_penis']),
        text='Убрать пЭнис',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Убирание пЭнисов возвращает стоимость пЭниса полностью</font>')

    exchange_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['exchange']),
        text='Обмен',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Обмен с другим игроком</font>')

    auction_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['auction']),
        text='Аукцион',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Выставить поле, которое вы не хотите покупать, на аукцион</font>')

    mortgage_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['mortgage']),
        text='Заложить',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Заложить купленное поле за половину стоимости</font>')

    redeem_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['redeem']),
        text='Выкупить',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Выкупить заложенное поле за полную стоимость</font>')

    surrender_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['surrender']),
        text='Сдаться',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Просто сдаться</font>')


    name_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['name']),
        placeholder_text='Введите имя',
        initial_text=settings.name,
        manager=manager)

    ip_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['IP']),
        placeholder_text='IP адрес',
        initial_text=settings.address,
        manager=manager)

    port_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['port']),
        placeholder_text='Порт',
        initial_text=settings.port,
        manager=manager)

    avatar_choose_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['choose_avatar']),
        text='Выбрать аватар',
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Только после начала игры</font>')

    connect_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['connect']),
        text='Подключиться',
        manager=manager)

    settings_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['settings']),
        text='Настройки',
        manager=manager)


    exchange_commit_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(exchange_coordinates['confirm']),
        text='Обмен',
        visible=False,
        manager=manager)

    exchange_cancel_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(exchange_coordinates['reject']),
        text='Отмена',
        visible=False,
        manager=manager)

    exchange_give_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect((exchange_coordinates['textbox_give'])),
        placeholder_text='Сумма пЭнисов',
        visible=False,
        manager=manager)

    exchange_get_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect((exchange_coordinates['textbox_get'])),
        placeholder_text='Сумма пЭнисов',
        visible=False,
        manager=manager)

    exchange_request_confirm_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(exchange_coordinates['confirm']),
        text='Обмен',
        visible=False,
        manager=manager)

    exchange_request_reject_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(exchange_coordinates['reject']),
        text='Отказ',
        visible=False,
        manager=manager)

    auction_buy_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(auction_coordinates['confirm']),
        text='Купить',
        visible=False,
        manager=manager)

    auction_reject_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(auction_coordinates['reject']),
        text='Отказаться',
        visible=False,
        manager=manager)

    exit_prison_egg_btn = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(egg_btns_coordinates[0]),
        text='',
        visible=False,
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#egg_button'),
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Выйти из тюрьмы</font>')

    exit_prison_eggs_btn = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(egg_btns_coordinates[0]),
        text='',
        visible=False,
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#eggs_button'),
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Выйти из тюрьмы</font>')

    dn_btn = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(egg_btns_coordinates[0]),
        text='',
        visible=False,
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#dn_button'),
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Удвоить или обнулить свой долг</font>')

    log_entry_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(log_textbox_coordinates['user_input_box']),
        placeholder_text='',
        manager=manager)

    log_text_send_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(log_textbox_coordinates['text_send_button']),
        text='',
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#text_send_button'),
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Отправить текст</font>')
    log_text_send_button.disable()

    log_audio_send_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(log_textbox_coordinates['audio_send_button']),
        text='',
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#audio_send_button'),
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Отправить аудио</font>')
    log_audio_send_button.disable()

    log_voice_message_send_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(log_textbox_coordinates['voice_message_send_button']),
        text='',
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#voice_message_send_button'),
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Отправить голосовое сообщение</font>',
        generate_click_events_from=frozenset([pg.BUTTON_LEFT, pg.BUTTON_RIGHT]))

    log_voice_message_send_button.disable()

    log_image_send_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(log_textbox_coordinates['image_send_button']),
        text='',
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#image_send_button'),
        manager=manager,
        tool_tip_text=f'<font face="BulBulPoly" pixel_size={1} color="#000000">Отправить изображение</font>')
    log_image_send_button.disable()

    message_panel = pygame_gui.elements.UIPanel(relative_rect=pg.Rect(tile_info_coordinates, tile_info_coordinates),
                                                manager=manager,
                                                visible=False)

    # time_bar = pygame_gui.elements.UIStatusBar(relative_rect=pg.Rect(676, 66, 148, 12),
    #                                            manager=manager)
    # print(time_bar.status_text())

    screen_widgets['board'] = [
        [cube_button, cube_button.visible],
        [buy_button, buy_button.visible],
        [pay_button, pay_button.visible],
        [shove_penis_button, shove_penis_button.visible],
        [remove_penis_button, remove_penis_button.visible],
        [exchange_button, exchange_button.visible],
        [auction_button, auction_button.visible],
        [mortgage_button, mortgage_button.visible],
        [redeem_button, redeem_button.visible],
        [surrender_button, surrender_button.visible],
        [name_textbox, name_textbox.visible],
        [ip_textbox, ip_textbox.visible],
        [port_textbox, port_textbox.visible],
        [avatar_choose_button, avatar_choose_button.visible],
        [connect_button, connect_button.visible],
        [settings_button, settings_button.visible],
        [exchange_commit_button, exchange_commit_button.visible],
        [exchange_cancel_button, exchange_cancel_button.visible],
        [exchange_give_textbox, exchange_give_textbox.visible],
        [exchange_get_textbox, exchange_get_textbox.visible],
        [exchange_request_confirm_button, exchange_request_confirm_button.visible],
        [exchange_request_reject_button, exchange_request_reject_button.visible],
        [auction_buy_button, auction_buy_button.visible],
        [auction_reject_button, auction_reject_button.visible],
        [exit_prison_egg_btn, exit_prison_egg_btn.visible],
        [exit_prison_eggs_btn, exit_prison_eggs_btn.visible],
        [dn_btn, dn_btn.visible],
        [log_entry_textbox, log_entry_textbox.visible],
        [log_text_send_button, log_text_send_button.visible],
        [log_audio_send_button, log_audio_send_button.visible],
        [log_voice_message_send_button, log_voice_message_send_button.visible],
        [log_image_send_button, log_image_send_button.visible],
        [message_panel, message_panel.visible]
    ]


def show_cubes(cube1, cube2):
    global cube_1_picture, cube_2_picture, state
    cube_1_picture = pg.image.load(f'resources/{settings.resolution_folder}/cubes/{cube1}.png').convert()
    cube_2_picture = pg.image.load(f'resources/{settings.resolution_folder}/cubes/{cube2}.png').convert()

    state['cube_animation_playing'] = True
    time.sleep(1.5)
    state['cube_animation_playing'] = False


def get_row_height():
    fixed = settings_buttons_coordinates.get('row_height', 0)
    if fixed > 0:
        return fixed
    max_h = 0
    for row in settings_layout:
        for item in row:
            if isinstance(item, tuple) and len(item) == 2:
                _, widget = item
            else:
                widget = item[0]
            if widget and hasattr(widget, 'relative_rect'):
                max_h = max(max_h, widget.relative_rect.height)
    return max_h


def update_settings_positions():
    y = default_offsets[settings.resolution_folder]['settings topleft'][1]
    widget_offset = settings_buttons_coordinates.get('widget_vertical_offset', 0)
    row_padding = settings_buttons_coordinates.get('row_vertical_padding', 10)

    for row in settings_layout:
        has_text = any(isinstance(item, tuple) and len(item) == 2 for item in row)

        if has_text:
            max_height = 0
            for item in row:
                if isinstance(item, tuple) and len(item) == 2:
                    if font:
                        max_height = max(max_height, font.get_height())
        else:
            max_height = 0
            for item in row:
                widget = item[0] if isinstance(item, tuple) else item
                if widget and hasattr(widget, 'relative_rect'):
                    max_height = max(max_height, widget.relative_rect.height)

        if max_height == 0:
            y += row_padding * 2
            continue

        current_x = default_offsets[settings.resolution_folder]['settings topleft'][0]
        for item in row:
            if isinstance(item, tuple) and len(item) == 2:
                label_text, widget = item
                label_width = font.size(label_text)[0] if font else 0
                widget_x = current_x + label_width + settings_buttons_coordinates['label_widget_gap']
            else:
                widget = item[0]
                widget_x = current_x

            if widget and hasattr(widget, 'relative_rect'):
                widget_height = widget.relative_rect.height
                widget_y = y + (max_height - widget_height) // 2 + widget_offset
                widget.set_relative_position((widget_x, widget_y))
                current_x = widget_x + widget.relative_rect.width + settings_buttons_coordinates['widget_widget_gap']
            else:
                current_x += settings_buttons_coordinates['widget_widget_gap']

        y += max_height + row_padding * 2

    if start_game_button:
        btn_rect = start_game_button.relative_rect
        start_game_button.set_relative_position(((screen.get_width() - btn_rect.width) // 2,
                                                 screen.get_height() - btn_rect.height - 20))


def render_screen():
    global prev_time, dt
    if state['screen'] == 'settings start':
        clock.tick(settings.FPS)
        dt, prev_time = delta_time(prev_time)
        screen.fill(settings.background_color_converted)
        event_handler()

        label_offset = settings_buttons_coordinates.get('label_vertical_offset', 0)
        for row in settings_layout:
            has_text = any(isinstance(item, tuple) and len(item) == 2 for item in row)

            if has_text:
                max_height = 0
                for item in row:
                    if isinstance(item, tuple) and len(item) == 2:
                        if font:
                            max_height = max(max_height, font.get_height())
            else:
                max_height = 0
                for item in row:
                    widget = item[0] if isinstance(item, tuple) else item
                    if widget and hasattr(widget, 'relative_rect'):
                        max_height = max(max_height, widget.relative_rect.height)

            if max_height == 0:
                continue

            for item in row:
                if isinstance(item, tuple) and len(item) == 2:
                    label_text, widget = item
                    if widget and hasattr(widget, 'relative_rect'):
                        widget_rect = pg.Rect(widget.relative_rect)
                        label_surf = font.render(label_text, False, 'black')
                        label_rect = label_surf.get_rect()
                        label_rect.right = widget_rect.left - settings_buttons_coordinates['label_widget_gap']
                        label_rect.centery = widget_rect.y + max_height // 2 + label_offset
                        screen.blit(label_surf, label_rect)

        try:
            manager.update(dt)
            manager.draw_ui(screen)
        except:
            pass

        pg.display.flip()

    elif state['screen'] == 'board':
        clock.tick(settings.FPS)
        dt, prev_time = delta_time(prev_time)
        screen.fill(settings.background_color_converted)
        event_handler()

        blit_board()
        blit_board_above_prices()
        log_textbox.render(screen)
        try:
            manager.update(dt)
            manager.draw_ui(screen)
        except:
            pass
        blit_board_above_interface()

        average_fps = clock.get_fps()

        average_fps_text = font.render(str(round(average_fps)), False, 'black')
        screen.blit(average_fps_text, fps_coordinates)

        pg.display.update()

    elif state['screen'] == 'currency drawing':
        clock.tick(settings.FPS)
        dt, prev_time = delta_time(prev_time)
        screen.fill(settings.background_color_converted)
        event_handler()

        for row in currency_drawing_widget_list:
            for button in row:
                button.render(screen)

        try:
            manager.update(dt)
            manager.draw_ui(screen)
        except:
            pass

        pg.display.update()


def change_screen(new_screen):
    current_screen = state['screen']
    if current_screen != new_screen:
        for element_list in screen_widgets[current_screen]:
            element_list[1] = element_list[0].visible
            element_list[0].hide()

        for element_list in screen_widgets[new_screen]:
            if element_list[1]:
                element_list[0].show()

        state['screen'] = new_screen


def change_screen_to_draw_currency():
    load_bmcf(f'resources/currency/{settings.resolution_folder}/{settings.currency}.bmcf')

    currency_drawing_buttons()

    change_screen('currency drawing')


def save_character():
    bitmap_ = []
    for row in currency_drawing_widget_list:
        row_ = []
        for button in row:
            row_.append(button.get_state())
        bitmap_.append(row_)

    # проверка на пустые столбцы
    x_len = len(bitmap_[0])
    y_len = len(bitmap_)

    discard_cols = []
    # ищем пустые столбцы слева
    for j in range(x_len):
        has_nonzero = False
        for i in range(y_len):
            if bitmap_[i][j] != 0:
                has_nonzero = True
                break
        if not has_nonzero:
            discard_cols.append(j)
        else:
            break

    # ищем пустые столбцы справа
    for j in range(x_len):
        has_nonzero = False
        for i in range(y_len):
            if bitmap_[y_len - i - 1][x_len - j - 1] != 0:
                has_nonzero = True
                break
        if not has_nonzero:
            discard_cols.append(x_len - j - 1)
        else:
            break

    keep_cols = list(range(x_len))
    for x in discard_cols:
        keep_cols.remove(x)

    result = []
    for row in bitmap_:
        new_row = []
        for j in keep_cols:
            new_row.append(row[j])
        result.append(new_row)

    file_name = save_character_textbox.get_text()
    save_path = f'resources/currency/{settings.resolution_folder}/{file_name}.bmcf'
    write_bmcf(path=save_path, res_index=settings.resolution_index, dim_x=len(result[0]), dim_y=len(result), bitmap=result)
    dropdown_save.add_options([file_name])
    dropdown_load.add_options([file_name])


def currency_drawing_buttons():
    global save_button, back_button, dropdown_load, save_character_textbox, dropdown_save, set_char_button, restart_button

    for element_list in screen_widgets['currency drawing']:
        element_list[0].kill()

    back_rect = pg.Rect(currency_drawing_coordinates['back'])
    back_rect.midbottom = (screen.width // 2, screen.height - currency_drawing_coordinates['gap'])
    back_button = pygame_gui.elements.UIButton(
        relative_rect=back_rect,
        text='Назад',
        manager=manager)

    options_list = os.listdir(f'resources/currency/{settings.resolution_folder}')
    for i in range(len(options_list)):
        option_split = options_list[i].split('.')
        option = option_split[:-1]
        options_list[i] = '.'.join(option)

    dropdown_load_rect = pg.Rect(currency_drawing_coordinates['dropdown load'])
    dropdown_load_rect.topleft = (currency_drawing_widget_list[-1][0].border_rect.left, currency_drawing_widget_list[-1][0].border_rect.bottom + currency_drawing_coordinates['gap'])
    dropdown_load = pygame_gui.elements.UIDropDownMenu(
        relative_rect=dropdown_load_rect,
        starting_option=settings.currency,
        options_list=options_list,
        manager=manager)

    save_character_textbox_rect = pg.Rect(currency_drawing_coordinates['char name textbox'])
    save_character_textbox_rect.topleft = (dropdown_load_rect.left, dropdown_load_rect.bottom + currency_drawing_coordinates['gap'])
    save_character_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=save_character_textbox_rect,
        placeholder_text='Введите название символа',
        initial_text='',
        object_id='#settings_font',
        manager=manager)

    save_rect = pg.Rect(currency_drawing_coordinates['save char'])
    save_rect.topleft = (save_character_textbox_rect.left, save_character_textbox_rect.bottom + currency_drawing_coordinates['gap'])
    save_button = pygame_gui.elements.UIButton(
        relative_rect=save_rect,
        text='Сохранить символ',
        manager=manager)

    dropdown_save_rect = pg.Rect(currency_drawing_coordinates['dropdown save'])
    dropdown_save_rect.topleft = (currency_drawing_widget_list[0][-1].border_rect.right + currency_drawing_coordinates['gap'], currency_drawing_widget_list[0][-1].border_rect.top)
    dropdown_save = pygame_gui.elements.UIDropDownMenu(
        relative_rect=dropdown_save_rect,
        starting_option=settings.currency,
        options_list=options_list,
        manager=manager)

    set_char_rect = pg.Rect(currency_drawing_coordinates['set char'])
    set_char_rect.topleft = (dropdown_save_rect.left, dropdown_save_rect.bottom + currency_drawing_coordinates['gap'])
    set_char_button = pygame_gui.elements.UIButton(
        relative_rect=set_char_rect,
        text='Установить',
        manager=manager)

    restart_rect = pg.Rect(currency_drawing_coordinates['restart'])
    restart_rect.topleft = (set_char_rect.left, set_char_rect.bottom + currency_drawing_coordinates['gap'])
    restart_button = pygame_gui.elements.UIButton(
        relative_rect=restart_rect,
        text='Перезапустить игру',
        manager=manager)

    # не надо позволять игроку перезапустить игру по время подключения
    if state['connected']:
        restart_button.disable()

    theme = manager.create_new_theme(f'resources/{settings.resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)

    screen_widgets['currency drawing'] = [
        [save_button, save_button.visible],
        [back_button, back_button.visible],
        [dropdown_load, dropdown_load.visible],
        [save_character_textbox, save_character_textbox.visible],
        [dropdown_save, dropdown_save.visible],
        [set_char_button, set_char_button.visible],
        [restart_button, restart_button.visible]
    ]


def load_bmcf(bmcf_path):
    res_index, dim_x, dim_y, bitmap_list = read_bmcf(bmcf_path)
    global currency_drawing_widget_list
    currency_drawing_widget_list = []
    y = default_offsets[settings.resolution_folder]['currency drawing topleft'][1]
    for row in bitmap_list:
        x = default_offsets[settings.resolution_folder]['currency drawing topleft'][0]
        widget_row = []
        for bit in row:
            widget_row.append(CurrencyDrawingButton(((x, y), currency_drawing_tile_size), bit))
            x += currency_drawing_tile_size[0]
        for i in range(abs(len(bitmap_list) - len(row))):
            widget_row.append(CurrencyDrawingButton(((x, y), currency_drawing_tile_size), 0))
            x += currency_drawing_tile_size[0]
        currency_drawing_widget_list.append(widget_row)
        y += currency_drawing_tile_size[1]


def restart_game():
    pg.quit()

    if sys.platform == 'win32':  # windows
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        flags = 0  # linux/mac (не знаю зачем, всё равно поддержки нет)

    if '__compiled__' in globals() and globals()['__compiled__']:
        subprocess.Popen([sys.argv[0]] + sys.argv[1:], creationflags=flags)
    else:
        subprocess.Popen([sys.executable, __file__] + sys.argv[1:], creationflags=flags)

    sys.exit()


# Проверки
# |
# V


def name_check():
    name = name_textbox.get_text()
    name = forbidden_characters_check(name, ['¦', '¥', '\n'])
    while font.size(name)[0] >= profile_picture.width - 10:
        name = name[:-1]
    if name_textbox.get_text() != name:
        name_textbox.set_text(name)


def fps_check(textbox):
    fps = textbox.get_text()
    fps = allowed_characters_check(fps, '0123456789.,')
    if textbox.get_text() != fps:
        textbox.set_text(fps)


def log_entry_check():
    log_text = log_entry_textbox.get_text()
    log_text = forbidden_characters_check(log_text, ['¦', '¥', '\n'])
    if log_entry_textbox.get_text() != log_text:
        log_entry_textbox.set_text(log_text)


def active_buttons_check():
    # Бросок кубов
    if not state['is_game_started'] or not state['throw_cubes_btn_active']:
        cube_button.disable()
    else:
        cube_button.enable()

    # Купить
    if not state['is_game_started'] or not state['buy_btn_active'][0]:
        buy_button.disable()
    else:
        buy_button.enable()

    # Аукцион
    if not state['is_game_started'] or not state['auction_btn_active']:
        auction_button.disable()
    else:
        auction_button.enable()

    # Оплатить
    if not state['is_game_started'] or state['pay_btn_active'][0] == False:
        pay_button.disable()
    else:
        pay_button.enable()

    # Сунуть пЭнис
    if not state['is_game_started'] or not state['penis_build_btn_active']:
        shove_penis_button.disable()
    else:
        shove_penis_button.enable()

    # Убрать пЭнис
    if not state['is_game_started'] or not state['penis_remove_btn_active']:
        remove_penis_button.disable()
    else:
        remove_penis_button.enable()

    # Обмен
    if not state['is_game_started'] or not state['exchange_btn_active']:
        exchange_button.disable()
    else:
        exchange_button.enable()

    # Заложить
    if not state['mortgage_btn_active']:
        mortgage_button.disable()
    else:
        mortgage_button.enable()

    # Выкупить
    if not state['redeem_btn_active']:
        redeem_button.disable()
    else:
        redeem_button.enable()

    # Сдаться
    if not state['surrender_btn_active']:
        surrender_button.disable()
    else:
        surrender_button.enable()

    # Подключиться
    if state['is_game_started'] or state['connected']:
        connect_button.disable()
    else:
        connect_button.enable()

    # Выбрать аватар
    if not state['is_game_started'] or state['avatar_chosen']:
        avatar_choose_button.disable()
    else:
        avatar_choose_button.enable()

    if state['connected']:
        log_text_send_button.enable()
        log_audio_send_button.enable()
        log_voice_message_send_button.enable()
        log_image_send_button.enable()
    else:
        log_text_send_button.disable()
        log_audio_send_button.disable()
        log_voice_message_send_button.disable()
        log_image_send_button.disable()


running = True

monopoly_init()

past_second_fps = []
prev_fps_time = time.time()
average_fps = 0

gc.collect()


while running:
    render_screen()

print('\nПрограмма завершена')

if log_textbox:
    del log_textbox
    if os.path.exists('resources/temp/audios/client'):
        for file in os.listdir('resources/temp/audios/client'):
            try:
                os.remove(f'resources/temp/audios/client/{file}')
            except:
                pass

if settings.debug:
    is_commanded = False
    for i in command_counter:
        if command_counter[i] > 0:
            is_commanded = True

    if is_commanded:
        os.makedirs('logs', exist_ok=True)
        sorted_dict = dict(sorted(command_counter.items(), key=lambda item: item[1], reverse=True))
        sorted_dict['unknown_commands'] = unknown_commands
        time_ = datetime.datetime.now()
        formatted_date = time_.strftime("%d.%m.%Y_%H-%M-%S")
        if os.path.exists(f'logs/commands_log_{formatted_date}.json'):
            counter = 1
            while os.path.exists(f'logs/commands_log_{formatted_date}_{counter}.json'):
                counter += 1
        with open(f'logs/commands_log_{formatted_date}.json', 'w') as file:
            json.dump(sorted_dict, file, indent=4, ensure_ascii=False)

# profiler.disable()
# s = io.StringIO()
# ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
# ps.print_stats(20)
# print(s.getvalue())