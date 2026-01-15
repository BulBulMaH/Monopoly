# для прочего
import time
time_for_loading = time.time()
import os
import traceback
import gc
import pprint
os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (0, 31) # (0, 30)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# для функционала игры
import pygame as pg
import socket as sck
import threading
import math

# для аватара
import io
from PIL import Image
import base64
import tkinter
import tkinter.filedialog

# для интерфейса
import pygame_gui

# классы
from Players_Class_Client_side import Player

# функции
from all_tiles_extraction import all_tiles_get
from colored_output import thread_open, information_sent, information_received, new_connection
from resolution_choice import resolution_definition

pg.init()
pg.mixer.init()  # для звука

resolution, resolution_folder, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, FPS, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates, font_size, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_font_size, egg_card_text_width, egg_btns_coordinates, optimized = resolution_definition(True)

TITLE = 'Monopoly v0.13'
icon = pg.image.load(f'resources/icon.png')
pg.display.set_icon(icon)
screen = pg.display.set_mode(resolution, pg.DOUBLEBUF)
manager = pygame_gui.UIManager(resolution, theme_path=f'resources/{resolution_folder}/gui_theme.json', enable_live_theme_updates=False)
pg.display.set_caption(TITLE)
clock = pg.time.Clock()
prev_time = time.time()
gc.enable()


def load_assets():
    global exchange_screen, auction_screen, darkening_full, darkening_tile, profile_picture, bars, player_bars, avatar_file, mortgaged_tile, font, eggs_card_uncovered, egg_font, board_image
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
    font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', font_size)
    egg_font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', egg_font_size)

    for penis in range(5):
        globals()[f'{penis + 1}_penises_image'] = pg.image.load(f'resources/{resolution_folder}/white penises/{penis + 1}.png').convert_alpha()

    global all_tiles, positions, all_players, players, exchange_value, exchange_color, state, sock, all_egg, all_eggs, update_list_static, update_list_dynamic, CLEAR_UPDATE_LIST
    property_family_count = {}
    all_tiles, positions, all_egg, all_eggs = all_tiles_get(resolution_folder, tile_size)
    for tile in all_tiles:
        tile.text_defining(font)
        if tile.buyable:
            property_family_count[tile.family] = 0

    board_image = pg.image.load(f'resources/temp/images/{resolution_folder}/board image.png').convert()

    all_players = [Player('red',    (all_tiles[0].x_center, all_tiles[0].y_center), resolution_folder, property_family_count),
                   Player('blue',   (all_tiles[0].x_center, all_tiles[0].y_center), resolution_folder, property_family_count),
                   Player('yellow', (all_tiles[0].x_center, all_tiles[0].y_center), resolution_folder, property_family_count),
                   Player('green',  (all_tiles[0].x_center, all_tiles[0].y_center), resolution_folder, property_family_count)]
    players = []
    exchange_value = -100
    exchange_color = ''
    state = {'throw_cubes_btn_active': False,
             'buy_btn_active': False,
             'pay_btn_active': ['False'],
             'penis_build_btn_active': False,
             'penis_remove_btn_active': False,
             'mortgage_btn_active': False,
             'redeem_btn_active': False,
             'auction_btn_active': False,

             'penis_remove_btn_used': False,
             'all_penises_build_btns_active': False,
             'all_penises_remove_btns_active': False,
             'mortgage_tile_btn_active': False,
             'redeem_tile_btn_active': False,
             'exchange_btn_active': False,
             'exchange_player_btn_active': False,
             'exchange_tile_btn_active': False,
             'show_exchange_screen': False,
             'show_exchange_request_screen': [False],
             'is_game_started': False,
             'ready': False,
             'connected': False,
             'double': False,
             'paid': False,
             'avatar_chosen': False,
             'cube_animation_playing': False,
             'tile_debug': False,
             'show_auction_screen': [False],
             'egg_btn_active': False,
             'eggs_btn_active': False}

    cube_1_picture = pg.image.load(f'resources/{resolution_folder}/cubes/1.png').convert()
    update_list_static = [
    pg.Rect(btn_coordinates['throw_cubes']),
    pg.Rect(btn_coordinates['buy']),
    pg.Rect(btn_coordinates['pay']),
    pg.Rect(btn_coordinates['shove_penis']),
    pg.Rect(btn_coordinates['remove_penis']),
    pg.Rect(btn_coordinates['exchange']),
    pg.Rect(btn_coordinates['auction']),
    pg.Rect(btn_coordinates['mortgage']),
    pg.Rect(btn_coordinates['redeem']),

    pg.Rect(start_btn_textboxes_coordinates['name']),
    pg.Rect(start_btn_textboxes_coordinates['IP']),
    pg.Rect(start_btn_textboxes_coordinates['port']),
    pg.Rect(start_btn_textboxes_coordinates['choose_avatar']),
    pg.Rect(start_btn_textboxes_coordinates['connect']),
    pg.Rect(start_btn_textboxes_coordinates['debug']),

    pg.Rect(exchange_coordinates['button']),
    pg.Rect(exchange_coordinates['textbox_give']),
    pg.Rect(exchange_coordinates['textbox_get']),
    pg.Rect(exchange_coordinates['confirm']),
    pg.Rect(exchange_coordinates['reject']),

    pg.Rect(auction_coordinates['confirm']),
    pg.Rect(auction_coordinates['reject']),

    pg.Rect(egg_btns_coordinates['egg']),
    pg.Rect(egg_btns_coordinates['eggs']),

    pg.Rect(fps_coordinates, (50, 50)),
    board_image.get_rect(),
    cube_1_picture.get_rect(topleft=cubes_coordinates[0]),
    cube_1_picture.get_rect(topleft=cubes_coordinates[1])]

    update_list_dynamic = [pg.Rect((0, 0), resolution)]
    CLEAR_UPDATE_LIST = pg.event.custom_type()
    pg.time.set_timer(CLEAR_UPDATE_LIST, 1000)

    sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)
    buttons()
    theme = manager.create_new_theme(f'resources/{resolution_folder}/gui_theme.json')
    manager.set_ui_theme(theme)
    pg.event.set_allowed([pg.QUIT, pg.KEYUP, pg.MOUSEBUTTONUP, pygame_gui.UI_BUTTON_PRESSED, pygame_gui.UI_TEXT_ENTRY_CHANGED, CLEAR_UPDATE_LIST])
    global assets_loaded
    assets_loaded = True
    print(f'Длительность загрузки: {time.time() - time_for_loading}')


