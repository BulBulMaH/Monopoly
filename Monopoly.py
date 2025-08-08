# для функционала игры
import pygame as pg
import socket as sck
import threading
import time
import traceback

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

resolution, resolution_folder, piece_color_coefficient, bars_coordinates, btn_coordinates, btn_font, profile_coordinates, start_btn_textboxes_coordinates, btn_radius, cubes_coordinates, speed, avatar_side_size, exchange_coordinates = resolution_definition()

FPS = 60
TITLE = 'Monopoly v0.9'
screen = pg.display.set_mode(resolution)
pg.display.set_caption(TITLE)
clock = pg.time.Clock()
prev_time = time.time()

sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)

positions = positions_extraction(resolution_folder)
background = pg.image.load(f'resources/{resolution_folder}/background.png')
board = pg.image.load(f'resources/{resolution_folder}/board.png')
exchange_screen = pg.image.load(f'resources/{resolution_folder}/exchange.png')
darkening_full = pg.image.load(f'resources/{resolution_folder}/darkening all.png')
darkening_tile = pg.image.load(f'resources/{resolution_folder}/darkening tile.png')
profile_picture = pg.image.load(f'resources/{resolution_folder}/profile/profile.png')
bars = pg.image.load(f'resources/{resolution_folder}/bars.png')
player_bars = pg.image.load(f'resources/{resolution_folder}/profile/profile_bars.png')
avatar_file = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png')
font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)


throw_cubes_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/throw_cubes_disabled.png')
buy_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/buy_disabled.png')
pay_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/pay_disabled.png')
shove_penis_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/shove_penis_disabled.png')
remove_penis_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/remove_penis_disabled.png')
exchange_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/exchange_disabled.png')
connect_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/connect_disabled.png')
avatar_choose_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/avatar_choose_disabled.png')
ready_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/ready_disabled.png')


def all_tiles_get():
    all_tiles = []
    test = open(f'resources/{resolution_folder}/text values/kletki.txt', 'r', encoding='utf-8')
    information = test.readlines()
    test.close()
    for i in range(40):
        all_tiles.append(Tiles(information[i]))
    information.clear()
    return all_tiles


all_tiles = all_tiles_get()

property_family_count = {}
for tile in all_tiles:
    if tile.buyable:
        property_family_count[tile.family] = 0

all_players = [Player('red', positions, resolution_folder, property_family_count),
               Player('blue', positions, resolution_folder, property_family_count),
               Player('yellow', positions, resolution_folder, property_family_count),
               Player('green', positions, resolution_folder, property_family_count)]
players = []
state = {'throw_cubes_btn_active': False,
         'buy_btn_active': False,
         'pay_btn_active': ['False'],
         'penis_build_btn_active': False,
         'penis_remove_btn_active': False,
         'penis_remove_btn_used': False,
         'all_penises_build_btns_active': False,
         'all_penises_remove_btns_active': False,
         'exchange_btn_active': False,
         'exchange_player_btn_active': False,
         'exchange_tile_btn_active': False,
         'show_exchange_screen': False,
         'is_game_started': False,
         'ready': False,
         'connected': False,
         'double': False,
         'paid': False,
         'avatar_chosen': False,
         'cube_animation_playing': False}


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

    if state['is_game_started'] and state['all_penises_remove_btns_active'] and not state['penis_remove_btn_used']:
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

    if state['is_game_started'] and state['exchange_tile_btn_active']:
        global exchange_give, exchange_get
        exchange_give = []
        exchange_get = []
        if (all_tiles[tile_position] in available_tiles_for_exchange and
                all_tiles[tile_position] not in exchange_give and
                all_tiles[tile_position] not in exchange_get):
            for player in players:
                if player.main:
                    if player.color == all_tiles[tile_position].owner:
                        exchange_give.append(all_tiles[tile_position])
                    else:
                        exchange_get.append(all_tiles[tile_position])


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


def exchange():
    global state
    if state['is_game_started'] and state['exchange_btn_active']:
        state['exchange_player_btn_active'] = True


