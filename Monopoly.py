# для прочего
import time
import os
import traceback
import gc
import pprint
import json

os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (0, 31) # (0, 31)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# для функционала игры
import pygame as pg
import socket as sck
import threading
import math

# для отправки файлов
import io
from PIL import Image
import base64
import tkinter
import tkinter.filedialog
import zlib
import magic
import mimetypes
import wave

# для интерфейса
import pygame_gui

# классы
from Players_Class_Client_side import Player
from Channel_Class import Channel
from Recorder_Class import AudioRecorder

# функции
from all_tiles_extraction import all_tiles_get
from colored_output import thread_open, information_sent, information_received, new_connection
from resolution_choice import resolution_definition


def settings_buttons(previous_values):
    global start_game_button, dropdown, fps_textbox, optimization_checkbox, debug_checkbox, pick_color_button, color_picker, fullscreen_checkbox, sharp_scale_checkbox, apply_button
    dropdown = pygame_gui.elements.UIDropDownMenu(
        relative_rect=pg.Rect(settings_buttons_coordinates['dropdown']),
        starting_option=previous_values['resolution'],
        options_list=['1280x720', '1920x1080', '2560x1440'],
        manager=manager)

    fps_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['fps_textbox']),
        placeholder_text='',
        initial_text=str(previous_values['fps']),
        object_id='#settings_font',
        manager=manager)

    optimization_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['optimization_checkbox']),
        text='',
        initial_state=previous_values['optimized movement'],
        manager=manager)

    debug_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['debug_checkbox']),
        text='',
        initial_state=previous_values['debug mode'],
        manager=manager)

    fullscreen_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['fullscreen_checkbox']),
        text='',
        initial_state=previous_values['fullscreen'],
        manager=manager)

    sharp_scale_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(settings_buttons_coordinates['sharp_scale_checkbox']),
        text='',
        initial_state=previous_values['sharp fullscreen'],
        manager=manager)
    if not fullscreen_checkbox.get_state():
        sharp_scale_checkbox.disable()

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

    color_picker = pygame_gui.windows.UIColourPickerDialog(
        rect=pg.Rect(settings_buttons_coordinates['color_picker']),
        initial_colour=settings_data['background color converted'],
        manager=manager,
        visible=False)

    start_game_button = pygame_gui.elements.UIButton(
        relative_rect=settings_buttons_coordinates['start_game_button'],
        text='Начать игру',
        object_id='#settings_font',
        manager=manager)