def throw_cubes():
    for player in players:
        if player.on_move and state['is_game_started']:
            print('Кнопка "Бросить кубы" нажата')
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


def buy():
    if state['is_game_started'] and state['buy_btn_active']:
        print('Кнопка "Купить" нажата')
        for player in players:
            if player.main:
                buy_command = f'buy|{player.piece_position}%'
                sock.send(buy_command.encode())
                information_sent('Команда отправлена', buy_command)
                if state['double']:
                    player_move_change(False)
                else:
                    player_move_change(True)


def pay():
    global state
    print('Кнопка "Оплатить" нажата')
    if state['is_game_started']:
        if state['pay_btn_active'][0] == 'minus':
            for player in players:
                if player.main:
                    pay_command = f'pay|{player.piece_position}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    if state['double']:
                        player_move_change(False)
                    else:
                        player_move_change(True)

        elif state['pay_btn_active'][0] == 'pay sum':
            for player in players:
                if player.main:
                    pay_command = f'pay sum|{state['pay_btn_active'][1]}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    if state['double']:
                        player_move_change(False)
                    else:
                        player_move_change(True)

        elif state['pay_btn_active'][0] == 'color':
            for player in players:
                if player.main:
                    pay_command = f'payToColor|{player.piece_position}|{state['pay_btn_active'][1]}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    if state['double']:
                        player_move_change(False)
                    else:
                        player_move_change(True)

        elif state['pay_btn_active'][0] == 'player':
            for player in players:
                if player.main:
                    pay_command = f'pay to player|{state['pay_btn_active'][1]}|{state['pay_btn_active'][2]}%' # 'pay to player|{color}|{sum}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    if state['double']:
                        player_move_change(False)
                    else:
                        player_move_change(True)

        elif state['pay_btn_active'][0] == 'players':
            for player in players:
                if player.main:
                    pay_command = f'pay to players|{state['pay_btn_active'][1]}%' # 'pay to players|{sum}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    if state['double']:
                        player_move_change(False)
                    else:
                        player_move_change(True)

        elif state['pay_btn_active'][0] == 'prison':
            for player in players:
                if player.main:
                    pay_command = f'pay for prison%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    player_move_change(False)
        state['pay_btn_active'] = ['False']


