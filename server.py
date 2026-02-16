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
import magic
import mimetypes
import wave

from Channel_Class import Channel

from all_tiles_extraction import all_tiles_get
from colored_output import thread_open, new_connection, information_received, information_sent_to

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
        self.ready = False
        self.on_move = False
        self.avatar_image = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png').convert_alpha()
        self.x = 0
        self.y = 0
        self.egg_prison_exit_card = False
        self.eggs_prison_exit_card = False
        self.double = False
        self.connection_errors = 0


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
        self.ready = False
        self.on_move = False

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
log_image_size = (128, 128)
debug_mode = True
ip = sck.gethostbyname(sck.gethostname())

profile_coordinates = [{'profile': (669, 20 ),  'avatar': (830, 46 ),  'money': (674, 38 ), 'name': (674, 18 )},
                       {'profile': (669, 169),  'avatar': (830, 195),  'money': (674, 187), 'name': (674, 167)},
                       {'profile': (669, 318),  'avatar': (830, 344),  'money': (674, 336), 'name': (674, 316)},
                       {'profile': (669, 467),  'avatar': (830, 493),  'money': (674, 485), 'name': (674, 465)}]
start_btn_textboxes_coordinates = {'name':           ((1040, 442), (217, 35)),
                                   'IP':            ((1040, 483), (150, 35)),
                                   'port':          ((1196, 483), (65,  35)),
                                   'connect':       ((1040, 534), (217, 38)),
                                   'choose_avatar': ((1040, 592), (217, 38)),
                                   'debug':         ((1040, 384), (140, 38))}
log_textbox_coordinates = {'main_box':                  (95,  95,  459, 426),
                           'user_input_box':            (95,  519, 350, 35),
                           'audio_send_button':         (411, 519, 38,  35),
                           'voice_message_send_button': (446, 519, 38,  35),
                           'image_send_button':         (481, 519, 38,  35),
                           'text_send_button':          (516, 519, 38,  35)}
piece_color_coefficient = 28
TITLE = 'Monopoly Server'
screen = pg.display.set_mode(resolution)
manager = pygame_gui.UIManager(resolution, theme_path=f'resources/{resolution_folder}/gui_theme.json', enable_live_theme_updates=False)
manager.add_font_paths('BulBulPoly', "resources/fonts/bulbulpoly-4.ttf")
manager.preload_fonts([{'name': 'BulBulPoly', 'point_size': f'{font_size}', 'style': 'regular', 'antialiased': '1'}])
pg.display.set_caption(TITLE)
clock = pg.time.Clock()

def load_assets():
    global all_tiles, all_egg, all_eggs
    all_tiles, all_egg, all_eggs = all_tiles_get(resolution_folder, tile_size)
    random.shuffle(all_egg)
    random.shuffle(all_eggs)

    global board_image, profile_picture, bars, player_bars, avatar_file, mortgaged_tile, font, players, state, sound_messages, voice_messages, sound_messages_channel, voice_messages_channel, image_messages, receive_size
    board_image = pg.image.load(f'resources/temp/images/{resolution_folder}/board image.png').convert_alpha()
    profile_picture = pg.image.load(f'resources/{resolution_folder}/profile/profile.png').convert_alpha()
    bars = pg.image.load(f'resources/{resolution_folder}/bars.png').convert_alpha()
    player_bars = pg.image.load(f'resources/{resolution_folder}/profile/profile_bars.png').convert_alpha()
    avatar_file = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png').convert_alpha()
    mortgaged_tile = pg.image.load(f'resources/{resolution_folder}/mortgaged.png').convert_alpha()
    font = pg.font.Font('resources/fonts/bulbulpoly-4.ttf',25)

    players = []
    state = {'is_server_started': False,
             'is_game_started': False,
             'tile_debug': False}
    sound_messages = {}
    voice_messages = {}
    sound_messages_channel = Channel(0)
    voice_messages_channel = Channel(1)
    image_messages = 0
    receive_size = 1024