def monopoly_init():
    global players, exchange_value, exchange_color, state, sound_messages, voice_messages, sound_messages_channel, voice_messages_channel, image_messages, receive_size, recorder

    gc.enable()
    pg.init()
    pg.mixer.init(frequency=44100, size=16, channels=1)  # для звука
    mimetypes.init()

    players = []
    exchange_value = -100
    exchange_color = ''

    recorder = AudioRecorder()
    sound_messages = {}
    voice_messages = {}
    sound_messages_channel = Channel(0)
    voice_messages_channel = Channel(1)
    image_messages = 0
    receive_size = 1024

    state = {'throw_cubes_btn_active': False,
             'buy_btn_active': False,
             'pay_btn_active': ['False'],
             'penis_build_btn_active': False,
             'penis_remove_btn_active': False,
             'mortgage_btn_active': False,
             'redeem_btn_active': False,
             'auction_btn_active': False,
             'exchange_btn_active': False,
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
             'egg_btn_active': False,
             'eggs_btn_active': False,
             'tile_info_show': [False],
             'audio_recording': False}

    global screen, clock, settings_data

    if os.path.exists('settings.json'):
        global resolution, resolution_folder, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, FPS, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates, font_size, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_font_size, egg_card_text_width, egg_btns_coordinates, optimized, background_color, log_textbox_coordinates, tile_info_coordinates, fullscreen, sharp_scale, settings_buttons_coordinates, settings_font_size, log_image_size, name, address, port
        resolution, resolution_folder, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, FPS, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates, font_size, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_font_size, egg_card_text_width, egg_btns_coordinates, optimized, background_color, log_textbox_coordinates, tile_info_coordinates, fullscreen, sharp_scale, settings_buttons_coordinates, settings_font_size, log_image_size, name, address, port = resolution_definition()
        f = open('settings.json')
        settings_data = json.load(f)
        if settings_data['resolution index'] == 1:
            settings_data['resolution'] = '1280x720'
        elif settings_data['resolution index'] == 2:
            settings_data['resolution'] = '1920x1080'
        elif settings_data['resolution index'] == 3:
            settings_data['resolution'] = '2560x1440'

        settings_data['background color converted'] = pg.Color(settings_data['background color'])

        if not settings_data['fullscreen']:
            settings_data['sharp fullscreen'] = False
    else:
        resolution = (1280, 650)
        resolution_folder = '720p'
        font_size = 25
        settings_font_size = 25
        FPS = 60
        settings_data = {'resolution index': 1,
                         'resolution': '1280x720',
                         'fps': 60,
                         'optimized movement': False,
                         'background color': [128, 128, 128],
                         'fullscreen': False,
                         'sharp fullscreen': False,
                         'debug mode': False,
                         'background color converted': pg.Color([128, 128, 128]),
                         'name': ''}

        settings_buttons_coordinates = {'dropdown': (10, 10, 230, 50),
                                        'start_game_button': (572, 602, 136, 38),
                                        'fps_textbox': (266, 70, 60, 30),
                                        'optimization_checkbox': (226, 105, 25, 25),
                                        'debug_checkbox': (120, 137, 25, 25),
                                        'fullscreen_checkbox': (222, 169, 25, 25),
                                        'sharp_scale_checkbox': (252, 201, 25, 25),
                                        'pick_color_button': (10, 240, 180, 38),
                                        'apply_button': (10, 298, 180, 38),
                                        'color_picker': (60, 120, 390, 390),
                                        'fps_text': (10, 70),
                                        'optimization_text': (10, 102),
                                        'debug_text': (10, 134),
                                        'fullscreen_text': (10, 166),
                                        'sharp_scale_text': (10, 198)}

    flags = pg.HWSURFACE
    if settings_data['fullscreen']:
        flags = flags | pg.FULLSCREEN
    if settings_data['sharp fullscreen']:
        flags = flags | pg.SCALED
    screen = pg.display.set_mode((2560, 1360))
    screen = pg.display.set_mode(resolution, flags)
    TITLE = 'Monopoly v0.16'
    icon = pg.image.load(f'resources/icon.png')
    pg.display.set_icon(icon)
    pg.display.set_caption(TITLE)
    clock = pg.time.Clock()

    global font, settings_font, manager, prev_time
    font = pg.font.Font('resources/fonts/bulbulpoly-4.ttf', font_size)
    settings_font = pg.font.Font('resources/fonts/bulbulpoly-4.ttf', settings_font_size)

    manager = pygame_gui.UIManager(resolution, theme_path=f'resources/{resolution_folder}/gui_theme.json', enable_live_theme_updates=False, starting_language='ru')

    settings_buttons(settings_data)

    theme = manager.create_new_theme(f'resources/{resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)

    prev_time = time.time()


def save_settings():
    settings_data_new = {'resolution index': settings_data['resolution index'],
                         'fps': int(fps_textbox.get_text()),
                         'optimized movement': optimization_checkbox.get_state(),
                         'background color': settings_data['background color'],
                         'fullscreen': fullscreen_checkbox.get_state(),
                         'sharp fullscreen': sharp_scale_checkbox.get_state(),
                         'debug mode': debug_checkbox.get_state(),
                         'name': name,
                         'address': address,
                         'port': port}

    with open("settings.json", "w+") as outfile:
        json.dump(settings_data_new, outfile, indent=4, ensure_ascii=False)


def load_assets():
    global resolution, resolution_folder, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, FPS, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates, font_size, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_font_size, egg_card_text_width, egg_btns_coordinates, optimized, background_color, log_textbox_coordinates, tile_info_coordinates, fullscreen, sharp_scale, settings_buttons_coordinates, settings_font_size, log_image_size, name, address, port
    resolution, resolution_folder, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, FPS, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates, font_size, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_font_size, egg_card_text_width, egg_btns_coordinates, optimized, background_color, log_textbox_coordinates, tile_info_coordinates, fullscreen, sharp_scale, settings_buttons_coordinates, settings_font_size, log_image_size, name, address, port = resolution_definition()

    global exchange_screen, auction_screen, darkening_full, darkening_tile, profile_picture, bars, player_bars, avatar_file, mortgaged_tile, font, eggs_card_uncovered, egg_font, board_image, settings_font
    exchange_screen = pg.image.load(f'resources/{resolution_folder}/exchange.png').convert_alpha()
    auction_screen = pg.image.load(f'resources/{resolution_folder}/auction.png').convert_alpha()
    darkening_full = pg.image.load(f'resources/{resolution_folder}/darkening all.png').convert_alpha()
    darkening_tile = pg.image.load(f'resources/{resolution_folder}/darkening tile.png').convert_alpha()
    profile_picture = pg.image.load(f'resources/{resolution_folder}/profile/profile.png').convert_alpha()
    bars = pg.image.load(f'resources/{resolution_folder}/bars.png').convert_alpha()
    player_bars = pg.image.load(f'resources/{resolution_folder}/profile/profile_bars.png').convert_alpha()
    avatar_file = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png').convert_alpha()
    mortgaged_tile = pg.image.load(f'resources/{resolution_folder}/mortgaged.png').convert_alpha()
    eggs_card_uncovered = pg.image.load(f'resources/{resolution_folder}/egg-s_card_uncovered.png').convert()
    font = pg.font.Font('resources/fonts/bulbulpoly-4.ttf', font_size)
    egg_font = pg.font.Font('resources/fonts/bulbulpoly-4.ttf', egg_font_size)
    settings_font = pg.font.Font('resources/fonts/bulbulpoly-4.ttf', settings_font_size)

    for penis in range(5):
        globals()[f'{penis + 1}_penises_image'] = pg.image.load(f'resources/{resolution_folder}/white penises/{penis + 1}.png').convert_alpha()

    global all_tiles, all_players, all_egg, all_eggs, update_list_static, update_list_dynamic, ideal_dt, screen
    all_tiles, all_egg, all_eggs = all_tiles_get(resolution_folder, tile_size)
    for tile in all_tiles:
        tile.text_defining(font)

    board_image = pg.image.load(f'resources/temp/images/{resolution_folder}/board image.png').convert()

    all_players = [Player('red',    (all_tiles[0].x_center, all_tiles[0].y_center), resolution_folder, '#ff0000'),
                   Player('blue',   (all_tiles[0].x_center, all_tiles[0].y_center), resolution_folder, '#0000ff'),
                   Player('yellow', (all_tiles[0].x_center, all_tiles[0].y_center), resolution_folder, '#ffff00'),
                   Player('green',  (all_tiles[0].x_center, all_tiles[0].y_center), resolution_folder, '#0AA00A')]

    ideal_dt = 1 / FPS

    flags = pg.HWSURFACE
    if fullscreen:
        flags = flags | pg.FULLSCREEN
    if sharp_scale:
        flags = flags | pg.SCALED

    f = open('settings.json')
    settings = json.load(f)
    if settings['resolution index'] == 1:
        settings['resolution'] = '1280x720'
    elif settings['resolution index'] == 2:
        settings['resolution'] = '1920x1080'
    elif settings['resolution index'] == 3:
        settings['resolution'] = '2560x1440'
    settings['background color converted'] = pg.Color(settings['background color'])
    if not settings['fullscreen']:
        settings['sharp fullscreen'] = False

    screen = pg.display.set_mode(resolution, flags)

    update_list_dynamic = [pg.Rect((0, 0), resolution)]

    start_game_button.kill()
    dropdown.kill()
    fps_textbox.kill()
    optimization_checkbox.kill()
    debug_checkbox.kill()
    pick_color_button.kill()
    color_picker.kill()
    fullscreen_checkbox.kill()
    sharp_scale_checkbox.kill()
    apply_button.kill()

    theme = manager.create_new_theme(f'resources/{resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)

    settings_buttons(settings)
    start_game_button.rebuild()
    dropdown.rebuild()
    fps_textbox.rebuild()
    optimization_checkbox.rebuild()
    debug_checkbox.rebuild()
    pick_color_button.rebuild()
    color_picker.rebuild()
    fullscreen_checkbox.rebuild()
    sharp_scale_checkbox.rebuild()
    apply_button.rebuild()

    theme = manager.create_new_theme(f'resources/{resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)

    manager.add_font_paths('BulBulPoly', "resources/fonts/bulbulpoly-4.ttf")
    manager.preload_fonts([{'name': 'BulBulPoly', 'point_size': f'{font_size}', 'style': 'regular', 'antialiased': '1'}])


def load_game():
    global sock, CLEAR_UPDATE_LIST
    start_game_button.kill()
    dropdown.kill()
    fps_textbox.kill()
    optimization_checkbox.kill()
    debug_checkbox.kill()
    pick_color_button.kill()
    color_picker.kill()
    fullscreen_checkbox.kill()
    sharp_scale_checkbox.kill()
    apply_button.kill()

    sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)
    sock.settimeout(0)
    sock.setblocking(True)

    buttons()

    theme = manager.create_new_theme(f'resources/{resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)
    active_buttons_check()

    global game_started
    game_started = True


def throw_cubes():
    exchange_screen_reset()
    for player in players:
        if player.on_move and state['is_game_started']:
            for player2 in players:
                if player2.main:
                    move_command = 'move%'
                    sock.send(move_command.encode())
                    information_sent('Команда отправлена', move_command)
                    player2.on_move = False
                    state['throw_cubes_btn_active'] = False
                    state['penis_build_btn_active'] = False
                    state['penis_remove_btn_active'] = False
                    state['exchange_btn_active'] = False
                    state['mortgage_btn_active'] = False
                    state['pay_btn_active'] = ['False']
                    state['paid'] = False
                    state['refused_to_buy'] = False
                    active_buttons_check()


def buy():
    if state['is_game_started'] and state['buy_btn_active']:
        for player in players:
            if player.main:
                buy_command = f'buy|{player.piece_position}%'
                sock.send(buy_command.encode())
                information_sent('Команда отправлена', buy_command)
                state['buy_btn_active'] = False
                # if state['double']:
                #     player_move_change(False)
                # else:
                #     player_move_change(True)
        mortgage_btn_check()
        active_buttons_check()


def pay():
    if state['is_game_started']:
        if state['pay_btn_active'][0] == 'minus':
            for player in players:
                if player.main:
                    pay_command = f'pay|{player.piece_position}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    # if state['double']:
                    #     player_move_change(False)
                    # else:
                    #     player_move_change(True)
                    state['pay_btn_active'] = ['False']

        elif state['pay_btn_active'][0] == 'pay sum':
            for player in players:
                if player.main:
                    pay_command = f'pay sum|{state['pay_btn_active'][1]}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    # if state['double']:
                    #     player_move_change(False)
                    # else:
                    #     player_move_change(True)
                    state['pay_btn_active'] = ['False']

        elif state['pay_btn_active'][0] == 'color':
            for player in players:
                if player.main:
                    pay_command = f'payToColor|{player.piece_position}|{state['pay_btn_active'][1]}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    # if state['double']:
                    #     player_move_change(False)
                    # else:
                    #     player_move_change(True)
                    state['pay_btn_active'] = ['False']

        elif state['pay_btn_active'][0] == 'player':
            for player in players:
                if player.main:
                    if player.money >= state['pay_btn_active'][2]:
                        pay_command = f'pay to player|{state['pay_btn_active'][1]}|{state['pay_btn_active'][2]}%' # 'pay to player|{color}|{sum}%'
                        sock.send(pay_command.encode())
                        information_sent('Команда отправлена', pay_command)
                        # if state['double']:
                        #     player_move_change(False)
                        # else:
                        #     player_move_change(True)

        elif state['pay_btn_active'][0] == 'players':
            for player in players:
                if player.main:
                    if player.money >= state['pay_btn_active'][1] * (len(players) - 1):
                        pay_command = f'pay to players|{state['pay_btn_active'][1]}%' # 'pay to players|{sum}%'
                        sock.send(pay_command.encode())
                        information_sent('Команда отправлена', pay_command)
                        # if state['double']:
                        #     player_move_change(False)
                        # else:
                        #     player_move_change(True)
                        state['pay_btn_active'] = ['False']

        elif state['pay_btn_active'][0] == 'prison':
            for player in players:
                if player.main:
                    pay_command = f'pay for prison%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    # player_move_change(False)
                    state['pay_btn_active'] = ['False']

        mortgage_btn_check()
        active_buttons_check()


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
              f'       on_move: {player.on_move}\n'
              f'       imprisoned: {player.imprisoned}\n')

    pprint.pp(state)


def connect():
    if not state['is_game_started'] and not state['connected']:
        try:
            ip_ = ip_textbox.get_text()
            port_ = port_textbox.get_text()
            port_ = int(port_)
            name_ = name_textbox.get_text()
            if '%' not in name_ and '|' not in name_:
                if name_:
                    sock.connect((ip_, port_))
                    sock.send(f'name|{name_}%'.encode())
                    state['connected'] = True

                    with open("settings.json", "r") as read_file:
                        settings = json.load(read_file)
                        settings['name'] = name_
                        settings['address'] = ip_
                        settings['port'] = str(port_)

                    with open("settings.json", "r+") as file:
                        json.dump(settings, file, indent=4, ensure_ascii=False)

                    log_text_send_button.enable()
                    log_audio_send_button.enable()
                    log_voice_message_send_button.enable()
                    log_image_send_button.enable()
                    connection_handler = threading.Thread(target=handle_connection, name='connection_handler', daemon=True)
                    connection_handler.start()
                    thread_open('Поток открыт', connection_handler.name)

                    new_connection('Подключено к', f'{ip_}:{port_}')
                else:
                    print(f'{"\033[31m{}".format('Ваше имя не должно быть пустым')}{'\033[0m'}')
                    log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#D0392A">Ваше имя не должно быть пустым</font><br>')
                    if log_textbox.scroll_bar:
                        log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
            else:
                print(f'{"\033[31m{}".format('Ваше имя не должно содержать символов "|" и "%"')}{'\033[0m'}')
                log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#D0392A">Ваше имя не должно содержать символов "|" и "%"</font><br>')
                if log_textbox.scroll_bar:
                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')
            print(f'{"\033[31m{}".format('Не удалось подключиться')}{'\033[0m'}')  # красный
            log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#D0392A">Не удалось подключиться</font><br>')
            if log_textbox.scroll_bar:
                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)


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
              f'{tile.x_position = }\n'
              f'{tile.y_position = }\n'
              f'{tile.xText = }\n'
              f'{tile.yText = }\n'
              f'{tile.x_center = }\n'
              f'{tile.y_center = }\n'
              f'{tile.family_members = }\n'
              f'{tile.penis_price = }\n'
              f'{tile.penises = }\n'
              f'{tile.income = }\n'
              f'{tile.owned = }\n'
              f'{tile.owner = }\n'
              f'{tile.full_family = }\n'
              f'{tile.mortgaged = }\n'
              f'{tile.mortgaged_moves_count = }\n')

    if state['is_game_started'] and state['all_penises_build_btns_active']:
        for player in players:
            if player.main:
                if (all_tiles[tile_position].full_family and
                        all_tiles[tile_position].penises < 5 and
                        player.money >= all_tiles[tile_position].penis_price and
                        all_tiles[tile_position].type == 'buildable' and
                        all_tiles[tile_position].owner == player.color):
                    state['penis_build_btn_active'] = False
                    state['penis_remove_btn_active'] = True
                    state['all_penises_build_btns_active'] = False
                    penis_command = f'penis build|{tile_position}%'
                    sock.send(penis_command.encode())
                    information_sent('Информация отправлена', penis_command)
                    active_buttons_check()

    elif state['is_game_started'] and state['all_penises_remove_btns_active']:
        for player in players:
            if player.main:
                if (all_tiles[tile_position].full_family and
                        1 <= all_tiles[tile_position].penises <= 5 and
                        all_tiles[tile_position].type == 'buildable' and
                        all_tiles[tile_position].owner == player.color):
                    state['penis_remove_btn_active'] = False
                    state['all_penises_remove_btns_active'] = False
                    penis_command = f'penis remove|{tile_position}%'
                    sock.send(penis_command.encode())
                    information_sent('Информация отправлена', penis_command)

    elif state['is_game_started'] and state['exchange_tile_btn_active']:
        global exchange_give, exchange_get
        if tile_position in available_tiles_for_exchange:
            if (tile_position not in exchange_give and
                    tile_position not in exchange_get):
                for player in players:
                    if player.main:
                        if player.color == all_tiles[tile_position].owner:
                            exchange_give.append(tile_position)
                        else:
                            exchange_get.append(tile_position)
            else:
                for player in players:
                    if player.main:
                        if player.color == all_tiles[tile_position].owner:
                            exchange_give.remove(tile_position)
                        else:
                            exchange_get.remove(tile_position)
            exchange_value_calculation()

    elif state['is_game_started'] and state['mortgage_tile_btn_active']:
        built_family = False
        for tile in all_tiles:
            if tile.family == all_tiles[tile_position].family:
                if tile.penises: # > 0
                    built_family = True

        if not all_tiles[tile_position].mortgaged and not built_family:
            mortgage_command = f'mortgage|{tile_position}%'
            sock.send(mortgage_command.encode())
            information_sent('Команда отправлена', mortgage_command)
            state['mortgage_tile_btn_active'] = False

    elif state['is_game_started'] and state['redeem_tile_btn_active']:
        for player in players:
            if player.main:
                if all_tiles[tile_position].mortgaged and player.money >= all_tiles[tile_position].price / 2 * 1.1:
                    redeem_command = f'redeem|{tile_position}%'
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
                       f'Базовая стоимость: {            math.ceil(tile.price / coef * (coef2 ** -1))}~',
                       f'Стоимость при полной семье: {   math.ceil(tile.price / coef * (coef2 ** 0))}~',
                       f'Стоимость при 1 белом пЭнисе: { math.ceil(tile.price / coef * (coef2 ** 1))}~',
                       f'Стоимость при 2 белых пЭнисах: {math.ceil(tile.price / coef * (coef2 ** 2))}~',
                       f'Стоимость при 3 белых пЭнисах: {math.ceil(tile.price / coef * (coef2 ** 3))}~',
                       f'Стоимость при 4 белых пЭнисах: {math.ceil(tile.price / coef * (coef2 ** 4))}~',
                       f'Стоимость при 5 белых пЭнисах: {math.ceil(tile.price / coef * (coef2 ** 5))}~',
                       f'Стоимость белого пЭниса: {      tile.penis_price}~']
        elif tile.type == 'train':
            coef = 8
            coef2 = 2
            message = [f'{tile.name}:',
                       f'Стоимость при 1 поле: { math.ceil(tile.price / coef * (coef2 ** 0))}~',
                       f'Стоимость при 2 полях: {math.ceil(tile.price / coef * (coef2 ** 1))}~',
                       f'Стоимость при 3 полях: {math.ceil(tile.price / coef * (coef2 ** 2))}~',
                       f'Стоимость при 4 полях: {math.ceil(tile.price / coef * (coef2 ** 3))}~']
        elif tile.type == 'infrastructure':
            message = [f'{tile.name}:',
                       f'Стоимость при 1 поле: сумма кубов * 4',
                       f'Стоимость при 2 полях: сумма кубов * 10']
        elif tile.type == 'minus':
            message = [f'{tile.name}:',
                       f'Это {tile.family}, он украдёт ваши {-tile.price}~, хе-хе',]
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
        for player2 in players:
            if player2.color == color:
                if not player2.main:
                    available_tiles_for_exchange = []
                    for player in players:
                        if player.main:
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
                for player in players:
                    if player.main:
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
                    for player in players:
                        if player.main:
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
        log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#000000">Нажмите на аватар человека, с которым хотите обменяться</font><br>')
        if log_textbox.scroll_bar:
            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
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
            exchange_command = f'exchange request|{exchange_money_give_sum}_'

            for give_tile in exchange_give:
                exchange_command += f'{all_tiles[give_tile].position}-'
            if exchange_give:
                exchange_command = exchange_command[:-1]
            exchange_command = exchange_command + f'|{exchange_money_get_sum}_'

            for get_tile in exchange_get:
                exchange_command += f'{all_tiles[get_tile].position}-'
            if exchange_get:
                exchange_command = exchange_command[:-1]
            exchange_command = exchange_command + f'|{exchange_color}%'

            sock.send(exchange_command.encode())
            information_sent('Команда отправлена', exchange_command)
            state['exchange_tile_btn_active'] = False
            state['exchange_player_btn_active'] = False
            state['show_exchange_screen'] = False
            # del available_tiles_for_exchange, exchange_color, exchange_give, exchange_get\

            exchange_commit_button.hide()
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

            exchange_command = f'exchange|{give_money}_'
            for give_tile in give_property:
                try:
                    exchange_command += f'{all_tiles[int(give_tile)].position}-'
                except:
                    pass
            if give_tile:
                exchange_command = exchange_command[:-1]
            exchange_command = exchange_command + f'|{get_money}_'

            for get_tile in get_property:
                try:
                    exchange_command += f'{all_tiles[int(get_tile)].position}-'
                except:
                    pass
            if get_tile:
                exchange_command = exchange_command[:-1]
            exchange_command = exchange_command + f'|{color}%'

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


def exchange_request_reject():
    if state['is_game_started'] and state['show_exchange_request_screen'][0]:
        reject_command = 'exchange request rejected%'
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
            image = Image.open(file_name)

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
            sendable_data = b'avatar|' + image_bytes_encoded_bytes_base64 + b'%'
            sock.send(sendable_data)


def auction():
    if state['is_game_started'] and state['auction_btn_active']:
        for player in players:
            if player.main:
                if all_tiles[player.piece_position].buyable:
                    auction_command = f'auction initiate|{player.piece_position}%'
                    sock.send(auction_command.encode())
                    information_sent('Команда отправлена', auction_command)
                    state['buy_btn_active'] = False
                    state['auction_btn_active'] = False
                    state['exchange_btn_active'] = False
                    state['mortgage_btn_active'] = False
                    state['refused_to_buy'] = True
                    active_buttons_check()


def auction_buy():
    if state['show_auction_screen'][0]:
        for player in players:
            if player.main:
                if player.money >= int(state['show_auction_screen'][2]) + 20:
                    auction_command = f'auction accept|{state['show_auction_screen'][1]}|{int(state['show_auction_screen'][2]) + 20}%'
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
                    state['mortgage_btn_active'] = False
                    state['redeem_btn_active'] = False
                    active_buttons_check()


def auction_reject():
    if state['show_auction_screen'][0]:
        auction_command = f'auction reject|{state['show_auction_screen'][1]}|{state['show_auction_screen'][2]}%'
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
        state['mortgage_btn_active'] = False
        state['redeem_btn_active'] = False
        active_buttons_check()


def mortgage():  # заложить
    exchange_screen_reset()
    if state['mortgage_btn_active']:
        state['mortgage_tile_btn_active'] = True
        state['redeem_tile_btn_active'] = False
        state['exchange_tile_btn_active'] = False
        state['all_penises_build_btns_active'] = False
        state['all_penises_remove_btns_active'] = False
        active_buttons_check()
        log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#000000">Нажмите на поле, которое хотите заложить</font><br>')
        if log_textbox.scroll_bar:
            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)


def redeem():  # выкупить
    exchange_screen_reset()
    if state['redeem_btn_active']:
        state['redeem_tile_btn_active'] = True
        state['mortgage_tile_btn_active'] = False
        state['exchange_tile_btn_active'] = False
        state['all_penises_build_btns_active'] = False
        state['all_penises_remove_btns_active'] = False
        active_buttons_check()
        log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#000000">Нажмите на поле, которое хотите выкупить</font><br>')
        if log_textbox.scroll_bar:
            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)


