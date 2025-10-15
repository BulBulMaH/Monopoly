import socket as sck
import time
import random
import threading
import traceback
import csv
from PIL import Image
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame as pg
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox

from all_tiles_extraction import all_tiles_get
from resolution_choice import resolution_definition

from colored_output import thread_open, new_connection, information_received, information_sent, information_sent_to
from Tiles_Class import Tiles

class Player:
    def __init__(self,conn,address,color):
        self.conn = conn
        self.address = address
        self.piece_position = 0
        self.name = ''
        self.property = []
        self.color = color
        self.imprisoned = False
        self.prison_break_attempts = 0
        self.money = 1500
        self.ready = False
        self.on_move = False
        self.avatar = []
        self.x = 0
        self.y = 0

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
        self.property = []
        self.color = ''
        self.imprisoned = False
        self.money = 1500
        self.ready = False
        self.on_move = False

pg.init()
resolution, resolution_folder, piece_color_coefficient, bars_coordinates, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, btn_radius, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, FPS, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates = resolution_definition(False)
TITLE = 'Monopoly Server'
screen = pg.display.set_mode((1280, 650))
pg.display.set_caption(TITLE)
clock = pg.time.Clock()

all_tiles, positions = all_tiles_get(resolution_folder, tile_size)
background = pg.image.load(f'resources/{resolution_folder}/background.png').convert()
board = pg.image.load(f'resources/{resolution_folder}/board grid.png').convert_alpha()
profile_picture = pg.image.load(f'resources/{resolution_folder}/profile/profile.png').convert_alpha()
bars = pg.image.load(f'resources/{resolution_folder}/bars.png').convert_alpha()
player_bars = pg.image.load(f'resources/{resolution_folder}/profile/profile_bars.png').convert_alpha()
avatar_file = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png').convert_alpha()
mortgaged_tile = pg.image.load(f'resources/{resolution_folder}/mortgaged.png').convert_alpha()
font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)

start_server_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/start_server_disabled.png').convert_alpha()
start_game_disabled_btn = pg.image.load(f'resources/{resolution_folder}/buttons/start_game_disabled.png').convert_alpha()

for tile_image in range(40):
    if tile_image not in (0, 10, 20, 30):
        globals()[f'tile_{tile_image}_image'] = pg.transform.smoothscale(
            pg.image.load(f'resources/tiles_data/images/{tile_image}.png'), tile_size).convert()

auction_players = []
auction_players_who_are_wanting_to_buy = []

players = []
is_server_started = False
is_game_started = False

