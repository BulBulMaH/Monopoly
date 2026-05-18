import socket as sck
import time
import random
import threading
import traceback
import gc
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame as pg
import pygame_gui

import io
from PIL import Image
import base64
import pprint
import zlib
import json

from Textbox_Class import Textbox

from all_tiles_extraction import all_tiles_get
from colored_output import thread_open, new_connection, information_received, information_sent_to
from ProgressBar_Class import ProgressBar


class Player:
    def __init__(self, conn, address, color, color_value):
        self.conn = conn
        self.address = address
        self.piece_position = 0
        self.name = ''
        self.color = color
        self.color_value = color_value
        self.imprisoned = False
        self.prison_break_attempts = 0
        self.money = 1500
        self.value = self.money
        self.avatar_image = pg.image.load(
            f'resources/{resolution_folder}/profile/avatar_placeholder.png').convert_alpha()
        self.x = 0
        self.y = 0
        self.egg_prison_exit_card = False
        self.eggs_prison_exit_card = False
        self.dn_card = False
        self.connection_errors = 0
        self.pay_multiplier = 1
        self.doubles_count = 0
        self.bankrupt = False
        self.time_left = 10800
        self.max_time = 10800
        self.active_timer = False
        self.timer_bar = None
        self.state = {'on_move': False,
                      'double': False,
                      'paid': False,
                      'refused_to_buy': False,

                      'thinking_on_auction': [False],
                      'thinking_on_exchange': False,

                      'throw_cubes_btn_active': False,
                      'buy_btn_active': [False, None],  # is_active, tile_position
                      'pay_btn_active': [False, None],  # is_active, command, ...
                      'penis_build_btn_active': False,
                      'penis_remove_btn_active': False,
                      'mortgage_btn_active': False,
                      'redeem_btn_active': False,
                      'auction_btn_active': False,
                      'exchange_btn_active': False,
                      'surrender_btn_active': False}

    def connect(self, colors):
        new_sck, address = main_sck.accept()
        new_connection('Новое подключение', address)
        new_sck.setblocking(False)
        self.conn = new_sck
        self.address = address
        colors.pop(0)
        color_data_main = f'color main|{self.color}%'
        self.conn.send(color_data_main.encode())
        print('Игроку', self.address, 'назначен', self.color, 'цвет')
        information_sent_to('Информация отправлена к', self.color, color_data_main)

    def clear(self):
        self.conn = ''
        self.address = ''
        self.piece_position = 0
        self.name = ''
        self.color = ''
        self.imprisoned = False
        self.money = 1500


# замена файлов библиотек на модифицированные
if os.path.exists('lib/modified_library_files/magic/__init__.py'):
    os.replace('lib/modified_library_files/magic/__init__.py', '.venv/Lib/site-packages/magic/__init__.py')
if os.path.exists('lib/modified_library_files/pygame-gui/html_parser.py'):
    os.replace('lib/modified_library_files/pygame-gui/html_parser.py',
               '.venv/Lib/site-packages/pygame_gui/core/text/html_parser.py')
if os.path.exists('lib/modified_library_files/pygame-gui/ui_font_dictionary.py'):
    os.replace('lib/modified_library_files/pygame-gui/ui_font_dictionary.py',
               '.venv/Lib/site-packages/pygame_gui/core/ui_font_dictionary.py')

pg.init()
pg.mixer.init(frequency=22050, size=16, channels=1)

background_color = pg.Color(128, 128, 128)
resolution = (1280, 650)
resolution_folder = '720p'
fps_coordinates = (652, -5)
font_size = 25
avatar_side_size = 100
FPS = 30
tile_size = (55, 55)
max_log_image_size = (423, 211)
debug_mode = True
ip = sck.gethostbyname(sck.gethostname())

profile_coordinates = [{'profile': (669, 20 ),  'avatar': (830, 46 ),  'money': (692, 40 ), 'value': (692, 58 ), 'name': (674, 22 ), 'timer_bar': (677, 85,  146, 10)},
                       {'profile': (669, 169),  'avatar': (830, 195),  'money': (692, 189), 'value': (692, 207), 'name': (674, 171), 'timer_bar': (677, 234, 146, 10)},
                       {'profile': (669, 318),  'avatar': (830, 344),  'money': (692, 338), 'value': (692, 356), 'name': (674, 320), 'timer_bar': (677, 383, 146, 10)},
                       {'profile': (669, 467),  'avatar': (830, 493),  'money': (692, 487), 'value': (692, 505), 'name': (674, 469), 'timer_bar': (677, 532, 146, 10)}]
start_btn_textboxes_coordinates = {'name': (1040, 442, 217, 35),
                                   'IP': (1040, 483, 150, 35),
                                   'port': (1196, 483, 65, 35),
                                   'connect': (1040, 534, 217, 38),
                                   'choose_avatar': (1040, 592, 217, 38),
                                   'debug': (1040, 384, 140, 38)}
log_textbox_coordinates = {'main_box': (95, 95, 459, 426),
                           'user_input_box': (95, 519, 350, 35),
                           'audio_send_button': (411, 519, 38, 35),
                           'voice_message_send_button': (446, 519, 38, 35),
                           'image_send_button': (481, 519, 38, 35),
                           'text_send_button': (516, 519, 38, 35)}
piece_color_coefficient = 28
TITLE = 'Monopoly Server'
screen = pg.display.set_mode(resolution)
manager = pygame_gui.UIManager(resolution, theme_path=f'resources/{resolution_folder}/gui_theme.json',
                               enable_live_theme_updates=False)
manager.add_font_paths('BulBulPoly', "resources/fonts/BulBulPoly 4 1x.bdf")
manager.preload_fonts([{'name': 'BulBulPoly', 'point_size': f'{font_size}', 'style': 'regular', 'antialiased': '0'}])
pg.display.set_caption(TITLE)
clock = pg.time.Clock()

play_with_timer = True
timer_duration = {'to move': 60,
                  'to pay': 60,
                  'to buy': 60,
                  'to accept exchange': 30,
                  'to accept auction': 30,
                  'placeholder': 10800} # 3 часа


def load_assets():
    global all_tiles, all_egg, all_eggs, all_question, player_dict
    all_tiles, all_egg, all_eggs, all_question = all_tiles_get(resolution_folder, tile_size)
    random.shuffle(all_egg)
    random.shuffle(all_eggs)
    weights = []
    for i in all_question:
        weights.append(i.weight)
    for i in all_question:
        i.all_weights = weights
    del weights

    player_dict = {}

    global board_image, profile_picture, bars, player_bars, mortgaged_tile, font, players, state, bankrupt_picture
    board_image = pg.image.load(f'resources/temp/images/{resolution_folder}/board image.png').convert_alpha()
    profile_picture = pg.image.load(f'resources/{resolution_folder}/profile/profile.png').convert_alpha()
    bankrupt_picture = pg.image.load(f'resources/{resolution_folder}/profile/bankrupt.png').convert_alpha()
    bars = pg.image.load(f'resources/{resolution_folder}/bars.png').convert_alpha()
    player_bars = pg.image.load(f'resources/{resolution_folder}/profile/profile_bars.png').convert_alpha()
    mortgaged_tile = pg.image.load(f'resources/{resolution_folder}/mortgaged.png').convert_alpha()
    font = pg.font.Font('resources/fonts/BulBulPoly 4 1x.bdf', 25)

    players = []
    state = {'is_server_started': False,
             'is_game_started': False,
             'tile_debug': False}


