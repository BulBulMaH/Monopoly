import pygame as pg
import socket as sck
import threading
import time
import traceback
import pygame_widgets
from pygame.draw_py import draw_pixel
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox

from functions.Players_Class_Client_side import Player
from functions.Tiles_Class import Tiles

from functions.positions_extraction import positions_extraction
from functions.colored_output import thread_open, information_sent, information_received, new_connection
from functions.resolution_choice import resolution_definition

pg.init()
pg.mixer.init()  # для звука

resolution, resolution_folder, piece_color_coefficient, bars_coordinates, btn_coordinates, btn_text_coordinates, btn_font, profile_coordinates, start_btn_textboxes_coordinates, btn_radius, cubes_coordinates, speed = resolution_definition()

FPS = 60
TITLE = 'Monopoly v0.7'
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
font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)

throw_cubes_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/throw_cubes_disabled.png')
buy_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/buy_disabled.png')
pay_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/pay_disabled.png')
connect_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/connect_disabled.png')
ready_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/ready_disabled.png')

all_players = [Player('red', positions),
               Player('blue', positions),
               Player('yellow', positions),
               Player('green', positions)]
players = []
state = {'buy_btn_active': False,
         'pay_btn_active': ['False'],
         'is_game_started': False,
         'ready': False,
         'connected': False,
         'double': False}


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
            state['pay_btn_active'] = ['False']

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
            state['pay_btn_active'] = ['False']


def debug_output():
    print(f'\nPlayers: {players}')
    for player in players:
        print(f'       piece_position: {player.piece_position}\n'
              f'       name: {player.name}\n'
              f'       property: {player.property}\n'
              f'       color: {player.color}\n'
              f'       money: {player.money}\n'
              f'       main: {player.main}\n'
              f'       x: {player.x}\n'
              f'       y: {player.y}\n'
              f'       baseX: {player.baseX}\n'
              f'       baseY: {player.baseY}\n'
              f'       on_move: {player.on_move}\n')
    print(f'State: buy_btn_active: {state['buy_btn_active']}'
          f'\n       pay_btn_active: {state['pay_btn_active']}'
          f'\n       is_game_started: {state['is_game_started']}'
          f'\n       ready: {state['ready']}'
          f'\n       connected: {state['connected']}'
          f'\n       double: {state['double']}')


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


