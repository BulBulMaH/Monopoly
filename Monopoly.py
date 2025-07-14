import pygame as pg
import socket as sck
import threading
import time
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox

from functions.colored_output import thread_open, new_connection, information_received, information_sent, information_sent_to
from functions.positions_extraction import positions_extraction
from functions.resolution_choice import resolution_definition
from functions.button_functions import buy, throw_cubes
from functions.position_update import position_update
from functions.connection_handler import handle_connection
from functions.debug import debug_output

pg.init()
pg.mixer.init()  # для звука

resolution, resolution_folder, piece_color_coefficient, bars_coordinates, btn_coordinates, btn_text_coordinates, btn_font, profile_coordinates, start_btn_textboxes_coordinates, btn_radius = resolution_definition()

FPS = 60
TITLE = 'Monopoly v0.5.1'
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

players = []
state = {'buy_btn_active': False,
         'is_game_started': False,
         'ready': False}
name = ''

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
                     font=font,
                     text='Бросить кубы',
                     onClick=throw_cubes,
                     onClickParams=(players, sock, state))

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
                    font=font,
                    text='Купить',
                    onClick=buy,
                    onClickParams=(state, players, sock))

name_textbox = TextBox(screen,
                       start_btn_textboxes_coordinates[0][0],
                       start_btn_textboxes_coordinates[0][1],
                       start_btn_textboxes_coordinates[0][2],
                       start_btn_textboxes_coordinates[0][3],
                       colour=(200, 200, 200),
                       textColour=(0, 0, 0),
                       borderThickness=2,
                       borderColour=(0, 0, 0),
                       font=font,
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
                       font=font,
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
                       font=font,
                       radius=btn_radius,
                       placeholderText='Порт',
                       placeholderTextColour=(128, 128, 128))


def connect():
    global connected, name
    connected = False
    if not state['is_game_started'] and not connected:
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
            connected = True
            print(f'Подключено к {ip}:{port}')
            new_connection('Подключено к', f'{ip}:{port}')
        except:
            print(f'{"\033[31m{}".format('Не удалось подключиться')}{'\033[0m'}') # красный

def start_game():
    global state
    if connected:
        sock.send('ready'.encode())
        state['ready'] = True


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
                     font=font,
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
                     font=font,
                     text='Готов',
                     onClick=start_game)


def debug_output1():
    global players, state
    print(f'\nPlayers: {players}'
          f'\nState: buy_btn_active: {state['buy_btn_active']}'
          f'\n       is_game_started: {state['is_game_started']}'
          f'\n       ready: {state['ready']}')


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
                     font=font,
                     text='debug',
                     onClick=debug_output1)


def blit_items():
    screen.blit(background, (0, 0))  # инициализация поля
    for player in players:
        player_index = players.index(player)
        screen.blit(profile_picture, (profile_coordinates[player_index][0][0], profile_coordinates[player_index][0][1]))
        screen.blit(pg.image.load(f'resources/{resolution_folder}/profile/{player.color}Profile.png'),
                    (profile_coordinates[player_index][1][0], profile_coordinates[player_index][1][1]))
        screen.blit(btn_font.render(f'{player.money}~', False, 'black'),
                    (profile_coordinates[player_index][2][0], profile_coordinates[player_index][2][1] - 10))
        position_update(player.color, players, piece_color_coefficient, screen)

        for company in player.property:
            screen.blit(pg.image.load(f'resources/{resolution_folder}/{player.color}Property.png'), ((int(positions[company][0])), int(positions[company][1])))

    screen.blit(bars, bars_coordinates)


def delta_time(old_time):
    now = time.time()
    dt = now - old_time
    old_time = now
    return dt, old_time


def event_handler():
    events = pg.event.get()
    pygame_widgets.update(events)
    for event in events:
        if event.type == pg.QUIT:
            global running
            running = False

running = True

connHandler = threading.Thread(target = handle_connection, args=(sock,positions,name,running,screen,), name='ConnectionHandler')
connHandler.start()

while running:
    clock.tick(FPS)
    dt = delta_time(prev_time)

    blit_items()

    event_handler()
    pg.display.flip()
pg.quit()