def player_button(color):
    global state, available_tiles_for_exchange
    if state['is_game_started'] and state['exchange_player_btn_active']:
        available_tiles_for_exchange = []
        for player in players:
            if player.main:
                available_tiles_for_exchange += player.property
            elif player.color == color:
                available_tiles_for_exchange += player.property
        state['exchange_tile_btn_active'] = True


# ^
# |
# Функционал кнопок


def blit_items():
    screen.blit(background, (0, 0))
    if state['cube_animation_playing']:
        screen.blit(cube_1_picture, cubes_coordinates[0])
        screen.blit(cube_2_picture, cubes_coordinates[1])

    if state['show_exchange_screen']:
        screen.blit(darkening_full, (0, 0))
        for tile in all_tiles:
            if tile.position not in available_tiles_for_exchange and tile.buyable:
                screen.blit(darkening_tile,
                            (int(positions[tile.position][0]), int(positions[tile.position][1])))

        screen.blit(exchange_screen, exchange_coordinates['exchange_screen'])
        give_text = ''
        get_text = ''
        for i in exchange_give:
            give_text += f'{all_tiles[i].name}\n'

        for i in exchange_get:
            get_text += f'{all_tiles[i].name}\n'

        screen.blit(font.render(give_text, False, 'black'),
                    exchange_coordinates['text_give'])

        screen.blit(font.render(get_text, False, 'black'),
                    exchange_coordinates['text_get'])