def debug_output():
    global state
    state['tile_debug'] = not state['tile_debug']
    print(f'\nPlayers: {players}')
    for player in players:
        print(f'       piece_position: {player.piece_position}\n'
              f'       name: {player.name}\n'
              f'       property: {player.property}\n'
              f'       property_family_count: {player.property_family_count}\n'
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
            ip = ip_textbox.get_text()
            port = port_textbox.get_text()
            if ip == '':
                ip = '26.190.64.4'
            if port == '':
                port = 1247
            else:
                port = int(port)
            name = name_textbox.get_text()
            if '%' not in name and '|' not in name:
                sock.connect((ip, port))
                sock.send(f'name|{name}%'.encode())
                state['connected'] = True

                connection_handler = threading.Thread(target=handle_connection, name='connection_handler')
                connection_handler.start()
                thread_open('Поток открыт', connection_handler.name)

                new_connection('Подключено к', f'{ip}:{port}')
            else:
                print(f'{"\033[31m{}".format('Ваше имя не должно содержать символов "|" и "%"')}{'\033[0m'}')
        except:
            print(f'{"\033[31m{}".format('Не удалось подключиться')}{'\033[0m'}')  # красный


def start_game():
    global state
    if state['connected'] and not state['ready']:
        sock.send('ready%'.encode())
        state['ready'] = True


def tile_button(tile_position):
    global state
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
              f'{tile.x_position}\n'
              f'{tile.y_position}\n'
              f'{tile.xText = }\n'
              f'{tile.yText = }\n'
              f'{tile.x_center}\n'
              f'{tile.y_center}\n'
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

    elif state['is_game_started'] and state['all_penises_remove_btns_active'] and not state['penis_remove_btn_used']:
        for player in players:
            if player.main:
                print(all_tiles[tile_position].full_family, all_tiles[tile_position].penises < 5,
                      player.money >= all_tiles[tile_position].penis_price,
                      all_tiles[tile_position].type == 'buildable', all_tiles[tile_position].owner == player.color)
                if (all_tiles[tile_position].full_family and
                        1 <= all_tiles[tile_position].penises <= 5 and
                        player.money >= all_tiles[tile_position].penis_price and
                        all_tiles[tile_position].type == 'buildable' and
                        all_tiles[tile_position].owner == player.color):
                    state['penis_remove_btn_active'] = False
                    state['all_penises_remove_btns_active'] = False
                    state['penis_remove_btn_used'] = True
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
        if not all_tiles[tile_position].mortgaged:
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


def player_button(color):
    global state, available_tiles_for_exchange, exchange_color, exchange_give, exchange_get
    for player2 in players:
        if player2.color == color:
            if not player2.main:
                if state['is_game_started'] and state['exchange_player_btn_active']:
                    print(f'Нажат игрок: {color}')
                    available_tiles_for_exchange = []
                    for player in players:
                        if player.main:
                            available_tiles_for_exchange += player.property
                            # print(player.property)
                        elif player.color == color:
                            # print(player.property)
                            available_tiles_for_exchange += player.property
                    # print(available_tiles_for_exchange)
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
                    exchange_give_textbox.show()
                    exchange_get_textbox.show()


def shove_penis_activation():
    global state
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


def remove_penis_activation():
    global state
    if state['is_game_started'] and state['penis_remove_btn_active'] and not state['penis_remove_btn_used']:
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


def exchange():
    global state
    if state['is_game_started'] and state['exchange_btn_active']:
        state['exchange_player_btn_active'] = True
        print('Нажата кнопка обмена')


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

        if -50 <= exchange_value <= 50 and not incorrect_values:
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
            # print(value_give, value_get)
            exchange_value = round((value_get - value_give) * 100 / max(value_give, value_get))
        else:
            exchange_value = -100
    else:
        exchange_value = -100


def exchange_request_confirm():
    if state['is_game_started'] and state['show_exchange_request_screen'][0]:
        if -50 <= exchange_value <= 50:
            give_money = state['show_exchange_request_screen'][1]
            give_property = state['show_exchange_request_screen'][2]
            get_money = state['show_exchange_request_screen'][3]
            get_property = state['show_exchange_request_screen'][4]
            color = state['show_exchange_request_screen'][5]

            exchange_command = f'exchange|{give_money}_'
            print(give_property, get_property)
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


def exchange_request_reject():
    if state['is_game_started'] and state['show_exchange_request_screen'][0]:
        reject_command = 'exchange request rejected%'
        sock.send(reject_command.encode())
        information_sent('Информация отправлена', reject_command)
        state['show_exchange_request_screen'] = [False]
        exchange_request_confirm_button.hide()
        exchange_request_reject_button.hide()


def choose_avatar():
    global state, sendable_data
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
            image = Image.open(file_name)
            width, height = image.size
            if width > 203:
                image = image.resize([203, height])
                width, height = image.size
            if height > 203:
                image = image.resize([width, 203])

            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()

            for player in players:
                if player.main:
                    color = player.color

            image_bytes_encoded_bytes_base64 = base64.b64encode(image_bytes)
            all_sendable_data = []
            sendable_data = f'avatar|{color}|{len(all_sendable_data) + 1}|'.encode()
            for i in image_bytes_encoded_bytes_base64:
                if len(b''.join([sendable_data, int.to_bytes(i), '|1000'.encode()])) < 1024:
                    sendable_data = b''.join([sendable_data, int.to_bytes(i)])
                else:
                    all_sendable_data.append(sendable_data)
                    sendable_data = b''.join(
                        [f'avatar|{color}|{len(all_sendable_data) + 1}|'.encode(), int.to_bytes(i)])
            all_sendable_data.append(sendable_data)

            for i in range(len(all_sendable_data)):
                all_sendable_data[i] = b''.join([all_sendable_data[i], f'|{len(all_sendable_data)}%'.encode()])

            for i in all_sendable_data:
                sock.send(i)
                time.sleep(0.1)


def auction():
    global state
    if state['is_game_started'] and state['auction_btn_active']:
        for player in players:
            if player.main:
                if all_tiles[player.piece_position].buyable:
                    auction_command = f'auction initiate|{player.piece_position}%'
                    sock.send(auction_command.encode())
                    information_sent('Команда отправлена', auction_command)
                    state['buy_btn_active'] = False
                    state['auction_btn_active'] = False


def auction_buy():
    global state
    if state['show_auction_screen'][0]:
        for player in players:
            if player.main:
                if player.money >= int(state['show_auction_screen'][2]) + 20:
                    auction_command = f'auction accept|{state['show_auction_screen'][1]}|{int(state['show_auction_screen'][2]) + 20}%'
                    sock.send(auction_command.encode())
                    information_sent('Команда отправлена', auction_command)
                    state['show_auction_screen'] = [False]
                    auction_buy_button.disable()
                    auction_buy_button.hide()
                    auction_reject_button.disable()
                    auction_reject_button.hide()


def auction_reject():
    global state
    if state['show_auction_screen'][0]:
        auction_command = f'auction reject|{state['show_auction_screen'][1]}|{state['show_auction_screen'][2]}%'
        sock.send(auction_command.encode())
        information_sent('Команда отправлена', auction_command)
        state['show_auction_screen'] = [False]
        auction_buy_button.disable()
        auction_buy_button.hide()
        auction_reject_button.disable()
        auction_reject_button.hide()


def mortgage():  # заложить
    global state
    if state['mortgage_btn_active']:
        state['mortgage_tile_btn_active'] = True
        state['redeem_tile_btn_active'] = False
        state['exchange_tile_btn_active'] = False
        state['all_penises_build_btns_active'] = False
        state['all_penises_remove_btns_active'] = False


def redeem():  # выкупить
    global state
    if state['redeem_btn_active']:
        state['redeem_tile_btn_active'] = True
        state['mortgage_tile_btn_active'] = False
        state['exchange_tile_btn_active'] = False
        state['all_penises_build_btns_active'] = False
        state['all_penises_remove_btns_active'] = False


def exit_prison_by_egg_s(egg_type):
    prison_exit_information = ''
    for player in players:
        if player.main:
            if player.egg_prison_exit_card and egg_type == 'Яйцо':
                prison_exit_information = f'prison exit by eggs|Яйцо%'
                player.egg_prison_exit_card = False
            elif player.eggs_prison_exit_card and egg_type == 'Яйца':
                prison_exit_information = f'prison exit by eggs|Яйца%'
                player.eggs_prison_exit_card = False
            sock.send(prison_exit_information.encode())


def egg_s_reset():
    state['egg_btn_active'] = False
    state['eggs_btn_active'] = False
    print('Произведён сброс яиц')


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
    if state['egg_btn_active'] or state['eggs_btn_active']:
        screen.blit(eggs_card_uncovered, egg_card_coordinates)
        screen.blit(pulled_card_title, pulled_card_title_rect)
        render_multiline_text(pulled_card_strings, egg_card_text_center[0], egg_card_text_center[1], egg_font, egg_font.get_linesize(), 'center')

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
                screen.blit(darkening_tile,
                            (tile.x_position, tile.y_position))

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
                screen.blit(darkening_tile, (int(positions[tile_.position][0]), int(positions[tile_.position][1])))
        screen.blit(auction_screen, auction_coordinates['auction_screen'])
        screen.blit(font.render(tile.name, False, 'black'), auction_coordinates['company_text'])
        screen.blit(font.render(text, False, 'black'), auction_coordinates['price_text'])


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
            #     aver_time.append(time.time() - now)
            #     print(time.time() - now)
            # print(sum(aver_time) / len(aver_time)) # 1.3432168165842693
            position_update()


            if player.main:
                # print(player.color, player.main, state['double'])
                if all_tiles[player.piece_position].family == 'Угловые':
                    if not state['double']:
                        player_move_change(True)  # TODO: поменять, когда будет функционал
                    else:
                        player_move_change(False)

                if player.piece_position in player.property:
                    if not state['double']:
                        player_move_change(True)
                    else:
                        player_move_change(False)

                for tile in all_tiles:
                    if tile.full_family and tile.owner == player.color and tile.type == 'buildable':
                        if 1 <= tile.penises <= 5:
                            state['penis_remove_btn_active'] = True

                if len(players) > 1:
                    state['exchange_btn_active'] = True

                sock.send('moved%'.encode())
                information_sent('Информация отправлена', 'moved%')

                if all_tiles[player.piece_position].family == 'Яйцо':
                    sock.send('pull card|Яйцо%'.encode())
                    information_sent('Информация отправлена', 'pull card|Яйцо%')

                elif all_tiles[player.piece_position].family == 'Яйца':
                    sock.send('pull card|Яйца%'.encode())
                    information_sent('Информация отправлена', 'pull card|Яйца%')

                mortgage_btn_check()

                buy_btn_check(player.color)
                pay_btn_check()


def move(players_on_tile, end_positions, cube_sum):
    global players
    steps = []

    # print(players_on_tile[0].piece_position, '\n')
    for i in range(len(players_on_tile)):

        start_position = (players_on_tile[i].x, players_on_tile[i].y)
        diff_x = end_positions[i][0] - start_position[0]
        diff_y = end_positions[i][1] - start_position[1]

        if i == 0:
            if not optimized:
                step_amount = abs(round(math.sqrt(diff_x ** 2 + diff_y ** 2) * (7 / cube_sum) * 75 * speed))
                # print((diff_x ** 2 + diff_y ** 2) ** 0.5 * (7 / (cube1 + cube2)) * 1 / dt)
            else:
                step_amount = abs(round(math.sqrt(diff_x ** 2 + diff_y ** 2) * (7 / cube_sum) * 10 * speed))
        if step_amount != 0:
            steps.append((diff_x / step_amount, diff_y / step_amount))
        else:
            steps.append((0, 0))
    # print(f'{diff_x = }, {diff_y = }, {step_amount = }, {steps = }, {start_position = }, {end_positions = }')
    for i in range(step_amount):
        for player in players_on_tile:
            for player2 in players:
                if player == player2:
                    # print(f'{diff_x = :.2f}, {diff_y = :.2f}, {step_amount = }, {steps = }, {player2.x = :.2f}, {player2.y = :.2f}, {player.piece_position = }, {average_fps = :.2f}, {start_position = }, {end_positions = }')
                    if not optimized:
                        time.sleep(abs(7 / cube_sum) * speed)
                    else:
                        time.sleep(abs(7 / cube_sum) * 25 * speed)
                    step_index = players_on_tile.index(player)
                    # print((steps[step_index][0] * average_fps, steps[step_index][1] * average_fps))
                    player2.x += steps[step_index][0] #* (1 / (10 * dt)) # 100
                    player2.y += steps[step_index][1] #* (1 / (10 * dt)) # 86.0135
                    player2.player_piece_rect = player2.player_piece.get_rect(center=(player2.x, player2.y))


def handle_connection():
    global players, all_tiles, avatar, avatar_file, cube_1_picture, cube_2_picture
    avatar = ''
    while running:
        if assets_loaded:
            if state['connected']:
                try:
                    data_unsplit = sock.recv(1024).decode().replace('test', '')
                    data_split_by_types = data_unsplit.split('%')
                    while len(data_split_by_types) > 1:
                        data = data_split_by_types[0].split('|')

                        data_split_by_types.pop(0)
                        if data[0] != '':

                            if data[0] != 'avatar':
                                information_received('Информация получена', data)

                            if data[0] == 'color main':
                                for allPlayer in all_players:
                                    if allPlayer.color == data[1]:
                                        allPlayer.main_color(data[1])

                            elif data[0] == 'avatar':
                                state['avatar_chosen'] = True
                                avatar += data[3]
                                if data[2] == data[4]:
                                    image_bytes_ascii_decoded = avatar.encode("ascii")
                                    image_bytes_decoded = base64.b64decode(image_bytes_ascii_decoded)
                                    image_decoded = Image.open(io.BytesIO(image_bytes_decoded))
                                    # image_decoded.save('avatar.png')
                                    image_decoded = image_decoded.resize((avatar_side_size, avatar_side_size))
                                    image_bytes = io.BytesIO()
                                    image_decoded.save(image_bytes, format='PNG')
                                    image_bytes.seek(0)
                                    try:
                                        for i, player in enumerate(players):
                                            if player.color == data[1]:
                                                player.avatar = pg.image.load(image_bytes).convert_alpha()
                                                avatar = ''
                                                state['avatar_chosen'] = False
                                                update_list_dynamic.append(pg.Rect(profile_coordinates[i]['avatar'], (avatar_side_size, avatar_side_size)))
                                                print('Аватар установлен')
                                    except:
                                        image_decoded.save('error.png')
                                        print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')
                                        print('image saved')

                            elif data[0] == 'move':
                                for player in players:
                                    if player.main and player.color == data[1]:
                                        state['double'] = int(data[2]) == int(data[3])
                                        print(f'Состояние double установлено на {state['double']}')
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

                                        move([player], end_positions, 7)
                                        if all_tiles[player.piece_position].owner == player.color:
                                            player_move_change(True)

                                        position_update()
                                        pay_btn_check()
                                        buy_btn_check(player.color)
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
                                    if profile_picture.get_rect(topleft=profile_coordinates[i]['profile']) not in update_list_static:
                                        update_list_static.append(profile_picture.get_rect(topleft=profile_coordinates[i]['profile']))

                                position_update()
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'property':
                                for player in players:
                                    if data[1] == player.color:
                                        tile_position = int(data[2])
                                        player.property.append(tile_position)
                                        player.property_family_count[all_tiles[tile_position].family] += 1
                                        all_tiles[tile_position].owner = data[1]
                                        all_tiles[tile_position].owned = True
                                        all_tiles[tile_position].family_members += 1

                                        for i in range(len(all_tiles)):
                                            if all_tiles[i].family == all_tiles[tile_position].family and all_tiles[
                                                i].owner == all_tiles[tile_position].owner:
                                                all_tiles[i].family_members = player.property_family_count[
                                                    all_tiles[tile_position].family]
                                                if all_tiles[i].family_members == all_tiles[i].max_family_members:
                                                    all_tiles[i].full_family = True

                                                all_tiles[i].text_defining(font)

                                        print(f'У {player.color} есть {player.property}')

                                        buy_btn_check(data[1])
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
                                        pay_btn_check()
                                        buy_btn_check(player.color)
                                        mortgage_btn_check()
                                        redeem_btn_check()

                            elif data[0] == 'playerDeleted':
                                for player in players:
                                    if player.color == data[1]:
                                        players.remove(player)

                            elif data[0] == 'gameStarted':
                                state['is_game_started'] = True
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
                                            if len(players) > 1:
                                                state['exchange_btn_active'] = True

                                            state['throw_cubes_btn_active'] = True
                                            state['penis_remove_btn_used'] = False
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

                                                if tile.mortgaged:
                                                    tile.mortgaged_moves_count -= 1
                                        else:
                                            state['throw_cubes_btn_active'] = False
                                            state['exchange_btn_active'] = False
                                            state['penis_remove_btn_active'] = False
                                            state['pay_btn_active'] = ['False']
                                            mortgage_btn_check()
                                            redeem_btn_check()

                            elif data[0] == 'error':
                                print(f'Ошибка: {"\033[31m{}".format(data[1])}{'\033[0m'}')

                            elif data[0] == 'imprisoned':
                                for i, player in enumerate(players):
                                    if data[1] == player.color:
                                        player.imprisoned = True
                                        player.piece_position = 10
                                        update_list_dynamic.append(profile_picture.get_rect(topleft=profile_coordinates[i]['profile']))
                                        pay_btn_check()
                                        mortgage_btn_check()
                                        redeem_btn_check()

                            elif data[0] == 'unimprisoned':
                                for i, player in enumerate(players):
                                    if data[1] == player.color:
                                        player.imprisoned = False
                                        update_list_dynamic.append(profile_picture.get_rect(topleft=profile_coordinates[i]['profile']))

                                if len(data) > 2:
                                    move_by_cubes(int(data[2]), int(data[3]), data[1])
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'penis built':
                                all_tiles[int(data[1])].penises += 1
                                all_tiles[int(data[1])].text_defining(font)
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'penis removed':
                                all_tiles[int(data[1])].penises -= 1
                                all_tiles[int(data[1])].text_defining(font)
                                mortgage_btn_check()
                                redeem_btn_check()

                            elif data[0] == 'bribe':
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
                                        for i in player.property:
                                            player.property_family_count[all_tiles[i].family] = 0
                                        new_int_property = []
                                        for i in new_property:
                                            new_int_property.append(int(i))
                                            player.property_family_count[all_tiles[int(i)].family] += 1
                                        player.property = new_int_property
                                        for tile in new_int_property:
                                            all_tiles[tile].owner = data[1]
                                            all_tiles[tile].family_members = player.property_family_count[
                                                all_tiles[tile].family]
                                            if all_tiles[tile].family_members == all_tiles[tile].max_family_members:
                                                all_tiles[tile].full_family = True
                                                sock.send(f'full family|{all_tiles[tile].family}%'.encode())
                                                information_sent('Информация отправлена', f'full family|{all_tiles[tile].family}')
                                            tile.text_defining(font)
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

                                # print(value_give, value_get)
                                exchange_value = round((value_get - value_give) * 100 / max(value_give, value_get))

                                state['show_exchange_request_screen'] = [True, give_money, give_property, get_money,
                                                                         get_property, color]
                                exchange_request_confirm_button.show()
                                exchange_request_reject_button.show()

                            elif data[0] == 'auction bid':
                                state['show_auction_screen'] = [True, int(data[1]), int(data[2])]
                                auction_buy_button.show()
                                auction_reject_button.show()

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

                                if int(data[1]):
                                    state['pay_btn_active'] = ['pay sum', int(data[1])]
                                else:
                                    if state['double']:
                                        player_move_change(False)
                                    else:
                                        player_move_change(True)

                            elif data[0] == 'need to pay to player':
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
                                global pulled_card_text, pulled_card_strings, pulled_card_title, pulled_card_title_rect
                                if data[1] == 'Яйцо':
                                    pulled_card_title = egg_font.render('Вопросительное яйцо', False, 'black')
                                    pulled_card_title_rect = pulled_card_title.get_rect(center=egg_card_title_center)
                                    state['egg_btn_active'] = True
                                    egg_card_position = int(data[2])
                                    pulled_card_strings = []
                                    text = all_egg[egg_card_position].description
                                    if '{value}' in text:
                                        text = text.replace('{value}', f'{all_egg[egg_card_position].value}')
                                    if '{tile_name}' in text:
                                        text = text.replace('{tile_name}', all_tiles[all_egg[egg_card_position].value].name)
                                    # text = 'Заплатите всем игрокам моральную компенсацию в размере 50~ за то, что вы показали всем пЭнис'
                                    text = text.split(' ')

                                elif data[1] == 'Яйца':
                                    pulled_card_title = egg_font.render('Груда вопросительных яиц', False, 'black')
                                    pulled_card_title_rect = pulled_card_title.get_rect(center=egg_card_title_center)
                                    state['eggs_btn_active'] = True
                                    egg_card_position = int(data[2])
                                    pulled_card_strings = []
                                    text = all_eggs[egg_card_position].description
                                    if '{value}' in text:
                                        text = text.replace('{value}', f'{all_eggs[egg_card_position].value}')
                                    if '{tile_name}' in text:
                                        text = text.replace('{tile_name}', all_tiles[all_eggs[egg_card_position].value].name)
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
                                    if player.main:
                                        if data[1] == 'Яйцо':
                                            player.egg_prison_exit_card = True
                                            exit_prison_egg_btn.show()
                                        else:
                                            player.eggs_prison_exit_card = True
                                            exit_prison_eggs_btn.show()
                                        player_move_change(True)

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
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            global running
            running = False

        elif event.type == pg.KEYUP and debug_mode and not optimized:
            if not ip_textbox.is_focused and not port_textbox.is_focused and not name_textbox.is_focused and not exchange_give_textbox.is_focused and not exchange_get_textbox.is_focused:
                if event.key == pg.K_c:
                    connect()
                elif event.key == pg.K_d:
                    debug_output()

        elif event.type == pg.MOUSEBUTTONUP:
            if state['egg_btn_active']:
                egg_s_reset()
            elif state['eggs_btn_active']:
                egg_s_reset()

        if assets_loaded:
            if event.type == CLEAR_UPDATE_LIST:
                if update_list_dynamic:
                    print(f'{update_list_dynamic = }')
                    update_list_dynamic.clear()

        manager_initiated = False
        while not manager_initiated:
            try:
                manager.process_events(event)
                manager_initiated = True
            except:
                print(f'{"\033[32m{}".format(f'Не беспокойтесь. Эта ошибка не вредит игре:\n{traceback.format_exc()}')}{'\033[0m'}')

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


def player_move_change(do_change):
    for player in players:
        if player.main:
            next_player_command = f'nextPlayer|{do_change}%'
            sock.send(next_player_command.encode())
            information_sent('Команда отправлена', next_player_command)


def buttons():
    global cube_button, buy_button, pay_button, name_textbox, ip_textbox, port_textbox, connect_button, debug_button, avatar_choose_button, shove_penis_button, remove_penis_button, exchange_button, exchange_commit_button, exchange_give_textbox, exchange_get_textbox, exchange_request_confirm_button, exchange_request_reject_button, auction_button, auction_buy_button, auction_reject_button, mortgage_button, redeem_button, exit_prison_egg_btn, exit_prison_eggs_btn

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


    name_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['name']),
        placeholder_text='Введите имя',
        manager=manager)

    ip_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['IP']),
        placeholder_text='IP адрес',
        manager=manager)

    port_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['port']),
        placeholder_text='Порт',
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
        relative_rect=pg.Rect(exchange_coordinates['button']),
        text='Обмен',
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

    for i in range(40):
        globals()[f'tile_{i}_button'] = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect(positions[i], tile_size),
            # tool_tip_text=all_tiles[i].name,
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