def blit_items():
    screen.blit(background, (0, 0))  # инициализация поля
    for player in players:
        player_index = players.index(player)
        screen.blit(profile_picture,
                    (profile_coordinates[player_index][0][0],
                     profile_coordinates[player_index][0][1]))

        screen.blit(pg.image.load(f'resources/{resolution_folder}/profile/{player.color}Profile.png'),
                    (profile_coordinates[player_index][1][0],
                     profile_coordinates[player_index][1][1]))

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
    global players, state, all_tiles
    while True:
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

                elif data[0] == 'move':
                    move(data[1], int(data[2]), int(data[3]))
                    for player in players:
                        if player.main and player.color == data[1]:
                            state['double'] = int(data[2]) == int(data[3])
                            if state['double']:
                                player.on_move = True

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

                elif data[0] == 'error':
                    print(data[1])

                if not running:
                    break
        except OSError:
            pass
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def move(color, cube1, cube2):
    global players, state

    cube_1_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{cube1}.png')
    cube_2_picture = pg.image.load(f'resources/{resolution_folder}/cubes/{cube2}.png')

    for i in range(150):
        time.sleep(dt/2)
        screen.blit(cube_1_picture, cubes_coordinates[0])
        screen.blit(cube_2_picture, cubes_coordinates[1])

    for player in players:
        if player.color == color:
            if player.main:
                global state
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

                ii = 0
                if min(diff_x, diff_y) != 0:
                    x_step = diff_x / (min(diff_x, diff_y) * ((cube1 + cube2) / speed))
                    y_step = diff_y / (min(diff_x, diff_y) * ((cube1 + cube2) / speed))
                else:
                    x_step = diff_x / (max(diff_x, diff_y) * ((cube1 + cube2) / speed))
                    y_step = diff_y / (max(diff_x, diff_y) * ((cube1 + cube2) / speed))

                for ii in range(round(tile_width * ((cube1 + cube2) / speed))):
                    # time.sleep(dt/(2 * ((1 + i + ii/10) * (cube1 + cube2) / 10)))  # была 1/120, но dt это ~1/60 => (1/60)/2=1/120
                    time.sleep(dt)
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

                    # print(dt)
                    player.baseX += x_step * x_sign # * (0.8 + (cube1 + cube2) / 10) # 0.8 чтобы при кубах
                    player.baseY += y_step * y_sign # * (0.8 + (cube1 + cube2) / 10) # 1/1 было 1, а 6/6 было 2
                    position_update(player.color)

                #     print(f'\nЦвет: {player.color}\nСтарт: {start}\nКонец: {end}\nРазница: {diff_x}, {diff_y}\nШаги: {x_step}, {y_step}\nКоординаты игрока: {player.baseX}, {player.baseY}\nПозиция игрока: {player.piece_position}\nШирина клетки: {tile_width}\nЗнаки: {x_sign}, {y_sign}\nПуть (в клетках): {i}')
                # print(f'\nИГРОК {player.color} НА НОВОЙ КЛЕТКЕ {player.piece_position}!')
            player.baseX = positions[player.piece_position][0]
            player.baseY = positions[player.piece_position][1]
            buy_btn_check(player.color)
            pay_btn_check()

            if player.main:
                if all_tiles[player.piece_position].family in ['Угловые', 'Яйца', 'Яйцо'] and not state['double']:
                    player_move_change()  # TODO: поменять, когда будет функционал
                if player.piece_position in player.property and not state['double']:
                    player_move_change()
                sock.send('moved'.encode())


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
    global cube_button, buy_button, pay_button, name_textbox, ip_textbox, port_textbox, connect_button, start_button, debug_button
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
            if not player.on_move:
                screen.blit(throw_cubes_disabled_btn,
                            (btn_coordinates[0][0],
                             btn_coordinates[0][1],
                             btn_coordinates[0][2],
                             btn_coordinates[0][3]))

    if not state['is_game_started']:
        screen.blit(throw_cubes_disabled_btn,
                    (btn_coordinates[0][0],
                     btn_coordinates[0][1],
                     btn_coordinates[0][2],
                     btn_coordinates[0][3]))

    if not state['is_game_started'] or not state['buy_btn_active']:
        screen.blit(buy_disabled_btn,
                    (btn_coordinates[1][0],
                    btn_coordinates[1][1],
                    btn_coordinates[1][2],
                    btn_coordinates[1][3]))

    if not state['is_game_started'] or state['pay_btn_active'][0] == 'False':
        screen.blit(pay_disabled_btn,
                    (btn_coordinates[2][0],
                    btn_coordinates[2][1],
                    btn_coordinates[2][2],
                    btn_coordinates[2][3]))

    if state['is_game_started'] or state['connected']:
        screen.blit(connect_disabled_btn,
                    (start_btn_textboxes_coordinates[3][0],
                            start_btn_textboxes_coordinates[3][1],
                            start_btn_textboxes_coordinates[3][2],
                            start_btn_textboxes_coordinates[3][3]))

    if state['is_game_started'] or state['ready']:
        screen.blit(ready_disabled_btn,
                    (start_btn_textboxes_coordinates[4][0],
                            start_btn_textboxes_coordinates[4][1],
                            start_btn_textboxes_coordinates[4][2],
                            start_btn_textboxes_coordinates[4][3]))


def pay_btn_check():
    global state
    if state['is_game_started']:
        for player in players:
            if player.main:
                if player.piece_position == 4 or player.piece_position == 38:
                    state['pay_btn_active'] = ['minus']
                else:
                    for player2 in players:
                        if not player2.main:
                            if player.piece_position in player2.property:
                                state['pay_btn_active'] = ['color', player2.color]
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

connection_handler = threading.Thread(target = handle_connection, name='connection_handler') # , args=(sock,positions,name,running,screen,)
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
pg.quit()