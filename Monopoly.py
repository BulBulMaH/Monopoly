# для функционала игры
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import socket as sck
import threading
import time
import traceback
import csv
import math

# для аватара
import io
from PIL import Image
import base64
import tkinter
import tkinter.filedialog

# для интерфейса
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox

# классы
from Players_Class_Client_side import Player
from Tiles_Class import Tiles

# функции
from positions_extraction import positions_extraction
from colored_output import thread_open, information_sent, information_received, new_connection
from resolution_choice import resolution_definition
pg.init()
pg.mixer.init()  # для звука

resolution, resolution_folder, piece_color_coefficient, bars_coordinates, btn_coordinates, btn_font, profile_coordinates, start_btn_textboxes_coordinates, btn_radius, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, FPS, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates = resolution_definition(True)

positions = positions_extraction(resolution_folder)

TITLE = 'Monopoly v0.11'
icon = pg.image.load(f'resources/icon.png')
pg.display.set_icon(icon)
screen = pg.display.set_mode(resolution)
pg.display.set_caption(TITLE)
clock = pg.time.Clock()
prev_time = time.time()

def load_assets():
    global background, board, exchange_screen, auction_screen, darkening_full, darkening_tile, profile_picture, bars, player_bars, avatar_file, font, mortgaged_tile
    background = pg.image.load(f'resources/{resolution_folder}/background.png').convert()
    board = pg.image.load(f'resources/{resolution_folder}/board grid.png').convert_alpha()
    exchange_screen = pg.image.load(f'resources/{resolution_folder}/exchange.png').convert_alpha()
    auction_screen = pg.image.load(f'resources/{resolution_folder}/auction.png').convert_alpha()
    darkening_full = pg.image.load(f'resources/{resolution_folder}/darkening all.png').convert_alpha()
    darkening_tile = pg.image.load(f'resources/{resolution_folder}/darkening tile.png').convert_alpha()
    profile_picture = pg.image.load(f'resources/{resolution_folder}/profile/profile.png').convert_alpha()
    bars = pg.image.load(f'resources/{resolution_folder}/bars.png').convert_alpha()
    player_bars = pg.image.load(f'resources/{resolution_folder}/profile/profile_bars.png').convert_alpha()
    avatar_file = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png').convert_alpha()
    mortgaged_tile = pg.image.load(f'resources/{resolution_folder}/mortgaged.png').convert_alpha()
    font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)

    for color in ['green', 'red', 'yellow', 'blue']:
        globals()[f'{color}_property_image'] = pg.image.load(f'resources/{resolution_folder}/property/{color}_property.png').convert_alpha()
        globals()[f'{color}_piece_image'] = pg.image.load(f'resources/{resolution_folder}/pieces/{color}_piece.png').convert_alpha()

    for penis in range(5):
        globals()[f'{penis + 1}_penises_image'] = pg.image.load(f'resources/{resolution_folder}/white penises/{penis + 1}.png').convert_alpha()

    global throw_cubes_disabled_btn, buy_disabled_btn, pay_disabled_btn, shove_penis_disabled_btn, remove_penis_disabled_btn, exchange_disabled_btn, auction_disabled_btn, mortgage_disabled_btn, redeem_disabled_btn, connect_disabled_btn, avatar_choose_disabled_btn, ready_disabled_btn
    throw_cubes_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/throw_cubes_disabled.png').convert_alpha()
    buy_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/buy_disabled.png').convert_alpha()
    pay_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/pay_disabled.png').convert_alpha()
    shove_penis_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/shove_penis_disabled.png').convert_alpha()
    remove_penis_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/remove_penis_disabled.png').convert_alpha()
    exchange_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/exchange_disabled.png').convert_alpha()
    auction_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/auction_disabled.png').convert_alpha()
    mortgage_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/mortgage_disabled.png').convert_alpha()
    redeem_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/redeem_disabled.png').convert_alpha()
    connect_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/connect_disabled.png').convert_alpha()
    avatar_choose_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/avatar_choose_disabled.png').convert_alpha()
    ready_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/ready_disabled.png').convert_alpha()

    global all_tiles, all_players, players, exchange_value, exchange_color, state, sock
    property_family_count = {}
    for tile in all_tiles:
        if tile.buyable:
            property_family_count[tile.family] = 0

    all_players = [Player('red', positions, resolution_folder, property_family_count),
                   Player('blue', positions, resolution_folder, property_family_count),
                   Player('yellow', positions, resolution_folder, property_family_count),
                   Player('green', positions, resolution_folder, property_family_count)]
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
             'show_auction_screen': [False]}

    sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)


def all_tiles_get():
    all_tiles = []
    with open('resources/tiles_data/kletki.csv', 'r', encoding='utf-8') as kletki:
        kletki_reader = csv.DictReader(kletki)
        kletki_list = []
        for i in kletki_reader:
            kletki_list.append(i)

    with open(f'resources/{resolution_folder}/tiles_positions.csv', 'r', encoding='utf-8') as tile_position:
        tile_position_reader = csv.DictReader(tile_position)
        tile_position_list = []
        for i in tile_position_reader:
            tile_position_list.append(i)
        for i in range(40):
            all_tiles.append(Tiles(kletki_list[i], tile_position_list[i]))
            if i not in (0, 10, 20, 30):
                image = Image.open(f'resources/tiles_data/images/{i}.png')
                image = image.resize(tile_size)
                image.save(f'resources/temp/client/images/{i}.png')
                globals()[f'tile_{i}_image'] = pg.image.load(f'resources/temp/client/images/{i}.png').convert()
    return all_tiles


all_tiles = all_tiles_get()

load_assets()


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
                    state['pay_btn_active'] = ['False']


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
    if state['is_game_started']:
        if state['pay_btn_active'][0] == 'minus':
            print('Кнопка "Оплатить" нажата')
            for player in players:
                if player.main:
                    pay_command = f'pay|{player.piece_position}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    if state['double']:
                        player_move_change(False)
                    else:
                        player_move_change(True)

        elif state['pay_btn_active'][0] == 'color':
            print('Кнопка "Оплатить" нажата')
            for player in players:
                if player.main:
                    pay_command = f'payToColor|{player.piece_position}|{state['pay_btn_active'][1]}%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    if state['double']:
                        player_move_change(False)
                    else:
                        player_move_change(True)

        elif state['pay_btn_active'][0] == 'prison':
            print('Кнопка "Оплатить" нажата')
            for player in players:
                if player.main:
                    pay_command = f'pay for prison%'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
        state['pay_btn_active'] = ['False']