def exit_prison_by_egg_s(egg_type):
    prison_exit_information = ''
    for player in players:
        if player.main:
            if player.imprisoned:
                if player.egg_prison_exit_card and egg_type == 'Яйцо':
                    prison_exit_information = f'prison exit by eggs|Яйцо%'
                    player.egg_prison_exit_card = False
                    exit_prison_egg_btn.hide()
                elif player.eggs_prison_exit_card and egg_type == 'Яйца':
                    prison_exit_information = f'prison exit by eggs|Яйца%'
                    player.eggs_prison_exit_card = False
                    exit_prison_eggs_btn.hide()
                sock.send(prison_exit_information.encode())
                information_sent('Команда отправлена', prison_exit_information)


def egg_s_reset():
    state['egg_btn_active'] = False
    state['eggs_btn_active'] = False
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
            message_information = f'message|{message}%'
            log_entry_textbox.set_text('')
            sock.send(message_information.encode())
            information_sent('Команда отправлена', message_information)


def send_audio():
    if state['connected']:
        top = tkinter.Tk()
        top.withdraw()
        file_name = tkinter.filedialog.askopenfilename(parent=top, filetypes=[('Аудио файлы',
                                                                               ('*.aiff', '*.flac', '*.iff', '*.mp3',
                                                                                '*.oga', '*.opus', '*.wav'))])
        top.destroy()
        if file_name:
            audio_bytes = open(file_name, 'rb').read()
            encoding = zlib.compress(audio_bytes, level=9)
            audio_bytes_encoded_base64 = base64.b64encode(encoding)
            sendable_data = b'sound message|' + audio_bytes_encoded_base64 + '%'.encode()
            size_information = f'receive size|{len(sendable_data)}%'.encode()

            sock.send(size_information)
            sock.send(sendable_data)