def dynamic_changes():
    while running:
        active_buttons_check()


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
    name = forbidden_characters_check(name, '|%')
    if name_textbox.get_text() != name:
        name_textbox.set_text(name)


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
    global state
    if state['is_game_started']:
        for player in players:
            if player.main:
                if player.imprisoned:
                    state['pay_btn_active'] = ['prison']
                elif not state['paid']:
                    if (player.piece_position == 4 or player.piece_position == 38) and player.money >= all_tiles[
                        player.piece_position].income * -1:
                        state['pay_btn_active'] = ['minus']
                        state['paid'] = True
                    else:
                        for player2 in players:
                            if not player2.main:
                                if player.piece_position in player2.property and not all_tiles[
                                    player.piece_position].mortgaged:
                                    state['pay_btn_active'] = ['color', player2.color]
                                    state['paid'] = True
                                else:
                                    state['pay_btn_active'] = ['False']
                    print(f'Состояние pay_btn_active установлено на {state['pay_btn_active']}')


def buy_btn_check(color):
    global state, players
    for player in players:
        if player.main and player.color == color:
            if all_tiles[player.piece_position].buyable:
                if not all_tiles[player.piece_position].owned:
                    if player.money >= int(all_tiles[player.piece_position].price):
                        state['buy_btn_active'] = True
                    else:
                        state['buy_btn_active'] = False
                    print(f'Состояние buy_btn_active установлено на {state['buy_btn_active']}')
                    state['auction_btn_active'] = True
                else:
                    state['auction_btn_active'] = False
                    state['buy_btn_active'] = False