def receive_data():
    global auction_players, auction_players_who_are_wanting_to_buy, eggs_players_who_need_to_pay_to_one_player, egg_exit_prison, eggs_exit_prison, receive_size, image_messages
    auction_players = []
    auction_players_who_are_wanting_to_buy = []
    eggs_players_who_need_to_pay_to_one_player = []


    def auction_win():
        for player2 in players:
            if player2 == auction_players_who_are_wanting_to_buy[0]:
                player2.money -= price
                all_tiles[tile_position].owner = player2.color
                all_tiles[tile_position].owned = True
                price_update(all_tiles[tile_position])
                print(f'Владельцем {all_tiles[tile_position].name} является {all_tiles[tile_position].owner}')
                message = (
                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player2.color_value}">{player2.name} </font>'
                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">побеждает в аукционе и приобретает {all_tiles[tile_position].name} за {price}~</font><br>')
                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                if log_textbox.scroll_bar:
                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
        property_data = f'property|{player2.color}|{tile_position}%'
        money_data = f'money|{player2.color}|{player2.money}%'
        message_data = f'message|{message}%'
        for player3 in players:
            player3.conn.send(property_data.encode())
            player3.conn.send(money_data.encode())
            player3.conn.send(message_data.encode())
            information_sent_to('Информация отправлена к', player3.color, property_data)
            information_sent_to('Информация отправлена к', player3.color, money_data)
            information_sent_to('Информация отправлена к', player3.color, message_data)
        print('Аукцион прошёл успешно!')
        moving_player_changing(True)


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
                    # print(tile_.family_members, tile_.name)


    buffer = ''
    while running:
        time.sleep(0.01)
        for player in players:

            try:
                data_unsplit = player.conn.recv(receive_size).decode()
                buffer += data_unsplit
                while '%' in buffer:
                    single_command, buffer = buffer.split('%', 1)
                    data = single_command.split('|')

                    if data[0] != '' and data[0] not in ['avatar', 'sound message', 'voice message']:
                        information_received(f'Информация получена от {player.color}', data)

                    if data[0] == 'name':
                        player.name = data[1]
                        players_send()

                    elif data[0] == 'avatar':
                        for player2 in players:
                            player2.conn.send(f'avatar|{player.color}|{data[1]}%'.encode())

                        image_bytes_decoded = base64.b64decode(data[1])
                        image_decoded = Image.open(io.BytesIO(image_bytes_decoded))
                        image_decoded = image_decoded.resize((avatar_side_size, avatar_side_size))
                        image_bytes = io.BytesIO()
                        image_decoded.save(image_bytes, format='PNG')
                        image_bytes.seek(0)
                        player.avatar_image = pg.image.load(image_bytes).convert_alpha()
                        print('Аватар установлен')

                    elif data[0] == 'move':
                        cube1 = random.randint(1,6)
                        cube2 = random.randint(1,6)
                        # cube1 = 3
                        # cube2 = 4
                        player.double = cube1 == cube2
                        print(f'Дубль игрока {player.color} установлен на {player.double}')

                        if player.imprisoned:
                            if player.double:
                                player.imprisoned = False
                                player.prison_break_attempts = 0
                                player.piece_position += cube1 + cube2
                                prison_data = f'unimprisoned|{player.color}|{cube1}|{cube2}%'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">выходит из тюрьмы</font><br>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">выбросил {cube1}:{cube2} и попал на поле {all_tiles[player.piece_position].name}</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                for player2 in players:
                                    player2.conn.send(prison_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, prison_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)

                            else:
                                player.prison_break_attempts += 1
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">У </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">осталось {3 - player.prison_break_attempts} попытки, чтобы выйти из тюрьмы</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                imprisoned_double_failed_data = f'imprisoned double failed|{player.color}|{cube1}|{cube2}|{player.prison_break_attempts}%'
                                for player2 in players:
                                    player2.conn.send(imprisoned_double_failed_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, imprisoned_double_failed_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                if player.prison_break_attempts < 3:
                                    moving_player_changing(True)

                            if player.prison_break_attempts >= 3:
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">не смог выйти из тюрьмы и должен заплатить {(player.prison_break_attempts + 1) * 25}~</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                prison_bribe_data = f'bribe|{player.color}|{(player.prison_break_attempts + 1) * 25}%'
                                for player2 in players:
                                    player2.conn.send(prison_bribe_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, prison_bribe_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)

                        else:
                            cube_sum = cube1 + cube2
                            player.piece_position += cube_sum

                            move_data = f'move|{player.color}|{cube1}|{cube2}%'

                            for player2 in players:
                                player2.conn.send(move_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, move_data)

                            if player.piece_position > 39:
                                player.piece_position -= 40
                                player.money += 200
                                if player.piece_position != 0:
                                    message = (
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">проходит через поле {all_tiles[0].name} и получает 200~</font><br>')
                                    message_data = f'message|{message}%'
                                    log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                    if log_textbox.scroll_bar:
                                        log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                    for player2 in players:
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, message_data)

                            if player.piece_position == 0:
                                player.money += 100
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">попадает на поле {all_tiles[0].name} и получает 300~</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                for player2 in players:
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, message_data)

                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">выбросил {cube1}:{cube2} и попал на поле {all_tiles[player.piece_position].name}</font><br>')
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                            for player2 in players:
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                            if player.piece_position == 30:
                                player.piece_position = 10
                                player.imprisoned = True
                                prison_data = f'imprisoned|{player.color}%'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">отправляется Туда</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                move_data = f'move diagonally|{player.color}|10%'
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    player2.conn.send(prison_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                    information_sent_to('Информация отправлена к', player2.color, prison_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                if all_tiles[player.piece_position].owner == player.color:
                                    moving_player_changing(True)

                            elif player.piece_position == 10:
                                player.piece_position = 30
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">переносится на поле {all_tiles[player.piece_position].name}</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                move_data = f'move diagonally|{player.color}|30%'
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                if all_tiles[player.piece_position].owner == player.color:
                                    moving_player_changing(not player.double)

                        if all_tiles[player.piece_position].type == 'infrastructure' and all_tiles[player.piece_position].owned and all_tiles[player.piece_position].owner != player.color:
                            cube1 = random.randint(1, 6)

                            if not all_tiles[player.piece_position].full_family:
                                pay_sum = (cube1 + cube2) * 4
                            else:
                                pay_sum = (cube1 + cube2) * 10

                            for player2 in players:
                                if player2.color == all_tiles[player.piece_position].owner:
                                    message = (
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">должен заплатить игроку </font>'
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="{player2.color_value}">{player2.name} </font>'
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{pay_sum}~</font><br>')
                                    message_data = f'message|{message}%'
                                    log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                    if log_textbox.scroll_bar:
                                        log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                            cubes_information = f'show cubes|{cube1}|{cube2}%'
                            pay_command = f'need to pay to player|{all_tiles[player.piece_position].owner}|{pay_sum}%'
                            for player2 in players:
                                player2.conn.send(cubes_information.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, cubes_information)
                                information_sent_to('Информация отправлена к', player2.color, message_data)
                            player.conn.send(pay_command.encode())
                            information_sent_to('Информация отправлена к', player.color, pay_command)

                    elif data[0] == 'nextPlayer':
                        if data[1] == 'True':
                            moving_player_changing(True)
                        else:
                            moving_player_changing(False)

                    elif data[0] == 'buy':
                        if player.piece_position == int(data[1]):
                            player.piece_position = int(data[1])
                            if player.money >= int(all_tiles[player.piece_position].price):
                                all_tiles[player.piece_position].owned = True
                                all_tiles[player.piece_position].owner = player.color
                                player.money -= int(all_tiles[player.piece_position].price)

                                price_update(all_tiles[player.piece_position])

                                property_data = f'property|{player.color}|{data[1]}%'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">приобретает {all_tiles[player.piece_position].name} за {int(all_tiles[player.piece_position].price)}~</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                money_data = f'money|{player.color}|{player.money}%'

                                for player2 in players:
                                    player2.conn.send(property_data.encode())
                                    player2.conn.send(money_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, property_data)
                                    information_sent_to('Информация отправлена к', player2.color, money_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(not player.double)
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
                        money_data = f'money|{player.color}|{player.money}%'
                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, money_data)

                        if all_tiles[player.piece_position].family == 'Угловые':
                            moving_player_changing(not player.double) # TODO: поменять, когда будет функционал

                        elif all_tiles[player.piece_position].owner == player.color or all_tiles[player.piece_position].mortgaged:
                            moving_player_changing(not player.double)

                    elif data[0] == 'auction initiate':
                        tile_position = int(data[1])
                        if tile_position == player.piece_position:
                            auction_players = players.copy()
                            for auction_player in auction_players:
                                if auction_player.imprisoned or auction_player.money < all_tiles[tile_position].price + 20:
                                    auction_players.remove(auction_player)

                            auction_players.pop(0) # удаляем того, кто инициировал аукцион
                            auction_players_who_are_wanting_to_buy = []
                            if len(auction_players) > 0:
                                auction_information = f'auction bid|{tile_position}|{all_tiles[tile_position].price}%'
                                auction_players[0].conn.send(auction_information.encode())
                                information_sent_to('Информация отправлена к', auction_players[0].color, auction_information)
                            else:
                                moving_player_changing(True)
                                print('Игроки не смогли принять участие в аукционе')

                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">Игроки не смогли принять участие в аукционе</font><br>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">Аукцион не состоялся</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                for player2 in players:
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">выставляет {all_tiles[tile_position].name} на аукцион</font><br>')
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                            for player2 in players:
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'auction accept':
                        tile_position = int(data[1])
                        price = int(data[2])
                        auction_information = f'auction bid|{tile_position}|{price}%'
                        if len(auction_players) > 0:
                            if auction_players[0].money >= price:
                                auction_players_who_are_wanting_to_buy.append(auction_players[0])
                            auction_players.pop(0)
                            for auction_player in auction_players:
                                if auction_player.imprisoned or auction_player.money < price + 20:
                                    auction_players.remove(auction_player)
                            if len(auction_players) > 0:
                                auction_players[0].conn.send(auction_information.encode())
                                information_sent_to('Информация отправлена к', auction_players[0].color, auction_information)
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{auction_players_who_are_wanting_to_buy[-1].color_value}">{auction_players_who_are_wanting_to_buy[-1].name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">участвует в аукционе. Ставка {price}~</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                for player2 in players:
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                            else:
                                auction_win()
                        else:
                            auction_players_who_are_wanting_to_buy.append(auction_players_who_are_wanting_to_buy[0])
                            auction_players_who_are_wanting_to_buy.pop(0)
                            auction_players_who_are_wanting_to_buy[0].conn.send(auction_information.encode())
                            information_sent_to('Информация отправлена к', auction_players[0].color, auction_information)

                    elif data[0] == 'auction reject':
                        # global auction_players, auction_players_who_are_wanting_to_buy
                        tile_position = int(data[1])
                        price = int(data[2])
                        auction_information = f'auction bid|{tile_position}|{price}%'

                        message = (
                            f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                            f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">отказался от участия в аукционе</font><br>')
                        message_data = f'message|{message}%'
                        log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                        if log_textbox.scroll_bar:
                            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                        for player2 in players:
                            player2.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, message_data)

                        auction_players.pop(0)
                        if len(auction_players) > 0:
                            auction_players[0].conn.send(auction_information.encode())
                            information_sent_to('Информация отправлена к', auction_players[0].color, auction_information)
                        else:
                            if len(auction_players_who_are_wanting_to_buy) > 0:
                                auction_players_who_are_wanting_to_buy.pop(0)
                                if len(auction_players_who_are_wanting_to_buy) > 1:
                                    auction_players_who_are_wanting_to_buy[0].conn.send(auction_information.encode())
                                    information_sent_to('Информация отправлена к', auction_players_who_are_wanting_to_buy[0].color, auction_information)
                                else:
                                    auction_win()
                            else:
                                moving_player_changing(True)
                                print('Все игроки отказались от аукциона')

                                message = (f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">Все игроки отказались от участия в аукционе</font><br>'
                                           f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">Аукцион не состоялся</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                for player2 in players:
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'pay':
                        player.piece_position = int(data[1])
                        if player.piece_position == 4 or player.piece_position == 38:
                            player.money += int(all_tiles[player.piece_position].price)
                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">заплатил Глебу {-all_tiles[player.piece_position].price}~</font><br>')
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                        else:
                            player.money -= all_tiles[player.piece_position].penis_income_calculation()
                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">заплатил {all_tiles[player.piece_position].penis_income_calculation()}~ за что-то</font><br>')
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                        money_data = f'money|{player.color}|{player.money}%'
                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            player2.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, money_data)
                            information_sent_to('Информация отправлена к', player2.color, message_data)
                        moving_player_changing(not player.double)

                    elif data[0] == 'pay sum':
                        player.money -= int(data[1])
                        message = (
                            f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                            f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">заплатил {data[1]}~</font><br>')
                        message_data = f'message|{message}%'
                        log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                        if log_textbox.scroll_bar:
                            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                        money_data = f'money|{player.color}|{player.money}%'
                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            player2.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, money_data)
                            information_sent_to('Информация отправлена к', player2.color, message_data)
                        moving_player_changing(not player.double)

                    elif data[0] == 'payToColor':
                        player.piece_position = int(data[1])
                        pay_sum = all_tiles[player.piece_position].penis_income_calculation()
                        player.money -= pay_sum
                        for player2 in players:
                            if player2.color == data[2]:
                                player2.money += pay_sum
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">заплатил игроку </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player2.color_value}">{player2.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{pay_sum}~</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                money_data1 = f'money|{player2.color}|{player2.money}%'
                        money_data2 = f'money|{player.color}|{player.money}%'

                        for player3 in players:
                            player3.conn.send(money_data1.encode())
                            player3.conn.send(money_data2.encode())
                            player3.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, money_data1)
                            information_sent_to('Информация отправлена к', player3.color, money_data2)
                            information_sent_to('Информация отправлена к', player3.color, message_data)
                        moving_player_changing(not player.double)

                    elif data[0] == 'pay to player':
                        if eggs_players_who_need_to_pay_to_one_player:
                            eggs_players_who_need_to_pay_to_one_player.remove(player)
                        player.money -= int(data[2])

                        for player2 in players:
                            if player2.color == data[1]:
                                player2.money += int(data[2])
                                money_data1 = f'money|{player2.color}|{player2.money}%'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">заплатил игроку </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player2.color_value}">{player2.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{data[2]}~</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                        if not eggs_players_who_need_to_pay_to_one_player:
                            if not player.double:
                                moving_player_changing(True)
                            else:
                                moving_player_changing(False)
                        money_data2 = f'money|{player.color}|{player.money}%'


                        for player3 in players:
                            player3.conn.send(money_data1.encode())
                            player3.conn.send(money_data2.encode())
                            player3.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, money_data1)
                            information_sent_to('Информация отправлена к', player3.color, money_data2)
                            information_sent_to('Информация отправлена к', player3.color, message_data)
                        moving_player_changing(not player.double)

                    elif data[0] == 'pay to players':
                        player.money -= int(data[1]) * (len(players) - 1)
                        money_data2 = f'money|{player.color}|{player.money}%'
                        for player2 in players:
                            if player2 != player:
                                player2.money += int(data[1])
                                money_data1 = f'money|{player2.color}|{player2.money}%'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">заплатил игроку </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player2.color_value}">{player2.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{int(data[1])}~</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)

                                for player3 in players:
                                    player3.conn.send(money_data1.encode())
                                    player3.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player3.color, money_data1)
                                    information_sent_to('Информация отправлена к', player3.color, message_data)

                        for player3 in players:
                            player3.conn.send(money_data2.encode())
                            information_sent_to('Информация отправлена к', player3.color, money_data2)
                        moving_player_changing(not player.double)

                    elif data[0] == 'pay for prison':
                        if player.money - (player.prison_break_attempts + 1) * 25 >= 0:
                            player.money -= (player.prison_break_attempts + 1) * 25
                            player.imprisoned = False
                            money_data = f'money|{player.color}|{player.money}%'
                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">заплатил {(player.prison_break_attempts + 1) * 25}~ за выход из тюрьмы</font><br>')
                            player.prison_break_attempts = 0
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
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
                            all_egg.append(egg_exit_prison)
                            prison_data = f'unimprisoned|{player.color}%'
                        elif player.eggs_prison_exit_card and data[1] == 'Яйца':
                            player.eggs_prison_exit_card = False
                            player.imprisoned = False
                            player.prison_break_attempts = 0
                            all_eggs.append(eggs_exit_prison)
                            prison_data = f'unimprisoned|{player.color}%'
                        for player2 in players:
                            player2.conn.send(prison_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, prison_data)

                    elif data[0] == 'penis build':
                        tile_position = int(data[1])
                        # print(all_tiles[tile_position].full_family, all_tiles[tile_position].penises < 5, player.money >= all_tiles[tile_position].penis_price, all_tiles[tile_position].type == 'buildable', all_tiles[tile_position].owner == player.color)
                        if (all_tiles[tile_position].full_family and
                            all_tiles[tile_position].penises < 5 and
                            player.money >= all_tiles[tile_position].penis_price and
                            all_tiles[tile_position].type == 'buildable' and
                            all_tiles[tile_position].owner == player.color):

                            player.money -= all_tiles[tile_position].penis_price
                            all_tiles[tile_position].penises += 1
                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">сунул пЭнис в {all_tiles[tile_position].name} и потратил {all_tiles[tile_position].penis_price}~</font><br>')
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                            money_data = f'money|{player.color}|{player.money}%'
                            penis_data = f'penis built|{tile_position}%'
                            for player2 in players:
                                player2.conn.send(money_data.encode())
                                player2.conn.send(penis_data.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, money_data)
                                information_sent_to('Информация отправлена к', player2.color, penis_data)
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'penis remove':
                        tile_position = int(data[1])
                        # print(all_tiles[tile_position].full_family, all_tiles[tile_position].penises, all_tiles[tile_position].type, all_tiles[tile_position].owner)
                        if (all_tiles[tile_position].full_family and
                                all_tiles[tile_position].penises < 5 and
                                all_tiles[tile_position].type == 'buildable' and
                                all_tiles[tile_position].owner == player.color):

                            player.money += all_tiles[tile_position].penis_price
                            all_tiles[tile_position].penises -= 1
                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">высунул пЭнис из {all_tiles[tile_position].name} и получил {all_tiles[tile_position].penis_price}~</font><br>')
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                            money_data = f'money|{player.color}|{player.money}%'
                            penis_data = f'penis removed|{tile_position}%'
                            for player2 in players:
                                player2.conn.send(money_data.encode())
                                player2.conn.send(penis_data.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, money_data)
                                information_sent_to('Информация отправлена к', player2.color, penis_data)
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'exchange request':
                        for player2 in players:
                            if player2.color == data[3]:
                                message = (f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                           f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">предлагает игроку </font>'
                                           f'<font face="BulBulPoly" pixel_size=[font_size] color="{player2.color_value}">{player2.name} </font>'
                                           f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">обмен</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                exchange_request = f'exchange request|{data[1]}|{data[2]}|{player.color}%'
                                player2.conn.send(exchange_request.encode())
                                information_sent_to('Информация отправлена к', player2.color, exchange_request)
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
                            get_p_ += f' {all_tiles[int(p_)].name},'
                        get_p_ = get_p_[:-1]
                        give_p_ = ''
                        for p_ in give_property:
                            give_p_ += f' {all_tiles[int(p_)].name},'
                        give_p_ = give_p_[:-1]
                        get_m_ = ''
                        if get_money:
                            get_m_ = f' и {get_money}~'
                        give_m_ = ''
                        if give_money:
                            give_m_ = f' и {give_money}~'

                        for tile_position in get_property:
                            if tile_position:
                                all_tiles[int(tile_position)].owner = player.color

                        # А зачем оно так устроено?
                        # А, ладно, понял. Всё работает как надо, ничего менять не надо
                        for player2 in players:
                            if player2.color == data[3]:
                                player2.money = player2.money + give_money - get_money
                                for tile_position in give_property:
                                    if tile_position:
                                        all_tiles[int(tile_position)].owner = player2.color

                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">получает{get_p_}{get_m_}</font><br>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player2.color_value}">{player2.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">получает{give_p_}{give_m_}</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)

                                all_property_information = f'all property|{player2.color}|'
                                for tile in all_tiles:
                                    if tile.owner == player2.color:
                                        all_property_information += f'{tile.position}_'
                                all_property_information = all_property_information[:-1] + '%'
                                money_data = f'money|{player2.color}|{player2.money}%'
                                for player3 in players:
                                    player3.conn.send(all_property_information.encode())
                                    player3.conn.send(money_data.encode())
                                    information_sent_to('Информация отправлена к', player3.color, all_property_information)
                                    information_sent_to('Информация отправлена к', player3.color, money_data)

                        all_property_information = f'all property|{player.color}|'
                        for tile in all_tiles:
                            if tile.owner == player.color:
                                all_property_information += f'{tile.position}_'
                        all_property_information = all_property_information[:-1] + '%'
                        money_data = f'money|{player.color}|{player.money}%'
                        for player3 in players:
                            player3.conn.send(all_property_information.encode())
                            player3.conn.send(money_data.encode())
                            player3.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, all_property_information)
                            information_sent_to('Информация отправлена к', player3.color, money_data)
                            information_sent_to('Информация отправлена к', player3.color, message_data)

                        for tile_position in give_property:
                            if tile_position:
                                price_update(all_tiles[int(tile_position)])

                        for tile_position in get_property:
                            if tile_position:
                                price_update(all_tiles[int(tile_position)])

                    elif data[0] == 'exchange request rejected':
                        print(f'Игрок {player.color} отказался от обмена')
                        message = (
                            f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                            f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">отказался от обмена </font><br>')
                        message_data = f'message|{message}%'
                        log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                        if log_textbox.scroll_bar:
                            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                        for player3 in players:
                            player3.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player3.color, message_data)

                    elif data[0] == 'mortgage':
                        tile = all_tiles[int(data[1])]
                        if not tile.mortgaged and tile.owner == player.color:
                            player.money += int(tile.price / 2)
                            tile.mortgaged = True
                            tile.mortgaged_moves_count = 15

                            price_update(tile)
                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">закладывает {tile.name} и получает {int(tile.price / 2)}~</font><br>')
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                            mortgage_information = f'mortgaged|{data[1]}%'
                            money_information = f'money|{player.color}|{player.money}%'
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

                            price_update(tile)
                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">закладывает {tile.name} и тратит {tile.price}~</font><br>')
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                            redeem_information = f'redeemed|{data[1]}%'
                            money_information = f'money|{player.color}|{player.money}%'
                            for player2 in players:
                                player2.conn.send(redeem_information.encode())
                                player2.conn.send(money_information.encode())
                                player2.conn.send(message_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, redeem_information)
                                information_sent_to('Информация отправлена к', player2.color, money_information)
                                information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'pull card':

                        if data[1] == 'Яйцо':
                            pulled_card = all_egg[0]
                            if pulled_card.command != 'exit prison':
                                all_egg.append(pulled_card)
                            else:
                                egg_exit_prison = pulled_card
                            all_egg.pop(0)

                        else: # data[1] == 'Груда вопросительных яиц':
                            pulled_card = all_eggs[0]
                            if pulled_card.command != 'exit prison':
                                all_eggs.append(pulled_card)
                            else:
                                eggs_exit_prison = pulled_card
                            all_eggs.pop(0)

                        pulled_card_data = f'pulled card position|{player.color}|{data[1]}|{pulled_card.position}%'
                        for player2 in players:
                            player2.conn.send(pulled_card_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, pulled_card_data)

                        match pulled_card.command:
                            case 'get money':
                                player.money += pulled_card.value
                                if data[1] == 'Яйцо':
                                    first_message_part = 'Яйцо даёт'
                                else:
                                    first_message_part = 'Яйца дают'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{first_message_part} игроку </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{pulled_card.value}~</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                money_data = f'money|{player.color}|{player.money}%'
                                for player2 in players:
                                    player2.conn.send(money_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, money_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(not player.double)

                            case 'get money from players':
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">Все игроки должны заплатить {pulled_card.value}~ игроку </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name}</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                pay_command = f'need to pay to player|{player.color}|{pulled_card.value}%'
                                for player2 in players:
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player.color, message_data)
                                    if len(players) > 1:
                                        if player2 != player:
                                            eggs_players_who_need_to_pay_to_one_player.append(player2)
                                            player2.conn.send(pay_command.encode())
                                            information_sent_to('Информация отправлена к', player.color, pay_command)
                                    else:
                                        message = (
                                            f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">Ни одного игрока не найдено</font><br>')
                                        message_data = f'message|{message}%'
                                        log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                        if log_textbox.scroll_bar:
                                            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player.color, message_data)

                            case 'go to start':
                                player.piece_position = 0
                                move_data = f'move diagonally|{player.color}|0%'
                                player.money += pulled_card.value
                                if data[1] == 'Яйцо':
                                    first_message_part = 'Яйцо переносит'
                                else:
                                    first_message_part = 'Яйца переносят'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{first_message_part} игрока </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">на поле {all_tiles[player.piece_position].name} и </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">получает {pulled_card.value}~</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                money_data = f'money|{player.color}|{player.money}%'
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    player2.conn.send(money_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                    information_sent_to('Информация отправлена к', player2.color, money_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(not player.double)

                            case 'pay':
                                if pulled_card.value:
                                    message = (
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">должен заплатить {pulled_card.value}~</font><br>')
                                    message_data = f'message|{message}%'
                                    log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                    if log_textbox.scroll_bar:
                                        log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                    pay_command = f'need to pay|{pulled_card.value}%'
                                    player.conn.send(pay_command.encode())
                                    information_sent_to('Информация отправлена к', player.color, pay_command)
                                    for player2 in players:
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                else:
                                    moving_player_changing(not player.double)

                            case 'pay to players':
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">должен заплатить {pulled_card.value}~ каждому игроку</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                for player2 in players:
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, message_data)

                                pay_command = f'need to pay to players|{pulled_card.value}%'
                                player.conn.send(pay_command.encode())
                                information_sent_to('Информация отправлена к', player.color, pay_command)

                            case 'pay for white penises':
                                penises = 0
                                for tile in all_tiles:
                                    if tile.owner == player.color:
                                        penises += tile.penises
                                if penises:
                                    pay_command = f'need to pay|{pulled_card.value * penises}%'
                                    player.conn.send(pay_command.encode())
                                    information_sent_to('Информация отправлена к', player.color, pay_command)
                                    message = (
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">должен заплатить {pulled_card.value}~ за каждый белый пЭнис, то есть {pulled_card.value * penises}~</font><br>')
                                    message_data = f'message|{message}%'
                                    log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                    if log_textbox.scroll_bar:
                                        log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                    for player2 in players:
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                else:
                                    moving_player_changing(not player.double)
                                    message = (
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">У игрока </font>'
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                        f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">нет белых пЭнисов, он не должен ничего платить</font><br>')
                                    message_data = f'message|{message}%'
                                    log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                    if log_textbox.scroll_bar:
                                        log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                    for player2 in players:
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, message_data)

                            case 'go back':
                                player.piece_position -= pulled_card.value
                                if data[1] == 'Яйцо':
                                    first_message_part = 'Яйцо отправляет'
                                else:
                                    first_message_part = 'Яйца отправляют'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{first_message_part} игрока </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">на 3 клетки назад</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                move_data = f'move|{player.color}|-1|-2%'
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)

                            case 'go to':
                                player.piece_position = pulled_card.value
                                move_data = f'move diagonally|{player.color}|{player.piece_position}%'
                                if data[1] == 'Яйцо':
                                    first_message_part = 'Яйцо переносит'
                                else:
                                    first_message_part = 'Яйца переносят'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{first_message_part} игрока </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">на поле {all_tiles[player.piece_position].name}</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                if all_tiles[player.piece_position].owner == player.color:
                                    moving_player_changing(not player.double)

                            case 'go to next':
                                while all_tiles[player.piece_position].type != pulled_card.value:
                                    player.piece_position += 1
                                    if player.piece_position >= 40:
                                        player.piece_position -= 40
                                move_data = f'move diagonally|{player.color}|{player.piece_position}%'
                                if data[1] == 'Яйцо':
                                    first_message_part = 'Яйцо переносит'
                                else:
                                    first_message_part = 'Яйца переносят'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{first_message_part} игрока </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">на поле {all_tiles[player.piece_position].name}</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                if all_tiles[player.piece_position].owner == player.color:
                                    moving_player_changing(not player.double)


                                if (all_tiles[player.piece_position].type == 'infrastructure' and
                                        all_tiles[player.piece_position].owned and
                                        all_tiles[player.piece_position].owner != player.color):
                                    cube1 = random.randint(1, 6)
                                    cube2 = random.randint(1, 6)
                                    if not all_tiles[player.piece_position].full_family:
                                        pay_sum = (cube1 + cube2) * 4
                                    else:
                                        pay_sum = (cube1 + cube2) * 10
                                    for player2 in players:
                                        if player2.color == all_tiles[player.piece_position].owner:
                                            message = (
                                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">должен заплатить игроку </font>'
                                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player2.color_value}">{player2.name} </font>'
                                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{pay_sum}~</font><br>')
                                            message_data = f'message|{message}%'
                                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                            if log_textbox.scroll_bar:
                                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                    cubes_information = f'show cubes|{cube1}|{cube2}%'
                                    pay_command = f'need to pay to player|{all_tiles[player.piece_position].owner}|{pay_sum}%'
                                    for player2 in players:
                                        player2.conn.send(cubes_information.encode())
                                        player2.conn.send(message_data.encode())
                                        information_sent_to('Информация отправлена к', player2.color, cubes_information)
                                        information_sent_to('Информация отправлена к', player2.color, message_data)
                                    player.conn.send(pay_command.encode())
                                    information_sent_to('Информация отправлена к', player.color, pay_command)

                            case 'go to prison':
                                player.piece_position = 10
                                player.imprisoned = True
                                prison_data = f'imprisoned|{player.color}%'
                                move_data = f'move diagonally|{player.color}|10%'
                                if data[1] == 'Яйцо':
                                    first_message_part = 'Яйцо отправляет'
                                else:
                                    first_message_part = 'Яйца отправляют'
                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">{first_message_part} игрока </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">в тюрьму. Удачи!</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    player2.conn.send(prison_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)
                                    information_sent_to('Информация отправлена к', player2.color, prison_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(True)

                            case 'exit prison':
                                if data[1] == 'Яйцо':
                                    player.egg_prison_exit_card = True
                                else:
                                    player.eggs_prison_exit_card = True

                                message = (
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                    f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">вытянул карточку выхода из тюрьмы</font><br>')
                                message_data = f'message|{message}%'
                                log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                                if log_textbox.scroll_bar:
                                    log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                                prison_escape_data = f'free prison escape card|{data[1]}|{player.color}%'
                                for player2 in players:
                                    player2.conn.send(prison_escape_data.encode())
                                    player2.conn.send(message_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, prison_escape_data)
                                    information_sent_to('Информация отправлена к', player2.color, message_data)
                                moving_player_changing(not player.double)

                    elif data[0] == 'message':
                        message = data[1]
                        message_data = f'message|<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name}: </font><font face="BulBulPoly" pixel_size=[font_size] color="#000000">{message}</font><br>%'
                        log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="{player.color_value}">{player.name}: </font>'
                                                     f'<font face="BulBulPoly" pixel_size={font_size} color="#000000">{message}</font><br>')
                        if log_textbox.scroll_bar:
                            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                        for player2 in players:
                            player2.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, message_data)

                    elif data[0] == 'sound message':
                        audio_bytes_ascii_decoded = data[1]
                        audio_bytes_decoded_base64 = base64.b64decode(audio_bytes_ascii_decoded)
                        audio_bytes_decoded = zlib.decompress(audio_bytes_decoded_base64)

                        sound_id = len(sound_messages)
                        sound_messages[f'{sound_id}'] = audio_bytes_decoded
                        message = (f'<a href="sound:{sound_id}"><font face="BulBulPoly" pixel_size=[font_size] color="#4FC3F7">Аудио файл</font></a>'
                                   f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000"> от </font>'
                                   f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name}. </font>'
                                   f'<a href="save sound:{sound_id}"><font face="BulBulPoly" pixel_size=[font_size] color="#4FC3F7">Сохранить</font></a><br>')
                        message_data = f'message|{message}%'
                        log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                        if log_textbox.scroll_bar:
                            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)

                        sendable_data = f'sound message|{sound_id}|{data[1]}%'
                        size_information = f'receive size|{len(sendable_data)}%'

                        for player2 in players:
                            player2.conn.send(size_information.encode())
                            player2.conn.send(sendable_data.encode())
                            player2.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, size_information)
                            information_sent_to('Информация отправлена к', player2.color, message_data)
                        receive_size = 1024

                    elif data[0] == 'voice message':
                        audio_bytes_ascii_decoded = data[1]
                        audio_bytes_decoded_base64 = base64.b64decode(audio_bytes_ascii_decoded)
                        audio_bytes_decoded = zlib.decompress(audio_bytes_decoded_base64)

                        voice_id = len(voice_messages)
                        voice_messages[f'{voice_id}'] = audio_bytes_decoded
                        message = (
                            f'<a href="voice:{voice_id}"><font face="BulBulPoly" pixel_size=[font_size] color="#4FC3F7">Голосовое сообщение</font></a>'
                            f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000"> от </font>'
                            f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name}. </font>'
                            f'<a href="save voice:{voice_id}"><font face="BulBulPoly" pixel_size=[font_size] color="#4FC3F7">Сохранить</font></a><br>')
                        message_data = f'message|{message}%'
                        log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                        if log_textbox.scroll_bar:
                            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)

                        sendable_data = f'voice message|{voice_id}|{data[1]}%'
                        size_information = f'receive size|{len(sendable_data)}%'

                        for player2 in players:
                            player2.conn.send(size_information.encode())
                            player2.conn.send(sendable_data.encode())
                            player2.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, size_information)
                            information_sent_to('Информация отправлена к', player2.color, message_data)
                        receive_size = 1024

                    elif data[0] == 'image message':
                        if not os.path.exists(f'resources/temp/images/server image messages'):
                            if not os.path.exists('resources/temp/images'):
                                if not os.path.exists('resources/temp'):
                                    os.mkdir('resources/temp')
                                os.mkdir('resources/temp/images')
                            os.mkdir(f'resources/temp/images/server image messages')

                        image_bytes_decoded = base64.b64decode(data[1])
                        image_decoded = Image.open(io.BytesIO(image_bytes_decoded))

                        # image_decoded = Image.open(image_bytes_decoded)
                        image_decoded = image_decoded.resize(log_image_size)
                        image_decoded.save(f'resources/temp/images/server image messages/{image_messages}.png')


                        message_data = f'message|<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name}: </font><img src="resources/temp/images/client image messages/{image_messages}.png" width="100" height="100"><br>%'
                        log_textbox.append_html_text(
                            f'<font face="BulBulPoly" pixel_size={font_size} color="{player.color_value}">{player.name}: </font>'
                            f'<img src="resources/temp/images/server image messages/{image_messages}.png" width="100" height="100"><br>')
                        if log_textbox.scroll_bar:
                            log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                        for player2 in players:
                            player2.conn.send(f'image message|{image_messages}|{data[1]}%'.encode())
                            player2.conn.send(message_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, message_data)
                        image_messages += 1

                    elif data[0] == 'receive size':
                        receive_size = int(data[1])

                    else:
                        player.conn.send(f'error|Незарегистрированная команда: {data[0]}%'.encode())
                        information_sent_to('Информация отправлена к', player.color, f'error|Незарегистрированная команда: {data[0]}%')

            except (BlockingIOError, ConnectionAbortedError, ConnectionResetError, AttributeError):
                pass
            except:
                print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def players_send():
    for player in players:
        player_data = f'playersData|{player.color}|{player.money}|{player.piece_position}|{player.name}%'
        for player2 in players:
            player2.conn.send(player_data.encode())
            information_sent_to('Информация отправлена к', player2.color, player_data)