def send_voice_message():
    if state['connected']:
        state['audio_recording'] = not state['audio_recording']
        if state['audio_recording']:
            log_textbox.append_html_text(
                f'<font face="BulBulPoly" pixel_size={font_size} color="#000000">Началась запись голоса. Чтобы остановить и отправить запись, нажмите на кнопку ещё раз</font><br>')
            if log_textbox.scroll_bar:
                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
            recorder.start_recording()
        else:
            audio_bytes = recorder.stop_recording()
            encoding = zlib.compress(audio_bytes, level=9)
            audio_bytes_encoded_base64 = base64.b64encode(encoding)
            sendable_data = b'voice message|' + audio_bytes_encoded_base64 + '%'.encode()
            size_information = f'receive size|{len(sendable_data)}%'.encode()

            sock.send(size_information)
            sock.send(sendable_data)


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
        image = Image.open(file_name)
        width, height = image.size
        if width <= height:
            new_side_size = width
        else:
            new_side_size = height
        image = image.crop(((width - new_side_size) // 2, (height - new_side_size) // 2, (width + new_side_size) // 2,
                            (height + new_side_size) // 2))
        image = image.resize([256, 256])

        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()
        image_bytes_encoded_bytes_base64 = base64.b64encode(image_bytes)

        sendable_data = b'image message|' + image_bytes_encoded_bytes_base64 + b'%'
        sock.send(sendable_data)


# ^
# |
# Функционал кнопок и текст боксов


def render_multiline_text(text, x, y, font_, line_height, align):
    lines = text
    for i, line in enumerate(lines):
        line_surface = font_.render(line, True, 'black').convert_alpha()
        if align == 'topleft':
            line_rect = line_surface.get_rect(topleft=(x, y + i * line_height))
        elif align == 'center':
            line_rect = line_surface.get_rect(center=(x, y + (i - len(lines) / 2 + 0.5) * line_height))
        screen.blit(line_surface, line_rect)


def blit_board():
    screen.blit(board_image)

    for tile in all_tiles:
        if tile.owned:
            screen.blit(globals()[f'{tile.owner}_property_image'], (tile.x_position, tile.y_position))

        if 1 <= tile.penises <= 5:
            screen.blit(globals()[f'{tile.penises}_penises_image'], (tile.x_position, tile.y_position))

        if tile.mortgaged:
            screen.blit(mortgaged_tile, (tile.x_position, tile.y_position))

            text = font.render(str(tile.mortgaged_moves_count), False, 'white')
            text_rect = text.get_rect(center=(tile.x_center, tile.y_center))
            screen.blit(text, text_rect)

    if state['cube_animation_playing']:
        screen.blit(cube_1_picture, cubes_coordinates[0])
        screen.blit(cube_2_picture, cubes_coordinates[1])

    if state['show_exchange_screen']:
        screen.blit(darkening_full, (0, 0))
        for tile in all_tiles:
            if tile.position not in available_tiles_for_exchange and tile.buyable:
                screen.blit(darkening_tile,
                            (tile.x_position, tile.y_position))

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
                screen.blit(darkening_tile, (tile.x_position, tile.y_position))

        screen.blit(exchange_screen, exchange_coordinates['exchange_screen'])

        give_text = []
        get_text = []
        for i in give_property:
            try:
                give_text.append(str(all_tiles[int(i)].name))
            except:
                pass
        for i in get_property:
            try:
                get_text.append(str(all_tiles[int(i)].name))
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

        give_money_text = font.render(f'{give_money}~', False, 'black')
        give_money_text_rect = give_money_text.get_rect(
            center=(exchange_coordinates['textbox_give'][0] + round(exchange_coordinates['textbox_give'][2] / 2),
                    exchange_coordinates['textbox_give'][1] + round(exchange_coordinates['textbox_give'][3] / 2)))
        screen.blit(give_money_text, give_money_text_rect)

        get_money_text = font.render(f'{get_money}~', False, 'black')
        get_money_text_rect = get_money_text.get_rect(
            center=(exchange_coordinates['textbox_get'][0] + round(exchange_coordinates['textbox_get'][2] / 2),
                    exchange_coordinates['textbox_get'][1] + round(exchange_coordinates['textbox_get'][3] / 2)))
        screen.blit(get_money_text, get_money_text_rect)

    elif state['show_auction_screen'][0]:
        tile_position = int(state['show_auction_screen'][1])
        price = int(state['show_auction_screen'][2])
        tile = all_tiles[tile_position]
        text = f'{price} + 20~'
        screen.blit(darkening_full, (0, 0))
        for tile_ in all_tiles:
            if tile_.buyable and tile_ != tile:
                screen.blit(darkening_tile, (tile_.x_position, tile_.y_position))
        screen.blit(auction_screen, auction_coordinates['auction_screen'])
        screen.blit(font.render(tile.name, False, 'black'), auction_coordinates['company_text'])
        screen.blit(font.render(text, False, 'black'), auction_coordinates['price_text'])


def blit_board_above_interface():
    if state['egg_btn_active'] or state['eggs_btn_active']:
        screen.blit(eggs_card_uncovered, egg_card_coordinates)
        screen.blit(pulled_card_title, pulled_card_title_rect)
        render_multiline_text(pulled_card_strings, egg_card_text_center[0], egg_card_text_center[1], egg_font, egg_font.get_linesize(), 'center')

    if state['connected']:
        for player in players:
            player_index = players.index(player)

            screen.blit(profile_picture, profile_coordinates[player_index]['profile'])

            screen.blit(player.avatar, profile_coordinates[player_index]['avatar'])

            if player.imprisoned:
                screen.blit(player_bars, profile_coordinates[player_index]['avatar'])

            screen.blit(globals()[f'{player.color}_profile'], profile_coordinates[player_index]['avatar'])

            screen.blit(font.render(f'{player.money}~', False, 'black'), profile_coordinates[player_index]['money'])

            screen.blit(font.render(player.name, False, 'black'), profile_coordinates[player_index]['name'])

            screen.blit(player.player_piece, player.player_piece_rect)

    screen.blit(bars, (all_tiles[10].x_position, all_tiles[10].y_position))

    if state['tile_info_show'][0]:
        tile_info = state['tile_info_show'][1]
        render_multiline_text(tile_info, tile_info_coordinates[0] + 10, tile_info_coordinates[1], font, font.get_linesize(), 'topleft')


def price_printing():
    for tile in all_tiles:
        if tile.price != '':
            screen.blit(tile.prerendered_text, tile.text_rect)


def position_update():
    global players
    for player in players:
        players_on_tile = []
        for player2 in players:
            if player2.piece_position == player.piece_position:
                players_on_tile.append(player2)
        end_positions = []
        for player3 in players_on_tile:
            end_positions.append((all_tiles[player3.piece_position].x_center + margin[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                  all_tiles[player3.piece_position].y_center + margin[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))
        move(players_on_tile, end_positions, 7)
        for player4 in players:
            player4.x = round(player4.x)
            player4.y = round(player4.y)


def move_by_cubes(cube1, cube2, color):  # Не спрашивайте, как тут что работает, я сам не знаю
    global players, state
    if cube1 >= 0:
        show_cubes(cube1, cube2)

    for player in players:
        if player.color == color:
            if player.main:
                state['buy_btn_active'] = False
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
                    end_positions.append((all_tiles[player3.piece_position].x_center + margin[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                          all_tiles[player3.piece_position].y_center + margin[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))
                move(players_on_tile, end_positions, cube1 + cube2)
            position_update()


            if player.main:
                if all_tiles[player.piece_position].family == 'Яйцо':
                    sock.send('pull card|Яйцо%'.encode())
                    information_sent('Информация отправлена', 'pull card|Яйцо%')

                elif all_tiles[player.piece_position].family == 'Яйца':
                    sock.send('pull card|Яйца%'.encode())
                    information_sent('Информация отправлена', 'pull card|Яйца%')

                sock.send('moved%'.encode())
                information_sent('Информация отправлена', 'moved%')
                mortgage_btn_check()

                buy_btn_check()
                pay_btn_check()


def move(players_on_tile, end_positions, cube_sum):
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

    if not optimized:
        step_amount = round(distance * cube_speed * 75 * speed)
        sleep_seconds = cube_speed * 3.3 * speed
    else:
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
            player.x = sx + (ex - sx) * t
            player.y = sy + (ey - sy) * t
            player.player_piece_rect = player.player_piece.get_rect(center=(player.x, player.y))

        time.sleep(0.01)


def handle_connection():
    global players, all_tiles, avatar_file, cube_1_picture, cube_2_picture, receive_size, image_messages


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


    buffer = ''
    while running:
        time.sleep(ideal_dt)
        if game_started:
            if state['connected']:
                try:
                    data_unsplit = sock.recv(receive_size).decode().replace('[1foe_S]', '')
                    buffer += data_unsplit

                    while '%' in buffer:
                        single_command, buffer = buffer.split('%', 1)
                        data = single_command.split('|')

                        if data[0] != '':

                            if data[0] not in ['avatar', 'sound message', 'voice message']:
                                information_received('Информация получена', data)

                            if data[0] == 'color main':
                                for allPlayer in all_players:
                                    if allPlayer.color == data[1]:
                                        allPlayer.main_color(data[1])

                            elif data[0] == 'avatar':
                                state['avatar_chosen'] = True
                                avatar = data[2]
                                image_bytes_ascii_decoded = avatar.encode("ascii")
                                image_bytes_decoded = base64.b64decode(image_bytes_ascii_decoded)
                                image_decoded = Image.open(io.BytesIO(image_bytes_decoded))
                                image_decoded = image_decoded.resize((avatar_side_size, avatar_side_size))
                                image_bytes = io.BytesIO()
                                image_decoded.save(image_bytes, format='PNG')
                                image_bytes.seek(0)
                                try:
                                    for i, player in enumerate(players):
                                        if player.color == data[1]:
                                            player.avatar = pg.image.load(image_bytes).convert_alpha()
                                            state['avatar_chosen'] = False
                                            update_list_dynamic.append(pg.Rect(profile_coordinates[i]['avatar'], (avatar_side_size, avatar_side_size)))
                                except:
                                    image_decoded.save('error.png')
                                    print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')
                                    print('an error has occurred. avatar image saved inside main folder')

                            elif data[0] == 'move':
                                for player in players:
                                    if player.main and player.color == data[1]:
                                        state['double'] = data[2] == data[3]
                                move_by_cubes(int(data[2]), int(data[3]), data[1])

                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'move diagonally':
                                for player in players:
                                    if player.color == data[1]:
                                        new_position = int(data[2])
                                        player.piece_position = new_position
                                        players_on_tile = []
                                        for player2 in players:
                                            if player2.piece_position == new_position:
                                                players_on_tile.append(player2)
                                        end_positions = []
                                        for player3 in players_on_tile:
                                            end_positions.append((all_tiles[player3.piece_position].x_center + margin[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                                                  all_tiles[player3.piece_position].y_center + margin[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))

                                        move([player], end_positions, 10)

                                        position_update()
                                        pay_btn_check()
                                        buy_btn_check()
                                        mortgage_btn_check()
                                        redeem_btn_check()

                            elif data[0] == 'playersData':
                                globals()[f'{data[1]}_profile'] = pg.image.load(f'resources/{resolution_folder}/profile/{data[1]}_profile.png').convert_alpha()
                                globals()[f'{data[1]}_property_image'] = pg.image.load(f'resources/{resolution_folder}/property/{data[1]}_property.png').convert_alpha()
                                for allPlayer in all_players:
                                    for i in data:
                                        if i == allPlayer.color:
                                            if allPlayer not in players:
                                                players.append(allPlayer)
                                for i, player in enumerate(players):
                                    if player.color == data[1]:
                                        player.money = int(data[2])
                                        player.piece_position = int(data[3])
                                        player.name = data[4]

                                position_update()
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'property':
                                for player in players:
                                    if data[1] == player.color:
                                        tile_position = int(data[2])
                                        all_tiles[tile_position].owner = data[1]
                                        all_tiles[tile_position].owned = True
                                        all_tiles[tile_position].family_members += 1
                                        price_update(all_tiles[tile_position])
                                        buy_btn_check()
                                    if player.main:
                                        if int(data[2]) == player.piece_position:
                                            state['paid'] = True
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'money':
                                for i, player in enumerate(players):
                                    if data[1] == player.color:
                                        player.money = int(data[2])
                                        update_list_dynamic.append(profile_picture.get_rect(topleft=profile_coordinates[i]['profile']))
                                        if not state['egg_btn_active'] or not state['eggs_btn_active']:
                                            pay_btn_check()
                                        buy_btn_check()
                                        mortgage_btn_check()
                                        redeem_btn_check()

                            elif data[0] == 'playerDeleted':
                                for player in players:
                                    if player.color == data[1]:
                                        players.remove(player)

                            elif data[0] == 'gameStarted':
                                state['is_game_started'] = True
                                players_queue = data[1].split('_')
                                players_temp = []
                                for new_color in players_queue:
                                    for player in players:
                                        if player.color == new_color:
                                            players_temp.append(player)
                                players = players_temp

                                for player in players:
                                    globals()[f'{player.color}_player_button'] = pygame_gui.elements.UIButton(
                                        relative_rect=pg.Rect(profile_coordinates[players.index(player)]['avatar'], (avatar_side_size, avatar_side_size)),
                                        text='',
                                        manager=manager,
                                        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons'))
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'onMove':
                                for player in players:
                                    if player.color == data[1]:
                                        player.on_move = True

                                        if player.main:
                                            if len(players) > 1 and not player.imprisoned:
                                                state['exchange_btn_active'] = True

                                            state['throw_cubes_btn_active'] = True
                                            mortgage_btn_check()
                                            redeem_btn_check()

                                            if player.imprisoned:
                                                state['pay_btn_active'] = ['prison']

                                            for tile in all_tiles:
                                                if tile.full_family and tile.owner == player.color and tile.type == 'buildable':
                                                    if not player.imprisoned:
                                                        state['penis_build_btn_active'] = True
                                                    if 1 <= tile.penises <= 5:
                                                        state['penis_remove_btn_active'] = True

                                        else:
                                            player.on_move = False
                                            state['throw_cubes_btn_active'] = False
                                            state['exchange_btn_active'] = False
                                            state['penis_remove_btn_active'] = False
                                            state['pay_btn_active'] = ['False']
                                            mortgage_btn_check()
                                            redeem_btn_check()

                            elif data[0] == 'error':
                                print(f'Ошибка: {"\033[31m{}".format(data[1])}{'\033[0m'}')
                                state['avatar_chosen'] = False

                            elif data[0] == 'imprisoned':
                                for i, player in enumerate(players):
                                    if data[1] == player.color:
                                        player.imprisoned = True
                                        player.piece_position = 10
                                        pay_btn_check()
                                        mortgage_btn_check()
                                        redeem_btn_check()

                            elif data[0] == 'unimprisoned':
                                for i, player in enumerate(players):
                                    if data[1] == player.color:
                                        player.imprisoned = False
                                        update_list_dynamic.append(profile_picture.get_rect(topleft=profile_coordinates[i]['profile']))
                                if len(data) > 2:
                                    state['double'] = data[2] == data[3]
                                    move_by_cubes(int(data[2]), int(data[3]), data[1])
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'penis built':
                                tile_position = int(data[1])
                                all_tiles[tile_position].penises += 1
                                all_tiles[tile_position].text_defining(font)
                                for tile in all_tiles:
                                    if tile.family == all_tiles[tile_position].family:
                                        tile.penised_family = True
                                mortgage_btn_check()
                                redeem_btn_check()

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
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'bribe':
                                for player in players:
                                    if player.color == data[1]:
                                        if player.main:
                                            state['throw_cubes_btn_active'] = False
                                            state['pay_btn_active'] = ['prison']
                                            mortgage_btn_check()
                                            redeem_btn_check()

                            elif data[0] == 'imprisoned double failed':
                                show_cubes(data[2], data[3])

                                mortgage_btn_check()
                                redeem_btn_check()

                                print(f'У игрока {data[1]} осталось {3 - int(data[4])} попытки чтобы выйти из тюрьмы')

                            elif data[0] == 'all property':
                                for player in players:
                                    if player.color == data[1]:
                                        new_property = data[2].split('_')
                                        for i in new_property:
                                            tile = int(i)
                                            all_tiles[tile].owner = data[1]
                                            price_update(all_tiles[tile])
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'exchange request':
                                global exchange_value
                                get_data = data[1].split('_')
                                give_data = data[2].split('_')
                                give_money = int(give_data[0])
                                get_money = int(get_data[0])
                                give_property = give_data[1].split('-')
                                get_property = get_data[1].split('-')
                                color = data[3]

                                value_give = 0
                                value_get = 0
                                for give_tile in give_property:
                                    try:
                                        value_give += int(all_tiles[int(give_tile)].price) / 2
                                    except:
                                        pass
                                value_give += give_money

                                for get_tile in get_property:
                                    try:
                                        value_get += int(all_tiles[int(get_tile)].price) / 2
                                    except:
                                        pass
                                value_get += get_money
                                exchange_value = round((value_get - value_give) * 100 / max(value_give, value_get))

                                state['show_exchange_request_screen'] = [True, give_money, give_property, get_money,
                                                                         get_property, color]
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
                                mortgage_btn_check()
                                for player in players:
                                    if player.main:
                                        for tile in all_tiles:
                                            if tile.full_family and tile.owner == player.color and tile.type == 'buildable':
                                                if 1 <= tile.penises <= 5:
                                                    state['penis_remove_btn_active'] = True

                                if len(players) > 1:
                                    state['exchange_btn_active'] = True

                            elif data[0] == 'mortgaged':
                                all_tiles[int(data[1])].mortgaged = True
                                all_tiles[int(data[1])].mortgaged_moves_count = 15
                                for tile in all_tiles:
                                    if tile.family == all_tiles[int(data[1])].family:
                                        tile.family_members -= 1
                                        tile.text_defining(font)

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

                            elif data[0] == 'need to pay':
                                for player in players:
                                    if player.main:
                                        for tile in all_tiles:
                                            if tile.full_family and tile.owner == player.color and tile.type == 'buildable':
                                                if 1 <= tile.penises <= 5:
                                                    state['penis_remove_btn_active'] = True

                                if len(players) > 1:
                                    state['exchange_btn_active'] = True

                                mortgage_btn_check()

                                state['pay_btn_active'] = ['pay sum', int(data[1])]

                            elif data[0] == 'need to pay to player':
                                global pulled_card_strings
                                for player in players:
                                    if player.main:
                                        for tile in all_tiles:
                                            if tile.full_family and tile.owner == player.color and tile.type == 'buildable':
                                                if 1 <= tile.penises <= 5:
                                                    state['penis_remove_btn_active'] = True

                                if len(players) > 1:
                                    state['exchange_btn_active'] = True

                                mortgage_btn_check()

                                state['pay_btn_active'] = ['player', data[1], int(data[2])]
                                if state['egg_btn_active'] or state['eggs_btn_active']:
                                    for player in players:
                                        if player.color == data[1]:
                                            for i in pulled_card_strings:
                                                i.replace('{player_name}', player.name)

                            elif data[0] == 'need to pay to players':
                                for player in players:
                                    if player.main:
                                        for tile in all_tiles:
                                            if tile.full_family and tile.owner == player.color and tile.type == 'buildable':
                                                if 1 <= tile.penises <= 5:
                                                    state['penis_remove_btn_active'] = True

                                if len(players) > 1:
                                    state['exchange_btn_active'] = True

                                mortgage_btn_check()

                                state['pay_btn_active'] = ['players', int(data[1])]

                            elif data[0] == 'pulled card position':
                                global pulled_card_text,  pulled_card_title, pulled_card_title_rect
                                if data[2] == 'Яйцо':
                                    pulled_card_title = egg_font.render('Вопросительное яйцо', False, 'black')
                                    pulled_card_title_rect = pulled_card_title.get_rect(center=egg_card_title_center)
                                    state['egg_btn_active'] = True
                                    egg_card_position = int(data[3])
                                    pulled_card_strings = []
                                    text = all_egg[egg_card_position].description
                                    if '{value}' in text:
                                        text = text.replace('{value}', f'{all_egg[egg_card_position].value}')
                                    if '{tile_name}' in text:
                                        text = text.replace('{tile_name}', all_tiles[all_egg[egg_card_position].value].name)
                                    if '{player_name}' in text:
                                        for player in players:
                                            if player.color == data[1]:
                                                text = text.replace('{player_name}', player.name)
                                    text = text.split(' ')

                                elif data[2] == 'Яйца':
                                    pulled_card_title = egg_font.render('Груда вопросительных яиц', False, 'black')
                                    pulled_card_title_rect = pulled_card_title.get_rect(center=egg_card_title_center)
                                    state['eggs_btn_active'] = True
                                    egg_card_position = int(data[3])
                                    pulled_card_strings = []
                                    text = all_eggs[egg_card_position].description
                                    if '{value}' in text:
                                        text = text.replace('{value}', f'{all_eggs[egg_card_position].value}')
                                    if '{tile_name}' in text:
                                        text = text.replace('{tile_name}', all_tiles[all_eggs[egg_card_position].value].name)
                                    if '{player_name}' in text:
                                        for player in players:
                                            if player.color == data[1]:
                                                text = text.replace('{player_name}', player.name)
                                    text = text.split(' ')

                                while text:
                                    text_new = []
                                    while egg_font.size(' '.join(text_new))[0] <= egg_card_text_width and text:
                                        text_new.append(text[0])
                                        text.pop(0)
                                    text.insert(0, text_new[-1])
                                    text_new.pop(-1)
                                    pulled_card_strings.append(' '.join(text_new))
                                    if egg_font.size(' '.join(text))[0] <= egg_card_text_width:
                                        pulled_card_strings.append(' '.join(text))
                                        text.clear()

                            elif data[0] == 'show cubes':
                                show_cubes(data[1], data[2])

                            elif data[0] == 'free prison escape card':
                                for player in players:
                                    if player.color == data[2]:
                                        if player.main:
                                            if data[1] == 'Яйцо':
                                                player.egg_prison_exit_card = True
                                                exit_prison_egg_btn.show()
                                            else:
                                                player.eggs_prison_exit_card = True
                                                exit_prison_eggs_btn.show()

                            elif data[0] == 'message':
                                log_textbox.append_html_text(data[1].replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)

                            elif data[0] == 'mortgaged_moves_count':
                                all_tiles[int(data[1])].mortgaged_moves_count = int(data[2])

                            elif data[0] == 'sound message':
                                # sound_buffer.append(data[2])
                                audio_bytes_ascii_decoded = data[2]
                                audio_bytes_decoded_base64 = base64.b64decode(audio_bytes_ascii_decoded)
                                audio_bytes_decoded = zlib.decompress(audio_bytes_decoded_base64)

                                sound_id = data[1]
                                sound_messages[f'{sound_id}'] = audio_bytes_decoded
                                receive_size = 1024

                            elif data[0] == 'voice message':
                                audio_bytes_ascii_decoded = data[2]
                                audio_bytes_decoded_base64 = base64.b64decode(audio_bytes_ascii_decoded)
                                audio_bytes_decoded = zlib.decompress(audio_bytes_decoded_base64)

                                sound_id = data[1]
                                voice_messages[f'{sound_id}'] = audio_bytes_decoded
                                receive_size = 1024

                            elif data[0] == 'image message':
                                if not os.path.exists(f'resources/temp/images/client image messages'):
                                    if not os.path.exists('resources/temp/images'):
                                        if not os.path.exists('resources/temp'):
                                            os.mkdir('resources/temp')
                                        os.mkdir('resources/temp/images')
                                    os.mkdir(f'resources/temp/images/client image messages')

                                image_bytes_decoded = base64.b64decode(data[2])
                                image_decoded = Image.open(io.BytesIO(image_bytes_decoded))
                                image_decoded = image_decoded.resize(log_image_size)
                                image_decoded.save(f'resources/temp/images/client image messages/{image_messages}.png')
                                image_messages += 1

                            elif data[0] == 'receive size':
                                receive_size = int(data[1])

                            else:
                                print(f'Ошибка: {"\033[31m{}".format(f'Незарегистрированная команда на стороне клиента: {data[0]}')}{'\033[0m'}')

                            active_buttons_check()

                        if not running:
                            break
                except OSError:
                    pass
                except:
                    print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def delta_time(old_time):
    now = time.time()
    dt = now - old_time
    old_time = now
    return dt, old_time


def event_handler():
    global color_picker

    events = pg.event.get()
    for event in events:
        # print(event)
        if event.type == pg.QUIT:
            global running
            running = False

        elif event.type == pg.MOUSEBUTTONUP:
            if state['egg_btn_active']:
                egg_s_reset()
            elif state['eggs_btn_active']:
                egg_s_reset()
            elif state['tile_info_show'][0]:
                tile_info_reset()

            elif event.type == pg.KEYUP and debug_mode and not optimized:
                if not ip_textbox.is_focused and not port_textbox.is_focused and not name_textbox.is_focused and not exchange_give_textbox.is_focused and not exchange_get_textbox.is_focused and not log_entry_textbox.is_focused:
                    if event.key == pg.K_c:
                        connect()
                    elif event.key == pg.K_d:
                        debug_output()
                elif name_textbox.is_focused:
                    if event.key == pg.K_RETURN:
                        connect()
                elif log_entry_textbox.is_focused:
                    if event.key == pg.K_RETURN:
                        send_message()

            elif event.type == pg.WINDOWRESTORED or event.type == pg.WINDOWMOVED:
                update_list_dynamic.append(pg.Rect((0, 0), resolution))

        manager_initiated = False
        while not manager_initiated:
            try:
                manager.process_events(event)
                manager_initiated = True
            except:
                print(f'{"\033[32m{}".format(f'Не беспокойтесь. Эта ошибка не вредит игре:\n{traceback.format_exc()}')}{'\033[0m'}')

        if game_started:
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
                        choose_avatar()
                    elif event_type == connect_button:
                        connect()
                    elif event_type == debug_button:
                        debug_output()
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
                        send_audio()
                    elif event_type == log_voice_message_send_button:
                        send_voice_message()
                    elif event_type == log_image_send_button:
                        send_image()
                    else:
                        if state['is_game_started']:
                            for player in players:
                                if event_type == globals()[f'{player.color}_player_button']:
                                    player_button(player.color)
                        for i in range(40):
                            if event_type == globals()[f'tile_{i}_button']:
                                tile_button(i)
    
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
    
                case pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
                    try:
                        if event.link_target.startswith('sound:'):
                            audio_id = event.link_target.split(':')[1]
                            sound = pg.mixer.Sound(io.BytesIO(sound_messages[audio_id]))
    
                            if sound_messages_channel.get_busy() and sound_messages_channel.audio_id == audio_id and sound_messages_channel.is_paused:
                                sound_messages_channel.unpause()
                            else:
                                if sound_messages_channel.audio_id != audio_id:
                                    sound_messages_channel.play(sound, audio_id)
                                else:
                                    sound_messages_channel.pause()
    
                        elif event.link_target.startswith('voice:'):
                            audio_id = event.link_target.split(':')[1]
                            sound = pg.mixer.Sound(voice_messages[audio_id])
    
                            if voice_messages_channel.get_busy() and voice_messages_channel.audio_id == audio_id and voice_messages_channel.is_paused:
                                voice_messages_channel.unpause()
                            else:
                                if voice_messages_channel.audio_id != audio_id or not voice_messages_channel.get_busy():
                                    voice_messages_channel.play(sound, audio_id)
                                else:
                                    voice_messages_channel.pause()
    
                        elif event.link_target.startswith('save sound:'):
                            audio_id = event.link_target.split(':')[1]
                            mimetype = magic.from_buffer(sound_messages[audio_id], mime=True)
                            extension = mimetypes.guess_extension(mimetype)#[0]
    
                            with open(f'sound_message_{audio_id}{extension}', 'wb') as audio_file:
                                audio_file.write(sound_messages[audio_id])
    
                            log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#000000">Файл сохранён: sound_message_{audio_id}{extension}</font><br>')
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
    
                        elif event.link_target.startswith('save voice:'):
                            audio_id = event.link_target.split(':')[1]
                            extension = '.wav'
                            with wave.open(f'voice_message_{audio_id}{extension}', 'wb') as audio_file:
                                audio_file.setnchannels(1)
                                audio_file.setsampwidth(2)
                                audio_file.setframerate(44100)
                                audio_file.writeframes(voice_messages[audio_id])
    
                            log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#000000">Файл сохранён: voice_message_{audio_id}{extension}</font><br>')
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
    
                    except:
                        print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')

        else:
            match event.type:
                case pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_game_button:
                        save_settings()
                        monopoly_init()
                        load_assets()
                        load_game()
                    elif event.ui_element == pick_color_button:
                        color_picker.show()
                    elif event.ui_element == apply_button:
                        save_settings()
                        monopoly_init()
                        load_assets()

                case pygame_gui.UI_CHECK_BOX_CHECKED:
                    if event.ui_element == fullscreen_checkbox:
                        sharp_scale_checkbox.enable()

                case pygame_gui.UI_CHECK_BOX_UNCHECKED:
                    if event.ui_element == fullscreen_checkbox:
                        sharp_scale_checkbox.disable()
                        sharp_scale_checkbox.set_state(False)

                case pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    resolution_to_index = {'1280x720': 1,
                                           '1920x1080': 2,
                                           '2560x1440': 3}
                    settings_data['resolution index'] = resolution_to_index[event.text]

                case pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                    if event.ui_element == color_picker:
                        settings_data['background color converted'] = event.colour
                        settings_data['background color'] = list(event.colour)
                        color_picker.kill()
                        color_picker = pygame_gui.windows.UIColourPickerDialog(
                            rect=pg.Rect(60, 120, 390, 390),
                            initial_colour=settings_data['background color converted'],
                            manager=manager,
                            visible=0)


def player_move_change(do_change):
    for player in players:
        if player.main:
            next_player_command = f'nextPlayer|{do_change}%'
            sock.send(next_player_command.encode())
            information_sent('Команда отправлена', next_player_command)


def buttons():
    global cube_button, buy_button, pay_button, name_textbox, ip_textbox, port_textbox, connect_button, debug_button, avatar_choose_button, shove_penis_button, remove_penis_button, exchange_button, exchange_commit_button, exchange_cancel_button, exchange_give_textbox, exchange_get_textbox, exchange_request_confirm_button, exchange_request_reject_button, auction_button, auction_buy_button, auction_reject_button, mortgage_button, redeem_button, exit_prison_egg_btn, exit_prison_eggs_btn, log_textbox, log_entry_textbox, log_text_send_button, log_audio_send_button, log_voice_message_send_button, log_image_send_button, message_panel

    cube_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['throw_cubes']),
        text='Бросить кубы',
        manager=manager)

    buy_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['buy']),
        text='Купить',
        manager=manager)

    pay_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['pay']),
        text='Оплатить',
        manager=manager)

    shove_penis_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['shove_penis']),
        text='Сунуть пЭнис',
        manager=manager)

    remove_penis_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['remove_penis']),
        text='Убрать пЭнис',
        manager=manager)

    exchange_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['exchange']),
        text='Обмен',
        manager=manager)

    auction_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['auction']),
        text='Аукцион',
        manager=manager)

    mortgage_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['mortgage']),
        text='Заложить',
        manager=manager)

    redeem_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(btn_coordinates['redeem']),
        text='Выкупить',
        manager=manager)

    print(name)
    name_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['name']),
        placeholder_text='Введите имя',
        initial_text=name,
        manager=manager)

    ip_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['IP']),
        placeholder_text='IP адрес',
        initial_text=address,
        manager=manager)

    port_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['port']),
        placeholder_text='Порт',
        initial_text=port,
        manager=manager)

    avatar_choose_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['choose_avatar']),
        text='Выбрать аватар',
        manager=manager)

    connect_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['connect']),
        text='Подключиться',
        manager=manager)

    debug_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['debug']),
        text='debug',
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
        relative_rect=pg.Rect(egg_btns_coordinates['egg']),
        text='',
        visible=False,
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#egg_button'),
        manager=manager)

    exit_prison_eggs_btn = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(egg_btns_coordinates['eggs']),
        text='',
        visible=False,
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#eggs_button'),
        manager=manager)

    log_textbox = pygame_gui.elements.UITextBox(
        relative_rect=pg.Rect(log_textbox_coordinates['main_box']),
        html_text='',
        manager=manager)
    # log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#000000">иконка монополии: </font><img src="resources/icon.png" align="center" width="128" height="128"><br>')

    log_entry_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(log_textbox_coordinates['user_input_box']),
        placeholder_text='',
        manager=manager)

    log_text_send_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(log_textbox_coordinates['text_send_button']),
        text='',
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#text_send_button'),
        manager=manager)
    log_text_send_button.disable()

    log_audio_send_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(log_textbox_coordinates['audio_send_button']),
        text='',
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#audio_send_button'),
        manager=manager)
    log_audio_send_button.disable()

    log_voice_message_send_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(log_textbox_coordinates['voice_message_send_button']),
        text='',
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#voice_message_send_button'),
        manager=manager)
    log_voice_message_send_button.disable()

    log_image_send_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(log_textbox_coordinates['image_send_button']),
        text='',
        object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#image_send_button'),
        manager=manager)
    log_image_send_button.disable()

    message_panel = pygame_gui.elements.UIPanel(relative_rect=pg.Rect(tile_info_coordinates, tile_info_coordinates),
                                                manager=manager,
                                                visible=False)

    # time_bar = pygame_gui.elements.UIStatusBar(relative_rect=pg.Rect(676, 66, 148, 12),
    #                                            manager=manager)
    # print(time_bar.status_text())
    for i in range(40):
        globals()[f'tile_{i}_button'] = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((all_tiles[i].x_position, all_tiles[i].y_position), tile_size),
            text='',
            manager=manager,
            object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#tile_button'))

    if not debug_mode:
        debug_button.hide()