def receive_data():
    global auction_players, auction_players_who_are_wanting_to_buy


    def auction_win():
        for player2 in players:
            if player2 == auction_players_who_are_wanting_to_buy[0]:
                player2.property.append(tile_position)
                player2.money -= price
        property_data = f'property|{player2.color}|{tile_position}%'
        money_data = f'money|{player2.color}|{player2.money}%'
        for player3 in players:
            player3.conn.send(property_data.encode())
            player3.conn.send(money_data.encode())
            information_sent_to('Информация отправлена к', player3.color, property_data)
            information_sent_to('Информация отправлена к', player3.color, money_data)
        print('Аукцион прошёл успешно!')
        moving_player_changing(True)


    def price_update(tile):
        global all_tiles
        tile_family_members = 0
        for tile_ in all_tiles:
            if tile_.family == tile.family:
                if tile_.owner == tile.owner and not tile_.mortgaged:
                    tile_family_members += 1

        for tile_ in all_tiles:
            if tile_.family == tile.family:
                if tile_.owner == tile.owner and not tile_.mortgaged:
                    tile_.family_members = tile_family_members
                    print(tile_.family_members, tile_.name)


    while running:
        for player in players:
            try:
                data_unsplit = player.conn.recv(1024).decode()
                if data_unsplit != '':
                    information_received('data_unsplit', data_unsplit)
                data_split_by_types = data_unsplit.split('%')
                while len(data_split_by_types) > 1:
                    data_unsplit_by_content = data_split_by_types[0]
                    data = data_unsplit_by_content.split('|')
                    data_split_by_types.pop(0)

                    if data != ['']:
                        information_received(f'Информация получена от {player.color}', data)

                    if data[0] == 'name':
                        player.name = data[1]
                        players_send()

                    elif data[0] == 'avatar':
                        player.avatar.append(data_unsplit_by_content + '%')
                        # print(1, data_unsplit_by_content + '%')
                        if data[2] == data[4]:
                            for player2 in players:
                                for avatar in player.avatar:
                                    time.sleep(0.07)
                                    player2.conn.send(avatar.encode())
                            player.avatar = []

                    elif data[0] == 'move':
                        cube1 = random.randint(1,6)
                        cube2 = random.randint(1,6)
                        # cube1 = 3
                        # cube2 = 4
                        double = cube1 == cube2

                        if player.imprisoned:
                            if double:
                                player.imprisoned = False
                                player.prison_break_attempts = 0
                                prison_data = f'unimprisoned|{player.color}|{cube1}|{cube2}%'
                                player.piece_position += cube1 + cube2
                                for player2 in players:
                                    player2.conn.send(prison_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, prison_data)
                            else:
                                player.prison_break_attempts += 1
                                imprisoned_double_failed_data = f'imprisoned double failed|{player.color}|{cube1}|{cube2}|{player.prison_break_attempts}%'
                                for player2 in players:
                                    player2.conn.send(imprisoned_double_failed_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, imprisoned_double_failed_data)
                                moving_player_changing(True)


                            if player.prison_break_attempts >= 3:
                                prison_bribe_data = f'bribe|{player.prison_break_attempts * 25}%'
                                player.conn.send(prison_bribe_data.encode())
                                information_sent_to('Информация отправлена к', player.color, prison_bribe_data)

                        else:
                            cube_sum = cube1 + cube2
                            player.piece_position += cube_sum

                            if player.piece_position == 40:
                                player.money += 100

                            if player.piece_position > 39:
                                player.piece_position -= 40
                                player.money += 200 # todo убрать 2000

                            move_data = f'move|{player.color}|{cube1}|{cube2}%'
                            for player2 in players:
                                player2.conn.send(move_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, move_data)

                            if player.piece_position == 30:
                                player.piece_position = 10
                                player.imprisoned = True
                                prison_data = f'imprisoned|{player.color}%'
                                move_data = f'move diagonally|{player.color}|10%'
                                for player2 in players:
                                    player2.conn.send(prison_data.encode())
                                    player2.conn.send(move_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, prison_data)
                                    information_sent_to('Информация отправлена к', player2.color, move_data)

                            elif player.piece_position == 10:
                                player.piece_position = 30
                                move_data = f'move diagonally|{player.color}|30%'
                                for player2 in players:
                                    player2.conn.send(move_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, move_data)

                    elif data[0] == 'nextPlayer':
                        if data[1] == 'True':
                            moving_player_changing(True)
                        else:
                            moving_player_changing(False)

                    elif data[0] == 'buy':
                        if player.piece_position == int(data[1]):
                            player.piece_position = int(data[1])
                            if player.money >= int(all_tiles[player.piece_position].price):
                                player.property.append(player.piece_position)
                                all_tiles[player.piece_position].owned = True
                                all_tiles[player.piece_position].owner = player.color
                                player.money -= int(all_tiles[player.piece_position].price)
                                tile_family_members = 0

                                price_update(all_tiles[player.piece_position])

                                property_data = f'property|{player.color}|{data[1]}%'
                                money_data = f'money|{player.color}|{player.money}%'
                                for player2 in players:
                                    player2.conn.send(property_data.encode())
                                    player2.conn.send(money_data.encode())
                                    information_sent_to('Информация отправлена к', player2.color, property_data)
                                    information_sent_to('Информация отправлена к', player2.color, money_data)
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

                    elif data[0] == 'auction initiate':
                        # global auction_players, auction_players_who_are_wanting_to_buy
                        print(players)
                        tile_position = int(data[1])
                        if tile_position == player.piece_position:
                            auction_players = players.copy()
                            auction_players.pop(0) # удаляем того, кто инициировал аукцион
                            auction_players_who_are_wanting_to_buy = []
                            if len(auction_players) > 0:
                                auction_information = f'auction bid|{tile_position}|{all_tiles[tile_position].price}%'
                                auction_players[0].conn.send(auction_information.encode())
                                information_sent_to('Информация отправлена к', auction_players[0].color, auction_information)
                            else:
                                moving_player_changing(True)

                    elif data[0] == 'auction accept':
                        tile_position = int(data[1])
                        price = int(data[2])
                        auction_information = f'auction bid|{tile_position}|{price}%'
                        if len(auction_players) > 0:
                            if auction_players[0].money >= price:
                                auction_players_who_are_wanting_to_buy.append(auction_players[0])
                            auction_players.pop(0)
                            if len(auction_players) > 0:
                                auction_players[0].conn.send(auction_information.encode())
                                information_sent_to('Информация отправлена к', auction_players[0].color, auction_information)
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

                    elif data[0] == 'ready':
                        player.ready = True

                    elif data[0] == 'pay':
                        player.piece_position = int(data[1])
                        if player.piece_position == 4 or player.piece_position == 38:
                            player.money += int(all_tiles[player.piece_position].price)
                        else:
                            player.money -= all_tiles[player.piece_position].penis_income_calculation()
                        money_data = f'money|{player.color}|{player.money}%'
                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, money_data)

                    elif data[0] == 'payToColor':
                        player.piece_position = int(data[1])
                        if all_tiles[player.piece_position].type == 'infrastructure':
                            cube1 = random.randint(1, 6)
                            cube2 = random.randint(1, 6)
                            if not all_tiles[player.piece_position].full_family:
                                pay_sum = (cube1 + cube2) * 4
                            else:
                                pay_sum = (cube1 + cube2) * 10 # todo: отправлять анимацию
                        else:
                            pay_sum = all_tiles[player.piece_position].penis_income_calculation()
                        player.money -= pay_sum
                        for player2 in players:
                            if player2.color == data[2]:
                                player2.money += pay_sum
                                money_data1 = f'money|{player2.color}|{player2.money}%'
                        money_data2 = f'money|{player.color}|{player.money}%'
                        for player3 in players:
                            player3.conn.send(money_data1.encode())
                            player3.conn.send(money_data2.encode())
                            information_sent_to('Информация отправлена к', player2.color, money_data1)
                            information_sent_to('Информация отправлена к', player2.color, money_data2)

                    elif data[0] == 'pay for prison':
                        player.money -= player.prison_break_attempts * 25
                        player.imprisoned = False
                        money_data = f'money|{player.color}|{player.money}%'
                        prison_data = f'unimprisoned|{player.color}%'
                        for player2 in players:
                            player2.conn.send(prison_data.encode())
                            player2.conn.send(money_data.encode())
                            information_sent_to('Информация отправлена к', player2.color, prison_data)
                            information_sent_to('Информация отправлена к', player2.color, money_data)

                    elif data[0] == 'penis build':
                        tile_position = int(data[1])
                        print(all_tiles[tile_position].full_family, all_tiles[tile_position].penises < 5, player.money >= all_tiles[tile_position].penis_price, all_tiles[tile_position].type == 'buildable', all_tiles[tile_position].owner == player.color)
                        if (all_tiles[tile_position].full_family and
                            all_tiles[tile_position].penises < 5 and
                            player.money >= all_tiles[tile_position].penis_price and
                            all_tiles[tile_position].type == 'buildable' and
                            all_tiles[tile_position].owner == player.color):

                            player.money -= all_tiles[tile_position].penis_price
                            all_tiles[tile_position].penises += 1
                            money_data = f'money|{player.color}|{player.money}%'
                            penis_data = f'penis built|{tile_position}%'
                            for player2 in players:
                                player2.conn.send(money_data.encode())
                                player2.conn.send(penis_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, money_data)
                                information_sent_to('Информация отправлена к', player2.color, penis_data)

                    elif data[0] == 'penis remove':
                        tile_position = int(data[1])

                        if (all_tiles[tile_position].full_family and
                                all_tiles[tile_position].penises < 5 and
                                all_tiles[tile_position].type == 'buildable' and
                                all_tiles[tile_position].owner == player.color):

                            player.money += round(all_tiles[tile_position].penis_price * 0.75)
                            all_tiles[tile_position].penises += 1
                            money_data = f'money|{player.color}|{player.money}%'
                            penis_data = f'penis removed|{tile_position}%'
                            for player2 in players:
                                player2.conn.send(money_data.encode())
                                player2.conn.send(penis_data.encode())
                                information_sent_to('Информация отправлена к', player2.color, money_data)
                                information_sent_to('Информация отправлена к', player2.color, penis_data)

                    elif data[0] == 'full family':
                        # for i in range(len(all_tiles)):
                        #     if all_tiles[i].family == data[1]:
                        #         all_tiles[i].full_family = True
                        pass

                    elif data[0] == 'exchange request':
                        for player2 in players:
                            if player2.color == data[3]:
                                exchange_request = f'exchange request|{data[1]}|{data[2]}|{player.color}%'
                                player2.conn.send(exchange_request.encode())
                                information_sent_to('Информация отправлена к', player2.color, exchange_request)

                    elif data[0] == 'exchange':
                        give_data = data[1].split('_')
                        get_data = data[2].split('_')
                        give_money = int(give_data[0])
                        get_money = int(get_data[0])
                        give_property = give_data[1].split('-')
                        get_property = get_data[1].split('-')
                        player.money = player.money - give_money + get_money
                        print(f'Обмен с {data[3]}: +{get_money}~, +{get_property}, -{give_money}~, -{give_property}')
                        for tile_position in give_property:
                            player.property.remove(int(tile_position))
                        for tile_position in get_property:
                            player.property.append(int(tile_position))
                            all_tiles[int(tile_position)].owner = player.color

                        for player2 in players:
                            if player2.color == data[3]:
                                player2.money = player2.money + give_money - get_money
                                for tile_position in give_property:
                                    player2.property.append(int(tile_position))
                                    all_tiles[int(tile_position)].owner = player2.color
                                for tile_position in get_property:
                                    player2.property.remove(int(tile_position))

                                all_property_information = f'all property|{player2.color}|'
                                for property in player2.property:
                                    all_property_information += f'{property}_'
                                all_property_information = all_property_information[:-1] + '%'
                                for player3 in players:
                                    player3.conn.send(all_property_information.encode())
                                    information_sent_to('Информация отправлена к', player3.color,all_property_information)

                        all_property_information = f'all property|{player.color}|'
                        for property in player.property:
                            all_property_information += f'{property}_'
                        all_property_information = all_property_information[:-1] + '%'
                        for player3 in players:
                            player3.conn.send(all_property_information.encode())
                            information_sent_to('Информация отправлена к', player3.color, all_property_information)

                    elif data[0] == 'exchange request rejected':
                        print(f'Игрок {player.color} отказался от обмена')

                    elif data[0] == 'mortgage':
                        tile = all_tiles[int(data[1])]
                        if not tile.mortgaged and tile.owner == player.color:
                            player.money += int(tile.price / 2)
                            tile.mortgaged = True
                            tile.mortgaged_moves_count = 15

                            price_update(tile)

                            for player2 in players:
                                mortgage_information = f'mortgaged|{data[1]}%'
                                money_information = f'money|{player.color}|{player.money}%'
                                player2.conn.send(mortgage_information.encode())
                                player2.conn.send(money_information.encode())
                                information_sent_to('Информация отправлена к', player2.color, mortgage_information)
                                information_sent_to('Информация отправлена к', player2.color, money_information)

                    elif data[0] == 'redeem':
                        tile = all_tiles[int(data[1])]
                        if tile.mortgaged and tile.owner == player.color:
                            player.money -= int(tile.price * 1.1 / 2)
                            tile.mortgaged = False

                            price_update(tile)

                            for player2 in players:
                                redeem_information = f'redeemed|{data[1]}%'
                                money_information = f'money|{player.color}|{player.money}%'
                                player2.conn.send(redeem_information.encode())
                                player2.conn.send(money_information.encode())
                                information_sent_to('Информация отправлена к', player2.color, redeem_information)
                                information_sent_to('Информация отправлена к', player2.color, money_information)

                    else:
                        player.conn.send(f'error|Незарегистрированная команда: {data[0]}'.encode())

            except (BlockingIOError, ConnectionAbortedError, ConnectionResetError, AttributeError):
                pass
            # except ConnectionAbortedError:
            #     pass
            # except ConnectionResetError:
            #     pass
            except:
                print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def players_send():
    for player in players:
        player_data = f'playersData|{player.color}|{player.money}|{player.piece_position}|{player.name}%'
        for player2 in players:
            player2.conn.send(player_data.encode())
            information_sent_to('Информация отправлена к', player2.color, player_data)