def message_send():
    message = log_entry_textbox.get_text()
    if message:
        if message[0] != '~':
            message_data = f'message|<font face="BulBulPoly" pixel_size=[font_size] color="#000000">server: {message}</font><br>%'
            log_textbox.append_html_text(f'<font face="BulBulPoly" pixel_size={font_size} color="#000000">server: {message}</font><br>')
            if log_textbox.scroll_bar:
                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
            log_entry_textbox.set_text('')
            for player in players:
                player.conn.send(message_data.encode())
                information_sent_to('Информация отправлена к', player.color, message_data)
        else:
            message_command = message[1:].split(' ')
            if message_command[0] == 'money':
                for player in players:
                    if player.color == message_command[2]:
                        if message_command[1] == 'add':
                            player.money += int(message_command[3])
                        elif message_command[1] == 'set':
                            player.money = int(message_command[3])
                        money_data = f'money|{player.color}|{player.money}%'
                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, money_data)
            if message_command[0] == 'onmove':
                for player in players:
                    if player.color == message_command[1]:
                        player.on_move = True

                        for player2 in players:
                            player2.conn.send(f'onMove|{player.color}%'.encode())
                            information_sent_to('Информация отправлена к', player2.color, f'onMove|{player.color}%')


def connection():
    while not state['is_game_started'] and running:
        time.sleep(0.1)
        if colors[0] == 'red':
            color_value = '#ff0000'
        elif colors[0] == 'blue':
            color_value = '#0000ff'
        elif colors[0] == 'yellow':
            color_value = '#ffff00'
        elif colors[0] == 'green':
            color_value = '#0AA00A'
        player = Player('', '', colors[0], color_value)
        try:
            player.connect(colors)
            players.append(player)
            globals()[f'{player.color}_profile'] = pg.image.load(f'resources/{resolution_folder}/profile/{player.color}_profile.png').convert_alpha()
            globals()[f'{player.color}_property_image'] = pg.image.load(f'resources/{resolution_folder}/property/{player.color}_property.png').convert_alpha()
            print(f'Игрок с цветом {player.color} добавлен в список')
        except BlockingIOError:
            pass
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def disconnect_check():
    while running:
        time.sleep(1)
        for player in players:
            try:
                player.conn.send('[1foe_S]'.encode())
                player.connection_errors = 0
            except:
                player.connection_errors += 1
                if player.connection_errors >= 5:
                    colors.append(player.color)
                    deleted_color = player.color
                    message = (
                        f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                        f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">отключился</font><br>')
                    log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                    if log_textbox.scroll_bar:
                        log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                    print(f'Игрок {player.color} отключился.\nЦвет {player.color} возвращён')
                    player.clear()
                    players.remove(player)
                    players_send()
                    message_data = f'message|{message}%'
                    deletion_player_data = f'playerDeleted|{deleted_color}%'
                    for player2 in players:
                        player2.conn.send(deletion_player_data.encode())
                        player2.conn.send(message_data.encode())
                        information_sent_to('Информация отправлена к', player2.color, deletion_player_data)
                        information_sent_to('Информация отправлена к', player2.color, message_data)


def start_server():
    global colors, main_sck
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

            print(f'Сервер открыт: {ip}:{port}')

        except:
            print(f'{"\033[31m{}".format('Не удалось создать сервер')}{'\033[0m'}')


def start_game():
    if state['is_server_started'] and not state['is_game_started']:
        state['is_game_started'] = True
        random.shuffle(players)
        game_started_command = 'gameStarted|'
        for player in players:
            game_started_command += f'{player.color}_'
        game_started_command = game_started_command[:-1] + '%'
        print('Игра начата')
        for player in players:

            player.conn.send(game_started_command.encode())
            player.conn.send(f'onMove|{players[0].color}%'.encode())
            information_sent_to('Информация отправлена к', player.color, game_started_command)
            information_sent_to('Информация отправлена к', player.color, f'onMove|{players[0].color}%')


def moving_player_changing(do_change):
    if do_change:
        players.append(players[0])
        players.pop(0)

        for tile in all_tiles:
            if tile.mortgaged:
                tile.mortgaged_moves_count -= 1
                mortgaged_moves_count_information = f'mortgaged_moves_count|{tile.position}|{tile.mortgaged_moves_count}%'
                for player2 in players:
                    player2.conn.send(mortgaged_moves_count_information.encode())
                    information_sent_to('Информация отправлена к', player2.color, mortgaged_moves_count_information)
                if tile.mortgaged_moves_count == 0:
                    for player in players:
                        if player.color == tile.owner:
                            message = (
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="{player.color_value}">{player.name} </font>'
                                f'<font face="BulBulPoly" pixel_size=[font_size] color="#000000">не смог выкупить {tile.name}</font><br>')
                            message_data = f'message|{message}%'
                            log_textbox.append_html_text(message.replace('[font_size]', str(font_size)))
                            if log_textbox.scroll_bar:
                                log_textbox.scroll_bar.set_scroll_from_start_percentage(1)
                    tile.mortgaged = False
                    tile.owned = False
                    tile.owner = ''
                    late_to_redeem_information = f'late to redeem|{tile.position}%'
                    for player2 in players:
                        player2.conn.send(late_to_redeem_information.encode())
                        player2.conn.send(message_data.encode())
                        information_sent_to('Информация отправлена к', player2.color, late_to_redeem_information)
                        information_sent_to('Информация отправлена к', player2.color, message_data)
                for tile_ in all_tiles:
                    if tile_.family == tile.family:
                        tile_.family_members -= 1
                tile.family_members = 0

    for player in players:
        player.conn.send(f'onMove|{players[0].color}%'.encode())
        information_sent_to('Информация отправлена к', player.color, f'onMove|{players[0].color}%')


def position_update(color):
    for player in players:
        if player.color == color:
            if color == 'red':
                player.x = all_tiles[player.piece_position].x_position
                player.y = all_tiles[player.piece_position].y_position
            elif color == 'green':
                player.x = all_tiles[player.piece_position].x_position + piece_color_coefficient
                player.y = all_tiles[player.piece_position].y_position
            elif color == 'yellow':
                player.x = all_tiles[player.piece_position].x_position
                player.y = all_tiles[player.piece_position].y_position + piece_color_coefficient
            elif color == 'blue':
                player.x = all_tiles[player.piece_position].x_position + piece_color_coefficient
                player.y = all_tiles[player.piece_position].y_position + piece_color_coefficient
            screen.blit(pg.image.load(f'resources/{resolution_folder}/pieces/{player.color}_piece.png'), (player.x, player.y))


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
            screen.blit(pg.image.load(f'resources/{resolution_folder}/white penises/{tile.penises}.png'), (tile.x_position, tile.y_position))

    try:
        for player in players:
            position_update(player.color)

            player_index = players.index(player)

            screen.blit(profile_picture,
                        (profile_coordinates[player_index]['profile'][0],
                         profile_coordinates[player_index]['profile'][1]))

            screen.blit(player.avatar_image, (profile_coordinates[player_index]['avatar'][0],
                                        profile_coordinates[player_index]['avatar'][1]))

            if player.imprisoned:
                screen.blit(player_bars, (profile_coordinates[player_index]['avatar'][0],
                                          profile_coordinates[player_index]['avatar'][1]))



            screen.blit(globals()[f'{player.color}_profile'], profile_coordinates[player_index]['avatar'])



            screen.blit(font.render(f'{player.money}~', False, 'black'),
                        (profile_coordinates[player_index]['money'][0],
                         profile_coordinates[player_index]['money'][1]))

            screen.blit(font.render(player.name, False, 'black'),
                        (profile_coordinates[player_index]['name'][0],
                         profile_coordinates[player_index]['name'][1]))
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
        if event.type == pg.QUIT:
            global running
            running = False
        manager.process_events(event)
        match event.type:
            case pygame_gui.UI_BUTTON_PRESSED:
                event_type = event.ui_element
                if event_type == start_server_button:
                    start_server()
                    start_server_button.disable()
                    start_button.enable()
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


def buttons():
    global start_button, ip_textbox, port_textbox, start_server_button, log_textbox, log_entry_textbox, log_entry_button, debug_button
    ip_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect((start_btn_textboxes_coordinates['IP'][0], start_btn_textboxes_coordinates['IP'][1])),
        placeholder_text='IP адрес',
        initial_text=ip,
        manager=manager)

    port_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect((start_btn_textboxes_coordinates['port'][0], start_btn_textboxes_coordinates['port'][1])),
        placeholder_text='Порт',
        initial_text='1247',
        manager=manager)

    start_server_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect((1040, 534), (217, 38)),
        text='Запуск сервера',
        manager=manager)

    start_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect((1040, 592), (217, 38)),
        text='Начать игру',
        manager=manager)
    start_button.disable()

    log_textbox = pygame_gui.elements.UITextBox(
        relative_rect=pg.Rect(log_textbox_coordinates['main_box']),
        html_text='',
        manager=manager)

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
              f'       on_move: {player.on_move}\n'
              f'       imprisoned: {player.imprisoned}\n'
              f'       prison_break_attempts: {player.prison_break_attempts}\n'
              f'       egg_prison_exit_card: {player.egg_prison_exit_card}\n'
              f'       eggs_prison_exit_card: {player.eggs_prison_exit_card}\n'
              f'       double: {player.double}\n')
    pprint.pp(state)


load_assets()
buttons()
theme = manager.create_new_theme(f'resources/{resolution_folder}/gui_theme.json')
manager.set_ui_theme(theme)
running = True

gc.enable()

past_second_fps = []
prev_fps_time = time.time()
prev_time = time.time()
average_fps = 0
all_fps = []
average_fps_text = font.render(str(average_fps), False, 'black')

while running:
    clock.tick(FPS)
    dt, prev_time = delta_time(prev_time)
    blit_items()
    price_printing()
    event_handler()
    try:
        manager.update(dt)
        manager.draw_ui(screen)
    except:
        pass

    if debug_mode:
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

    pg.display.update()

if os.path.exists(f'resources/temp/images/server image messages'):
    for file in os.listdir('resources/temp/images/server image messages'):
        os.remove(f'resources/temp/images/server image messages/{file}')

print('Сервер закрыт')
if debug_mode:
    print(f'Средний FPS: {sum(all_fps) / len(all_fps)}')