def show_cubes(cube1, cube2):
    global cube_1_picture, cube_2_picture, state
    cube_1_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{cube1}.png').convert()
    cube_2_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{cube2}.png').convert()

    state['cube_animation_playing'] = True
    time.sleep(1.5)
    state['cube_animation_playing'] = False


# Проверки
# |
# V


def allowed_characters_check(text, allowed_characters):
    new_text = text
    for character in text:
        if character not in allowed_characters:
            new_text = new_text.replace(character, '')
    return new_text


def forbidden_characters_check(text, forbidden_characters):
    new_text = text
    for character in text:
        if character in forbidden_characters:
            new_text = new_text.replace(character, '')
    return new_text


def name_check():
    name = name_textbox.get_text()
    name = forbidden_characters_check(name, ['|', '%', '[1foe_S]', '\n'])
    while font.size(name)[0] >= profile_picture.width - 10:
        name = name[:-1]
    if name_textbox.get_text() != name:
        name_textbox.set_text(name)


def log_entry_check():
    log_text = log_entry_textbox.get_text()
    log_text = forbidden_characters_check(log_text, ['|', '%', '[1foe_S]', '\n'])
    if log_entry_textbox.get_text() != log_text:
        log_entry_textbox.set_text(log_text)


def active_buttons_check():
    # Бросок кубов
    if not state['is_game_started'] or not state['throw_cubes_btn_active']:
        cube_button.disable()
    else:
        cube_button.enable()

    # Купить
    if not state['is_game_started'] or not state['buy_btn_active']:
        buy_button.disable()
    else:
        buy_button.enable()

    # Аукцион
    if not state['is_game_started'] or not state['auction_btn_active']:
        auction_button.disable()
    else:
        auction_button.enable()

    # Оплатить
    if not state['is_game_started'] or state['pay_btn_active'][0] == 'False':
        pay_button.disable()
    else:
        pay_button.enable()

    # Сунуть пЭнис
    if not state['is_game_started'] or not state['penis_build_btn_active']:
        shove_penis_button.disable()
    else:
        shove_penis_button.enable()

    # Убрать пЭнис
    if not state['is_game_started'] or not state['penis_remove_btn_active'] or state['penis_remove_btn_used']:
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