def debug_output():
    global state
    state['tile_debug'] = not state['tile_debug']
    print( f'\nPlayers: {players}')
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
              f'       baseX: {player.baseX}\n'
              f'       baseY: {player.baseY}\n'
              f'       on_move: {player.on_move}\n'
              f'       imprisoned: {player.imprisoned}\n')

    print(    f'State: throw_cubes_btn_active: {state['throw_cubes_btn_active']}\n'
              f'       buy_btn_active: {state['buy_btn_active']}\n'
              f'       pay_btn_active: {state['pay_btn_active']}\n'
              f'       penis_build_btn_active: {state['penis_build_btn_active']}\n'
              f'       penis_remove_btn_active: {state['penis_remove_btn_active']}\n'
              f'       penis_remove_btn_used: {state['penis_remove_btn_used']}\n'
              f'       all_penises_build_btns_active: {state['all_penises_build_btns_active']}\n'
              f'       all_penises_remove_btns_active: {state['all_penises_remove_btns_active']}\n'
              f'       exchange_btn_active: {state['exchange_btn_active']}\n'
              f'       exchange_player_btn_active: {state['exchange_player_btn_active']}\n'
              f'       exchange_tile_btn_active: {state['exchange_tile_btn_active']}\n'
              f'       show_exchange_screen: {state['show_exchange_screen']}\n'
              f'       is_game_started: {state['is_game_started']}\n'
              f'       ready: {state['ready']}\n'
              f'       connected: {state['connected']}\n'
              f'       double: {state['double']}\n'
              f'       paid: {state['paid']}\n'
              f'       avatar_chosen: {state['avatar_chosen']}\n'
              f'       cube_animation_playing: {state['cube_animation_playing']}\n')