def mortgage_btn_check():  # заложить
    global state
    if state['is_game_started']: # and (state['buy_btn_active'] or state['pay_btn_active'][0] != 'False' or state['throw_cubes_btn_active']):
        for player in players:
            if player.main and player.on_move:
                for tile_position in player.property:
                    if all_tiles[tile_position].penises <= 0 and not all_tiles[tile_position].mortgaged:
                        state['mortgage_btn_active'] = True


def redeem_btn_check():  # выкупить
    global state
    if state['is_game_started'] and state['throw_cubes_btn_active']:

        for tile in all_tiles:
            if tile.mortgaged:

                for player in players:
                    if player.main:

                        if player.color == tile.owner:
                            if player.money >= tile.price / 2 * 1.1:
                                state['redeem_btn_active'] = True


running = True
assets_loaded = False

load_assets_handler = threading.Thread(target=load_assets, name='load_assets_handler')
load_assets_handler.start()
thread_open('Поток открыт', load_assets_handler.name)

loading_text_1 = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', 120).render('Загрузка...', False, 'black').convert_alpha()
loading_text_1_rect = loading_text_1.get_rect(center=(resolution[0] // 2, resolution[1] // 2))

# first_launch = not os.path.exists(f'resources/temp/images/{resolution_folder}')
# if first_launch:
#     loading_text_2 = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', 60).render('Первая загрузка может занять до минуты', False, 'black').convert_alpha()
#     loading_text_2_rect = loading_text_2.get_rect(center=(resolution[0] // 2, resolution[1] // 2 + 90))

past_second_fps = []
prev_fps_time = time.time()
average_fps = 0
all_fps = []

while running and not assets_loaded:
    clock.tick(FPS)
    screen.fill((128, 128, 128))
    screen.blit(loading_text_1, loading_text_1_rect)
    # if first_launch:
    #     screen.blit(loading_text_2, loading_text_2_rect)
    event_handler()
    pg.display.flip()

gc.collect()

dynamic_changes_handler = threading.Thread(target=dynamic_changes, name='dynamic_changes')
dynamic_changes_handler.start()
thread_open('Поток открыт', dynamic_changes_handler.name)

while running:
    clock.tick(FPS)
    dt, prev_time = delta_time(prev_time)
    screen.fill((128, 128, 128))
    event_handler()
    blit_board()
    price_printing()
    manager.update(dt)
    manager.draw_ui(screen)

    past_second_fps.append(1 / dt)
    fps_time = time.time()
    all_fps.append(1 / dt)
    if fps_time - prev_fps_time < 0.05:
        past_second_fps.append(1 / dt)
    else:
        prev_fps_time = fps_time
        average_fps = round(sum(past_second_fps) / len(past_second_fps))
        average_fps_text = font.render(str(average_fps), False, 'black')
        past_second_fps.clear()
    screen.blit(average_fps_text, fps_coordinates)

    pg.display.update(update_list_static + update_list_dynamic)

print('\nПрограмма завершена')
print(f'Средний FPS: {sum(all_fps) / len(all_fps)}') # 112.31550775040346