def pay_btn_check():
    if state['is_game_started']:
        for player in players:
            if player.main:
                if player.imprisoned and player.on_move:
                    state['pay_btn_active'] = ['prison']
                    mortgage_btn_check()
                elif not state['paid']:
                    if (player.piece_position == 4 or player.piece_position == 38) and player.money >= -all_tiles[player.piece_position].income:
                        state['pay_btn_active'] = ['minus']
                        state['paid'] = True
                        mortgage_btn_check()
                    else:
                        if all_tiles[player.piece_position].owner != player.color and all_tiles[player.piece_position].owned and not all_tiles[player.piece_position].mortgaged and player.money >= all_tiles[player.piece_position].penis_income_calculation() and all_tiles[player.piece_position].type != 'infrastructure':
                            state['pay_btn_active'] = ['color', all_tiles[player.piece_position].owner]
                            mortgage_btn_check()
                            state['paid'] = True
                        else:
                            if state['pay_btn_active'][0] not in ('pay sum', 'player', 'players'):
                                state['pay_btn_active'] = ['False']
                                mortgage_btn_check()
                print(f'Состояние pay_btn_active установлено на {state['pay_btn_active']}')
                if state['pay_btn_active'][0] not in ('False', 'prison') or player.on_move:
                    if len(players) > 1:
                        state['exchange_btn_active'] = True
                else:
                    state['exchange_btn_active'] = False


