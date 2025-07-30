import socket as sck
import time
import random
import threading
import traceback

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
        self.prison_bribe = self.prison_break_attempts * 25
        self.money = 1500
        self.ready = False
        self.on_move = False
        self.avatar = []

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
        information_sent('Информация отправлена', color_data_main)

        game_start_check_handler = threading.Thread(target=game_start_check, name='game_start_check_handler')
        game_start_check_handler.start()
        thread_open('Поток открыт', game_start_check_handler.name)

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

all_tiles = []
test = open(f'resources/720p/text values/kletki.txt', 'r', encoding='utf-8')
information = test.readlines()
test.close()
for i in range(40):
    all_tiles.append(Tiles(information[i]))
information.clear()

main_sck = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
main_sck.setsockopt(sck.IPPROTO_TCP,sck.TCP_NODELAY, 1)
main_sck.bind(('26.190.64.4',1247))
main_sck.setblocking(False)
main_sck.listen(4) # количество доступных подключений
print('Сервер открыт')

players = []
colors = ['red', 'blue', 'yellow', 'green']
random.shuffle(colors)
is_game_started = False

def receive_data():
    while True:
        for player in players:
            try:
                data_temp = player.conn.recv(1024)
                data = data_temp.decode().split('|')
                if data != ['']:
                    information_received('Информация получена', data)

                if data[0] == 'name':
                    player.name = data[1]
                    players_send()

                elif data[0] == 'avatar':
                    player.avatar.append(data_temp)
                    if data[2] == data[4][:-1]:
                        players_send()

                elif data[0] == 'move':
                    cube1 = random.randint(1,6)
                    cube2 = random.randint(1,6)
                    double = cube1 == cube2

                    if player.imprisoned:
                        if double:
                            player.imprisoned = False
                            player.prison_break_attempts = 0
                            prison_data = f'unimprisoned|{player.color}%'
                            for player2 in players:
                                player2.conn.send(prison_data.encode())
                                information_sent('Информация отправлена', prison_data)
                        else:
                            player.prison_break_attempts += 1

                        if player.prison_break_attempts >= 3:
                            prison_bribe_data = f'bribe|{player.prison_bribe}%'
                            player.conn.send(prison_bribe_data.encode())
                            information_sent_to('Информация отправлена к', player.color, prison_bribe_data)

                    else:
                        cube_sum = cube1 + cube2
                        player.piece_position += cube_sum

                        if player.piece_position == 40:
                            player.money += 100
                            money_data = f'money|{player.color}|{player.money}%'
                            for player2 in players:
                                player2.conn.send(money_data.encode())
                                information_sent('Информация отправлена', money_data)

                        if player.piece_position > 39:
                            player.piece_position -= 40
                            player.money += 2000 # todo убрать 2000
                            money_data = f'money|{player.color}|{player.money}%'
                            for player2 in players:
                                player2.conn.send(money_data.encode())
                                information_sent('Информация отправлена', money_data)

                        move_data = f'move|{player.color}|{cube1}|{cube2}%'
                        for player2 in players:
                            player2.conn.send(move_data.encode())
                            information_sent('Информация отправлена', move_data)

                        if player.piece_position == 30:
                            player.piece_position = 10
                            player.imprisoned = True
                            prison_data = f'imprisoned|{player.color}%'
                            move_data = f'move diagonally|{player.color}|30|10%'
                            for player2 in players:
                                player2.conn.send(prison_data.encode())
                                player2.conn.send(move_data.encode())
                                information_sent('Информация отправлена', prison_data)
                                information_sent('Информация отправлена', move_data)

                        elif player.piece_position == 10:
                            player.piece_position = 30
                            move_data = f'move diagonally|{player.color}|10|30%'
                            for player2 in players:
                                player2.conn.send(move_data.encode())
                                information_sent('Информация отправлена', move_data)

                elif data[0] == 'nextPlayer':
                    moving_player_changing()

                elif data[0] == 'buy':
                    if player.piece_position == int(data[1]):
                        player.piece_position = int(data[1])
                        if player.money >= int(all_tiles[player.piece_position].price):
                            player.property.append(player.piece_position)
                            all_tiles[player.piece_position].owned = True
                            all_tiles[player.piece_position].owner = player.color
                            for tile in all_tiles:
                                if tile.family_members == all_tiles[player.piece_position].family:
                                    tile.family_members += 1
                            player.money -= int(all_tiles[player.piece_position].price)
                            property_data = f'property|{player.color}|{data[1]}%'
                            money_data = f'money|{player.color}|{player.money}%'
                            for player2 in players:
                                player2.conn.send(property_data.encode())
                                player2.conn.send(money_data.encode())
                                information_sent('Информация отправлена', property_data)
                                information_sent('Информация отправлена', money_data)
                        else:
                            player.conn.send('error|У вас недостаточно пЭнисов, чтобы это купить. '
                                             'Вы не должны были получить это сообщение. '
                                             'Только если у вас чИтЫ??7?%'.encode())
                    else:
                        player.conn.send('error|Произошла разсинхронизация, сервер думает, что вы находитесь '
                                         f'на {player.piece_position} позиции, но у вас позиция {data[1]}. '
                                         'Вы не должны были получить это сообщение. '
                                         'Только если у вас чИтЫ??7?%'.encode())

                elif data[0] == 'moved':
                    print(f'Игрок {player.color} переместился.')

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
                        information_sent('Информация отправлена', money_data)

                elif data[0] == 'payToColor':
                    player.piece_position = int(data[1])
                    if all_tiles[player.piece_position].type == 'infrastructure':
                        cube1 = random.randint(1, 6)
                        cube2 = random.randint(1, 6)
                        if not all_tiles[player.piece_position].full_family:
                            pay_sum = (cube1 + cube2) * 4
                        else:
                            pay_sum = (cube1 + cube2) * 10
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
                        information_sent('Информация отправлена', money_data1)
                        information_sent('Информация отправлена', money_data2)

                elif data[0] == 'pay for prison':
                    player.money -= player.prison_bribe
                    player.imprisoned = False
                    prison_data = f'unimprisoned|{player.color}%'
                    for player2 in players:
                        player2.conn.send(prison_data.encode())
                        information_sent('Информация отправлена', prison_data)

            except BlockingIOError:
                pass
            except:
                print(f'{"\033[31m{}".format(traceback.format_exc())}{'\033[0m'}')


def players_send():
    for player in players:
        player_data = f'playersData|{player.color}|{player.money}|{player.piece_position}|{player.name}%'
        for player2 in players:
            for avatar in player.avatar:
                time.sleep(0.07)
                player2.conn.send(avatar)
                print(avatar)
            player2.conn.send(player_data.encode())
            information_sent_to('Информация отправлена к', player2.color, player_data)


def connection():
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
    while True:
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


def game_start_check():
    global is_game_started
    while not is_game_started:
        all_ready_states = []
        try:
            for player in players:
                all_ready_states.append(player.ready)
            if False not in all_ready_states and players:
                is_game_started = True
                print('Игра начата')
                for player in players:
                    player.conn.send('gameStarted%'.encode())
                    player.conn.send(f'onMove|{players[0].color}%'.encode())
        except:
            pass


def moving_player_changing():
    players.append(players[0])
    players.pop(0)
    for player in players:
        player.conn.send(f'onMove|{players[0].color}%'.encode())
        information_sent('Информация отправлена', f'onMove|{players[0].color}%')


receive_handler = threading.Thread(target=receive_data, name='receive_handler')
receive_handler.start()
thread_open('Поток открыт', receive_handler.name)

disconnect_handler = threading.Thread(target=disconnect_check, name='disconnect_handler')
disconnect_handler.start()
thread_open('Поток открыт', disconnect_handler.name)

while not is_game_started:
    connection()

