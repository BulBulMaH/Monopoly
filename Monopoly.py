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

resolution, resolution_folder, piece_color_coefficient, bars_coordinates, btn_coordinates, btn_text_coordinates, btn_font, profile_coordinates, start_btn_textboxes_coordinates, btn_radius, cubes_coordinates, speed, avatar_side_size = resolution_definition()

FPS = 60
TITLE = 'Monopoly v0.8'
screen = pg.display.set_mode(resolution)
pg.display.set_caption(TITLE)
clock = pg.time.Clock()
prev_time = time.time()

sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)

positions = positions_extraction(resolution_folder)
background = pg.image.load(f'resources/{resolution_folder}/board.png')
profile_picture = pg.image.load(f'resources/{resolution_folder}/profile/profile.png')
bars = pg.image.load(f'resources/{resolution_folder}/bars.png')
player_bars = pg.image.load(f'resources/{resolution_folder}/profile/profile_bars.png')
avatar_file = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png')
font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)


throw_cubes_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/throw_cubes_disabled.png')
buy_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/buy_disabled.png')
pay_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/pay_disabled.png')
connect_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/connect_disabled.png')
ready_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/ready_disabled.png')
avatar_choose_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/avatar_choose_disabled.png')


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
state = {'buy_btn_active': False,
         'pay_btn_active': ['False'],
         'is_game_started': False,
         'ready': False,
         'connected': False,
         'double': False,
         'paid': False,
         'avatar_chosen': False}


def throw_cubes():
    for player in players:
        if player.on_move and state['is_game_started']:
            print('Кнопка "Бросить кубы" нажата')
            for player2 in players:
                if player2.main:
                    move_command = 'move'
                    sock.send(move_command.encode())
                    information_sent('Команда отправлена', move_command)
                    player2.on_move = False


def buy():
    if state['is_game_started'] and state['buy_btn_active']:
        print('Кнопка "Купить" нажата')
        for player in players:
            if player.main:
                buy_command = 'buy|' + str(player.piece_position)
                sock.send(buy_command.encode())
                information_sent('Команда отправлена', buy_command)
                if state['double']:
                    player.on_move = True
                else:
                    player_move_change()