def buy_btn_check():
    global players
    for player in players:
        if player.main:
            if all_tiles[player.piece_position].buyable:
                if not state['refused_to_buy']:
                    if not all_tiles[player.piece_position].owned:
                        if player.money >= int(all_tiles[player.piece_position].price):
                            state['buy_btn_active'] = True
                        else:
                            state['buy_btn_active'] = False
                        # print(f'Состояние buy_btn_active установлено на {state['buy_btn_active']}')
                        state['auction_btn_active'] = True
                    else:
                        state['auction_btn_active'] = False
                        state['buy_btn_active'] = False

    # if state['buy_btn_active']:
    #     if len(players) > 1:
    #         state['exchange_btn_active'] = True
    # else:
    #     state['exchange_btn_active'] = False


def mortgage_btn_check():  # заложить
    if state['is_game_started']: # and (state['buy_btn_active'] or state['pay_btn_active'][0] != 'False' or state['throw_cubes_btn_active']):
        for player in players:
            if player.main:
                if player.on_move or state['buy_btn_active'] or state['pay_btn_active'][0] != 'False' or state['show_auction_screen'][0] or (all_tiles[player.piece_position].owner != player.color and all_tiles[player.piece_position].owned):
                    state['mortgage_btn_active'] = False
                    for tile in all_tiles:
                        if tile.owner == player.color:
                            if tile.penises <= 0 and not tile.mortgaged:
                                state['mortgage_btn_active'] = True

                elif all_tiles[player.piece_position].buyable and not state['refused_to_buy']: # если нельзя купить, то можно заложить
                    if not all_tiles[player.piece_position].owned:                             # Я честно не понимаю, что я имел в виду
                        state['mortgage_btn_active'] = True
                    else:
                        state['mortgage_btn_active'] = False

                else:
                    state['mortgage_btn_active'] = False
    redeem_btn_check()
                # print(f'Состояние mortgage_btn_active установлено на {state['mortgage_btn_active']}')