def receive_data():
    global auction_players, auction_players_who_are_wanting_to_buy, eggs_players_who_need_to_pay_to_one_player, egg_exit_prison, eggs_exit_prison, list_for_file_handler, player_for_file_handler
    auction_players = []
    auction_players_who_are_wanting_to_buy = []
    eggs_players_who_need_to_pay_to_one_player = []

    def number_to_bf(number):
        digits = [6]
        for i in str(number):
            digits.append(int(i))
        all_signs = ''
        for i in range(1, len(digits)):
            number_of_signs = digits[i] - digits[i - 1]
            signs = ''
            if number_of_signs > 0:
                signs += '+' * number_of_signs
            elif number_of_signs < 0:
                signs += '-' * abs(number_of_signs)
            signs += '.'
            all_signs += signs
        return all_signs

    buffer = ''
    while running:
        time.sleep(0.01)
        for player in players:

            try:
                data_unsplit = player.conn.recv(1024).decode()
                buffer += data_unsplit
                while '%' in buffer:
                    single_command, buffer = buffer.split('%', 1)
                    data = single_command.split('|')

                    if data[0] != '' and data[0] not in ['avatar', 'sound message', 'voice message', 'image message', 'pong']:
                        information_received(f'Информация получена от {player.color}', data)

                    if data[0] == 'pong':
                        player.ping = int(data[1])
                        for player2 in players:
                            player2.conn.send(f'ping by player|{player.color}|{player.ping}%'.encode())

                    elif data[0] == 'name':
                        player.name = data[1]
                        players_send()

                    elif data[0] == 'move':
                        if player.state['on_move']:
                            player.state['on_move'] = False
                            player.state['throw_cubes_btn_active'] = False
                            player.state['penis_build_btn_active'] = False
                            player.state['penis_remove_btn_active'] = False
                            player.state['exchange_btn_active'] = False
                            player.state['mortgage_btn_active'] = False
                            player.state['buy_btn_active'] = [False, None]
                            player.state['pay_btn_active'] = [False, None]
                            player.state['surrender_btn_active'] = False
                            player.state['paid'] = False
                            player.state['refused_to_buy'] = False
                            # set_timer_on_player('placeholder', player.color, True)
                            player.active_timer = False

                            cube1 = random.randint(1, 6)
                            cube2 = random.randint(1, 6)

                            player.state['double'] = cube1 == cube2
                            if player.state['double']:
                                player.doubles_count += 1
                            else:
                                player.doubles_count = 0
                            send_player_state(player.color)
                            print(f'Дубль игрока {player.color} установлен на {player.state['double']}')

                            if player.doubles_count < 3:
                                if player.imprisoned:
                                    if player.state['double']:
                                        player.imprisoned = False
                                        player.prison_break_attempts = 0
                                        player.piece_position += cube1 + cube2

                                        mortgage_btn_check(player.color)
                                        redeem_btn_check(player.color)
                                        send_player_state(player.color)

                                        prison_data = f'unimprisoned|{player.color}|{cube1}|{cube2}%'

                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': f'{player.name}', 'color': player.color_value},
                                                        {'text': f'выходит из тюрьмы',
                                                         'color': (0, 0, 0)}]},

                                                   {'type': 'text',
                                                    'value': [
                                                        {'text': f'{player.name}', 'color': player.color_value},
                                                        {
                                                            'text': f'выбрасывает {cube1}:{cube2} и попадает на поле {all_tiles[player.piece_position].name}',
                                                            'color': (0, 0, 0)}]}]
                                        log_textbox_.append_messages(message)

                                        message_data = f'message|{json.dumps(message)}%'

                                        for player2 in players:
                                            player2.conn.send(prison_data.encode())
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player2.color, prison_data)
                                            information_sent_to('Информация отправлена к', player2.color, message_data)

                                    else:
                                        player.prison_break_attempts += 1

                                        mortgage_btn_check(player.color)
                                        redeem_btn_check(player.color)
                                        send_player_state(player.color)

                                        if 3 - player.prison_break_attempts == 1:
                                            tries_text = 'попытка'
                                        elif 1 < 3 - player.prison_break_attempts < 5:
                                            tries_text = 'попытки'
                                        else:
                                            tries_text = 'попыток'

                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': 'У ', 'color': (0, 0, 0)},
                                                        {'text': player.name, 'color': player.color_value},
                                                        {
                                                            'text': f' осталось {3 - player.prison_break_attempts} {tries_text}, чтобы выйти из тюрьмы',
                                                            'color': (0, 0, 0)}
                                                    ]}]
                                        message_data = f'message|{json.dumps(message)}%'
                                        log_textbox_.append_messages(message)
                                        imprisoned_double_failed_data = f'imprisoned double failed|{player.color}|{cube1}|{cube2}|{player.prison_break_attempts}%'
                                        for player2 in players:
                                            player2.conn.send(imprisoned_double_failed_data.encode())
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player2.color,
                                                                imprisoned_double_failed_data)
                                            information_sent_to('Информация отправлена к', player2.color, message_data)
                                        if player.prison_break_attempts < 3:
                                            moving_player_changing(True)

                                    if player.prison_break_attempts >= 3:
                                        player.state['pay_btn_active'] = [
                                            player.money >= (player.prison_break_attempts + 1) * 25 * player.pay_multiplier,
                                            'prison', (player.prison_break_attempts + 1) * 25]
                                        mortgage_btn_check(player.color)
                                        redeem_btn_check(player.color)
                                        send_player_state(player.color)

                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': player.name, 'color': player.color_value},
                                                        {
                                                            'text': f' не смог выйти из тюрьмы и должен заплатить {(player.prison_break_attempts + 1) * 25}~',
                                                            'color': (0, 0, 0)}
                                                    ]}]
                                        message_data = f'message|{json.dumps(message)}%'
                                        log_textbox_.append_messages(message)
                                        player.state['throw_cubes_btn_active'] = False
                                        for player2 in players:
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player2.color, message_data)

                                else:
                                    cube_sum = cube1 + cube2
                                    player.piece_position += cube_sum

                                    move_data = f'move|{player.color}|{cube1}|{cube2}%'

                                    for player2 in players:
                                        player2.conn.send(move_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, move_data)

                                    if player.piece_position <= 39:
                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': player.name, 'color': player.color_value},
                                                        {
                                                            'text': f' выбрасывает {cube1}:{cube2} и попадает на поле {all_tiles[player.piece_position].name}',
                                                            'color': (0, 0, 0)}
                                                    ]}]
                                        message_data = f'message|{json.dumps(message)}%'
                                        log_textbox_.append_messages(message)
                                        for player2 in players:
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player2.color, message_data)

                                    elif player.piece_position > 39:
                                        player.piece_position -= 40

                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': player.name, 'color': player.color_value},
                                                        {
                                                            'text': f' выбрасывает {cube1}:{cube2} и попадает на поле {all_tiles[player.piece_position].name}',
                                                            'color': (0, 0, 0)}
                                                    ]}]
                                        message_data = f'message|{json.dumps(message)}%'
                                        log_textbox_.append_messages(message)
                                        for player2 in players:
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player2.color, message_data)

                                        player.money += 200
                                        if player.piece_position != 0:
                                            message = [{'type': 'text',
                                                        'value': [
                                                            {'text': player.name, 'color': player.color_value},
                                                            {
                                                                'text': f' проходит через поле {all_tiles[0].name} и получает 200~',
                                                                'color': (0, 0, 0)}
                                                        ]}]
                                            message_data = f'message|{json.dumps(message)}%'
                                            log_textbox_.append_messages(message)
                                            for player2 in players:
                                                player2.conn.send(message_data.encode())
                                                information_sent_to('Информация отправлена к', player2.color, message_data)

                            else:
                                player.doubles_count = 0
                                player.piece_position = 10
                                player.imprisoned = True

                                pay_btn_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)
                                exchange_check(player.color)
                                send_player_state(player.color)

                                cubes_information = f'show cubes|{cube1}|{cube2}%'
                                move_data = f'move diagonally|{player.color}|10%'
                                prison_data = f'imprisoned|{player.color}%'

                                message = [
                                    {'type': 'text',
                                     'value': [
                                         {'text': player.name, 'color': player.color_value},
                                         {
                                             'text': f' выбрасывает {cube1}:{cube2} и попадает на поле {all_tiles[player.piece_position].name}',
                                             'color': (0, 0, 0)}
                                     ]},
                                    {'type': 'text',
                                     'value': [
                                         {'text': player.name, 'color': player.color_value},
                                         {'text': ' выбрасывает 3 дубля подряд и отправляется в тюрьму. Удачи!',
                                          'color': (0, 0, 0)}
                                     ]}
                                ]
                                log_textbox_.append_messages(message)
                                message_data = f'message|{json.dumps(message)}%'
                                for player2 in players:
                                    player2.conn.send(cubes_information.encode())
                                    player2.conn.send(move_data.encode())
                                    player2.conn.send(prison_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, cubes_information)
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                    information_sent_to('Информация отправлена к', player2.color, prison_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(True)
                                position_update()

                    elif data[0] == 'buy':
                        if player.piece_position == int(data[1]) and player.state['buy_btn_active'][0]:
                            if player.money >= int(all_tiles[player.piece_position].price):

                                player.state['buy_btn_active'] = [False, None]

                                all_tiles[player.piece_position].owned = True
                                all_tiles[player.piece_position].owner = player.color
                                player.money -= int(all_tiles[player.piece_position].price)

                                price_update(all_tiles[player.piece_position])
                                buy_btn_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)
                                exchange_check(player.color)
                                send_player_state(player.color)

                                property_data = f'property|{player.color}|{data[1]}%'
                                message = [{'type': 'text',
                                            'value': [
                                                {'text': player.name, 'color': player.color_value},
                                                {
                                                    'text': f' приобретает {all_tiles[player.piece_position].name} за {int(all_tiles[player.piece_position].price)}~',
                                                    'color': (0, 0, 0)}
                                            ]}]
                                message_data = f'message|{json.dumps(message)}%'
                                log_textbox_.append_messages(message)
                                money_data = f'money|{player.color}|{player.money}%'
                                player_value_calculation(player.color)

                                for player2 in players:
                                    player2.conn.send(property_data.encode())
                                    player2.conn.send(money_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, property_data)
                                    information_sent_to('Информация отправлена к', player2.color, money_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(not player.state['double'])
                            else:
                                player.conn.send('error|У вас недостаточно пЭнисов, чтобы это купить. '
                                                 'Вы не должны были получить это сообщение. '
                                                 'Только если у вас чИтЫ??7?%'.encode())
                        else:
                            player.conn.send('error|Произошла рассинхронизация, сервер думает, что вы находитесь '
                                             f'на {player.piece_position} позиции, но у вас позиция {data[1]}. '
                                             'Вы не должны были получить это сообщение. '
                                             'Только если у вас чИтЫ??7?%'.encode())

                    elif data[0] == 'moved':
                        print(f'Игрок {player.color} переместился.')

                        pay_btn_check(player.color)
                        buy_btn_check(player.color)
                        mortgage_btn_check(player.color)
                        redeem_btn_check(player.color)
                        penises_check(player.color)
                        exchange_check(player.color)
                        if player.imprisoned:
                            set_timer_on_player('to move', player.color, True)
                        else:
                            if player.state['pay_btn_active']:
                                set_timer_on_player('to pay', player.color, True)
                            elif player.state['buy_btn_active']:
                                set_timer_on_player('to buy', player.color, True)

                        send_player_state(player.color)

                        if player.piece_position == 0:
                            player.money += 100
                            money_data = f'money|{player.color}|{player.money}%'
                            player_value_calculation(player.color)

                            message = [{'type': 'text',
                                        'value': [
                                            {'text': player.name, 'color': player.color_value},
                                            {'text': f' попадает на поле {all_tiles[0].name} и получает 300~',
                                             'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)

                            for player2 in players:
                                player2.conn.send(message_data.encode())
                                player2.conn.send(money_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, message_data)
                                information_sent_to('Информация отправлена к', player2.color, money_data)
                            moving_player_changing(not player.state['double'])

                        elif player.piece_position == 30:
                            player.doubles_count = 0
                            player.piece_position = 10
                            player.imprisoned = True

                            pay_btn_check(player.color)
                            mortgage_btn_check(player.color)
                            redeem_btn_check(player.color)

                            prison_data = f'imprisoned|{player.color}%'
                            message = [{'type': 'text',
                                        'value': [
                                            {'text': player.name, 'color': player.color_value},
                                            {'text': ' отправляется Туда', 'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            move_data = f'move diagonally|{player.color}|10%'
                            for player2 in players:
                                player2.conn.send(move_data.encode())
                                player2.conn.send(prison_data.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, move_data)
                                information_sent_to('Информация отправлена к', player2.color, prison_data)
                                information_sent_to('Информация отправлена к', player2.color, message_data)
                            moving_player_changing(True)

                        elif player.piece_position == 10:
                            if not player.imprisoned:
                                player.piece_position = 30
                                message = [{'type': 'text',
                                            'value': [
                                                {'text': player.name, 'color': player.color_value},
                                                {
                                                    'text': f' переносится на поле {all_tiles[player.piece_position].name}',
                                                    'color': (0, 0, 0)}
                                            ]}]
                                message_data = f'message|{json.dumps(message)}%'
                                log_textbox_.append_messages(message)
                                move_data = f'move diagonally|{player.color}|30%'
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(not player.state['double'])

                        elif player.piece_position == 20:
                            if player.dn_card:
                                question = random.choices(all_question, all_question[0].all_weights)[0]
                                while question.command == 'double or nothing':
                                    question = random.choices(all_question, all_question[0].all_weights)[0]
                            else:
                                question = random.choices(all_question, all_question[0].all_weights)[0]

                            color_to_bf = {'red': '<--.++<<++.-.->>>',
                                           'blue': '<<<-.+++++ +++++.>>+.-<<----- --.-->>>',
                                           'green': '<<<++++.>>--.<<--..-->>----.++++++>',
                                           'yellow': '<+++++.<<++.+++++++..+++.--- ------- -->>--.--->'}
                            description = question.description.replace('{bfcolor}', color_to_bf[player.color])

                            if question.command == 'get random money':
                                pay_sum = random.randint(question.value_range[0], question.value_range[1])

                                all_signs = number_to_bf(pay_sum)

                                description = description.replace('{bfvalue}', all_signs)
                                player.money += pay_sum

                                buy_btn_check(player.color)
                                penises_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)
                                send_player_state(player.color)

                                money_data = f'money|{player.color}|{player.money}%'
                                player_value_calculation(player.color)

                                for player2 in players:
                                    player2.conn.send(money_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, money_data)
                                moving_player_changing(not player.state['double'])

                            elif question.command == 'pay random money':
                                pay_sum = random.randint(question.value_range[0], question.value_range[1])

                                all_signs = number_to_bf(pay_sum)

                                description = description.replace('{bfvalue}', all_signs)

                                player.state['pay_btn_active'] = [player.money >= pay_sum * player.pay_multiplier,
                                                                  'pay sum', pay_sum]
                                mortgage_btn_check(player.color)
                                penises_check(player.color)
                                exchange_check(player.color)
                                send_player_state(player.color)

                            elif question.command == 'double or nothing':
                                player.dn_card = True
                                dn_card_data = f'd/n card|{player.color}%'
                                for player2 in players:
                                    player2.conn.send(dn_card_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, dn_card_data)
                                moving_player_changing(not player.state['double'])

                            elif question.command == 'teleport':
                                tile_position = random.choice(question.value_range)
                                player.piece_position = tile_position

                                pay_btn_check(player.color)
                                buy_btn_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)
                                penises_check(player.color)
                                send_player_state(player.color)

                                all_signs = number_to_bf(tile_position)
                                description = description.replace('{bftileposition}', all_signs)

                                move_data = f'move diagonally|{player.color}|{player.piece_position}%'
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                if all_tiles[player.piece_position].owner == player.color or all_tiles[
                                    player.piece_position].mortgaged:
                                    moving_player_changing(not player.state['double'])

                            message = [{'type': 'text', 'value': [{'text': f'???: {description}', 'color': (0, 0, 0)}]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            for player2 in players:
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                        elif (all_tiles[player.piece_position].type == 'infrastructure' and
                              all_tiles[player.piece_position].owned and
                              all_tiles[player.piece_position].owner != player.color):
                            cube1 = random.randint(1, 6)
                            cube2 = random.randint(1, 6)

                            if not all_tiles[player.piece_position].full_family:
                                pay_sum = (cube1 + cube2) * 4
                            else:
                                pay_sum = (cube1 + cube2) * 10

                            player2 = player_dict[all_tiles[player.piece_position].owner]
                            message = [{'type': 'text',
                                        'value': [
                                            {'text': player.name, 'color': player.color_value},
                                            {'text': f' должен заплатить игроку {player2.name} {pay_sum}~',
                                             'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)

                            player.state['pay_btn_active'] = [player.money >= pay_sum * player.pay_multiplier, 'player',
                                                              all_tiles[player.piece_position].owner, pay_sum]
                            mortgage_btn_check(player.color)
                            penises_check(player.color)
                            exchange_check(player.color)
                            set_timer_on_player('to pay', player.color, True)

                            cubes_information = f'show cubes|{cube1}|{cube2}%'
                            pay_command = f'need to pay to player|{all_tiles[player.piece_position].owner}|{pay_sum}%'
                            for player2 in players:
                                player2.conn.send(cubes_information.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, cubes_information)
                                information_sent_to('Информация отправлена к', player2.color, message_data)
                            player.conn.send(pay_command.encode())
                            information_sent_to('Информация отправлена к', player.color, pay_command)

                            send_player_state(player.color)

                        elif all_tiles[player.piece_position].family == 'Яйцо' or all_tiles[player.piece_position].family == 'Яйца':
                            if all_tiles[player.piece_position].family == 'Яйцо':
                                pulled_card = all_egg[0]
                                if pulled_card.command != 'exit prison':
                                    all_egg.append(pulled_card)
                                else:
                                    egg_exit_prison = pulled_card
                                all_egg.pop(0)

                            else:
                                pulled_card = all_eggs[0]
                                if pulled_card.command != 'exit prison':
                                    all_eggs.append(pulled_card)
                                else:
                                    eggs_exit_prison = pulled_card
                                all_eggs.pop(0)

                            pulled_card_data = f'pulled card position|{player.color}|{all_tiles[player.piece_position].family}|{pulled_card.position}%'
                            for player2 in players:
                                player2.conn.send(pulled_card_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, pulled_card_data)

                            match pulled_card.command:
                                case 'get money':
                                    player.money += pulled_card.value

                                    buy_btn_check(player.color)
                                    mortgage_btn_check(player.color)
                                    redeem_btn_check(player.color)
                                    penises_check(player.color)
                                    send_player_state(player.color)

                                    if all_tiles[player.piece_position].family == 'Яйцо':
                                        first_message_part = 'Яйцо даёт'
                                    else:
                                        first_message_part = 'Яйца дают'
                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': f'{first_message_part} игроку ', 'color': (0, 0, 0)},
                                                    {'text': player.name, 'color': player.color_value},
                                                    {'text': f' {pulled_card.value}~', 'color': (0, 0, 0)}
                                                ]}]
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)
                                    money_data = f'money|{player.color}|{player.money}%'
                                    player_value_calculation(player.color)

                                    for player2 in players:
                                        player2.conn.send(money_data.encode())
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, money_data)
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                    moving_player_changing(not player.state['double'])

                                case 'get money from players':
                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': 'Все игроки должны заплатить ', 'color': (0, 0, 0)},
                                                    {'text': f'{pulled_card.value}~ игроку ', 'color': (0, 0, 0)},
                                                    {'text': player.name, 'color': player.color_value}
                                                ]}]
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)

                                    pay_command = f'need to pay to player|{player.color}|{pulled_card.value}%'
                                    for player2 in players:
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player.color, message_data)
                                        if len(players) > 1:
                                            if player2 != player:
                                                player2.state['pay_btn_active'] = [
                                                    player.money >= pulled_card.value * player.pay_multiplier,
                                                    'player', player.color,
                                                    pulled_card.value]
                                                mortgage_btn_check(player2.color)
                                                penises_check(player2.color)
                                                exchange_check(player2.color)
                                                send_player_state(player2.color)
                                                set_timer_on_player('to pay', player2.color, False)

                                                eggs_players_who_need_to_pay_to_one_player.append(player2)
                                                player2.conn.send(pay_command.encode())
                                                information_sent_to('Информация отправлена к', player.color,
                                                                    pay_command)
                                        else:
                                            message = [{'type': 'text', 'value': [
                                                {'text': 'Ни одного игрока не найдено', 'color': (0, 0, 0)}]}]
                                            message_data = f'message|{json.dumps(message)}%'
                                            log_textbox_.append_messages(message)
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player.color, message_data)

                                case 'go to start':
                                    player.piece_position = 0
                                    move_data = f'move diagonally|{player.color}|0%'
                                    player.money += pulled_card.value

                                    buy_btn_check(player.color)
                                    mortgage_btn_check(player.color)
                                    redeem_btn_check(player.color)
                                    send_player_state(player.color)

                                    if all_tiles[player.piece_position].family == 'Яйцо':
                                        first_message_part = 'Яйцо переносит'
                                    else:
                                        first_message_part = 'Яйца переносят'
                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': f'{first_message_part} игрока ', 'color': (0, 0, 0)},
                                                    {'text': player.name, 'color': player.color_value},
                                                    {'text': f' на поле {all_tiles[player.piece_position].name} и ',
                                                     'color': (0, 0, 0)},
                                                    {'text': player.name, 'color': player.color_value},
                                                    {'text': f' получает {pulled_card.value}~', 'color': (0, 0, 0)}
                                                ]}]
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)
                                    money_data = f'money|{player.color}|{player.money}%'
                                    player_value_calculation(player.color)

                                    for player2 in players:
                                        player2.conn.send(move_data.encode())
                                        player2.conn.send(money_data.encode())
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, move_data)
                                        information_sent_to('Информация отправлена к', player2.color, money_data)
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                    moving_player_changing(not player.state['double'])

                                case 'pay':
                                    if pulled_card.value:
                                        player.state['pay_btn_active'] = [
                                            player.money >= pulled_card.value * player.pay_multiplier, 'pay sum',
                                            pulled_card.value]
                                        mortgage_btn_check(player.color)
                                        penises_check(player.color)
                                        exchange_check(player.color)
                                        send_player_state(player.color)
                                        set_timer_on_player('to pay', player.color, True)

                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': player.name, 'color': player.color_value},
                                                        {'text': f' должен заплатить {pulled_card.value}~',
                                                         'color': (0, 0, 0)}
                                                    ]}]
                                        message_data = f'message|{json.dumps(message)}%'
                                        log_textbox_.append_messages(message)
                                        for player2 in players:
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player2.color, message_data)
                                    else:
                                        moving_player_changing(not player.state['double'])

                                case 'pay to players':
                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': player.name, 'color': player.color_value},
                                                    {'text': f' должен заплатить {pulled_card.value}~ каждому игроку',
                                                     'color': (0, 0, 0)}
                                                ]}]
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)
                                    for player2 in players:
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, message_data)

                                    player.state['pay_btn_active'] = [
                                        player.money >= pulled_card.value * (len(players) - 1) * player.pay_multiplier,
                                        'players',
                                        pulled_card.value]
                                    mortgage_btn_check(player.color)
                                    penises_check(player.color)
                                    exchange_check(player.color)
                                    send_player_state(player.color)
                                    set_timer_on_player('to pay', player.color, True)

                                case 'pay for white penises':
                                    penises = 0
                                    for tile in all_tiles:
                                        if tile.owner == player.color:
                                            penises += tile.penises
                                    if penises:
                                        player.state['pay_btn_active'] = [
                                            player.money >= pulled_card.value * penises * player.pay_multiplier,
                                            'pay sum', pulled_card.value * penises]
                                        mortgage_btn_check(player.color)
                                        penises_check(player.color)
                                        exchange_check(player.color)
                                        send_player_state(player.color)
                                        set_timer_on_player('to pay', player.color, True)

                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': player.name, 'color': player.color_value},
                                                        {
                                                            'text': f' должен заплатить {pulled_card.value}~ за каждый белый пЭнис, то есть {pulled_card.value * penises}~',
                                                            'color': (0, 0, 0)}
                                                    ]}]
                                        message_data = f'message|{json.dumps(message)}%'
                                        log_textbox_.append_messages(message)
                                        for player2 in players:
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player2.color, message_data)
                                    else:
                                        moving_player_changing(not player.state['double'])
                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': 'У игрока ', 'color': (0, 0, 0)},
                                                        {'text': player.name, 'color': player.color_value},
                                                        {'text': ' нет белых пЭнисов, он не должен ничего платить',
                                                         'color': (0, 0, 0)}
                                                    ]}]
                                        message_data = f'message|{json.dumps(message)}%'
                                        log_textbox_.append_messages(message)
                                        for player2 in players:
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player2.color, message_data)

                                case 'go back':
                                    player.piece_position -= pulled_card.value

                                    pay_btn_check(player.color)
                                    buy_btn_check(player.color)
                                    mortgage_btn_check(player.color)
                                    redeem_btn_check(player.color)
                                    penises_check(player.color)
                                    send_player_state(player.color)

                                    if all_tiles[player.piece_position].family == 'Яйцо':
                                        first_message_part = 'Яйцо отправляет'
                                    else:
                                        first_message_part = 'Яйца отправляют'
                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': f'{first_message_part} игрока ', 'color': (0, 0, 0)},
                                                    {'text': player.name, 'color': player.color_value},
                                                    {'text': ' на 3 клетки назад', 'color': (0, 0, 0)}
                                                ]}]
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)
                                    move_data = f'move|{player.color}|-1|-2%'
                                    for player2 in players:
                                        player2.conn.send(move_data.encode())
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, move_data)
                                        information_sent_to('Информация отправлена к', player2.color, message_data)

                                case 'go to':
                                    player.piece_position = pulled_card.value

                                    pay_btn_check(player.color)
                                    buy_btn_check(player.color)
                                    mortgage_btn_check(player.color)
                                    redeem_btn_check(player.color)
                                    penises_check(player.color)
                                    send_player_state(player.color)

                                    move_data = f'move diagonally|{player.color}|{player.piece_position}%'
                                    if all_tiles[player.piece_position].family == 'Яйцо':
                                        first_message_part = 'Яйцо переносит'
                                    else:
                                        first_message_part = 'Яйца переносят'
                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': f'{first_message_part} игрока ', 'color': (0, 0, 0)},
                                                    {'text': player.name, 'color': player.color_value},
                                                    {'text': f' на поле {all_tiles[player.piece_position].name}',
                                                     'color': (0, 0, 0)}
                                                ]}]
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)
                                    for player2 in players:
                                        player2.conn.send(move_data.encode())
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, move_data)
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                    if all_tiles[player.piece_position].owner == player.color or all_tiles[
                                        player.piece_position].mortgaged:
                                        moving_player_changing(not player.state['double'])

                                case 'go to next':
                                    while all_tiles[player.piece_position].type != pulled_card.value:
                                        player.piece_position += 1
                                        if player.piece_position >= 40:
                                            player.piece_position -= 40

                                    pay_btn_check(player.color)
                                    buy_btn_check(player.color)
                                    mortgage_btn_check(player.color)
                                    redeem_btn_check(player.color)
                                    penises_check(player.color)
                                    send_player_state(player.color)

                                    move_data = f'move diagonally|{player.color}|{player.piece_position}%'
                                    if all_tiles[player.piece_position].family == 'Яйцо':
                                        first_message_part = 'Яйцо переносит'
                                    else:
                                        first_message_part = 'Яйца переносят'
                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': f'{first_message_part} игрока ', 'color': (0, 0, 0)},
                                                    {'text': player.name, 'color': player.color_value},
                                                    {'text': f' на поле {all_tiles[player.piece_position].name}',
                                                     'color': (0, 0, 0)}
                                                ]}]
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)
                                    for player2 in players:
                                        player2.conn.send(move_data.encode())
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, move_data)
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                    if all_tiles[player.piece_position].owner == player.color or all_tiles[
                                        player.piece_position].mortgaged:
                                        moving_player_changing(not player.state['double'])

                                    if (all_tiles[player.piece_position].type == 'infrastructure' and
                                            all_tiles[player.piece_position].owned and
                                            all_tiles[player.piece_position].owner != player.color):
                                        cube1 = random.randint(1, 6)
                                        cube2 = random.randint(1, 6)
                                        if not all_tiles[player.piece_position].full_family:
                                            pay_sum = (cube1 + cube2) * 4
                                        else:
                                            pay_sum = (cube1 + cube2) * 10

                                        player.state['pay_btn_active'] = [
                                            player.money >= pay_sum * player.pay_multiplier, 'player',
                                            all_tiles[player.piece_position].owner,
                                            pay_sum]
                                        mortgage_btn_check(player.color)
                                        penises_check(player.color)
                                        exchange_check(player.color)

                                        owner_player = player_dict[all_tiles[player.piece_position].owner]
                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': player.name, 'color': player.color_value},
                                                        {
                                                            'text': f' должен заплатить игроку {owner_player.name} {pay_sum}~',
                                                            'color': (0, 0, 0)}
                                                    ]}]
                                        message_data = f'message|{json.dumps(message)}%'
                                        log_textbox_.append_messages(message)

                                        cubes_information = f'show cubes|{cube1}|{cube2}%'
                                        pay_command = f'need to pay to player|{all_tiles[player.piece_position].owner}|{pay_sum}%'
                                        for player2 in players:
                                            player2.conn.send(cubes_information.encode())
                                            player2.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player2.color,
                                                                cubes_information)
                                            information_sent_to('Информация отправлена к', player2.color, message_data)
                                        player.conn.send(pay_command.encode())
                                        information_sent_to('Информация отправлена к', player.color, pay_command)

                                        send_player_state(player.color)

                                case 'go to prison':
                                    player.doubles_count = 0
                                    player.piece_position = 10
                                    player.imprisoned = True

                                    pay_btn_check(player.color)
                                    mortgage_btn_check(player.color)
                                    redeem_btn_check(player.color)
                                    exchange_check(player.color)
                                    send_player_state(player.color)

                                    prison_data = f'imprisoned|{player.color}%'
                                    move_data = f'move diagonally|{player.color}|10%'
                                    if all_tiles[player.piece_position].family == 'Яйцо':
                                        first_message_part = 'Яйцо отправляет'
                                    else:
                                        first_message_part = 'Яйца отправляют'
                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': f'{first_message_part} игрока ', 'color': (0, 0, 0)},
                                                    {'text': player.name, 'color': player.color_value},
                                                    {'text': ' в тюрьму. Удачи!', 'color': (0, 0, 0)}
                                                ]}]
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)
                                    for player2 in players:
                                        player2.conn.send(move_data.encode())
                                        player2.conn.send(prison_data.encode())
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, move_data)
                                        information_sent_to('Информация отправлена к', player2.color, prison_data)
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                    moving_player_changing(True)

                                case 'exit prison':
                                    if all_tiles[player.piece_position].family == 'Яйцо':
                                        player.egg_prison_exit_card = True
                                    else:
                                        player.eggs_prison_exit_card = True

                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': player.name, 'color': player.color_value},
                                                    {'text': ' вытягивает карточку выхода из тюрьмы',
                                                     'color': (0, 0, 0)}
                                                ]}]
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)
                                    prison_escape_data = f'free prison escape card|{all_tiles[player.piece_position].family}|{player.color}%'
                                    for player2 in players:
                                        player2.conn.send(prison_escape_data.encode())
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color,
                                                            prison_escape_data)
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                    moving_player_changing(not player.state['double'])

                        elif all_tiles[player.piece_position].owner == player.color or all_tiles[
                            player.piece_position].mortgaged:
                            moving_player_changing(not player.state['double'])

                        money_data = f'money|{player.color}|{player.money}%'
                        player_value_calculation(player.color)

                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, money_data)

                    elif data[0] == 'auction initiate':
                        tile_position = int(data[1])
                        if tile_position == player.piece_position:

                            player.state['buy_btn_active'] = [False, None]
                            player.state['auction_btn_active'] = False
                            player.state['exchange_btn_active'] = False
                            player.state['mortgage_btn_active'] = False
                            player.state['refused_to_buy'] = True
                            send_player_state(player.color)

                            auction_players = players.copy()

                            if len(auction_players) > 0:
                                auction_players.pop(0)  # удаляем того, кто инициировал аукцион

                            for auction_player in auction_players:
                                if auction_player.imprisoned or auction_player.money < all_tiles[
                                    tile_position].price + 20:
                                    auction_players.remove(auction_player)

                            message = [{'type': 'text',
                                        'value': [
                                            {'text': player.name, 'color': player.color_value},
                                            {'text': f' выставляет {all_tiles[tile_position].name} на аукцион',
                                             'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            for player2 in players:
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                            auction_players_who_are_wanting_to_buy = []
                            if len(auction_players) > 0:
                                auction_information = f'auction bid|{tile_position}|{all_tiles[tile_position].price}%'
                                auction_players[0].state['thinking_on_auction'] = [True, tile_position, all_tiles[tile_position].price]
                                auction_players[0].conn.send(auction_information.encode())

                                mortgage_btn_check(auction_players[0].color)
                                penises_check(auction_players[0].color)
                                exchange_check(player.color)

                                send_player_state(auction_players[0].color)

                                information_sent_to('Информация отправлена к', auction_players[0].color,
                                                    auction_information)
                                set_timer_on_player('to accept auction', auction_players[0].color, True)
                            else:
                                moving_player_changing(not players[0].state['double'])
                                print('Игроки не смогли принять участие в аукционе')

                                message = [
                                    {'type': 'text', 'value': [
                                        {'text': 'Игроки не смогли принять участие в аукционе', 'color': (0, 0, 0)}]},
                                    {'type': 'text', 'value': [{'text': 'Аукцион не состоялся', 'color': (0, 0, 0)}]}
                                ]
                                message_data = f'message|{json.dumps(message)}%'
                                log_textbox_.append_messages(message)
                                for player2 in players:
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'auction accept':
                        tile_position = int(data[1])
                        price = int(data[2])
                        auction_information = f'auction bid|{tile_position}|{price}%'

                        mortgage_btn_check(player.color)
                        redeem_btn_check(player.color)
                        exchange_check(player.color)
                        send_player_state(player.color)

                        if auction_players:
                            if auction_players[0].money >= price:
                                auction_players_who_are_wanting_to_buy.append(auction_players[0])
                            auction_players.pop(0)

                            for auction_player in auction_players:
                                if auction_player.imprisoned or auction_player.money < price + 20:
                                    auction_players.remove(auction_player)

                        elif auction_players_who_are_wanting_to_buy:
                            if auction_players_who_are_wanting_to_buy[0].money >= price:
                                auction_players_who_are_wanting_to_buy.append(auction_players_who_are_wanting_to_buy[0])
                            auction_players_who_are_wanting_to_buy.pop(0)

                        if len(auction_players_who_are_wanting_to_buy) == 1:
                            auction_win(tile_position, price)

                        if auction_players:
                            auction_players[0].state['thinking_on_auction'] = [True, tile_position, price]
                            auction_players[0].conn.send(auction_information.encode())
                            information_sent_to('Информация отправлена к', auction_players[0].color,
                                                auction_information)
                            set_timer_on_player('to accept auction', auction_players[0].color, True)

                            message = [{'type': 'text',
                                        'value': [
                                            {'text': auction_players_who_are_wanting_to_buy[-1].name,
                                             'color': auction_players_who_are_wanting_to_buy[-1].color_value},
                                            {'text': f' участвует в аукционе. Ставка {price}~', 'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            for player2 in players:
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                        elif auction_players_who_are_wanting_to_buy:
                            auction_players_who_are_wanting_to_buy[0].conn.send(auction_information.encode())
                            information_sent_to('Информация отправлена к',
                                                auction_players_who_are_wanting_to_buy[0].color, auction_information)

                            message = [{'type': 'text',
                                        'value': [
                                            {'text': auction_players_who_are_wanting_to_buy[-1].name,
                                             'color': auction_players_who_are_wanting_to_buy[-1].color_value},
                                            {'text': f' участвует в аукционе. Ставка {price}~', 'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            for player2 in players:
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'auction reject':
                        tile_position = int(data[1])
                        price = int(data[2])
                        reject_auction(player.color)

                    elif data[0] == 'pay':
                        if player.state['pay_btn_active'][0] and not player.state['paid']:
                            if player.state['pay_btn_active'][1] == 'minus':
                                player.state['paid'] = True
                                pay_btn_check(player.color)
                                send_player_state(player.color)

                                multiplier = player.pay_multiplier
                                player.pay_multiplier = 1
                                pay_multiplier_data = f'pay multiplier|{player.color}|{player.pay_multiplier}%'
                                for player2 in players:
                                    player2.conn.send(pay_multiplier_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, pay_multiplier_data)

                                player.money += all_tiles[player.piece_position].price * multiplier
                                message = [{'type': 'text',
                                            'value': [
                                                {'text': player.name, 'color': player.color_value},
                                                {
                                                    'text': f' заплатил Глебу {-all_tiles[player.piece_position].price * multiplier}~',
                                                    'color': (0, 0, 0)}
                                            ]}]
                                message_data = f'message|{json.dumps(message)}%'
                                log_textbox_.append_messages(message)

                                money_data = f'money|{player.color}|{player.money}%'
                                player_value_calculation(player.color)

                                for player2 in players:
                                    player2.conn.send(money_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, money_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(not player.state['double'])

                    elif data[0] == 'pay sum':
                        if player.state['pay_btn_active'][0] and not player.state['paid']:
                            if player.state['pay_btn_active'][1] == 'pay sum':
                                multiplier = player.pay_multiplier
                                player.pay_multiplier = 1
                                pay_multiplier_data = f'pay multiplier|{player.color}|{player.pay_multiplier}%'
                                for player2 in players:
                                    player2.conn.send(pay_multiplier_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, pay_multiplier_data)
                                player.money -= int(data[1]) * multiplier

                                player.state['paid'] = True
                                player.state['pay_btn_active'] = [False, None]
                                buy_btn_check(player.color)
                                penises_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)
                                send_player_state(player.color)

                                message = [{'type': 'text',
                                            'value': [
                                                {'text': player.name, 'color': player.color_value},
                                                {'text': f' заплатил {int(data[1]) * multiplier}~', 'color': (0, 0, 0)}
                                            ]}]
                                message_data = f'message|{json.dumps(message)}%'
                                log_textbox_.append_messages(message)
                                money_data = f'money|{player.color}|{player.money}%'
                                player_value_calculation(player.color)

                                for player2 in players:
                                    player2.conn.send(money_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, money_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(not player.state['double'])

                    elif data[0] == 'payToColor':
                        if player.state['pay_btn_active'][0] and not player.state['paid']:
                            if player.state['pay_btn_active'][1] == 'color':
                                player.state['paid'] = True
                                pay_btn_check(player.color)

                                multiplier = player.pay_multiplier
                                player.pay_multiplier = 1
                                pay_multiplier_data = f'pay multiplier|{player.color}|{player.pay_multiplier}%'
                                for player2 in players:
                                    player2.conn.send(pay_multiplier_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, pay_multiplier_data)

                                pay_sum = all_tiles[player.piece_position].penis_income_calculation() * multiplier
                                player.money -= pay_sum

                                buy_btn_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)
                                send_player_state(player.color)

                                player2 = player_dict[data[2]]
                                player2.money += pay_sum
                                buy_btn_check(player2.color)
                                mortgage_btn_check(player2.color)
                                redeem_btn_check(player2.color)
                                send_player_state(player2.color)

                                message = [{'type': 'text',
                                            'value': [
                                                {'text': player.name, 'color': player.color_value},
                                                {'text': f' заплатил игроку {player2.name} {pay_sum}~', 'color': (0, 0, 0)}
                                            ]}]
                                message_data = f'message|{json.dumps(message)}%'
                                log_textbox_.append_messages(message)
                                money_data1 = f'money|{player2.color}|{player2.money}%'
                                money_data2 = f'money|{player.color}|{player.money}%'
                                player_value_calculation(player2.color)
                                player_value_calculation(player.color)

                                for player3 in players:
                                    player3.conn.send(money_data1.encode())
                                    player3.conn.send(money_data2.encode())
                                    player3.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player3.color, money_data1)
                                    information_sent_to('Информация отправлена к', player3.color, money_data2)
                                    information_sent_to('Информация отправлена к', player3.color, message_data)
                                moving_player_changing(not player.state['double'])

                    elif data[0] == 'pay to player':
                        if player.state['pay_btn_active'][0] and not player.state['paid']:
                            if player.state['pay_btn_active'][1] == 'player':
                                if eggs_players_who_need_to_pay_to_one_player:
                                    eggs_players_who_need_to_pay_to_one_player.remove(player)

                                multiplier = player.pay_multiplier
                                player.pay_multiplier = 1
                                pay_multiplier_data = f'pay multiplier|{player.color}|{player.pay_multiplier}%'
                                for player2 in players:
                                    player2.conn.send(pay_multiplier_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, pay_multiplier_data)
                                player.money -= int(data[2]) * multiplier

                                player.state['paid'] = True
                                player.state['pay_btn_active'] = [False, None]
                                buy_btn_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)
                                send_player_state(player.color)

                                player2 = player_dict[data[1]]
                                player2.money += int(data[2]) * multiplier
                                buy_btn_check(player2.color)
                                mortgage_btn_check(player2.color)
                                redeem_btn_check(player2.color)
                                send_player_state(player2.color)

                                money_data1 = f'money|{player2.color}|{player2.money}%'
                                player_value_calculation(player2.color)

                                message = [{'type': 'text',
                                            'value': [
                                                {'text': player.name, 'color': player.color_value},
                                                {'text': f'заплатил игроку', 'color': (0, 0, 0)},
                                                {'text': player2.name, 'color': player2.color_value},
                                                {'text': f'{int(data[2]) * multiplier}~', 'color': (0, 0, 0)},
                                            ]}]
                                message_data = f'message|{json.dumps(message)}%'
                                log_textbox_.append_messages(message)

                                if not eggs_players_who_need_to_pay_to_one_player:
                                    moving_player_changing(not player.state['double'])
                                money_data2 = f'money|{player.color}|{player.money}%'
                                player_value_calculation(player.color)

                                for player3 in players:
                                    player3.conn.send(money_data1.encode())
                                    player3.conn.send(money_data2.encode())
                                    player3.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player3.color, money_data1)
                                    information_sent_to('Информация отправлена к', player3.color, money_data2)
                                    information_sent_to('Информация отправлена к', player3.color, message_data)
                                # moving_player_changing(not player.state['double'])

                    elif data[0] == 'pay to players':
                        if player.state['pay_btn_active'][0] and not player.state['paid']:
                            if player.state['pay_btn_active'][1] == 'players':
                                multiplier = player.pay_multiplier
                                player.pay_multiplier = 1
                                pay_multiplier_data = f'pay multiplier|{player.color}|{player.pay_multiplier}%'
                                for player2 in players:
                                    player2.conn.send(pay_multiplier_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, pay_multiplier_data)
                                player.money -= int(data[1]) * (len(players) - 1) * multiplier

                                player.state['paid'] = True
                                player.state['pay_btn_active'] = [False, None]
                                buy_btn_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)
                                send_player_state(player.color)

                                money_data2 = f'money|{player.color}|{player.money}%'
                                player_value_calculation(player.color)

                                for player2 in players:
                                    if player2 != player:
                                        player2.money += int(data[1]) * multiplier

                                        buy_btn_check(player2.color)
                                        mortgage_btn_check(player2.color)
                                        redeem_btn_check(player2.color)
                                        send_player_state(player.color)

                                        money_data1 = f'money|{player2.color}|{player2.money}%'
                                        player_value_calculation(player2.color)

                                        message = [{'type': 'text',
                                                    'value': [
                                                        {'text': player.name, 'color': player.color_value},
                                                        {
                                                            'text': f' заплатил игроку {player2.name} {int(data[1]) * multiplier}~',
                                                            'color': (0, 0, 0)}
                                                    ]}]
                                        message_data = f'message|{json.dumps(message)}%'
                                        log_textbox_.append_messages(message)

                                        for player3 in players:
                                            player3.conn.send(money_data1.encode())
                                            player3.conn.send(message_data.encode())
                                            information_sent_to('Информация отправлена к', player3.color, money_data1)
                                            information_sent_to('Информация отправлена к', player3.color, message_data)

                                for player3 in players:
                                    player3.conn.send(money_data2.encode())
                                    information_sent_to('Информация отправлена к', player3.color, money_data2)
                                moving_player_changing(not player.state['double'])

                    elif data[0] == 'pay for prison':
                        if player.state['pay_btn_active'][0] and not player.state['paid']:
                            if player.state['pay_btn_active'][1] == 'prison':
                                multiplier = player.pay_multiplier
                                player.pay_multiplier = 1
                                pay_multiplier_data = f'pay multiplier|{player.color}|{player.pay_multiplier}%'
                                for player2 in players:
                                    player2.conn.send(pay_multiplier_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, pay_multiplier_data)
                                if player.money - (player.prison_break_attempts + 1) * 25 * multiplier >= 0:
                                    player.money -= (player.prison_break_attempts + 1) * 25 * multiplier
                                    player.imprisoned = False

                                    player.state['paid'] = True
                                    pay_btn_check(player.color)
                                    buy_btn_check(player.color)
                                    mortgage_btn_check(player.color)
                                    redeem_btn_check(player.color)
                                    exchange_check(player.color)
                                    send_player_state(player.color)

                                    money_data = f'money|{player.color}|{player.money}%'
                                    player_value_calculation(player.color)

                                    message = [{'type': 'text',
                                                'value': [
                                                    {'text': player.name, 'color': player.color_value},
                                                    {
                                                        'text': f' заплатил {(player.prison_break_attempts + 1) * 25 * multiplier}~ за выход из тюрьмы',
                                                        'color': (0, 0, 0)}
                                                ]}]
                                    player.prison_break_attempts = 0
                                    message_data = f'message|{json.dumps(message)}%'
                                    log_textbox_.append_messages(message)
                                    prison_data = f'unimprisoned|{player.color}%'
                                    for player2 in players:
                                        player2.conn.send(prison_data.encode())
                                        player2.conn.send(money_data.encode())
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, prison_data)
                                        information_sent_to('Информация отправлена к', player2.color, money_data)
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                    moving_player_changing(False)

                    elif data[0] == 'prison exit by eggs':
                        prison_data = ''
                        if player.egg_prison_exit_card and data[1] == 'Яйцо':
                            player.egg_prison_exit_card = False
                            player.imprisoned = False
                            player.prison_break_attempts = 0

                            mortgage_btn_check(player.color)
                            redeem_btn_check(player.color)
                            exchange_check(player.color)
                            send_player_state(player.color)

                            all_egg.append(egg_exit_prison)
                            prison_data = f'unimprisoned|{player.color}%'

                        elif player.eggs_prison_exit_card and data[1] == 'Яйца':
                            player.eggs_prison_exit_card = False
                            player.imprisoned = False
                            player.prison_break_attempts = 0

                            mortgage_btn_check(player.color)
                            redeem_btn_check(player.color)
                            exchange_check(player.color)
                            send_player_state(player.color)

                            all_eggs.append(eggs_exit_prison)
                            prison_data = f'unimprisoned|{player.color}%'

                        for player2 in players:
                            player2.conn.send(prison_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, prison_data)

                    elif data[0] == 'double or nothing':
                        if player.dn_card and player.state['pay_btn_active'][1]:
                            player.dn_card = False
                            is_debt_doubled = random.choice([True, False])
                            if is_debt_doubled:
                                player.pay_multiplier = 2

                                pay_btn_check(player.color)
                                buy_btn_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)

                                send_player_state(player.color)

                                pay_amount = 9999  # placeholder
                                if player.state['pay_btn_active'][1] == 'minus':
                                    pay_amount = -all_tiles[player.piece_position].price * player.pay_multiplier
                                elif player.state['pay_btn_active'][1] == 'pay sum':
                                    pay_amount = player.state['pay_btn_active'][2] * player.pay_multiplier
                                elif player.state['pay_btn_active'][1] == 'color':
                                    pay_amount = all_tiles[
                                                     player.piece_position].penis_income_calculation() * player.pay_multiplier
                                elif player.state['pay_btn_active'][1] == 'player':
                                    pay_amount = player.state['pay_btn_active'][3] * player.pay_multiplier
                                elif player.state['pay_btn_active'][1] == 'players':
                                    pay_amount = player.state['pay_btn_active'][2] * (
                                                len(players) - 1) * player.pay_multiplier
                                elif player.state['pay_btn_active'][1] == 'prison':
                                    pay_amount = (player.prison_break_attempts + 1) * 25 * player.pay_multiplier

                                message = [
                                    {'type': 'text',
                                     'value': [
                                         {'text': player.name, 'color': player.color_value},
                                         {'text': ' использовал Double or nothing', 'color': (0, 0, 0)}
                                     ]},
                                    {'type': 'text',
                                     'value': [
                                         {'text': player.name, 'color': player.color_value},
                                         {'text': f' удвоил свой долг, и теперь он составляет {pay_amount}~',
                                          'color': (0, 0, 0)}
                                     ]}
                                ]
                            else:
                                player.pay_multiplier = 0

                                pay_btn_check(player.color)
                                buy_btn_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)

                                send_player_state(player.color)

                                message = [
                                    {'type': 'text',
                                     'value': [
                                         {'text': player.name, 'color': player.color_value},
                                         {'text': ' использует Double or nothing', 'color': (0, 0, 0)}
                                     ]},
                                    {'type': 'text',
                                     'value': [
                                         {'text': player.name, 'color': player.color_value},
                                         {'text': ' успешно обнуляет свой долг', 'color': (0, 0, 0)}
                                     ]}
                                ]

                            pay_multiplier_data = f'pay multiplier|{player.color}|{player.pay_multiplier}%'
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            for player2 in players:
                                player2.conn.send(message_data.encode())
                                player2.conn.send(pay_multiplier_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, message_data)
                                information_sent_to('Информация отправлена к', player2.color, pay_multiplier_data)

                    elif data[0] == 'penis build':
                        tile = all_tiles[int(data[1])]
                        # print(all_tiles[tile_position].full_family, all_tiles[tile_position].penises < 5, player.money >= all_tiles[tile_position].penis_price, all_tiles[tile_position].type == 'buildable', all_tiles[tile_position].owner == player.color)
                        if (tile.full_family and
                                tile.owner == player.color and
                                tile.type == 'buildable' and
                                player.state['on_move'] and
                                not player.imprisoned and
                                not tile.recently_built and
                                player.money >= tile.penis_price and
                                tile.penises < 5):

                            for tile_ in all_tiles:
                                if tile_.family == tile.family:
                                    tile_.recently_built = True
                            player.money -= tile.penis_price
                            tile.penises += 1

                            penises_check(player.color)
                            buy_btn_check(player.color)
                            mortgage_btn_check(player.color)
                            redeem_btn_check(player.color)
                            send_player_state(player.color)

                            message = [{'type': 'text',
                                        'value': [
                                            {'text': player.name, 'color': player.color_value},
                                            {'text': f' суёт пЭнис в {tile.name} и тратит {tile.penis_price}~',
                                             'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            money_data = f'money|{player.color}|{player.money}%'
                            player_value_calculation(player.color)

                            penis_data = f'penis built|{tile.position}%'
                            for player2 in players:
                                player2.conn.send(money_data.encode())
                                player2.conn.send(penis_data.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, money_data)
                                information_sent_to('Информация отправлена к', player2.color, penis_data)
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'penis remove':
                        tile = all_tiles[int(data[1])]
                        # print(all_tiles[tile_position].full_family, all_tiles[tile_position].penises, all_tiles[tile_position].type, all_tiles[tile_position].owner)
                        if player.state['penis_remove_btn_active']:

                            player.money += tile.penis_price
                            tile.penises -= 1

                            penises_check(player.color)
                            pay_btn_check(player.color)
                            buy_btn_check(player.color)
                            mortgage_btn_check(player.color)

                            send_player_state(player.color)

                            message = [{'type': 'text',
                                        'value': [
                                            {'text': player.name, 'color': player.color_value},
                                            {'text': f' высовывает пЭнис из {tile.name} и получает {tile.penis_price}~',
                                             'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            money_data = f'money|{player.color}|{player.money}%'
                            player_value_calculation(player.color)

                            penis_data = f'penis removed|{tile.position}%'
                            for player2 in players:
                                player2.conn.send(money_data.encode())
                                player2.conn.send(penis_data.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, money_data)
                                information_sent_to('Информация отправлена к', player2.color, penis_data)
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'exchange request':
                        player2 = player_dict[data[3]]
                        message = [{'type': 'text',
                                    'value': [
                                        {'text': player.name, 'color': player.color_value},
                                        {'text': f' предлагает игроку {player2.name} обмен', 'color': (0, 0, 0)}
                                    ]}]
                        message_data = f'message|{json.dumps(message)}%'
                        log_textbox_.append_messages(message)
                        exchange_request = f'exchange request|{data[1]}|{data[2]}|{player.color}%'
                        player2.conn.send(exchange_request.encode())
                        player2.state['thinking_on_exchange'] = True
                        information_sent_to('Информация отправлена к', player2.color, exchange_request)
                        set_timer_on_player('to accept exchange', player2[0].color, True)
                        for player3 in players:
                            player3.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, message_data)

                    elif data[0] == 'exchange':
                        give_data = data[1].split('_')
                        get_data = data[2].split('_')
                        give_money = int(give_data[0])
                        get_money = int(get_data[0])
                        give_property = give_data[1].split('-')
                        get_property = get_data[1].split('-')
                        player.money = player.money - give_money + get_money
                        print(f'Обмен с {data[3]}: +{get_money}~, +{get_property}, -{give_money}~, -{give_property}')

                        get_p_ = ''
                        for p_ in get_property:
                            if p_:
                                get_p_ += f' {all_tiles[int(p_)].name},'
                        get_p_ = get_p_[:-1]

                        give_p_ = ''
                        for p_ in give_property:
                            if p_:
                                give_p_ += f' {all_tiles[int(p_)].name},'
                        give_p_ = give_p_[:-1]

                        if get_p_:
                            conjunction = ' и '
                        else:
                            conjunction = ' '
                        get_m_ = ''
                        if get_money:
                            get_m_ = f'{conjunction}{get_money}~'

                        if get_p_:
                            conjunction = ' и '
                        else:
                            conjunction = ' '
                        give_m_ = ''
                        if give_money:
                            give_m_ = f'{conjunction}{give_money}~'

                        for tile_position in get_property:
                            if tile_position:
                                all_tiles[int(tile_position)].owner = player.color

                        for tile_position in get_property:
                            if tile_position:
                                price_update(all_tiles[int(tile_position)])

                        buy_btn_check(player.color)
                        mortgage_btn_check(player.color)
                        redeem_btn_check(player.color)
                        penises_check(player.color)
                        send_player_state(player.color)

                        player2 = player_dict[data[3]]
                        player2.state['thinking_on_exchange'] = False
                        player2.money = player2.money + give_money - get_money
                        for tile_position in give_property:
                            if tile_position:
                                all_tiles[int(tile_position)].owner = player2.color

                        for tile_position in give_property:
                            if tile_position:
                                price_update(all_tiles[int(tile_position)])

                        buy_btn_check(player2.color)
                        mortgage_btn_check(player2.color)
                        redeem_btn_check(player2.color)
                        penises_check(player2.color)
                        send_player_state(player2.color)

                        message = [
                            {'type': 'text',
                             'value': [
                                 {'text': player.name, 'color': player.color_value},
                                 {'text': f' получает{get_p_}{get_m_}', 'color': (0, 0, 0)}
                             ]},
                            {'type': 'text',
                             'value': [
                                 {'text': player2.name, 'color': player2.color_value},
                                 {'text': f' получает{give_p_}{give_m_}', 'color': (0, 0, 0)}
                             ]}
                        ]
                        message_data = f'message|{json.dumps(message)}%'
                        log_textbox_.append_messages(message)

                        all_property_information = f'all property|{player2.color}|'
                        tiles_count = 0
                        for tile in all_tiles:
                            if tile.owner == player2.color:
                                tiles_count += 1
                                all_property_information += f'{tile.position}_'
                        if tiles_count:
                            all_property_information = all_property_information[:-1] + '%'
                        else:
                            all_property_information = all_property_information + '%'

                        money_data = f'money|{player2.color}|{player2.money}%'
                        player_value_calculation(player2.color)

                        for player3 in players:
                            player3.conn.send(all_property_information.encode())
                            player3.conn.send(money_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, all_property_information)
                            information_sent_to('Информация отправлена к', player3.color, money_data)

                        all_property_information = f'all property|{player.color}|'
                        tiles_count = 0
                        for tile in all_tiles:
                            if tile.owner == player.color:
                                tiles_count += 1
                                all_property_information += f'{tile.position}_'
                        if tiles_count:
                            all_property_information = all_property_information[:-1] + '%'
                        else:
                            all_property_information = all_property_information + '%'

                        money_data = f'money|{player.color}|{player.money}%'
                        player_value_calculation(player.color)

                        for player3 in players:
                            player3.conn.send(all_property_information.encode())
                            player3.conn.send(money_data.encode())
                            player3.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, all_property_information)
                            information_sent_to('Информация отправлена к', player3.color, money_data)
                            information_sent_to('Информация отправлена к', player3.color, message_data)

                    elif data[0] == 'exchange request rejected':
                        player.state['thinking_on_exchange'] = False
                        print(f'Игрок {player.color} отказался от обмена')
                        message = [{'type': 'text',
                                    'value': [
                                        {'text': player.name, 'color': player.color_value},
                                        {'text': ' отказывается от обмена', 'color': (0, 0, 0)}
                                    ]}]
                        message_data = f'message|{json.dumps(message)}%'
                        log_textbox_.append_messages(message)
                        for player3 in players:
                            player3.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, message_data)

                    elif data[0] == 'mortgage':
                        tile = all_tiles[int(data[1])]
                        if not tile.mortgaged and tile.owner == player.color:
                            player.money += int(tile.price / 2)
                            tile.mortgaged = True
                            tile.mortgaged_moves_count = 15

                            for tile_ in all_tiles:
                                if tile_.family == tile.family:
                                    if tile_.owner == tile.owner:
                                        tile_.family_members -= 1
                                        tile_.text_defining(font)

                            try:
                                pay_btn_check(player.color)
                                mortgage_btn_check(player.color)
                                redeem_btn_check(player.color)
                                price_update(tile)
                                buy_btn_check(player.color)
                                penises_check(player.color)
                                exchange_check(player.color)
                                send_player_state(player.color)
                            except:
                                print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')

                            message = [{'type': 'text',
                                        'value': [
                                            {'text': player.name, 'color': player.color_value},
                                            {'text': f' закладывает {tile.name} и получает {int(tile.price / 2)}~',
                                             'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            mortgage_information = f'mortgaged|{data[1]}%'
                            money_information = f'money|{player.color}|{player.money}%'
                            player_value_calculation(player.color)

                            for player2 in players:
                                player2.conn.send(mortgage_information.encode())
                                player2.conn.send(money_information.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, mortgage_information)
                                information_sent_to('Информация отправлена к', player2.color, money_information)
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'redeem':
                        tile = all_tiles[int(data[1])]
                        if tile.mortgaged and tile.owner == player.color:
                            player.money -= int(tile.price)
                            tile.mortgaged = False

                            mortgage_btn_check(player.color)
                            redeem_btn_check(player.color)
                            penises_check(player.color)
                            price_update(tile)
                            buy_btn_check(player.color)

                            send_player_state(player.color)

                            message = [{'type': 'text',
                                        'value': [
                                            {'text': player.name, 'color': player.color_value},
                                            {'text': f' закладывает {tile.name} и тратит {tile.price}~',
                                             'color': (0, 0, 0)}
                                        ]}]
                            message_data = f'message|{json.dumps(message)}%'
                            log_textbox_.append_messages(message)
                            redeem_information = f'redeemed|{data[1]}%'
                            money_information = f'money|{player.color}|{player.money}%'
                            player_value_calculation(player.color)

                            for player2 in players:
                                player2.conn.send(redeem_information.encode())
                                player2.conn.send(money_information.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, redeem_information)
                                information_sent_to('Информация отправлена к', player2.color, money_information)
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'message':
                        message = [{'type': 'text',
                                   'value': [
                                       {'text': f'{player.name}:', 'color': player.color_value},
                                       {'text': data[1], 'color': (0, 0, 0)}]}]  # data[1] содержит текст
                        message_data = f'message|{json.dumps(message)}%'
                        log_textbox_.append_messages(message)

                        for player2 in players:
                            player2.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'surrender':
                        if player.state['surrender_btn_active']:
                            bankrupt_player(player.color)

                    else:
                        player.conn.send(f'error|Незарегистрированная команда: {data[0]}%'.encode())
                        information_sent_to('Информация отправлена к', player.color,
                                            f'error|Незарегистрированная команда: {data[0]}%')

            except (BlockingIOError, ConnectionAbortedError, ConnectionResetError, AttributeError):
                pass
            except:
                print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def accept_file_connections():
    while running:
        try:
            conn, addr = file_sck.accept()
            conn.setblocking(False)
            threading.Thread(target=handle_file_socket, args=(conn,), daemon=True).start()
        except BlockingIOError:
            time.sleep(0.1)
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def handle_file_socket(conn):
    buffer = ''
    player = None

    while player is None and running:
        try:
            data = conn.recv(65536).decode()
            buffer += data
            if '%' in buffer:
                cmd, buffer = buffer.split('%', 1)
                parts = cmd.split('|')
                if parts[0] == 'file_bind':
                    color = parts[1]
                    player = player_dict.get(color)
                    if player:
                        player.file_conn = conn  # сохраняем в объекте Player
                        print(f'Файловый сокет привязан к игроку {color}')
                    else:
                        conn.close()
                        return
        except BlockingIOError:
            time.sleep(0.01)
        except (ConnectionAbortedError, ConnectionResetError, AttributeError):
            pass
        except:
            conn.close()
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')
            return

    while running and player:
        try:
            data = conn.recv(65536).decode()
            if not data:
                break
            buffer += data
            while '%' in buffer:
                cmd, buffer = buffer.split('%', 1)
                process_file_command(cmd, player)
        except BlockingIOError:
            time.sleep(0.01)
        except (ConnectionAbortedError, ConnectionResetError, AttributeError):
            pass
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')
            break
    conn.close()
    if player:
        player.file_conn = None


def process_file_command(cmd, player):
    parts = cmd.split('|')
    information_received('Информация получена', parts[0])
    if parts[0] == 'avatar':
        for player2 in players:
            player2.file_conn.send(f'avatar|{player.color}|{parts[1]}%'.encode())

        image_bytes_decoded = base64.b64decode(parts[1])
        image_decoded = Image.open(io.BytesIO(image_bytes_decoded))
        image_decoded = image_decoded.resize((avatar_side_size, avatar_side_size))
        image_bytes = io.BytesIO()
        image_decoded.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        player.avatar_image = pg.image.load(image_bytes).convert_alpha()
        print('Аватар установлен')

    elif parts[0] == 'sound message':
        audio_bytes_ascii_decoded = parts[1]
        audio_bytes_decoded_base64 = base64.b64decode(audio_bytes_ascii_decoded)
        audio_bytes_decoded = zlib.decompress(audio_bytes_decoded_base64)

        message = [{'type': 'text',
                    'value': [{'text': f'Аудио файл от {player.name}:', 'color': (0, 0, 0)}
                              ]}]
        message_data = f'message|{json.dumps(message)}%'
        log_textbox_.append_messages(message)
        log_textbox_.append_messages([{'type': 'audio',
                                      'value': audio_bytes_decoded,
                                      'color': (0, 0, 0)}])

        sendable_data = f'sound message|{parts[1]}%'

        for player2 in players:
            player2.file_conn.send(message_data.encode())
            player2.file_conn.send(sendable_data.encode())
            information_sent_to('Информация отправлена к', player2.color, message_data)

    elif parts[0] == 'voice message':
        audio_bytes_ascii_decoded = parts[1]
        audio_bytes_decoded_base64 = base64.b64decode(audio_bytes_ascii_decoded)
        audio_bytes_decoded = zlib.decompress(audio_bytes_decoded_base64)
        message = [{'type': 'text', 'value': [{'text': f'Голосовое сообщение от {player.name}:', 'color': (0, 0, 0)}]}]
        message_data = f'message|{json.dumps(message)}%'

        log_textbox_.append_messages(message)

        log_textbox_.append_messages([{'type': 'audio',
                                      'value': audio_bytes_decoded,
                                      'color': (0, 0, 0)}])

        sendable_data = f'voice message|{parts[1]}%'

        for player2 in players:
            player2.file_conn.send(message_data.encode())
            player2.file_conn.send(sendable_data.encode())
            information_sent_to('Информация отправлена к', player2.color, message_data)

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
        message = [{'type': 'text', 'value': [{'text': f'{player.name}: ', 'color': (0, 0, 0)}]}]
        log_textbox_.append_messages(message)
        log_textbox_.append_messages([{'type': 'image', 'value': image}])
        message_data = f'message|{json.dumps(message)}%'

        for player2 in players:
            player2.file_conn.send(message_data.encode())
            player2.file_conn.send(f'image message|{parts[1]}%'.encode())
            information_sent_to('Информация отправлена к', player2.color, message_data)


def players_send():
    for player in players:
        player_data = f'playersData|{player.color}|{player.money}|{player.piece_position}|{player.name}%'
        for player2 in players:
            player2.conn.send(player_data.encode())
            information_sent_to('Информация отправлена к', player2.color, player_data)


def message_send():
    msg_text = log_entry_textbox.get_text()
    if msg_text:
        if msg_text[0] != '~':
            message = [{'type': 'text', 'value': [{'text': f'server: {msg_text}', 'color': (0, 0, 0)}]}]
            log_textbox_.append_messages(message)
            message_data = f'message|{json.dumps(message)}%'
            log_entry_textbox.set_text('')
            for player in players:
                player.conn.send(message_data.encode())
                information_sent_to('Информация отправлена к', player.color, message_data)
        elif debug_mode:
            message_command = msg_text[1:].split(' ')

            if message_command[0] == 'money':
                player = player_dict[message_command[2]]
                if message_command[1] == 'add':
                    player.money += int(message_command[3])
                elif message_command[1] == 'set':
                    player.money = int(message_command[3])
                buy_btn_check(player.color)
                mortgage_btn_check(player.color)
                redeem_btn_check(player.color)
                money_data = f'money|{player.color}|{player.money}%'
                for player2 in players:
                    player2.conn.send(money_data.encode())
                    information_sent_to('Информация отправлена к', player2.color, money_data)

            elif message_command[0] == 'set_state':
                player = player_dict[message_command[1]]
                new_state_type = message_command[2]

                is_state_determined = False
                if message_command[3] in ('True', 'true', '1'):
                    new_state_value = True
                    is_state_determined = True
                elif message_command[3] in ('False', 'false', '0'):
                    new_state_value = False
                    is_state_determined = True

                if is_state_determined:
                    player.state[new_state_type] = new_state_value
                send_player_state(player.color)

            elif message_command[0] == 'buy':
                player = player_dict[message_command[1]]
                tile_position = int(message_command[2])
                all_tiles[tile_position].owned = True
                all_tiles[tile_position].owner = player.color
                player.money -= int(all_tiles[tile_position].price)

                price_update(all_tiles[tile_position])
                mortgage_btn_check(player.color)
                redeem_btn_check(player.color)
                exchange_check(player.color)
                send_player_state(player.color)

                property_data = f'property|{player.color}|{tile_position}%'
                message = [{'type': 'text',
                            'value': [
                                {'text': player.name, 'color': player.color_value},
                                {
                                    'text': f' приобретает {all_tiles[tile_position].name} за {int(all_tiles[tile_position].price)}~',
                                    'color': (0, 0, 0)}
                            ]}]
                message_data = f'message|{json.dumps(message)}%'
                log_textbox_.append_messages(message)
                money_data = f'money|{player.color}|{player.money}%'
                player_value_calculation(player.color)

                for player2 in players:
                    player2.conn.send(property_data.encode())
                    player2.conn.send(money_data.encode())
                    player2.conn.send(message_data.encode())
                    information_sent_to('Информация отправлена к', player2.color, property_data)
                    information_sent_to('Информация отправлена к', player2.color, money_data)
                    information_sent_to('Информация отправлена к', player2.color, message_data)


def connection():
    while not state['is_game_started'] and running:
        time.sleep(0.1)
        if colors[0] == 'red':
            color_value = (255, 0, 0)
        elif colors[0] == 'blue':
            color_value = (0, 0, 255)
        elif colors[0] == 'yellow':
            color_value = (255, 255, 0)
        elif colors[0] == 'green':
            color_value = (10, 160, 10)
        player = Player('', '', colors[0], color_value)
        player_dict[player.color] = player
        try:
            player.connect(colors)
            players.append(player)
            start_button.enable()
            globals()[f'{player.color}_profile'] = pg.image.load(
                f'resources/{resolution_folder}/profile/{player.color}_profile.png').convert_alpha()
            globals()[f'{player.color}_property_image'] = pg.image.load(
                f'resources/{resolution_folder}/property/{player.color}_property.png').convert_alpha()
            print(f'Игрок с цветом {player.color} добавлен в список')
            player.timer_bar = ProgressBar(profile_coordinates[len(players) - 1]['timer_bar'], color_value, 1)
        except BlockingIOError:
            pass
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def disconnect_check():
    while running:
        time.sleep(1)
        for player in players:
            try:
                time_ = time.time()
                player.conn.send(f'ping|{time_}%'.encode())
                player.connection_errors = 0
            except:
                player.connection_errors += 1
                if player.connection_errors >= 5:
                    colors.append(player.color)
                    deleted_color = player.color
                    message = [{'type': 'text',
                                'value': [
                                    {'text': player.name, 'color': player.color_value},
                                    {'text': ' отключился', 'color': (0, 0, 0)}
                                ]}]
                    log_textbox_.append_messages(message)
                    print(f'Игрок {player.color} отключился.\nЦвет {player.color} возвращён')
                    player.clear()
                    players.remove(player)
                    if not len(players):
                        start_button.disable()
                    players_send()
                    message_data = f'message|{json.dumps(message)}%'
                    deletion_player_data = f'playerDeleted|{deleted_color}%'
                    for player2 in players:
                        player2.conn.send(deletion_player_data.encode())
                        player2.conn.send(message_data.encode())
                        information_sent_to('Информация отправлена к', player2.color, deletion_player_data)
                        information_sent_to('Информация отправлена к', player2.color, message_data)


def start_server():
    global colors, main_sck, file_sck
    if not state['is_server_started']:
        try:
            ip_ = ip_textbox.get_text()
            port = port_textbox.get_text()
            port = int(port)

            main_sck = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
            main_sck.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)
            main_sck.bind((ip_, port))
            main_sck.setblocking(False)
            main_sck.listen(4)  # количество доступных подключений

            # Файловый сокет
            FILE_PORT = port + 1
            file_sck = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
            file_sck.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)
            file_sck.bind((ip_, FILE_PORT))
            file_sck.setblocking(False)
            file_sck.listen(4)

            colors = ['red', 'blue', 'yellow', 'green']
            random.shuffle(colors)
            state['is_server_started'] = True
            log_entry_button.enable()

            connection_handler = threading.Thread(target=connection, name='connection_handler', daemon=True)
            connection_handler.start()
            thread_open('Поток открыт', connection_handler.name)

            receive_handler = threading.Thread(target=receive_data, name='receive_handler', daemon=True)
            receive_handler.start()
            thread_open('Поток открыт', receive_handler.name)

            disconnect_handler = threading.Thread(target=disconnect_check, name='disconnect_handler', daemon=True)
            disconnect_handler.start()
            thread_open('Поток открыт', disconnect_handler.name)

            file_acceptor = threading.Thread(target=accept_file_connections, daemon=True)
            file_acceptor.start()
            thread_open('Поток открыт', file_acceptor.name)

            print(f'Сервер открыт: {ip}:{port}')

        except:
            print(f'{"\033[31m{}".format('Не удалось создать сервер')}{'\033[0m'}')


def start_game():
    global first_player_color, PLAYER_TIMER_UPDATE
    if state['is_server_started'] and not state['is_game_started']:
        state['is_game_started'] = True
        random.shuffle(players)
        game_started_command = 'gameStarted|'
        for player in players:
            game_started_command += f'{player.color}_'
        game_started_command = game_started_command[:-1] + '%'

        first_player_color = players[0].color
        players[0].state['on_move'] = True
        players[0].state['throw_cubes_btn_active'] = True
        for tile in all_tiles:
            tile.recently_built = False
        penises_check(players[0].color)
        surrender_check(players[0].color)
        exchange_check(players[0].color)

        if players[0].imprisoned:
            players[0].state['pay_btn_active'] = [
                players[0].money >= (players[0].prison_break_attempts + 1) * 25 * players[0].pay_multiplier, 'prison',
                (players[0].prison_break_attempts + 1) * 25]
        send_player_state(players[0].color)

        PLAYER_TIMER_UPDATE = pg.event.custom_type()
        if play_with_timer:
            pg.time.set_timer(PLAYER_TIMER_UPDATE, 1000)

        set_timer_on_player('to move', players[0].color, True)

        print('Игра начата')

        for player in players:
            player.conn.send(game_started_command.encode())
            information_sent_to('Информация отправлена к', player.color, game_started_command)


def moving_player_changing(do_change):
    try:
        if do_change:
            players[0].state['on_move'] = False
            players[0].state['throw_cubes_btn_active'] = False

            pay_btn_check(players[0].color)
            mortgage_btn_check(players[0].color)
            redeem_btn_check(players[0].color)
            penises_check(players[0].color)
            buy_btn_check(players[0].color)
            exchange_check(players[0].color)
            surrender_check(players[0].color)

            send_player_state(players[0].color)

            mortgage_tile_needs_update = False
            player_chosen = False
            while not player_chosen:
                players.append(players[0])
                players.pop(0)
                if not players[0].bankrupt:
                    player_chosen = True
                if players[0].color == first_player_color:
                    mortgage_tile_needs_update = True

            if player_chosen:
                if mortgage_tile_needs_update:
                    for tile in all_tiles:
                        if tile.mortgaged:
                            tile.mortgaged_moves_count -= 1
                            mortgaged_moves_count_information = f'mortgaged_moves_count|{tile.position}|{tile.mortgaged_moves_count}%'
                            for player2 in players:
                                player2.conn.send(mortgaged_moves_count_information.encode())
                                information_sent_to('Информация отправлена к', player2.color, mortgaged_moves_count_information)
                            if tile.mortgaged_moves_count == 0:
                                player = player_dict[tile.owner]
                                message = [{'type': 'text',
                                            'value': [
                                                {'text': player.name, 'color': player.color_value},
                                                {'text': f'не смог выкупить {tile.name}', 'color': (0, 0, 0)}
                                            ]}]
                                message_data = f'message|{json.dumps(message)}%'
                                log_textbox_.append_messages(message)
                                tile.reset_tile()

                                late_to_redeem_information = f'late to redeem|{tile.position}%'
                                for player2 in players:
                                    player2.conn.send(late_to_redeem_information.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, late_to_redeem_information)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
            else:
                message = [{'type': 'text',
                            'value': [
                                {'text': f'Ни одного игрока не осталось, все проиграли...', 'color': (0, 0, 0)}
                            ]}]
                message_data = f'message|{json.dumps(message)}%'
                log_textbox_.append_messages(message)
                for player2 in players:
                    player2.conn.send(message_data.encode())
                    information_sent_to('Информация отправлена к', player2.color, message_data)
                return

        players[0].state['on_move'] = True
        players[0].state['throw_cubes_btn_active'] = True
        for tile in all_tiles:
            tile.recently_built = False

        pay_btn_check(players[0].color)
        redeem_btn_check(players[0].color)
        penises_check(players[0].color)
        mortgage_btn_check(players[0].color)
        exchange_check(players[0].color)
        buy_btn_check(players[0].color)
        surrender_check(players[0].color)

        send_player_state(players[0].color)
        set_timer_on_player('to move', players[0].color, True)
    except:
        print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


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


def auction_win(tile_position, price):
    for player in players:
        if player == auction_players_who_are_wanting_to_buy[0]:
            player.state['thinking_on_auction'] = [False]
            auction_players_who_are_wanting_to_buy.clear()
            player.money -= price
            all_tiles[tile_position].owner = player.color
            all_tiles[tile_position].owned = True

            price_update(all_tiles[tile_position])

            for player2 in players:
                if player2 != player:
                    if tile_position == player.piece_position:
                        player.state['refused to buy'] = True

            pay_btn_check(player.color)
            buy_btn_check(player.color)
            mortgage_btn_check(player.color)
            redeem_btn_check(player.color)

            send_player_state(player.color)

            message = [{'type': 'text',
                       'value': [
                           {'text': f'{player.name}', 'color': player.color_value},
                           {
                               'text': f'побеждает в аукционе и приобретает {all_tiles[tile_position].name} за {price}~',
                               'color': (0, 0, 0)}]}]
            log_textbox_.append_messages(message)

            message_data = f'message|{json.dumps(message)}%'
            property_data = f'property|{player.color}|{tile_position}%'
            money_data = f'money|{player.color}|{player.money}%'
            player_value_calculation(player.color)

            for player3 in players:
                player3.conn.send(property_data.encode())
                player3.conn.send(money_data.encode())
                player3.conn.send(message_data.encode())
                information_sent_to('Информация отправлена к', player3.color, property_data)
                information_sent_to('Информация отправлена к', player3.color, money_data)
                information_sent_to('Информация отправлена к', player3.color, message_data)
            print('Аукцион прошёл успешно!')
            moving_player_changing(not players[0].state['double'])


def reject_auction(player_color):
    player = player_dict[player_color]
    tile_position, price = player.state['thinking_on_auction'][1], player.state['thinking_on_auction'][2]
    auction_information = f'auction bid|{tile_position}|{price}%'
    player.state['thinking_on_auction'] = [False]

    mortgage_btn_check(player.color)
    redeem_btn_check(player.color)
    exchange_check(player.color)
    send_player_state(player.color)

    message = [{'type': 'text',
                'value': [
                    {'text': player.name, 'color': player.color_value},
                    {'text': ' отказался от участия в аукционе', 'color': (0, 0, 0)}
                ]}]
    message_data = f'message|{json.dumps(message)}%'
    log_textbox_.append_messages(message)
    for player2 in players:
        player2.conn.send(message_data.encode())
        information_sent_to('Информация отправлена к', player2.color, message_data)

    if auction_players:
        auction_players.pop(0)
    elif auction_players_who_are_wanting_to_buy:
        auction_players_who_are_wanting_to_buy.pop(0)

    if auction_players:
        auction_players[0].conn.send(auction_information.encode())
        auction_players[0].state['thinking_on_auction'] = [True, tile_position, price]
        information_sent_to('Информация отправлена к', auction_players[0].color,
                            auction_information)
        set_timer_on_player('to accept auction', auction_players[0].color, True)

    elif auction_players_who_are_wanting_to_buy:
        if len(auction_players_who_are_wanting_to_buy) > 1:
            auction_players_who_are_wanting_to_buy[0].conn.send(auction_information.encode())
            information_sent_to('Информация отправлена к',
                                auction_players_who_are_wanting_to_buy[0].color,
                                auction_information)
            set_timer_on_player('to accept auction', auction_players_who_are_wanting_to_buy[0].color, True)
        else:
            auction_win()
    else:
        moving_player_changing(not players[0].state['double'])
        print('Все игроки отказались от аукциона')

        message = [
            {'type': 'text', 'value': [
                {'text': 'Все игроки отказались от участия в аукционе', 'color': (0, 0, 0)}]},
            {'type': 'text', 'value': [{'text': 'Аукцион не состоялся', 'color': (0, 0, 0)}]}
        ]
        message_data = f'message|{json.dumps(message)}%'
        log_textbox_.append_messages(message)
        for player2 in players:
            player2.conn.send(message_data.encode())
            information_sent_to('Информация отправлена к', player2.color, message_data)


def bankrupt_player(color):
    player = player_dict[color]
    player.bankrupt = True
    player.active_timer = False
    player.timer_bar.set_percentage(1)
    messages = []

    if player.state['pay_btn_active'][1] == 'prison':
        pay_amount = (player.prison_break_attempts + 1) * 25 * player.pay_multiplier
        if player.money >= pay_amount:
            player.money -= pay_amount
            player_value_calculation(player.color)
            paid = pay_amount
        else:
            if player.value >= pay_amount:
                player.value -= pay_amount
                player.money = 0
                paid = pay_amount
            else:
                paid = int(player.value)
                player.value = 0
                player.money = 0

            value_information = f'value|{player.color}|{player.value}%'
            for player2 in players:
                player2.conn.send(value_information.encode())
                information_sent_to('Информация отправлена к', player2.color, value_information)

        messages.append({'type': 'text',
                         'value': [
                             {'text': player.name, 'color': player.color_value},
                             {'text': f' заплатил {paid}~ за выход из тюрьмы', 'color': (0, 0, 0)}
                         ]})

        money_data = f'money|{player.color}|{player.money}%'
        for player2 in players:
            player2.conn.send(money_data.encode())
            information_sent_to('Информация отправлена к', player2.color, money_data)

    elif player.state['pay_btn_active'][1] == 'minus':
        pay_amount = -all_tiles[player.piece_position].price * player.pay_multiplier
        if player.money >= pay_amount:
            player.money -= pay_amount
            player_value_calculation(player.color)
            paid = pay_amount

        else:
            if player.value >= pay_amount:
                player.value -= pay_amount
                player.money = 0
                paid = pay_amount
            else:
                paid = int(player.value)
                player.value = 0
                player.money = 0

            value_information = f'value|{player.color}|{player.value}%'
            for player2 in players:
                player2.conn.send(value_information.encode())
                information_sent_to('Информация отправлена к', player2.color, value_information)

        messages.append({'type': 'text',
                         'value': [
                             {'text': player.name, 'color': player.color_value},
                             {'text': f' заплатил Глебу {paid}~', 'color': (0, 0, 0)}
                         ]})

        money_data = f'money|{player.color}|{player.money}%'
        for player2 in players:
            player2.conn.send(money_data.encode())
            information_sent_to('Информация отправлена к', player2.color, money_data)

    elif player.state['pay_btn_active'][1] == 'pay sum':
        pay_amount = player.state['pay_btn_active'][2] * player.pay_multiplier
        if player.money >= pay_amount:
            player.money -= pay_amount
            player_value_calculation(player.color)
            paid = pay_amount

        else:
            if player.value >= pay_amount:
                player.value -= pay_amount
                player.money = 0
                paid = pay_amount
            else:
                paid = int(player.value)
                player.value = 0
                player.money = 0

            value_information = f'value|{player.color}|{player.value}%'
            for player2 in players:
                player2.conn.send(value_information.encode())
                information_sent_to('Информация отправлена к', player2.color, value_information)

        messages.append({'type': 'text',
                         'value': [
                             {'text': player.name, 'color': player.color_value},
                             {'text': f' заплатил {paid}~',
                              'color': (0, 0, 0)}
                         ]})

        money_data = f'money|{player.color}|{player.money}%'
        for player2 in players:
            player2.conn.send(money_data.encode())
            information_sent_to('Информация отправлена к', player2.color, money_data)

    elif player.state['pay_btn_active'][1] == 'color':
        pay_amount = all_tiles[player.piece_position].penis_income_calculation() * player.pay_multiplier
        if player.money >= pay_amount:
            player.money -= pay_amount
            player_value_calculation(player.color)
            player_dict[all_tiles[player.piece_position].owner].money += pay_amount
            paid = pay_amount

        else:
            if player.value >= pay_amount:
                player.value -= pay_amount
                player.money = 0
                player_dict[all_tiles[player.piece_position].owner].money += pay_amount
                paid = pay_amount
            else:
                paid = int(player.value)
                player_dict[all_tiles[player.piece_position].owner].money += player.value
                player.value = 0
                player.money = 0

            value_information = f'value|{player.color}|{player.value}%'
            for player2 in players:
                player2.conn.send(value_information.encode())
                information_sent_to('Информация отправлена к', player2.color, value_information)

        messages.append({'type': 'text',
                         'value': [
                             {'text': player.name, 'color': player.color_value},
                             {'text': f' заплатил игроку', 'color': (0, 0, 0)},
                             {'text': player_dict[all_tiles[player.piece_position].owner].name,
                              'color': player_dict[all_tiles[player.piece_position].owner].color_value},
                             {'text': f'{paid}~', 'color': (0, 0, 0)},
                         ]})

        money_data = f'money|{player.color}|{player.money}%'
        money_data2 = f'money|{player_dict[all_tiles[player.piece_position].owner].color}|{player_dict[all_tiles[player.piece_position].owner].money}%'
        for player2 in players:
            player2.conn.send(money_data.encode())
            player2.conn.send(money_data2.encode())
            information_sent_to('Информация отправлена к', player2.color, money_data)
            information_sent_to('Информация отправлена к', player2.color, money_data2)

    elif player.state['pay_btn_active'][1] == 'player':
        pay_amount = player.state['pay_btn_active'][3] * player.pay_multiplier

        if player.money >= pay_amount:
            player.money -= pay_amount
            player_value_calculation(player.color)
            player_dict[player.state['pay_btn_active'][2]].money += pay_amount
            paid = pay_amount
        else:
            if player.value >= pay_amount:
                player.value -= pay_amount
                player.money = 0
                player_dict[player.state['pay_btn_active'][2]].money += pay_amount
                paid = pay_amount
            else:
                paid = int(player.value)
                player_dict[player.state['pay_btn_active'][2]].money += player.value
                player.value = 0
                player.money = 0

            value_information = f'value|{player.color}|{player.value}%'
            for player2 in players:
                player2.conn.send(value_information.encode())
                information_sent_to('Информация отправлена к', player2.color, value_information)

        messages.append({'type': 'text',
                         'value': [
                             {'text': player.name, 'color': player.color_value},
                             {'text': f' заплатил игроку', 'color': (0, 0, 0)},
                             {'text': player_dict[player.state['pay_btn_active'][2]].name,
                              'color': player_dict[player.state['pay_btn_active'][2]].color_value},
                             {'text': f'{paid}~', 'color': (0, 0, 0)}
                         ]})

        money_data = f'money|{player.color}|{player.money}%'
        money_data2 = f'money|{player_dict[player.state['pay_btn_active'][2]].color}|{player_dict[player.state['pay_btn_active'][2]].money}%'
        for player2 in players:
            player2.conn.send(money_data.encode())
            player2.conn.send(money_data2.encode())
            information_sent_to('Информация отправлена к', player2.color, money_data)
            information_sent_to('Информация отправлена к', player2.color, money_data2)

    elif player.state['pay_btn_active'][1] == 'players':
        pay_amount = player.state['pay_btn_active'][2] * (len(players) - 1) * player.pay_multiplier
        if player.money >= pay_amount:
            player.money -= pay_amount
            for player2 in players:
                if player2 != player:
                    player2.money += pay_amount // (len(players) - 1)
                    paid = pay_amount // (len(players) - 1)
                    player_value_calculation(player2.color)

                    messages.append({'type': 'text',
                                     'value': [
                                         {'text': player.name, 'color': player.color_value},
                                         {'text': f' заплатил игроку', 'color': (0, 0, 0)},
                                         {'text': player2.name, 'color': player2.color_value},
                                         {'text': f'{paid}~', 'color': (0, 0, 0)}
                                     ]})

                    for player3 in players:
                        money_data = f'money|{player2.color}|{player2.money}%'
                        player3.conn.send(money_data.encode())
                        information_sent_to('Информация отправлена к', player3.color, money_data)
            player_value_calculation(player.color)

        else:
            if player.value >= pay_amount:
                player.value -= pay_amount
                player.money = 0
                for player2 in players:
                    if player2 != player:
                        player2.money += pay_amount // (len(players) - 1)
                        paid = pay_amount // (len(players) - 1)
                        player_value_calculation(player2.color)

                        messages.append({'type': 'text',
                                         'value': [
                                             {'text': player.name, 'color': player.color_value},
                                             {'text': f' заплатил игроку', 'color': (0, 0, 0)},
                                             {'text': player2.name, 'color': player2.color_value},
                                             {'text': f'{paid}~', 'color': (0, 0, 0)}
                                         ]})

                        for player3 in players:
                            money_data = f'money|{player2.color}|{player2.money}%'
                            player3.conn.send(money_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, money_data)
            else:
                for player2 in players:
                    if player2 != player:
                        paid = player.value // (len(players) - 1)
                        player2.money += player.value // (len(players) - 1)
                        player_value_calculation(player2.color)

                        messages.append({'type': 'text',
                                         'value': [
                                             {'text': player.name, 'color': player.color_value},
                                             {'text': f' заплатил игроку', 'color': (0, 0, 0)},
                                             {'text': player2.name, 'color': player2.color_value},
                                             {'text': f'{paid}~', 'color': (0, 0, 0)}
                                         ]})

                        for player3 in players:
                            money_data = f'money|{player2.color}|{player2.money}%'
                            player3.conn.send(money_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, money_data)
                player.value = 0
                player.money = 0

        money_data = f'money|{player.color}|{player.money}%'
        player.conn.send(money_data.encode())
        information_sent_to('Информация отправлена к', player.color, money_data)

    if player.state['on_move']:
        moving_player_changing(True)

    if player.state['buy_btn_active'][1]:
        moving_player_changing(True)

    if player.state['thinking_on_auction'][0]:
        reject_auction(player.color)
        return

    if player.state['thinking_on_exchange']:
        return

    player.state['on_move'] = False
    player.state['double'] = False
    player.state['paid'] = False
    player.state['refused_to_buy'] = False
    player.state['throw_cubes_btn_active'] = False
    player.state['buy_btn_active'] = [False, None]
    player.state['pay_btn_active'] = [False, None]
    player.state['penis_build_btn_active'] = False
    player.state['penis_remove_btn_active'] = False
    player.state['mortgage_btn_active'] = False
    player.state['redeem_btn_active'] = False
    player.state['auction_btn_active'] = False
    player.state['exchange_btn_active'] = False
    player.state['surrender_btn_active'] = False
    player.state['thinking_on_auction'] = [False]
    player.state['thinking_on_exchange'] = False
    send_player_state(player.color)

    for tile in all_tiles:
        if tile.owner == player.color:
            tile.reset_tile()

    active_players_count = 0
    last_active_player = None
    for player2 in players:
        if not player2.bankrupt:
            active_players_count += 1
            last_active_player = player2

    messages.append({'type': 'text',
                     'value': [
                         {'text': player.name, 'color': player.color_value},
                         {'text': f'объявлен банкротом', 'color': (0, 0, 0)}
                     ]})
    if active_players_count == 1:
        messages.append({'type': 'text',
                         'value': [
                             {'text': last_active_player.name, 'color': last_active_player.color_value},
                             {'text': f'победил!', 'color': (0, 0, 0)}
                         ]})
    message_data = f'message|{json.dumps(messages)}%'
    log_textbox_.append_messages(messages)
    for player2 in players:
        player2.conn.send(message_data.encode())
        information_sent_to('Информация отправлена к', player2.color, message_data)

    for player3 in players:
        surrender_data = f'surrendered|{player.color}%'
        player3.conn.send(surrender_data.encode())
        information_sent_to('Информация отправлена к', player3.color, surrender_data)


def set_timer_on_player(timer_type, color, do_reset_other_timers):
    for player in players:
        if player.color != color and do_reset_other_timers:
            player.time_left = timer_duration['placeholder']
            player.max_time = timer_duration['placeholder']
            player.active_timer = False

            timer_data = f'timer|{player.color}|{player.time_left}|{player.max_time}%'
            for player2 in players:
                player2.conn.send(timer_data.encode())
        else:
            player.time_left = timer_duration[timer_type]
            player.max_time = timer_duration[timer_type]
            player.active_timer = True


def position_update():
    for player in players:
        if player.color == 'red':
            player.x = all_tiles[player.piece_position].x_position
            player.y = all_tiles[player.piece_position].y_position
        elif player.color == 'green':
            player.x = all_tiles[player.piece_position].x_position + piece_color_coefficient
            player.y = all_tiles[player.piece_position].y_position
        elif player.color == 'yellow':
            player.x = all_tiles[player.piece_position].x_position
            player.y = all_tiles[player.piece_position].y_position + piece_color_coefficient
        elif player.color == 'blue':
            player.x = all_tiles[player.piece_position].x_position + piece_color_coefficient
            player.y = all_tiles[player.piece_position].y_position + piece_color_coefficient


def blit_items():
    screen.fill(background_color)
    screen.blit(board_image)
    for tile in all_tiles:
        if tile.owned:
            screen.blit(globals()[f'{tile.owner}_property_image'], (tile.x_position, tile.y_position))

        if tile.mortgaged:
            screen.blit(mortgaged_tile, (tile.x_position, tile.y_position))
            text = font.render(str(tile.mortgaged_moves_count), False, 'white')
            text_rect = text.get_rect(center=(tile.x_center, tile.y_center))
            screen.blit(text, text_rect)

        if 1 <= tile.penises <= 5:
            screen.blit(pg.image.load(f'resources/{resolution_folder}/white penises/{tile.penises}.png'),
                        (tile.x_position, tile.y_position))

    try:
        for player in players:


            player_index = players.index(player)

            player.timer_bar.render(screen, (profile_coordinates[player_index]['timer_bar'][0],
                                             profile_coordinates[player_index]['timer_bar'][1]))
            screen.blit(profile_picture, profile_coordinates[player_index]['profile'])
            screen.blit(player.avatar_image, profile_coordinates[player_index]['avatar'])
            if player.imprisoned:
                screen.blit(player_bars, profile_coordinates[player_index]['avatar'])
            screen.blit(globals()[f'{player.color}_profile'], profile_coordinates[player_index]['avatar'])
            screen.blit(font.render(f'{player.money}~', False, 'black'), profile_coordinates[player_index]['money'])
            screen.blit(font.render(f'{player.value}~', False, 'black'), profile_coordinates[player_index]['value'])
            screen.blit(font.render(player.name, False, 'black'), profile_coordinates[player_index]['name'])
            if player.bankrupt:
                screen.blit(bankrupt_picture, profile_coordinates[player_index]['profile'])
            else:
                screen.blit(pg.image.load(f'resources/{resolution_folder}/pieces/{player.color}_piece.png'), (player.x, player.y))

    except ValueError:
        pass

    screen.blit(bars, (all_tiles[10].x_position, all_tiles[10].y_position))


def price_printing():
    for tile in all_tiles:
        if tile.price != '':
            tile.text_defining(font)
            screen.blit(tile.prerendered_text, tile.text_rect)


def event_handler():
    events = pg.event.get()
    for event in events:
        log_textbox_.process_events(event)
        if event.type == pg.QUIT:
            global running
            running = False
        elif state['is_game_started'] and event.type == PLAYER_TIMER_UPDATE:
            for player in players:
                if player.active_timer:
                    if player.time_left > 0:
                        player.time_left -= 1
                        player.timer_bar.set_percentage(player.time_left / player.max_time)

                        timer_data = f'timer|{player.color}|{player.time_left}|{player.max_time}%'
                        for player2 in players:
                            try:
                                player2.conn.send(timer_data.encode())
                            except:
                                pass
                            # information_sent_to('Информация отправлена к', player2.color, timer_data)
                    else:
                        bankrupt_player(player.color)
        manager.process_events(event)

        match event.type:
            case pygame_gui.UI_BUTTON_PRESSED:
                event_type = event.ui_element
                if event_type == start_server_button:
                    start_server()
                    start_server_button.disable()
                elif event_type == start_button:
                    start_game()
                    start_button.disable()
                elif event_type == log_entry_button:
                    message_send()
                elif event_type == debug_button:
                    debug_output()
                else:
                    for i in range(40):
                        if event_type == globals()[f'tile_{i}_button']:
                            tile_button(i)


def buttons():
    global start_button, ip_textbox, port_textbox, start_server_button, log_entry_textbox, log_entry_button, debug_button
    ip_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['IP']),
        placeholder_text='IP адрес',
        initial_text=ip,
        manager=manager)

    port_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['port']),
        placeholder_text='Порт',
        initial_text='1247',
        manager=manager)

    start_server_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(1040, 534, 217, 38),
        text='Запуск сервера',
        manager=manager)

    start_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(1040, 592, 217, 38),
        text='Начать игру',
        manager=manager)
    start_button.disable()

    log_entry_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(log_textbox_coordinates['user_input_box']),
        placeholder_text='',
        manager=manager)

    log_entry_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(443, 519, 111, 35),
        text='Отправить',
        manager=manager)
    log_entry_button.disable()

    debug_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(start_btn_textboxes_coordinates['debug']),
        text='debug',
        manager=manager)
    if not debug_mode:
        debug_button.hide()

    for i in range(40):
        globals()[f'tile_{i}_button'] = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((all_tiles[i].x_position, all_tiles[i].y_position), tile_size),
            text='',
            manager=manager,
            object_id=pygame_gui.core.ObjectID(class_id='@transparent_buttons', object_id='#tile_button'))


def delta_time(old_time):
    now = time.time()
    dt = now - old_time
    old_time = now
    return dt, old_time


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
              f'{tile.penised_family = }\n'
              f'{tile.recently_built = }\n'
              f'{tile.income = }\n'
              f'{tile.owned = }\n'
              f'{tile.owner = }\n'
              f'{tile.full_family = }\n'
              f'{tile.mortgaged = }\n'
              f'{tile.mortgaged_moves_count = }\n')


def debug_output():
    state['tile_debug'] = not state['tile_debug']
    for player in players:
        print(f'       piece_position: {player.piece_position}\n'
              f'       name: {player.name}\n'
              f'       color: {player.color}\n'
              f'       money: {player.money}\n'
              f'       x: {player.x}\n'
              f'       y: {player.y}\n'
              f'       state: {player.state}\n'
              f'       imprisoned: {player.imprisoned}\n'
              f'       prison_break_attempts: {player.prison_break_attempts}\n'
              f'       egg_prison_exit_card: {player.egg_prison_exit_card}\n'
              f'       eggs_prison_exit_card: {player.eggs_prison_exit_card}\n'
              f'       time_left: {player.time_left}\n'
              f'       max_time: {player.max_time}\n'
              f'       active_timer: {player.active_timer}\n')

    pprint.pp(state)


def send_player_state(color):
    if state['is_game_started']:
        player = player_dict[color]
        sendable_state = {}
        for state_key in player.state:
            if state_key not in ('on_move'):
                sendable_state[state_key] = player.state[state_key]
        json_encoded_state = f'player state|{json.dumps(sendable_state)}%'
        player.conn.send(json_encoded_state.encode())
        information_sent_to('Информация отправлена к', player.color, json_encoded_state)


def pay_btn_check(color):
    if state['is_game_started']:
        player = player_dict[color]
        if not player.bankrupt:
            temp_state = player.state['pay_btn_active']
            if player.state['pay_btn_active'][1] not in ('pay sum', 'player', 'players'):
                temp_state = [False, None]

            elif player.state['pay_btn_active'][1] == 'pay sum':
                temp_state = [player.money >= player.state['pay_btn_active'][2] * player.pay_multiplier, 'pay sum',
                              player.state['pay_btn_active'][2]]

            elif player.state['pay_btn_active'][1] == 'players':
                temp_state = [
                    player.money >= player.state['pay_btn_active'][2] * (len(players) - 1) * player.pay_multiplier,
                    'players', player.state['pay_btn_active'][2]]

            elif player.state['pay_btn_active'][1] == 'player':
                temp_state = [player.money >= player.state['pay_btn_active'][3] * player.pay_multiplier, 'player',
                              player.state['pay_btn_active'][2], player.state['pay_btn_active'][3]]

            if player.imprisoned and player.state['on_move']:
                temp_state = [player.money >= (player.prison_break_attempts + 1) * 25 * player.pay_multiplier,
                              'prison', (player.prison_break_attempts + 1) * 25]

            if not player.state['paid'] and not player.state['refused_to_buy']:
                if player.piece_position == 4 or player.piece_position == 38:
                    temp_state = [player.money >= -all_tiles[player.piece_position].income * player.pay_multiplier,
                                  'minus', -all_tiles[player.piece_position].income]

                elif all_tiles[player.piece_position].owner != player.color and all_tiles[
                    player.piece_position].owned and not all_tiles[player.piece_position].mortgaged and all_tiles[
                    player.piece_position].type != 'infrastructure':
                    temp_state = [player.money >= all_tiles[
                        player.piece_position].penis_income_calculation() * player.pay_multiplier, 'color',
                                  all_tiles[player.piece_position].owner]

            player.state['pay_btn_active'] = temp_state
            # print(f'Состояние pay_btn_active игрока {color} установлено на {player.state['pay_btn_active']}')


def buy_btn_check(color):
    if state['is_game_started']:
        player = player_dict[color]
        if not player.bankrupt:
            temp_state_buy = [False, None]
            temp_state_auc = False
            if all_tiles[player.piece_position].buyable:
                if not player.state['refused_to_buy']:
                    if not all_tiles[player.piece_position].owned:
                        temp_state_buy = [False, player.piece_position]
                        if player.money >= int(all_tiles[player.piece_position].price):
                            temp_state_buy = [True, player.piece_position]
                        temp_state_auc = True

            player.state['buy_btn_active'] = temp_state_buy
            player.state['auction_btn_active'] = temp_state_auc
            # print(f'Состояние buy_btn_active игрока {color} установлено на {player.state['buy_btn_active']}')
            # print(f'Состояние auction_btn_active игрока {color} установлено на {player.state['auction_btn_active']}')


def mortgage_btn_check(color):  # заложить
    if state['is_game_started']:
        player = player_dict[color]
        if not player.bankrupt:
            temp_state = False
            if (player.state['on_move'] or player.state['buy_btn_active'][1] or player.state['pay_btn_active'][1] or
                    (all_tiles[player.piece_position].owner != player.color and all_tiles[
                        player.piece_position].owned and not player.state['paid'] and not player.state[
                        'refused_to_buy'])):
                for tile in all_tiles:
                    if tile.owner == player.color:
                        if not tile.penised_family and not tile.mortgaged:
                            temp_state = True
            player.state['mortgage_btn_active'] = temp_state
            # print(f'Состояние mortgage_btn_active игрока {color} установлено на {player.state['mortgage_btn_active']}')


def redeem_btn_check(color):  # выкупить
    if state['is_game_started']:
        temp_state = False
        for tile in all_tiles:
            if tile.mortgaged:
                player = player_dict[color]
                if player.state['on_move'] and not player.imprisoned and not player.bankrupt:
                    if player.color == tile.owner:
                        if player.money >= tile.price:
                            temp_state = True
                player.state['redeem_btn_active'] = temp_state
                # print(f'Состояние redeem_btn_active игрока {color} установлено на {player.state['redeem_btn_active']}')


def penises_check(color):
    player = player_dict[color]
    if not player.bankrupt:
        temp_state_build = False
        temp_state_remove = False

        for tile in all_tiles:
            if tile.full_family and tile.owner == player.color and tile.type == 'buildable':
                if player.state[
                    'on_move'] and not player.imprisoned and not tile.recently_built and player.money >= tile.penis_price and tile.penises < 5:
                    temp_state_build = True
                if 1 <= tile.penises <= 5 and (player.state['on_move'] or player.state['pay_btn_active'][1] or
                                               player.state['buy_btn_active'][1]):
                    temp_state_remove = True

        player.state['penis_build_btn_active'] = temp_state_build
        player.state['penis_remove_btn_active'] = temp_state_remove
        # print(f'Состояние penis_build_btn_active игрока {color} установлено на {player.state['penis_build_btn_active']}')
        # print(f'Состояние penis_remove_btn_active игрока {color} установлено на {player.state['penis_remove_btn_active']}')


def exchange_check(color):
    if state['is_game_started']:
        player = player_dict[color]

        temp_state = False
        if (player.state['pay_btn_active'][1] not in (None, 'prison') or player.state['on_move']) and not player.bankrupt:
            if len(players) > 1 and not player.imprisoned:
                for tile in all_tiles:
                    if tile.owned:
                        temp_state = True
        player.state['exchange_btn_active'] = temp_state


def surrender_check(color):
    if state['is_game_started']:
        player = player_dict[color]

        temp_state = False
        if (player.state['throw_cubes_btn_active'] or player.state['pay_btn_active'][1] or player.state['buy_btn_active'][1]) and not player.bankrupt:
            temp_state = True
        player.state['surrender_btn_active'] = temp_state


def player_value_calculation(color):
    if state['is_game_started']:
        player = player_dict[color]
        if not player.bankrupt:
            value = player.money
            for tile in all_tiles:
                if tile.owner == color:
                    if not tile.mortgaged:
                        value += int(tile.price / 2)
                    value += tile.penis_price * tile.penises
            player.value = value

            value_information = f'value|{color}|{player.value}%'
            for player2 in players:
                player2.conn.send(value_information.encode())
                information_sent_to('Информация отправлена к', player2.color, value_information)


load_assets()
buttons()
log_textbox_ = Textbox(log_textbox_coordinates['main_box'], 2, 6, 1, font, (0, 0, 0), (200, 200, 200), manager)
theme = manager.create_new_theme(f'resources/{resolution_folder}/gui_theme.json')
manager.set_ui_theme(theme)
running = True

gc.enable()

past_second_fps = []
prev_fps_time = time.time()
prev_time = time.time()
average_fps = 0
average_fps_text = font.render(str(average_fps), False, 'black')

while running:
    clock.tick(FPS)
    dt, prev_time = delta_time(prev_time)
    blit_items()
    price_printing()
    event_handler()
    log_textbox_.render(screen)
    try:
        manager.update(dt)
        manager.draw_ui(screen)
    except:
        pass

    if debug_mode:
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

    pg.display.update()

if log_textbox_:
    del log_textbox_
    if os.path.exists(f'resources/temp/audios'):
        for file in os.listdir('resources/temp/audios'):
            try:
                os.remove(f'resources/temp/audios/{file}')
            except:
                pass

print('Сервер закрыт')