def pay():
    global state
    if state['is_game_started']:
        if state['pay_btn_active'][0] == 'minus':
            print('Кнопка "Оплатить" нажата')
            for player in players:
                if player.main:
                    pay_command = 'pay|' + str(player.piece_position)
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    if state['double']:
                        player.on_move = True
                    else:
                        player_move_change()

        elif state['pay_btn_active'][0] == 'color':
            print('Кнопка "Оплатить" нажата')
            for player in players:
                if player.main:
                    pay_command = f'payToColor|{player.piece_position}|{state['pay_btn_active'][1]}'
                    sock.send(pay_command.encode())
                    information_sent('Команда отправлена', pay_command)
                    if state['double']:
                        player.on_move = True
                    else:
                        player_move_change()

        elif state['pay_btn_active'][0] == 'prison':
            print('Кнопка "Оплатить" нажата')
            for player in players:
                if player.main:
                    pay_command = f'pay for prison|'
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
              f'       imprisoned: {player.imprisoned}')
    print(    f'State: buy_btn_active: {state['buy_btn_active']}\n'
              f'       pay_btn_active: {state['pay_btn_active']}\n'
              f'       is_game_started: {state['is_game_started']}\n'
              f'       ready: {state['ready']}\n'
              f'       connected: {state['connected']}\n'
              f'       double: {state['double']}\n'
              f'       paid: {state['paid']}\n'
              f'       avatar_chosen: {state['avatar_chosen']}\n')


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
            sock.connect((ip, port))
            name = name_textbox.getText()
            sock.send(f'name|{name}'.encode())
            state['connected'] = True
            new_connection('Подключено к', f'{ip}:{port}')
        except:
            print(f'{"\033[31m{}".format('Не удалось подключиться')}{'\033[0m'}') # красный


def start_game():
    global state
    if state['connected'] and not state['ready']:
        sock.send('ready'.encode())
        state['ready'] = True

# ^
# |
# Функционал кнопок


def blit_items():
    screen.blit(background, (0, 0))  # инициализация поля
    for player in players:
        player_index = players.index(player)
        screen.blit(player.avatar, (profile_coordinates[player_index][1][0],
                             profile_coordinates[player_index][1][1]))

        screen.blit(pg.image.load(f'resources/{resolution_folder}/profile/{player.color}Profile.png'),
                    (profile_coordinates[player_index][1][0],
                     profile_coordinates[player_index][1][1]))

        if player.imprisoned:
            screen.blit(player_bars,(profile_coordinates[player_index][1][0],
                             profile_coordinates[player_index][1][1]))

        screen.blit(profile_picture,
                    (profile_coordinates[player_index][0][0],
                     profile_coordinates[player_index][0][1]))

        screen.blit(btn_font.render(f'{player.money}~', False, 'black'),
                    (profile_coordinates[player_index][2][0],
                     profile_coordinates[player_index][2][1]))

        screen.blit(btn_font.render(player.name, False, 'black'),
                    (profile_coordinates[player_index][3][0],
                     profile_coordinates[player_index][3][1]))

        for company in player.property:
            screen.blit(pg.image.load(f'resources/{resolution_folder}/{player.color}Property.png'), ((int(positions[company][0])), int(positions[company][1])))

        position_update(player.color)

    screen.blit(bars, bars_coordinates)


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
    global players, state, all_tiles, avatar, avatar_file
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

                elif data[0] == 'property':
                    for player in players:
                        if data[1] == player.color:
                            player.property.append(int(data[2]))
                            player.property_family_count[all_tiles[int(data[2])].family] += 1

                            for i in range(len(all_tiles)):
                                if all_tiles[i].family == all_tiles[int(data[2])].family:
                                    all_tiles[i].family_members += 1

                            # if all_tiles[int(data[2])].max_family_members == player.property_family_count[all_tiles[int(data[2])].family]:
                            #     for i in range(len(all_tiles)):
                            #         if all_tiles[i].family == all_tiles[int(data[2])].family:
                            #             all_tiles[i].full_family = True

                            print(f'У {player.color} есть {player.property}')
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
                        else:
                            player.on_move = False

                        if player.main:
                            state['paid'] = False

                elif data[0] == 'error':
                    print(data[1])

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


                if not running:
                    break
        except OSError:
            pass
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def move(color, cube1, cube2, diagonal, start_position, end_position):
    global players, state

    if not diagonal:
        cube_1_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{cube1}.png')
        cube_2_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{cube2}.png')

        for i in range(150):
            clock.tick(FPS)
            screen.blit(cube_1_picture, cubes_coordinates[0])
            screen.blit(cube_2_picture, cubes_coordinates[1])

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
                        player_move_change()  # TODO: поменять, когда будет функционал
                    else:
                        player.on_move = True

                if player.piece_position in player.property:
                    if not state['double']:
                        player_move_change()
                    else:
                        player.on_move = True
                sock.send('moved'.encode())

    else:
        start = [positions[start_position][0], positions[start_position][1]]
        end = [positions[end_position][0], positions[end_position][1]]
        diff_x = end[0] - start[0]
        diff_y = end[1] - start[1]
        step_amount = round((diff_x ** 2 + diff_y ** 2) ** 0.5 * speed * dt)
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
                time.sleep(0.07)


def event_handler():
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            global running
            running = False
    pygame_widgets.update(events)


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


def player_move_change():
    for player in players:
        if player.main:
            next_player_command = 'nextPlayer'
            sock.send(next_player_command.encode())
            information_sent('Команда отправлена', next_player_command)


def buttons():
    global cube_button, buy_button, pay_button, name_textbox, ip_textbox, port_textbox, connect_button, start_button, debug_button, avatar_choose_button
    cube_button = Button(screen,
                         btn_coordinates[0][0],
                         btn_coordinates[0][1],
                         btn_coordinates[0][2],
                         btn_coordinates[0][3],
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
                        btn_coordinates[1][0],
                        btn_coordinates[1][1],
                        btn_coordinates[1][2],
                        btn_coordinates[1][3],
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
                        btn_coordinates[2][0],
                        btn_coordinates[2][1],
                        btn_coordinates[2][2],
                        btn_coordinates[2][3],
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

    name_textbox = TextBox(screen,
                           start_btn_textboxes_coordinates[0][0],
                           start_btn_textboxes_coordinates[0][1],
                           start_btn_textboxes_coordinates[0][2],
                           start_btn_textboxes_coordinates[0][3],
                           colour=(200, 200, 200),
                           textColour=(0, 0, 0),
                           borderThickness=2,
                           borderColour=(0, 0, 0),
                           font=btn_font,
                           radius=btn_radius,
                           placeholderText='Введите имя',
                           placeholderTextColour=(128, 128, 128))

    ip_textbox = TextBox(screen,
                         start_btn_textboxes_coordinates[1][0],
                         start_btn_textboxes_coordinates[1][1],
                         start_btn_textboxes_coordinates[1][2],
                         start_btn_textboxes_coordinates[1][3],
                         colour=(200, 200, 200),
                         textColour=(0, 0, 0),
                         borderThickness=2,
                         borderColour=(0, 0, 0),
                         font=btn_font,
                         radius=btn_radius,
                         placeholderText='IP адрес',
                         placeholderTextColour=(128, 128, 128))

    port_textbox = TextBox(screen,
                           start_btn_textboxes_coordinates[2][0],
                           start_btn_textboxes_coordinates[2][1],
                           start_btn_textboxes_coordinates[2][2],
                           start_btn_textboxes_coordinates[2][3],
                           colour=(200, 200, 200),
                           textColour=(0, 0, 0),
                           borderThickness=2,
                           borderColour=(0, 0, 0),
                           font=btn_font,
                           radius=btn_radius,
                           placeholderText='Порт',
                           placeholderTextColour=(128, 128, 128))

    avatar_choose_button = Button(screen,
                            start_btn_textboxes_coordinates[4][0],
                            start_btn_textboxes_coordinates[4][1],
                            start_btn_textboxes_coordinates[4][2],
                            start_btn_textboxes_coordinates[4][3],
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
                            start_btn_textboxes_coordinates[3][0],
                            start_btn_textboxes_coordinates[3][1],
                            start_btn_textboxes_coordinates[3][2],
                            start_btn_textboxes_coordinates[3][3],
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
                          start_btn_textboxes_coordinates[5][0],
                          start_btn_textboxes_coordinates[5][1],
                          start_btn_textboxes_coordinates[5][2],
                          start_btn_textboxes_coordinates[5][3],
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

# Проверки
# |
# V

def active_buttons_check():
    for player in players:
        if player.main:
            if not player.on_move and not player.imprisoned:
                # Бросок кубов
                screen.blit(throw_cubes_disabled_btn,
                            (btn_coordinates[0][0],
                                  btn_coordinates[0][1],
                                  btn_coordinates[0][2],
                                  btn_coordinates[0][3]))
    # Бросок кубов
    if not state['is_game_started']:
        screen.blit(throw_cubes_disabled_btn,
                    (btn_coordinates[0][0],
                          btn_coordinates[0][1],
                          btn_coordinates[0][2],
                          btn_coordinates[0][3]))
    # Купить
    if not state['is_game_started'] or not state['buy_btn_active']:
        screen.blit(buy_disabled_btn,
                    (btn_coordinates[1][0],
                          btn_coordinates[1][1],
                          btn_coordinates[1][2],
                          btn_coordinates[1][3]))
    # Оплатить
    if not state['is_game_started'] or state['pay_btn_active'][0] == 'False':
        screen.blit(pay_disabled_btn,
                    (btn_coordinates[2][0],
                          btn_coordinates[2][1],
                          btn_coordinates[2][2],
                          btn_coordinates[2][3]))
    # Подключиться
    if state['is_game_started'] or state['connected']:
        screen.blit(connect_disabled_btn,
                    (start_btn_textboxes_coordinates[3][0],
                          start_btn_textboxes_coordinates[3][1],
                          start_btn_textboxes_coordinates[3][2],
                          start_btn_textboxes_coordinates[3][3]))
    # Выбрать аватар
    if not state['connected'] or state['avatar_chosen']:
        screen.blit(avatar_choose_disabled_btn,
                    (start_btn_textboxes_coordinates[4][0],
                          start_btn_textboxes_coordinates[4][1],
                          start_btn_textboxes_coordinates[4][2],
                          start_btn_textboxes_coordinates[4][3]))
    # Готов
    if state['is_game_started'] or state['ready']:
        screen.blit(ready_disabled_btn,
                    (start_btn_textboxes_coordinates[5][0],
                          start_btn_textboxes_coordinates[5][1],
                          start_btn_textboxes_coordinates[5][2],
                          start_btn_textboxes_coordinates[5][3]))


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
    price_printing()

    event_handler()
    active_buttons_check()
    pg.display.flip()
print('Программа завершена')