def connection():
    while not is_game_started and running:
        player = Player('', '', colors[0])
        try:
            player.connect(colors)
            players.append(player)
            print(f'Игрок с цветом {player.color} добавлен в список')
        except BlockingIOError:
            pass
        except:
            print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def disconnect_check():
    while running:
        for player in players:
            try:
                player.conn.send('test'.encode())
            except:
                colors.append(player.color)
                deleted_color = player.color
                print(f'Игрок {player.color} отключился.\nЦвет {player.color} возвращён')
                player.clear()
                players.remove(player)
                players_send()
                for player2 in players:
                    deletion_player_data = f'playerDeleted|{deleted_color}%'
                    player2.conn.send(deletion_player_data.encode())
                    information_sent_to('Информация отправлена к', player2.color, deletion_player_data)
            time.sleep(1)


def start_server():
    global colors, main_sck, is_server_started
    if not is_server_started:
        try:
            ip = ip_textbox.getText()
            port = port_textbox.getText()
            if ip == '':
                ip = '26.190.64.4'
            if port == '':
                port = 1247
            else:
                port = int(port)
            main_sck = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
            main_sck.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)
            main_sck.bind((ip, port))
            main_sck.setblocking(False)
            main_sck.listen(4)  # количество доступных подключений
            colors = ['red', 'blue', 'yellow', 'green']
            random.shuffle(colors)
            is_server_started = True


            connection_handler = threading.Thread(target=connection, name='connection_handler')
            connection_handler.start()
            thread_open('Поток открыт', connection_handler.name)

            receive_handler = threading.Thread(target=receive_data, name='receive_handler')
            receive_handler.start()
            thread_open('Поток открыт', receive_handler.name)

            disconnect_handler = threading.Thread(target=disconnect_check, name='disconnect_handler')
            disconnect_handler.start()
            thread_open('Поток открыт', disconnect_handler.name)

            print(f'Сервер открыт: {ip}:{port}')

        except:
            print(f'{"\033[31m{}".format('Не удалось создать сервер')}{'\033[0m'}')


def start_game():
    global is_game_started
    if is_server_started and not is_game_started:
        is_game_started = True
        print('Игра начата')
        for player in players:
            player.conn.send('gameStarted%'.encode())
            player.conn.send(f'onMove|{players[0].color}%'.encode())
            information_sent_to('Информация отправлена к', player.color, 'gameStarted%')
            information_sent_to('Информация отправлена к', player.color, f'onMove|{players[0].color}%')


def moving_player_changing(do_change):
    if do_change:
        players.append(players[0])
        players.pop(0)
    for player in players:
        player.conn.send(f'onMove|{players[0].color}%'.encode())
        information_sent_to('Информация отправлена к', player.color, f'onMove|{players[0].color}%')
        for tile in all_tiles:
            if tile.mortgaged:
                tile.mortgaged_moves_count -= 1
                if tile.mortgaged_moves_count == 0:
                    tile.mortgaged = False
                    tile.owned = False
                    tile.owner = ''
                    for player2 in players:
                        late_to_redeem_information = f'late to redeem|{tile.position}%'
                        player2.conn.send(late_to_redeem_information.encode())
                        information_sent_to('Информация отправлена к', player2.color, late_to_redeem_information)
                for tile_ in all_tiles:
                    if tile_.family == tile.family:
                        tile_.family_members -= 1
                tile.family_members = 0


def position_update(color):
    for player in players:
        if player.color == color:
            if color == 'red':
                player.x = positions[player.piece_position][0]
                player.y = positions[player.piece_position][1]
            elif color == 'green':
                player.x = positions[player.piece_position][0] + piece_color_coefficient
                player.y = positions[player.piece_position][1]
            elif color == 'yellow':
                player.x = positions[player.piece_position][0]
                player.y = positions[player.piece_position][1] + piece_color_coefficient
            elif color == 'blue':
                player.x = positions[player.piece_position][0] + piece_color_coefficient
                player.y = positions[player.piece_position][1] + piece_color_coefficient
            screen.blit(pg.image.load(f'resources/{resolution_folder}/pieces/{player.color}_piece.png'), (player.x, player.y))


def blit_items():
    screen.blit(background, (0, 0))
    screen.blit(board, (0, 0))

    for tile in all_tiles:
        if tile.family != 'Угловые':
            screen.blit(globals()[f'tile_{tile.position}_image'], (tile.x_position, tile.y_position))
        if tile.owned:
            screen.blit(pg.image.load(f'resources/{resolution_folder}/property/{tile.owner}_property.png'), (tile.x_position, tile.y_position))
        if tile.mortgaged:
            screen.blit(mortgaged_tile, (tile.x_position, tile.y_position))
            text = font.render(str(tile.mortgaged_moves_count), False, 'white')
            text_rect = text.get_rect(center=(tile.x_center, tile.y_center))
            screen.blit(text, text_rect)
        if 1 <= tile.penises <= 5:
            screen.blit(pg.image.load(f'resources/{resolution_folder}/white penises/{tile.penises}.png'), (tile.x_position, tile.y_position))

    for player in players:
        position_update(player.color)

        player_index = players.index(player)

        screen.blit(profile_picture,
                    (profile_coordinates[player_index]['profile'][0],
                     profile_coordinates[player_index]['profile'][1]))

        screen.blit(avatar_file, (profile_coordinates[player_index]['avatar'][0],
                                    profile_coordinates[player_index]['avatar'][1]))

        if player.imprisoned:
            screen.blit(player_bars, (profile_coordinates[player_index]['avatar'][0],
                                      profile_coordinates[player_index]['avatar'][1]))

        screen.blit(pg.image.load(f'resources/{resolution_folder}/profile/{player.color}_profile.png'),
                    (profile_coordinates[player_index]['avatar'][0],
                     profile_coordinates[player_index]['avatar'][1]))



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

            if tile.angle == -90:
                offset = round((font.size(tile.text)[0] - 31) / 2)
            elif tile.angle == 90:
                offset = round((font.size(tile.text)[0] - 29) / 2)
            else:
                offset = 0

            text_rect = text.get_rect(center=(tile.xText + offset, tile.yText - offset))
            screen.blit(price_text, text_rect)


def event_handler():
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            global running
            running = False
    pygame_widgets.update(events)


def buttons():
    global start_button, ip_textbox, port_textbox, start_server_button
    ip_textbox = TextBox(screen,
                         start_btn_textboxes_coordinates['IP'][0],
                         start_btn_textboxes_coordinates['IP'][1],
                         start_btn_textboxes_coordinates['IP'][2],
                         start_btn_textboxes_coordinates['IP'][3],
                         colour=(200, 200, 200),
                         textColour=(0, 0, 0),
                         borderThickness=2,
                         borderColour=(0, 0, 0),
                         font=font,
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
                           font=font,
                           radius=btn_radius,
                           placeholderText='Порт',
                           placeholderTextColour=(128, 128, 128))

    start_server_button = Button(screen,
                          1121,
                          534,
                          140,
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
                          text='Запуск сервера',
                          onClick=start_server)

    start_button = Button(screen,
                          1121,
                          592,
                          140,
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
                          text='Начать игру',
                          onClick=start_game)


def active_buttons_check():
    # Бросок кубов
    if is_game_started or not is_server_started:
        screen.blit(start_game_disabled_btn, (1121, 592, 140, 38))

    if is_server_started:
        screen.blit(start_server_disabled_btn, (1121, 534, 140, 38))


buttons()
running = True

while running:
    clock.tick(FPS)
    blit_items()
    price_printing()
    event_handler()
    active_buttons_check()
    pg.display.flip()

for i in range(40):
    print(f'\rУдаление временных файлов: {i + 1} из 40.', end='\r', flush=True)
    if i not in (0, 10, 20, 30):
        os.remove(f'resources/temp/server/images/{i}.png')
print('\nСервер закрыт')