def blit_board():
    screen.blit(board, (0, 0))

    for tile in all_tiles:
        if tile.owned:
            screen.blit(pg.image.load(f'resources/{resolution_folder}/{tile.owner}Property.png'),
                        (int(positions[tile.position][0]), int(positions[tile.position][1])))

        if 1 <= tile.penises <= 5:
            screen.blit(pg.image.load(f'resources/{resolution_folder}/white penises/{tile.penises}.png'),
             (int(positions[tile.position][0]), int(positions[tile.position][1])))

    for player in players:
        position_update(player.color)

        player_index = players.index(player)
        screen.blit(player.avatar, (profile_coordinates[player_index]['avatar'][0],
                                    profile_coordinates[player_index]['avatar'][1]))

        if player.imprisoned:
            screen.blit(player_bars, (profile_coordinates[player_index]['avatar'][0],
                                      profile_coordinates[player_index]['avatar'][1]))

        screen.blit(pg.image.load(f'resources/{resolution_folder}/profile/{player.color}Profile.png'),
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

    screen.blit(bars, bars_coordinates)


def price_printing():
    for tile in all_tiles:
        if tile.price != '':
            tile.text_defining()
            if tile.position == 4 or tile.position == 38 or not tile.owned:
                text = font.render(tile.text, False, tile.color)
            else:
                text = font.render(tile.text, False, tile.color)
            price_text = pg.transform.rotate(text, tile.angle)

            offset = 0
            if tile.angle == -90:
                offset = round((font.size(tile.text)[0] - 31) / 2)
            elif tile.angle == 90:
                offset = round((font.size(tile.text)[0] - 29) / 2)

            text_rect = text.get_rect(center=(tile.xText + offset, tile.yText - offset))


            screen.blit(price_text, text_rect)


def position_update(color):
    for player in players:
        if player.color == color:
            if color == 'red':
                player.x = player.baseX
                player.y = player.baseY
            elif color == 'green':
                player.x = player.baseX + piece_color_coefficient
                player.y = player.baseY
            elif color == 'yellow':
                player.x = player.baseX
                player.y = player.baseY + piece_color_coefficient
            elif color == 'blue':
                player.x = player.baseX + piece_color_coefficient
                player.y = player.baseY + piece_color_coefficient
            screen.blit(pg.image.load(f'resources/{resolution_folder}/{player.color}Piece.png'), (player.x, player.y))


def handle_connection():
    global players, state, all_tiles, avatar, avatar_file, cube_1_picture, cube_2_picture
    avatar = ''
    while running:
        try:
            data_unsplit = sock.recv(1024).decode().replace('test','')
            if data_unsplit != '':
                information_received('data_unsplit', data_unsplit)
            data_split_by_types = data_unsplit.split('%')
            while len(data_split_by_types) > 1:
                data = data_split_by_types[0].split('|')

                data_split_by_types.pop(0)

                if data[0] != '':
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
                        image_decoded = image_decoded.resize((avatar_side_size, avatar_side_size))
                        image_bytes = io.BytesIO()
                        image_decoded.save(image_bytes, format='PNG')
                        image_bytes.seek(0)
                        try:
                            for player in players:
                                if player.color == data[1]:
                                    player.avatar = pg.image.load(image_bytes)
                                    avatar = ''
                                    state['avatar_chosen'] = False
                                    print('аватар установлен')
                        except:
                            image_decoded.save('error.png')
                            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')
                            print('image saved')

                elif data[0] == 'move':
                    move(data[1], int(data[2]), int(data[3]), False, 0, 0)
                    for player in players:
                        if player.main and player.color == data[1]:
                            state['double'] = int(data[2]) == int(data[3])
                            if state['double']:
                                player.on_move = True

                elif data[0] == 'move diagonally':
                    move(data[1], 0, 0, True, int(data[2]), int(data[3]))

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
                            position_update(player.color)
                    buttons()

                elif data[0] == 'property':
                    for player in players:
                        if data[1] == player.color:
                            player.property.append(int(data[2]))
                            player.property_family_count[all_tiles[int(data[2])].family] += 1

                            for i in range(len(all_tiles)):
                                if all_tiles[i].family == all_tiles[int(data[2])].family:
                                    all_tiles[i].family_members += 1
                                    if all_tiles[i].family_members == all_tiles[i].max_family_members:
                                        all_tiles[i].full_family = True

                            if all_tiles[int(data[2])].full_family:
                                sock.send(f'full family|{all_tiles[int(data[2])].family}%'.encode())
                                information_sent('Информация отправлена', f'full family|{all_tiles[int(data[2])].family}')

                            print(f'У {player.color} есть {player.property}')
                            all_tiles[int(data[2])].owner = data[1]
                            all_tiles[int(data[2])].owned = True
                            buy_btn_check(data[1])

                elif data[0] == 'money':
                    for player in players:
                        if data[1] == player.color:
                            player.money = int(data[2])

                elif data[0] == 'playerDeleted':
                    for player in players:
                        if player.color == data[1]:
                            players.remove(player)

                elif data[0] == 'gameStarted':
                    state['is_game_started'] = True

                elif data[0] == 'onMove':
                    for player in players:
                        if player.color == data[1]:
                            player.on_move = True
                            state['throw_cubes_btn_active'] = True
                            state['exchange_btn_active'] = True
                        else:
                            player.on_move = False
                            state['throw_cubes_btn_active'] = False

                        if player.main:
                            state['throw_cubes_btn_active'] = True
                            state['paid'] = False
                            state['penis_remove_btn_used'] = False
                            for tile in all_tiles:
                                if tile.full_family and tile.owner == player.color and tile.type == 'buildable':
                                    if not player.imprisoned:
                                        state['penis_build_btn_active'] = True
                                    if 1 <= tile.penises <= 5:
                                        state['penis_remove_btn_active'] = True

                elif data[0] == 'error':
                    print(f'Ошибка: {"\033[31m{}".format(data[1])}{'\033[0m'}')

                elif data[0] == 'imprisoned':
                    for player in players:
                        if data[1] == player.color:
                            player.imprisoned = True
                            player.piece_position = 10
                            pay_btn_check()

                elif data[0] == 'unimprisoned':
                    for player in players:
                        if data[1] == player.color:
                            player.imprisoned = False

                    move(data[1], int(data[2]), int(data[3]), False, 0, 0)

                elif data[0] == 'penis built':
                    all_tiles[int(data[1])].penises += 1

                elif data[0] == 'penis removed':
                    all_tiles[int(data[1])].penises -= 1

                elif data[0] == 'bribe':
                    state['throw_cubes_btn_active'] = False
                    state['pay_btn_active'] = ['prison']

                elif data[0] == 'imprisoned double failed':
                    cube_1_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{data[2]}.png')
                    cube_2_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{data[3]}.png')
                    state['cube_animation_playing'] = True
                    time.sleep(1.5)
                    state['cube_animation_playing'] = False

                    print(f'У игрока {data[1]} осталось {3 - int(data[4])} попытки чтобы выйти из тюрьмы')

                if not running:
                    break
        except OSError:
            pass
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def move(color, cube1, cube2, diagonal, start_position, end_position):
    global players, state, cube_1_picture, cube_2_picture

    if not diagonal:
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
                    start = [positions[player.piece_position][0], positions[player.piece_position][1]]
                    player.piece_position += 1
                    if player.piece_position > 39:
                        player.piece_position = 0
                    end = [positions[player.piece_position][0], positions[player.piece_position][1]]
                    tile_width = max(abs(positions[player.piece_position][0] - positions[player.piece_position - 1][0]),
                                     abs(positions[player.piece_position][1] - positions[player.piece_position - 1][1]))
                    diff_x = end[0] - start[0]
                    diff_y = end[1] - start[1]
                    speed_coef = (((cube1 + cube2 + 3) / 10) ** 2) * speed * dt
                    if min(diff_x, diff_y) != 0:
                        x_step = diff_x / (min(diff_x, diff_y) / speed_coef)
                        y_step = diff_y / (min(diff_x, diff_y) / speed_coef)
                    else:
                        x_step = diff_x / (max(diff_x, diff_y) / speed_coef)
                        y_step = diff_y / (max(diff_x, diff_y) / speed_coef)
                    for ii in range(round(tile_width / speed_coef)):
                        x_sign = 1
                        y_sign = 1

                        if 0 < player.piece_position <= 20:
                            x_sign = 1
                            y_sign = 1
                        elif 20 < player.piece_position <= 30:
                            x_sign = -1
                            y_sign = 1
                        elif player.piece_position > 30 or player.piece_position == 0:
                            x_sign = -1
                            y_sign = -1
                        player.baseX += x_step * x_sign
                        player.baseY += y_step * y_sign
                        position_update(player.color)
                player.baseX = positions[player.piece_position][0]
                player.baseY = positions[player.piece_position][1]
                buy_btn_check(player.color)
                pay_btn_check()

            if player.main:
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

    else:
        start = [positions[start_position][0], positions[start_position][1]]
        end = [positions[end_position][0], positions[end_position][1]]
        diff_x = end[0] - start[0]
        diff_y = end[1] - start[1]
        step_amount = round((diff_x ** 2 + diff_y ** 2) ** 0.5 * dt / speed)
        x_step = diff_x / step_amount
        y_step = diff_y / step_amount
        for player in players:
            if player.color == color:
                player.piece_position = end_position
                for i in range(step_amount):
                    clock.tick(FPS)
                    player.baseX += x_step
                    player.baseY += y_step


def delta_time(old_time):
    now = time.time()
    dt = now - old_time
    old_time = now
    return dt, old_time


def choose_avatar():
    global state, sendable_data
    if not state['avatar_chosen']:
        top = tkinter.Tk()
        top.withdraw()
        file_name = tkinter.filedialog.askopenfilename(parent=top, filetypes=[('Изображения', ('*.png', '*.jpg'))])
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


def event_handler():
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            global running
            running = False
    pygame_widgets.update(events)


def player_move_change(do_change):
    for player in players:
        if player.main:
            next_player_command = f'nextPlayer|{do_change}%'
            sock.send(next_player_command.encode())
            information_sent('Команда отправлена', next_player_command)


def buttons():
    global cube_button, buy_button, pay_button, name_textbox, ip_textbox, port_textbox, connect_button, start_button, debug_button, avatar_choose_button, shove_penis_button, remove_penis_button, exchange_button
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
                           placeholderTextColour=(128, 128, 128))

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

    start_button = Button(screen,
                          start_btn_textboxes_coordinates['ready'][0],
                          start_btn_textboxes_coordinates['ready'][1],
                          start_btn_textboxes_coordinates['ready'][2],
                          start_btn_textboxes_coordinates['ready'][3],
                          inactiveColour=(255, 255, 255),
                          inactiveBorderColour=(0, 0, 0),
                          hoverColour=(255, 255, 255),
                          hoverBorderColour=(105, 105, 105),
                          pressedColour=(191, 191, 191),
                          pressedBorderColour=(0, 0, 0),
                          borderThickness=3,
                          radius=btn_radius,
                          font=btn_font,
                          text='Готов',
                          onClick=start_game)

    debug_button = Button(screen,
                          954,
                          592,
                          136,
                          38,
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
    for i in range(40):
        globals()[f'penis_{i}_button'] = Button(screen,
                                                positions[i][0],
                                                positions[i][1],
                                                positions[2][0] - positions[1][0],
                                                positions[2][0] - positions[1][0],
                                                onClick=tile_button,
                                                onClickParams=(i,))

    for player in players:
        globals()[f'{player.color}_player_button'] = Button(screen,
                                                            profile_coordinates[players.index(player)]['avatar'][0],
                                                            profile_coordinates[players.index(player)]['avatar'][1],
                                                            avatar_side_size,
                                                            avatar_side_size,
                                                            onClick=tile_button,
                                                            onClickParams=(player.color,))

# Проверки
# |
# V

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

    if not state['is_game_started'] or not state['exchange_btn_active']:
        screen.blit(exchange_disabled_btn,
                         (btn_coordinates['exchange'][0],
                          btn_coordinates['exchange'][1],
                          btn_coordinates['exchange'][2],
                          btn_coordinates['exchange'][3]))
    # Подключиться
    if state['is_game_started'] or state['connected']:
        screen.blit(connect_disabled_btn,
                         (start_btn_textboxes_coordinates['connect'][0],
                          start_btn_textboxes_coordinates['connect'][1],
                          start_btn_textboxes_coordinates['connect'][2],
                          start_btn_textboxes_coordinates['connect'][3]))
    # Выбрать аватар
    if not state['connected'] or state['avatar_chosen']:
        screen.blit(avatar_choose_disabled_btn,
                         (start_btn_textboxes_coordinates['choose_avatar'][0],
                          start_btn_textboxes_coordinates['choose_avatar'][1],
                          start_btn_textboxes_coordinates['choose_avatar'][2],
                          start_btn_textboxes_coordinates['choose_avatar'][3]))
    # Готов
    if state['is_game_started'] or state['ready']:
        screen.blit(ready_disabled_btn,
                         (start_btn_textboxes_coordinates['ready'][0],
                          start_btn_textboxes_coordinates['ready'][1],
                          start_btn_textboxes_coordinates['ready'][2],
                          start_btn_textboxes_coordinates['ready'][3]))


def pay_btn_check():
    global state
    if state['is_game_started']:
        for player in players:
            if player.main:
                if player.imprisoned:
                    state['pay_btn_active'] = ['prison']
                elif not state['paid']:
                    if player.piece_position == 4 or player.piece_position == 38:
                        state['pay_btn_active'] = ['minus']
                        state['paid'] = True
                    else:
                        for player2 in players:
                            if not player2.main:
                                if player.piece_position in player2.property:
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
                if (not all_tiles[player.piece_position].owned and
                player.money - int(all_tiles[player.piece_position].price) > 0):
                    state['buy_btn_active'] = True
                else:
                    state['buy_btn_active'] = False
                print(f'Состояние buy_btn_active установлено на {state['buy_btn_active']}')


buttons()

running = True

connection_handler = threading.Thread(target = handle_connection, name='connection_handler')
connection_handler.start()
thread_open('Поток открыт', connection_handler.name)

while running:
    clock.tick(FPS)
    dt, prev_time = delta_time(prev_time)
    blit_items()
    event_handler()
    blit_board()

    price_printing()
    active_buttons_check()
    pg.display.flip()
print('Программа завершена')