def connect():
    if not state['is_game_started'] and not state['connected']:
        try:
            ip = ip_textbox.getText()
            port = port_textbox.getText()
            if ip == '':
                ip = '26.190.64.4'
            if port == '':
                port = 1247
            else:
                port = int(port_textbox.getText())
            name = name_textbox.getText()
            if '%' not in name and '|' not in name:
                sock.connect((ip, port))
                sock.send(f'name|{name}%'.encode())
                state['connected'] = True
                new_connection('Подключено к', f'{ip}:{port}')
            else:
                print(f'{"\033[31m{}".format('Ваше имя не должно содержать символов "|" и "%"')}{'\033[0m'}')
        except:
            print(f'{"\033[31m{}".format('Не удалось подключиться')}{'\033[0m'}') # красный


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
              f'{tile.xText = }\n'
              f'{tile.yText = }\n'
              f'{tile.price = }\n'
              f'{tile.color = }\n'
              f'{tile.angle = }\n'
              f'{tile.max_family_members = }\n'
              f'{tile.family_members = }\n'
              f'{tile.penis_price = }\n'
              f'{tile.penises = }\n'
              f'{tile.income = }\n'
              f'{tile.owned = }\n'
              f'{tile.owner = }\n'
              f'{tile.full_family = }\n'
              f'{tile.text = }\n')

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
                print(all_tiles[tile_position].full_family, all_tiles[tile_position].penises < 5, player.money >= all_tiles[tile_position].penis_price, all_tiles[tile_position].type == 'buildable', all_tiles[tile_position].owner == player.color)
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
    global state, available_tiles_for_exchange, exchange_color, exchange_give, exchange_get, exchange_commit_button, exchange_give_textbox, exchange_get_textbox
    for player2 in players:
        if player2.color == color:
            if not player2.main:
                if state['is_game_started'] and state['exchange_player_btn_active']:
                    print(f'Нажат игрок: {color}')
                    available_tiles_for_exchange = []
                    for player in players:
                        if player.main:
                            available_tiles_for_exchange += player.property
                            print(player.property)
                        elif player.color == color:
                            print(player.property)
                            available_tiles_for_exchange += player.property
                    print(available_tiles_for_exchange)
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
                    exchange_commit_button.enable()
                    exchange_commit_button.show()
                    exchange_give_textbox.enable()
                    exchange_give_textbox.show()
                    exchange_get_textbox.enable()
                    exchange_get_textbox.show()


def penis_build_activation():
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


def penis_remove_activation():
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
        exchange_money_give_sum = exchange_give_textbox.getText()
        exchange_money_get_sum = exchange_get_textbox.getText()
        incorrect_values = False
        if exchange_money_get_sum == '' and not incorrect_values:
            exchange_money_get_sum = 0
        else:
            try:
                exchange_money_get_sum = int(exchange_money_get_sum)
            except:
                exchange_get_textbox.setText(exchange_money_get_sum[:-1])
                incorrect_values = True

        if exchange_money_give_sum == '' and not incorrect_values:
            exchange_money_give_sum = 0
        else:
            try:
                exchange_money_give_sum = int(exchange_money_give_sum)
            except:
                exchange_give_textbox.setText(exchange_money_give_sum[:-1])
                incorrect_values = True

        if -50 <= exchange_value <= 50 and not incorrect_values:
            exchange_command = f'exchange request|{exchange_money_give_sum}_'
            # exchange_command = f'exchange|{exchange_money_give_sum}_'
            for give_tile in exchange_give:
                exchange_command += f'{all_tiles[give_tile].position}-'
            exchange_command = exchange_command[:-1] + f'|{exchange_money_get_sum}_'
            for get_tile in exchange_get:
                exchange_command += f'{all_tiles[get_tile].position}-'
            exchange_command = exchange_command[:-1] + f'|{exchange_color}%'

            sock.send(exchange_command.encode())
            information_sent('Команда отправлена', exchange_command)
            state['exchange_tile_btn_active'] = False
            state['exchange_player_btn_active'] = False
            state['show_exchange_screen'] = False
            exchange_commit_button.disable()
            exchange_commit_button.hide()
            exchange_give_textbox.setText('')
            exchange_give_textbox.disable()
            exchange_give_textbox.hide()
            exchange_get_textbox.setText('')
            exchange_get_textbox.disable()
            exchange_get_textbox.hide()


def exchange_value_calculation():
    global exchange_value
    incorrect_values = False
    value_give = 0
    value_get = 0

    exchange_money_give_sum_old = exchange_give_textbox.getText()
    exchange_money_get_sum_old = exchange_get_textbox.getText()
    exchange_money_give_sum = allowed_characters_check(exchange_money_give_sum_old, '0123456789')
    exchange_money_get_sum = allowed_characters_check(exchange_money_get_sum_old, '0123456789')
    if exchange_money_get_sum_old != exchange_money_get_sum:
        exchange_get_textbox.setText(exchange_money_get_sum)
    if exchange_money_give_sum_old != exchange_money_give_sum:
        exchange_give_textbox.setText(exchange_money_give_sum)

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
            print(value_give, value_get)
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
            for give_tile in give_property:
                exchange_command += f'{all_tiles[int(give_tile)].position}-'
            exchange_command = exchange_command[:-1] + f'|{get_money}_'
            for get_tile in get_property:
                exchange_command += f'{all_tiles[int(get_tile)].position}-'
            exchange_command = exchange_command[:-1] + f'|{color}%'

            sock.send(exchange_command.encode())
            information_sent('Команда отправлена', exchange_command)
            state['show_exchange_request_screen'] = [False]
            exchange_request_confirm_button.disable()
            exchange_request_confirm_button.hide()
            exchange_request_reject_button.disable()
            exchange_request_reject_button.hide()


def exchange_request_reject():
    if state['is_game_started'] and state['show_exchange_request_screen'][0]:
        reject_command = 'exchange request rejected%'
        sock.send(reject_command.encode())
        information_sent('Информация отправлена', reject_command)
        state['show_exchange_request_screen'] = [False]
        exchange_request_confirm_button.disable()
        exchange_request_confirm_button.hide()
        exchange_request_reject_button.disable()
        exchange_request_reject_button.hide()


def choose_avatar():
    global state, sendable_data
    if not state['avatar_chosen']:
        top = tkinter.Tk()
        top.withdraw()
        file_name = tkinter.filedialog.askopenfilename(parent=top, filetypes=[('Изображения', ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.icns', '*.ico', '*.apng', '*.tiff', '*.webp'))])
        top.destroy()
        if file_name != '' and not state['avatar_chosen']:
            state['avatar_chosen'] = True
            image = Image.open(file_name)
            width, height = image.size
            if width > 150:
                image = image.resize([150, height])
                width, height = image.size
            if height > 150:
                image = image.resize([width, 150])

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
                    sendable_data = b''.join([f'avatar|{color}|{len(all_sendable_data) + 1}|'.encode(), int.to_bytes(i)])
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


def mortgage(): # заложить
    global state
    if state['mortgage_btn_active']:
        state['mortgage_tile_btn_active'] = True
        state['redeem_tile_btn_active'] = False
        state['exchange_tile_btn_active'] = False
        state['all_penises_build_btns_active'] = False
        state['all_penises_remove_btns_active'] = False


def redeem(): # выкупить
    global state
    if state['redeem_btn_active']:
        state['redeem_tile_btn_active'] = True
        state['mortgage_tile_btn_active'] = False
        state['exchange_tile_btn_active'] = False
        state['all_penises_build_btns_active'] = False
        state['all_penises_remove_btns_active'] = False


# ^
# |
# Функционал кнопок и текст боксов


def render_multiline_text(text, x, y, line_height):
    lines = text
    for i, line in enumerate(lines):
        line_surface = font.render(line, True, 'black')
        screen.blit(line_surface, (x, y + i * line_height))


def blit_board():
    screen.blit(board, (0, 0))

    for tile in all_tiles:
        if tile.family != 'Угловые':
            screen.blit(globals()[f'tile_{tile.position}_image'], (tile.x_position, tile.y_position))

        if tile.owned:
            screen.blit(globals()[f'{tile.owner}_property_image'], (tile.x_position, tile.y_position))

        if 1 <= tile.penises <= 5:
            screen.blit(globals()[f'{tile.penises}_penises_image'], (tile.x_position, tile.y_position))

        if tile.mortgaged:
            screen.blit(mortgaged_tile, (tile.x_position, tile.y_position))


    for player in players:

        player_index = players.index(player)
        screen.blit(player.avatar, (profile_coordinates[player_index]['avatar'][0],
                                    profile_coordinates[player_index]['avatar'][1]))

        if player.imprisoned:
            screen.blit(player_bars, (profile_coordinates[player_index]['avatar'][0],
                                      profile_coordinates[player_index]['avatar'][1]))

        screen.blit(pg.image.load(f'resources/{resolution_folder}/profile/{player.color}_profile.png'),
                    (profile_coordinates[player_index]['avatar'][0],
                     profile_coordinates[player_index]['avatar'][1]))

        screen.blit(profile_picture,
                    (profile_coordinates[player_index]['profile'][0],
                     profile_coordinates[player_index]['profile'][1]))

        screen.blit(font.render(f'{player.money}~', False, 'black'),
                    (profile_coordinates[player_index]['money'][0],
                     profile_coordinates[player_index]['money'][1]))

        screen.blit(font.render(player.name, False, 'black'),
                    (profile_coordinates[player_index]['name'][0],
                     profile_coordinates[player_index]['name'][1]))

        screen.blit(globals()[f'{player.color}_piece_image'], (player.x, player.y))

    screen.blit(bars, bars_coordinates)

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
                              font.get_linesize())

        render_multiline_text(get_text,
                              exchange_coordinates['text_get'][0],
                              exchange_coordinates['text_get'][1],
                              font.get_linesize())

        value_text = font.render(str(exchange_value), False, 'black')
        value_text_rect = value_text.get_rect(center=exchange_coordinates['value'])
        screen.blit(value_text, value_text_rect)
        events = pg.event.get()
        exchange_commit_button.listen(events)
        exchange_commit_button.draw()
        exchange_give_textbox.listen(events)
        exchange_give_textbox.draw()
        exchange_get_textbox.listen(events)
        exchange_get_textbox.draw()

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
            give_text.append(str(all_tiles[int(i)].name))
        for i in get_property:
            get_text.append(str(all_tiles[int(i)].name))

        render_multiline_text(give_text,
                              exchange_coordinates['text_give'][0],
                              exchange_coordinates['text_give'][1],
                              font.get_linesize())

        render_multiline_text(get_text,
                              exchange_coordinates['text_get'][0],
                              exchange_coordinates['text_get'][1],
                              font.get_linesize())

        value_text = font.render(str(exchange_value), False, 'black')
        value_text_rect = value_text.get_rect(center=exchange_coordinates['value'])
        screen.blit(value_text, value_text_rect)

        give_money_text = font.render(f'{give_money}~', False, 'black')
        give_money_text_rect = give_money_text.get_rect(center=(exchange_coordinates['textbox_give'][0] + round(exchange_coordinates['textbox_give'][2] / 2),
                                                                exchange_coordinates['textbox_give'][1] + round(exchange_coordinates['textbox_give'][3] / 2)))
        screen.blit(give_money_text, give_money_text_rect)

        get_money_text = font.render(f'{get_money}~', False, 'black')
        get_money_text_rect = get_money_text.get_rect(center=(exchange_coordinates['textbox_get'][0] + round(exchange_coordinates['textbox_get'][2] / 2),
                                                                exchange_coordinates['textbox_get'][1] + round(exchange_coordinates['textbox_get'][3] / 2)))
        screen.blit(get_money_text, get_money_text_rect)

        events = pg.event.get()
        exchange_request_confirm_button.listen(events)
        exchange_request_confirm_button.draw()
        exchange_request_reject_button.listen(events)
        exchange_request_reject_button.draw()

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

        events = pg.event.get()
        auction_buy_button.listen(events)
        auction_buy_button.draw()
        auction_reject_button.listen(events)
        auction_reject_button.draw()
    else:
        pass


def price_printing():
    for tile in all_tiles:
        if tile.price != '':
            tile.text_defining()
            if tile.position == 4 or tile.position == 38 or not tile.owned:
                text = font.render(tile.text, False, tile.color)
            else:
                text = font.render(tile.text, False, tile.color)
            price_text = pg.transform.rotate(text, tile.angle)

            if tile.angle == -90:
                offset = round((font.size(tile.text)[0] - 31) / 2)
            elif tile.angle == 90:
                offset = round((font.size(tile.text)[0] - 29) / 2)
            else:
                offset = 0

            text_rect = text.get_rect(center=(tile.xText + offset, tile.yText - offset))
            screen.blit(price_text, text_rect)


def position_update():
    global players
    for player in players:
        players_on_tile = []
        for player2 in players:
            if player2.piece_position == player.piece_position:
                players_on_tile.append(player2)
        end_positions = []
        for player3 in players_on_tile:
            end_positions.append((positions[player3.piece_position][0] +
                                  margin[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                  positions[player3.piece_position][1] +
                                  margin[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))
            # print(len(players_on_tile), players_on_tile.index(player3))
        move(players_on_tile, end_positions, 3, 4)


def move_by_cubes(cube1, cube2, color):
    global players, state, cube_1_picture, cube_2_picture
    cube_1_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{cube1}.png')
    cube_2_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{cube2}.png')

    state['cube_animation_playing'] = True
    time.sleep(1.5)
    state['cube_animation_playing'] = False

    for player in players:
        if player.color == color:
            if player.main:
                state['buy_btn_active'] = False
            for i in range(cube1 + cube2):
                players_on_tile = []
                player.piece_position += 1
                if player.piece_position >= 40:
                    player.piece_position -= 40
                for player2 in players:
                    if player2.piece_position == player.piece_position:
                        players_on_tile.append(player2)
                end_positions = []
                for player3 in players_on_tile:
                    end_positions.append((positions[player3.piece_position][0] + margin[len(players_on_tile) - 1][players_on_tile.index(player3)][0],
                                          positions[player3.piece_position][1] + margin[len(players_on_tile) - 1][players_on_tile.index(player3)][1]))
                    # print(len(players_on_tile), players_on_tile.index(player3))
                move(players_on_tile, end_positions, cube1, cube2)
            buy_btn_check(player.color)
            pay_btn_check()
            position_update()

            if player.main:
                # print(player.color, player.main, state['double'])
                if all_tiles[player.piece_position].family in ['Угловые', 'Яйца', 'Яйцо']:
                    if not state['double']:
                        player_move_change(True)  # TODO: поменять, когда будет функционал
                    else:
                        player_move_change(False)

                if player.piece_position in player.property:
                    if not state['double']:
                        player_move_change(True)
                    else:
                        player_move_change(False)
                sock.send('moved%'.encode())


def move(players_on_tile, end_positions, cube1, cube2):
    global players, state, cube_1_picture, cube_2_picture
    steps = []
    step_amount = 1

    # print(players_on_tile[0].piece_position, '\n')
    for i in range(len(players_on_tile)):
        start_position = (players_on_tile[i].x, players_on_tile[i].y)
        diff_x = end_positions[i][0] - start_position[0]
        diff_y = end_positions[i][1] - start_position[1]
        if i == 0:

            step_amount = round(math.sqrt(diff_x ** 2 + diff_y ** 2) * (7 / (cube1 + cube2)) * 0.001 * average_fps)
            # print((diff_x ** 2 + diff_y ** 2) ** 0.5 * (7 / (cube1 + cube2)) * 1 / dt)
            if step_amount != 0:
                steps.append((diff_x / step_amount, diff_y / step_amount))
            else:
                steps.append((0, 0))
    # print(f'{diff_x = :.2f}, {diff_y = :.2f}, {step_amount = }, {steps = }, {start_position = }, {end_positions = }')
    for i in range(step_amount):
        for player in players_on_tile:
            for player2 in players:
                if player == player2:
                    # print(f'{diff_x = :.2f}, {diff_y = :.2f}, {step_amount = }, {steps = }, {player2.x = :.2f}, {player2.y = :.2f}, {start_position = }, {end_positions = }')
                    clock.tick(60)
                    step_index = players_on_tile.index(player)
                    player2.x += steps[step_index][0]
                    player2.y += steps[step_index][1]


def handle_connection():
    global players, state, all_tiles, avatar, avatar_file, cube_1_picture, cube_2_picture
    avatar = ''
    while running:
        try:
            data_unsplit = sock.recv(1024).decode().replace('test','')
            # if data_unsplit != '':
            #     information_received('data_unsplit', data_unsplit)
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
                                for player in players:
                                    if player.color == data[1]:

                                        player.avatar = pg.image.load(image_bytes).convert_alpha()
                                        avatar = ''
                                        state['avatar_chosen'] = False
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
                                player.piece_position = int(data[2])
                                move([player], [positions[player.piece_position]], 10, 10)

                    elif data[0] == 'playersData':
                        for allPlayer in all_players:
                            for i in data:
                                if i == allPlayer.color:
                                    if allPlayer not in players:
                                        players.append(allPlayer)
                        for player in players:
                            if player.color == data[1]:
                                player.money = int(data[2])
                                player.piece_position = int(data[3])
                                player.baseX = positions[player.piece_position][0]
                                player.baseY = positions[player.piece_position][1]
                                player.name = data[4]
                        position_update()
                        mortgage_btn_check()
                        redeem_btn_check()

                    elif data[0] == 'property':
                        for player in players:
                            if data[1] == player.color:
                                tile_position = int(data[2])
                                player.property.append(tile_position)
                                player.property_family_count[all_tiles[tile_position].family] += 1
                                print(player.property_family_count)
                                all_tiles[tile_position].owner = data[1]
                                all_tiles[tile_position].owned = True
                                all_tiles[tile_position].family_members += 1

                                for i in range(len(all_tiles)):
                                    if all_tiles[i].family == all_tiles[tile_position].family and all_tiles[i].owner == all_tiles[tile_position].owner:
                                        all_tiles[i].family_members = player.property_family_count[all_tiles[tile_position].family]
                                        if all_tiles[i].family_members == all_tiles[i].max_family_members:
                                            all_tiles[i].full_family = True

                                if all_tiles[tile_position].full_family:
                                    sock.send(f'full family|{all_tiles[tile_position].family}%'.encode())
                                    information_sent('Информация отправлена', f'full family|{all_tiles[tile_position].family}')

                                print(f'У {player.color} есть {player.property}')

                                buy_btn_check(data[1])
                            if player.main:
                                if int(data[2]) == player.piece_position:
                                    state['paid'] = True
                        mortgage_btn_check()
                        redeem_btn_check()

                    elif data[0] == 'money':
                        for player in players:
                            if data[1] == player.color:
                                player.money = int(data[2])
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
                            globals()[f'{player.color}_player_button'] = Button(screen,
                                                                                profile_coordinates[players.index(player)][
                                                                                    'avatar'][0],
                                                                                profile_coordinates[players.index(player)][
                                                                                    'avatar'][1],
                                                                                avatar_side_size,
                                                                                avatar_side_size,
                                                                                onClick=player_button,
                                                                                onClickParams=(player.color,))
                        mortgage_btn_check()
                        redeem_btn_check()

                    elif data[0] == 'onMove':
                        for player in players:
                            if player.color == data[1]:
                                player.on_move = True

                                if player.main:
                                    state['exchange_btn_active'] = True
                                    state['throw_cubes_btn_active'] = True
                                    state['paid'] = False
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
                                else:
                                    player.on_move = False
                                    state['throw_cubes_btn_active'] = False
                                    state['exchange_btn_active'] = False
                                    state['pay_btn_active'] = ['False']
                                    mortgage_btn_check()
                                    redeem_btn_check()

                    elif data[0] == 'error':
                        print(f'Ошибка: {"\033[31m{}".format(data[1])}{'\033[0m'}')

                    elif data[0] == 'imprisoned':
                        for player in players:
                            if data[1] == player.color:
                                player.imprisoned = True
                                player.piece_position = 10
                                pay_btn_check()
                                mortgage_btn_check()
                                redeem_btn_check()

                    elif data[0] == 'unimprisoned':
                        for player in players:
                            if data[1] == player.color:
                                player.imprisoned = False

                        if len(data) > 2:
                            move_by_cubes(int(data[2]), int(data[3]), data[1])
                        mortgage_btn_check()
                        redeem_btn_check()

                    elif data[0] == 'penis built':
                        all_tiles[int(data[1])].penises += 1
                        mortgage_btn_check()
                        redeem_btn_check()

                    elif data[0] == 'penis removed':
                        all_tiles[int(data[1])].penises -= 1
                        mortgage_btn_check()
                        redeem_btn_check()

                    elif data[0] == 'bribe':
                        state['throw_cubes_btn_active'] = False
                        state['pay_btn_active'] = ['prison']
                        mortgage_btn_check()
                        redeem_btn_check()

                    elif data[0] == 'imprisoned double failed':
                        cube_1_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{data[2]}.png')
                        cube_2_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{data[3]}.png')
                        state['cube_animation_playing'] = True
                        time.sleep(1.5)
                        state['cube_animation_playing'] = False

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
                                    all_tiles[tile].family_members = player.property_family_count[all_tiles[tile].family]
                                    if all_tiles[tile].family_members == all_tiles[tile].max_family_members:
                                        all_tiles[tile].full_family = True
                                        sock.send(f'full family|{all_tiles[tile].family}%'.encode())
                                        information_sent('Информация отправлена', f'full family|{all_tiles[tile].family}')
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
                            value_give += int(all_tiles[int(give_tile)].price) / 2
                        value_give += give_money

                        for get_tile in get_property:
                            value_get += int(all_tiles[int(get_tile)].price) / 2
                        value_get += get_money

                        print(value_give, value_get)
                        exchange_value = round((value_get - value_give) * 100 / max(value_give, value_get))

                        state['show_exchange_request_screen'] = [True, give_money, give_property, get_money, get_property, color]
                        exchange_request_confirm_button.enable()
                        exchange_request_confirm_button.show()
                        exchange_request_reject_button.enable()
                        exchange_request_reject_button.show()

                    elif data[0] == 'auction bid':
                        state['show_auction_screen'] = [True, int(data[1]), int(data[2])]
                        auction_buy_button.enable()
                        auction_buy_button.show()
                        auction_reject_button.enable()
                        auction_reject_button.show()

                    elif data[0] == 'mortgaged':
                        all_tiles[int(data[1])].mortgaged = True
                        for tile in all_tiles:
                            if tile.family == all_tiles[int(data[1])].family:
                                tile.family_members -= 1

                    elif data[0] == 'redeemed':
                        all_tiles[int(data[1])].mortgaged = False
                        for tile in all_tiles:
                            if tile.family == all_tiles[int(data[1])].family:
                                tile.family_members += 1


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
    try:
        pygame_widgets.update(events)
    except AttributeError:
        print(f'{"\033[31m{}".format('Снова вылезла эта поганая ошибка. Я надеюсь, что игра не зависла на этот раз.')}{'\033[0m'}\n')


def player_move_change(do_change):
    for player in players:
        if player.main:
            next_player_command = f'nextPlayer|{do_change}%'
            sock.send(next_player_command.encode())
            information_sent('Команда отправлена', next_player_command)


def buttons():
    global cube_button, buy_button, pay_button, name_textbox, ip_textbox, port_textbox, connect_button, start_button, debug_button, avatar_choose_button, shove_penis_button, remove_penis_button, exchange_button, exchange_commit_button, exchange_give_textbox, exchange_get_textbox, exchange_request_confirm_button, exchange_request_reject_button, auction_button, auction_buy_button, auction_reject_button, mortgage_button, redeem_button
    cube_button = Button(screen,
                         btn_coordinates['throw_cubes'][0],
                         btn_coordinates['throw_cubes'][1],
                         btn_coordinates['throw_cubes'][2],
                         btn_coordinates['throw_cubes'][3],
                         inactiveColour=(255, 255, 255),
                         inactiveBorderColour=(0, 0, 0),
                         hoverColour=(255, 255, 255),
                         hoverBorderColour=(105, 105, 105),
                         pressedColour=(191, 191, 191),
                         pressedBorderColour=(0, 0, 0),
                         borderThickness=3,
                         radius=btn_radius,
                         font=btn_font,
                         text='Бросить кубы',
                         onClick=throw_cubes)

    buy_button = Button(screen,
                        btn_coordinates['buy'][0],
                        btn_coordinates['buy'][1],
                        btn_coordinates['buy'][2],
                        btn_coordinates['buy'][3],
                        inactiveColour=(255, 255, 255),
                        inactiveBorderColour=(0, 0, 0),
                        hoverColour=(255, 255, 255),
                        hoverBorderColour=(105, 105, 105),
                        pressedColour=(191, 191, 191),
                        pressedBorderColour=(0, 0, 0),
                        borderThickness=3,
                        radius=btn_radius,
                        font=btn_font,
                        text='Купить',
                        onClick=buy)

    pay_button = Button(screen,
                        btn_coordinates['pay'][0],
                        btn_coordinates['pay'][1],
                        btn_coordinates['pay'][2],
                        btn_coordinates['pay'][3],
                        inactiveColour=(255, 255, 255),
                        inactiveBorderColour=(0, 0, 0),
                        hoverColour=(255, 255, 255),
                        hoverBorderColour=(105, 105, 105),
                        pressedColour=(191, 191, 191),
                        pressedBorderColour=(0, 0, 0),
                        borderThickness=3,
                        radius=btn_radius,
                        font=btn_font,
                        text='Оплатить',
                        onClick=pay)

    shove_penis_button = Button(screen,
                        btn_coordinates['shove_penis'][0],
                        btn_coordinates['shove_penis'][1],
                        btn_coordinates['shove_penis'][2],
                        btn_coordinates['shove_penis'][3],
                        inactiveColour=(255, 255, 255),
                        inactiveBorderColour=(0, 0, 0),
                        hoverColour=(255, 255, 255),
                        hoverBorderColour=(105, 105, 105),
                        pressedColour=(191, 191, 191),
                        pressedBorderColour=(0, 0, 0),
                        borderThickness=3,
                        radius=btn_radius,
                        font=btn_font,
                        text='Сунуть пЭнис',
                        onClick=penis_build_activation)

    remove_penis_button = Button(screen,
                        btn_coordinates['remove_penis'][0],
                        btn_coordinates['remove_penis'][1],
                        btn_coordinates['remove_penis'][2],
                        btn_coordinates['remove_penis'][3],
                        inactiveColour=(255, 255, 255),
                        inactiveBorderColour=(0, 0, 0),
                        hoverColour=(255, 255, 255),
                        hoverBorderColour=(105, 105, 105),
                        pressedColour=(191, 191, 191),
                        pressedBorderColour=(0, 0, 0),
                        borderThickness=3,
                        radius=btn_radius,
                        font=btn_font,
                        text='Убрать пЭнис',
                        onClick=penis_remove_activation)

    exchange_button = Button(screen,
                             btn_coordinates['exchange'][0],
                             btn_coordinates['exchange'][1],
                             btn_coordinates['exchange'][2],
                             btn_coordinates['exchange'][3],
                             inactiveColour=(255, 255, 255),
                             inactiveBorderColour=(0, 0, 0),
                             hoverColour=(255, 255, 255),
                             hoverBorderColour=(105, 105, 105),
                             pressedColour=(191, 191, 191),
                             pressedBorderColour=(0, 0, 0),
                             borderThickness=3,
                             radius=btn_radius,
                             font=btn_font,
                             text='Обмен',
                             onClick=exchange)

    auction_button = Button(screen,
                             btn_coordinates['auction'][0],
                             btn_coordinates['auction'][1],
                             btn_coordinates['auction'][2],
                             btn_coordinates['auction'][3],
                             inactiveColour=(255, 255, 255),
                             inactiveBorderColour=(0, 0, 0),
                             hoverColour=(255, 255, 255),
                             hoverBorderColour=(105, 105, 105),
                             pressedColour=(191, 191, 191),
                             pressedBorderColour=(0, 0, 0),
                             borderThickness=3,
                             radius=btn_radius,
                             font=btn_font,
                             text='Аукцион',
                             onClick=auction)

    auction_button = Button(screen,
                            btn_coordinates['auction'][0],
                            btn_coordinates['auction'][1],
                            btn_coordinates['auction'][2],
                            btn_coordinates['auction'][3],
                            inactiveColour=(255, 255, 255),
                            inactiveBorderColour=(0, 0, 0),
                            hoverColour=(255, 255, 255),
                            hoverBorderColour=(105, 105, 105),
                            pressedColour=(191, 191, 191),
                            pressedBorderColour=(0, 0, 0),
                            borderThickness=3,
                            radius=btn_radius,
                            font=btn_font,
                            text='Аукцион',
                            onClick=auction)

    mortgage_button = Button(screen,
                            btn_coordinates['mortgage'][0],
                            btn_coordinates['mortgage'][1],
                            btn_coordinates['mortgage'][2],
                            btn_coordinates['mortgage'][3],
                            inactiveColour=(255, 255, 255),
                            inactiveBorderColour=(0, 0, 0),
                            hoverColour=(255, 255, 255),
                            hoverBorderColour=(105, 105, 105),
                            pressedColour=(191, 191, 191),
                            pressedBorderColour=(0, 0, 0),
                            borderThickness=3,
                            radius=btn_radius,
                            font=btn_font,
                            text='Заложить',
                            onClick=mortgage)

    redeem_button = Button(screen,
                             btn_coordinates['redeem'][0],
                             btn_coordinates['redeem'][1],
                             btn_coordinates['redeem'][2],
                             btn_coordinates['redeem'][3],
                             inactiveColour=(255, 255, 255),
                             inactiveBorderColour=(0, 0, 0),
                             hoverColour=(255, 255, 255),
                             hoverBorderColour=(105, 105, 105),
                             pressedColour=(191, 191, 191),
                             pressedBorderColour=(0, 0, 0),
                             borderThickness=3,
                             radius=btn_radius,
                             font=btn_font,
                             text='Выкупить',
                             onClick=redeem)


    name_textbox = TextBox(screen,
                           start_btn_textboxes_coordinates['name'][0],
                           start_btn_textboxes_coordinates['name'][1],
                           start_btn_textboxes_coordinates['name'][2],
                           start_btn_textboxes_coordinates['name'][3],
                           colour=(200, 200, 200),
                           textColour=(0, 0, 0),
                           borderThickness=2,
                           borderColour=(0, 0, 0),
                           font=btn_font,
                           radius=btn_radius,
                           placeholderText='Введите имя',
                           placeholderTextColour=(128, 128, 128),
                           onTextChanged=name_check)

    ip_textbox = TextBox(screen,
                         start_btn_textboxes_coordinates['IP'][0],
                         start_btn_textboxes_coordinates['IP'][1],
                         start_btn_textboxes_coordinates['IP'][2],
                         start_btn_textboxes_coordinates['IP'][3],
                         colour=(200, 200, 200),
                         textColour=(0, 0, 0),
                         borderThickness=2,
                         borderColour=(0, 0, 0),
                         font=btn_font,
                         radius=btn_radius,
                         placeholderText='IP адрес',
                         placeholderTextColour=(128, 128, 128))

    port_textbox = TextBox(screen,
                           start_btn_textboxes_coordinates['port'][0],
                           start_btn_textboxes_coordinates['port'][1],
                           start_btn_textboxes_coordinates['port'][2],
                           start_btn_textboxes_coordinates['port'][3],
                           colour=(200, 200, 200),
                           textColour=(0, 0, 0),
                           borderThickness=2,
                           borderColour=(0, 0, 0),
                           font=btn_font,
                           radius=btn_radius,
                           placeholderText='Порт',
                           placeholderTextColour=(128, 128, 128))

    avatar_choose_button = Button(screen,
                            start_btn_textboxes_coordinates['choose_avatar'][0],
                            start_btn_textboxes_coordinates['choose_avatar'][1],
                            start_btn_textboxes_coordinates['choose_avatar'][2],
                            start_btn_textboxes_coordinates['choose_avatar'][3],
                            inactiveColour=(255, 255, 255),
                            inactiveBorderColour=(0, 0, 0),
                            hoverColour=(255, 255, 255),
                            hoverBorderColour=(105, 105, 105),
                            pressedColour=(191, 191, 191),
                            pressedBorderColour=(0, 0, 0),
                            borderThickness=3,
                            radius=btn_radius,
                            font=btn_font,
                            text='Выбрать аватар',
                            onClick=choose_avatar)

    connect_button = Button(screen,
                            start_btn_textboxes_coordinates['connect'][0],
                            start_btn_textboxes_coordinates['connect'][1],
                            start_btn_textboxes_coordinates['connect'][2],
                            start_btn_textboxes_coordinates['connect'][3],
                            inactiveColour=(255, 255, 255),
                            inactiveBorderColour=(0, 0, 0),
                            hoverColour=(255, 255, 255),
                            hoverBorderColour=(105, 105, 105),
                            pressedColour=(191, 191, 191),
                            pressedBorderColour=(0, 0, 0),
                            borderThickness=3,
                            radius=btn_radius,
                            font=btn_font,
                            text='Подключиться',
                            onClick=connect)

    if debug_mode:
        debug_button = Button(screen,
                              start_btn_textboxes_coordinates['debug'][0],
                              start_btn_textboxes_coordinates['debug'][1],
                              start_btn_textboxes_coordinates['debug'][2],
                              start_btn_textboxes_coordinates['debug'][3],
                              inactiveColour=(255, 255, 255),
                              inactiveBorderColour=(0, 0, 0),
                              hoverColour=(255, 255, 255),
                              hoverBorderColour=(105, 105, 105),
                              pressedColour=(191, 191, 191),
                              pressedBorderColour=(0, 0, 0),
                              borderThickness=3,
                              radius=btn_radius,
                              font=btn_font,
                              text='debug',
                              onClick=debug_output)

    exchange_commit_button = Button(screen,
                                    exchange_coordinates['button'][0],
                                    exchange_coordinates['button'][1],
                                    exchange_coordinates['button'][2],
                                    exchange_coordinates['button'][3],
                                    inactiveColour=(255, 255, 255),
                                    inactiveBorderColour=(0, 0, 0),
                                    hoverColour=(255, 255, 255),
                                    hoverBorderColour=(105, 105, 105),
                                    pressedColour=(191, 191, 191),
                                    pressedBorderColour=(0, 0, 0),
                                    borderThickness=3,
                                    radius=btn_radius,
                                    font=btn_font,
                                    text='Обмен',
                                    onClick=exchange_commit)

    exchange_give_textbox = TextBox(screen,
                                    exchange_coordinates['textbox_give'][0],
                                    exchange_coordinates['textbox_give'][1],
                                    exchange_coordinates['textbox_give'][2],
                                    exchange_coordinates['textbox_give'][3],
                                    colour=(200, 200, 200),
                                    textColour=(0, 0, 0),
                                    borderThickness=2,
                                    borderColour=(0, 0, 0),
                                    font=btn_font,
                                    radius=btn_radius,
                                    placeholderText='Сумма пЭнисов',
                                    placeholderTextColour=(128, 128, 128),
                                    onTextChanged=exchange_value_calculation)

    exchange_get_textbox = TextBox(screen,
                                   exchange_coordinates['textbox_get'][0],
                                   exchange_coordinates['textbox_get'][1],
                                   exchange_coordinates['textbox_get'][2],
                                   exchange_coordinates['textbox_get'][3],
                                   colour=(200, 200, 200),
                                   textColour=(0, 0, 0),
                                   borderThickness=2,
                                   borderColour=(0, 0, 0),
                                   font=btn_font,
                                   radius=btn_radius,
                                   placeholderText='Сумма пЭнисов',
                                   placeholderTextColour=(128, 128, 128),
                                   onTextChanged=exchange_value_calculation)

    exchange_request_confirm_button = Button(screen,
                                    exchange_coordinates['confirm'][0],
                                    exchange_coordinates['confirm'][1],
                                    exchange_coordinates['confirm'][2],
                                    exchange_coordinates['confirm'][3],
                                    inactiveColour=(255, 255, 255),
                                    inactiveBorderColour=(0, 0, 0),
                                    hoverColour=(255, 255, 255),
                                    hoverBorderColour=(105, 105, 105),
                                    pressedColour=(191, 191, 191),
                                    pressedBorderColour=(0, 0, 0),
                                    borderThickness=3,
                                    radius=btn_radius,
                                    font=btn_font,
                                    text='Обмен',
                                    onClick=exchange_request_confirm)

    exchange_request_reject_button = Button(screen,
                                             exchange_coordinates['reject'][0],
                                             exchange_coordinates['reject'][1],
                                             exchange_coordinates['reject'][2],
                                             exchange_coordinates['reject'][3],
                                             inactiveColour=(255, 255, 255),
                                             inactiveBorderColour=(0, 0, 0),
                                             hoverColour=(255, 255, 255),
                                             hoverBorderColour=(105, 105, 105),
                                             pressedColour=(191, 191, 191),
                                             pressedBorderColour=(0, 0, 0),
                                             borderThickness=3,
                                             radius=btn_radius,
                                             font=btn_font,
                                             text='Отказ',
                                             onClick=exchange_request_reject)

    auction_buy_button = Button(screen,
                                    auction_coordinates['confirm'][0],
                                    auction_coordinates['confirm'][1],
                                    auction_coordinates['confirm'][2],
                                    auction_coordinates['confirm'][3],
                                    inactiveColour=(255, 255, 255),
                                    inactiveBorderColour=(0, 0, 0),
                                    hoverColour=(255, 255, 255),
                                    hoverBorderColour=(105, 105, 105),
                                    pressedColour=(191, 191, 191),
                                    pressedBorderColour=(0, 0, 0),
                                    borderThickness=3,
                                    radius=btn_radius,
                                    font=btn_font,
                                    text='Купить',
                                    onClick=auction_buy)

    auction_reject_button = Button(screen,
                                   auction_coordinates['reject'][0],
                                   auction_coordinates['reject'][1],
                                   auction_coordinates['reject'][2],
                                   auction_coordinates['reject'][3],
                                   inactiveColour=(255, 255, 255),
                                   inactiveBorderColour=(0, 0, 0),
                                   hoverColour=(255, 255, 255),
                                   hoverBorderColour=(105, 105, 105),
                                   pressedColour=(191, 191, 191),
                                   pressedBorderColour=(0, 0, 0),
                                   borderThickness=3,
                                   radius=btn_radius,
                                   font=btn_font,
                                   text='Отказаться',
                                   onClick=auction_reject)

    exchange_request_confirm_button.disable()
    exchange_request_confirm_button.hide()
    exchange_request_reject_button.disable()
    exchange_request_reject_button.hide()
    exchange_commit_button.disable()
    exchange_commit_button.hide()
    exchange_give_textbox.disable()
    exchange_give_textbox.hide()
    exchange_get_textbox.disable()
    exchange_get_textbox.hide()

    auction_buy_button.disable()
    auction_buy_button.hide()
    auction_reject_button.disable()
    auction_reject_button.hide()

    for i in range(40):
        globals()[f'penis_{i}_button'] = Button(screen,
                                                positions[i][0],
                                                positions[i][1],
                                                positions[2][0] - positions[1][0],
                                                positions[2][0] - positions[1][0],
                                                onClick=tile_button,
                                                onClickParams=(i,))


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
    name = name_textbox.getText()
    name = forbidden_characters_check(name, '|%')
    if name_textbox.getText() != name:
        name_textbox.setText(name)


def active_buttons_check():
    # Бросок кубов
    if not state['is_game_started'] or not state['throw_cubes_btn_active']:
        screen.blit(throw_cubes_disabled_btn,
                         (btn_coordinates['throw_cubes'][0],
                          btn_coordinates['throw_cubes'][1],
                          btn_coordinates['throw_cubes'][2],
                          btn_coordinates['throw_cubes'][3]))
    # Купить
    if not state['is_game_started'] or not state['buy_btn_active']:
        screen.blit(buy_disabled_btn,
                         (btn_coordinates['buy'][0],
                          btn_coordinates['buy'][1],
                          btn_coordinates['buy'][2],
                          btn_coordinates['buy'][3]))
    # Аукцион
    if not state['is_game_started'] or not state['auction_btn_active']:
        screen.blit(auction_disabled_btn,
                    (btn_coordinates['auction'][0],
                     btn_coordinates['auction'][1],
                     btn_coordinates['auction'][2],
                     btn_coordinates['auction'][3]))
    # Оплатить
    if not state['is_game_started'] or state['pay_btn_active'][0] == 'False':
        screen.blit(pay_disabled_btn,
                         (btn_coordinates['pay'][0],
                          btn_coordinates['pay'][1],
                          btn_coordinates['pay'][2],
                          btn_coordinates['pay'][3]))
    # Сунуть пЭнис
    if not state['is_game_started'] or not state['penis_build_btn_active']:
        screen.blit(shove_penis_disabled_btn,
                         (btn_coordinates['shove_penis'][0],
                          btn_coordinates['shove_penis'][1],
                          btn_coordinates['shove_penis'][2],
                          btn_coordinates['shove_penis'][3]))
    # Убрать пЭнис
    if not state['is_game_started'] or not state['penis_remove_btn_active'] or state['penis_remove_btn_used']:
        screen.blit(remove_penis_disabled_btn,
                         (btn_coordinates['remove_penis'][0],
                          btn_coordinates['remove_penis'][1],
                          btn_coordinates['remove_penis'][2],
                          btn_coordinates['remove_penis'][3]))

    # Обмен
    if not state['is_game_started'] or not state['exchange_btn_active']:
        screen.blit(exchange_disabled_btn,
                         (btn_coordinates['exchange'][0],
                          btn_coordinates['exchange'][1],
                          btn_coordinates['exchange'][2],
                          btn_coordinates['exchange'][3]))

    # Заложить
    if not state['mortgage_btn_active']:
        screen.blit(mortgage_disabled_btn,
                    (btn_coordinates['mortgage'][0],
                     btn_coordinates['mortgage'][1],
                     btn_coordinates['mortgage'][2],
                     btn_coordinates['mortgage'][3]))

    # Выкупить
    if not state['redeem_btn_active']:
        screen.blit(redeem_disabled_btn,
                    (btn_coordinates['redeem'][0],
                     btn_coordinates['redeem'][1],
                     btn_coordinates['redeem'][2],
                     btn_coordinates['redeem'][3]))

    # Подключиться
    if state['is_game_started'] or state['connected']:
        screen.blit(connect_disabled_btn,
                         (start_btn_textboxes_coordinates['connect'][0],
                          start_btn_textboxes_coordinates['connect'][1],
                          start_btn_textboxes_coordinates['connect'][2],
                          start_btn_textboxes_coordinates['connect'][3]))
    # Выбрать аватар
    if not state['is_game_started'] or state['avatar_chosen']:
        screen.blit(avatar_choose_disabled_btn,
                         (start_btn_textboxes_coordinates['choose_avatar'][0],
                          start_btn_textboxes_coordinates['choose_avatar'][1],
                          start_btn_textboxes_coordinates['choose_avatar'][2],
                          start_btn_textboxes_coordinates['choose_avatar'][3]))


def pay_btn_check():
    global state
    if state['is_game_started']:
        for player in players:
            if player.main:
                if player.imprisoned:
                    state['pay_btn_active'] = ['prison']
                elif not state['paid']:
                    if (player.piece_position == 4 or player.piece_position == 38) and player.money >= all_tiles[player.piece_position].income * -1:
                        state['pay_btn_active'] = ['minus']
                        state['paid'] = True
                    else:
                        for player2 in players:
                            if not player2.main:
                                if player.piece_position in player2.property and not all_tiles[player.piece_position].mortgaged:
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
    if state['is_game_started'] and (state['buy_btn_active'] or state['pay_btn_active'][0] != 'False' or state['throw_cubes_btn_active']):
        for player in players:
            if player.main:
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


buttons()

running = True

connection_handler = threading.Thread(target = handle_connection, name='connection_handler')
connection_handler.start()
thread_open('Поток открыт', connection_handler.name)

past_second_fps = []
prev_fps_time = time.time()
average_fps = 0
average_fps_text = font.render(str(average_fps), False, 'black')
while running:
    clock.tick(FPS)
    dt, prev_time = delta_time(prev_time)

    screen.blit(background, (0, 0))
    event_handler()
    blit_board()

    price_printing()
    active_buttons_check()

    if debug_mode:
        screen.blit(font.render(str(round(1 / dt)), False, 'black'), (80, 70))
        screen.blit(font.render(str(dt), False, 'black'), (80, 85))
    past_second_fps.append(1 / dt)
    fps_time = time.time()
    if fps_time - prev_fps_time < 0.05:
        past_second_fps.append(1 / dt)
    else:
        prev_fps_time = fps_time
        average_fps = round(sum(past_second_fps) / len(past_second_fps))
        average_fps_text = font.render(str(average_fps), False, 'black')
        past_second_fps.clear()
    screen.blit(average_fps_text, fps_coordinates)

    pg.display.flip()

for i in range(40):
    print(f'\rУдаление временных файлов: {i + 1} из 40.', end='\r', flush=True)
    if i not in (0, 10, 20, 30):
        os.remove(f'resources/temp/client/images/{i}.png')
print('\nПрограмма завершена')