def redeem_btn_check():  # выкупить
    state['redeem_btn_active'] = False
    if state['is_game_started']:

        for tile in all_tiles:
            if tile.mortgaged:

                for player in players:
                    if player.main:
                        if player.on_move:
                            if player.color == tile.owner:
                                if player.money >= tile.price / 2 * 1.1:
                                    state['redeem_btn_active'] = True


running = True
game_started = False

monopoly_init()

past_second_fps = []
prev_fps_time = time.time()
average_fps = 0
all_fps = []

while running and not game_started:
    clock.tick(FPS)
    dt, prev_time = delta_time(prev_time)
    screen.fill(settings_data['background color converted'])
    event_handler()

    screen.blit(settings_font.render('Введите максимальный FPS:', False, 'black'), settings_buttons_coordinates['fps_text'])
    screen.blit(settings_font.render('Оптимизация движения:', False, 'black'), settings_buttons_coordinates['optimization_text'])
    screen.blit(settings_font.render('debug mode:', False, 'black'), settings_buttons_coordinates['debug_text'])
    screen.blit(settings_font.render('Полноэкранный режим:', False, 'black'), settings_buttons_coordinates['fullscreen_text'])
    screen.blit(settings_font.render('Чёткое растяжение экрана:', False, 'black'), settings_buttons_coordinates['sharp_scale_text'])

    try:
        manager.update(dt)
        manager.draw_ui(screen)
    except:
        pass

    pg.display.flip()

gc.collect()

while running:
    clock.tick(FPS)
    dt, prev_time = delta_time(prev_time)
    screen.fill(background_color)
    event_handler()
    blit_board()
    price_printing()
    try:
        manager.update(dt)
        manager.draw_ui(screen)
    except:
        pass
    blit_board_above_interface()

    average_fps = clock.get_fps()
    all_fps.append(average_fps)
    average_fps_text = font.render(str(round(average_fps)), False, 'black')
    screen.blit(average_fps_text, fps_coordinates)

    pg.display.update()#update_list_static + update_list_dynamic

if os.path.exists(f'resources/temp/images/client image messages'):
    for file in os.listdir('resources/temp/images/client image messages'):
        os.remove(f'resources/temp/images/client image messages/{file}')

print('\nПрограмма завершена')
if all_fps:
    print(f'Средний FPS: {sum(all_fps) / len(all_fps)}')
