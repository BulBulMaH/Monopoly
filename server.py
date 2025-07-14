import socket as sck
import time
import random
import threading

from functions.colored_output import thread_open, new_connection, information_received, information_sent, information_sent_to
from functions.Tiles_Class import Tiles

class Player:
    def __init__(self,conn,address,color):
        self.conn = conn
        self.address = address
        self.piece_position = 0
        self.name = ''
        self.property = []
        self.color = color
        self.imprisoned = False
        self.money = 1500
        self.ready = False
        self.on_move = False

    def connect(self, colors):
        new_sck, address = main_sck.accept()
        new_connection('Новое подключение', address)
        new_sck.setblocking(False)
        self.conn = new_sck
        self.address = address
        colors.pop(0)
        color_data_main = 'color main|' + self.color
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
test = open(f'resources/720p/text values/kletki.txt', 'r')
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
colors = ['red','blue','yellow','green']
random.shuffle(colors)
is_game_started = False

def receive_data():
    while True:
        for player in players:
            try:
                data_temp = player.conn.recv(1024).decode()
                data = data_temp.split('|')
                if data != ['']:
                    information_received('Информация получена', data)

                if data[0] == 'name':
                    player.name = data[1]

                elif data[0] == 'move':
                    cube1 = random.randint(1,6)
                    cube2 = random.randint(1,6)
                    cube_sum = cube1 + cube2
                    player.piece_position += cube_sum
                    if player.piece_position > 39:
                        player.piece_position -= 39
                        player.money += 200
                        money_data = f'money|{player.color}|{player.money}'
                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            information_sent('Информация отправлена', money_data)
                    if player.piece_position == 0:
                        player.money += 100
                        money_data = f'money|{player.color}|{player.money}'
                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            information_sent('Информация отправлена', money_data)
                    move_data = f'move|{player.color}|{cube1}|{cube2}'
                    for player2 in players:
                        player2.conn.send(move_data.encode())
                        information_sent('Информация отправлена',move_data)

                elif data[0] == 'nextPlayer':
                    moving_player_changing()

                elif data[0] == 'buy':
                    player.property.append(data[1])
                    player.money -= int(all_tiles[int(data[1])].priceTxt)
                    property_data = f'property|{player.color}|{data[1]}'
                    money_data = f'money|{player.color}|{player.money}'
                    for player2 in players:
                        player2.conn.send(property_data.encode())
                        player2.conn.send(money_data.encode())
                        information_sent('Информация отправлена', property_data)
                        information_sent('Информация отправлена', money_data)

                elif data[0] == 'moved':
                    print(f'Игрок {player.color} переместился.')

                elif data[0] == 'ready':
                    player.ready = True

                elif data[0] == 'pay':
                    player.piece_position = int(data[1])
                    if player.piece_position == 4 or player.piece_position == 38:
                        player.money += int(all_tiles[player.piece_position].priceTxt)
                    else:
                        player.money -= all_tiles[player.piece_position].penis_income_calculation()
                    money_data = f'money|{player.color}|{player.money}'
                    for player2 in players:
                        player2.conn.send(money_data.encode())
                        information_sent('Информация отправлена', money_data)


            except:
                pass


def players_send():
    for player in players:
        time.sleep(0.1)
        player_data = f'playersData|{player.color}|{player.money}|{player.piece_position}|{player.name}'
        for player2 in players:
            player2.conn.send(player_data.encode())
            information_sent_to('Информация отправлена к', player2.color, player_data)
            time.sleep(0.02)


def connection():
    player = Player('', '', colors[0])
    try:
        player.connect(colors)
        players.append(player)
        print(f'Игрок с цветом {player.color} добавлен в список')
        time.sleep(0.1)
        players_send()
    except:
        pass


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
                    deletion_player_data = 'playerDeleted|' + deleted_color
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
                    player.conn.send('gameStarted'.encode())
                    time.sleep(0.01)
                    player.conn.send(f'onMove|{players[0].color}'.encode())
        except:
            pass


def moving_player_changing():
    players.append(players[0])
    players.pop(0)
    for player in players:
        player.conn.send(f'onMove|{players[0].color}'.encode())
        information_sent('Информация отправлена', f'onMove|{players[0].color}')


receive_handler = threading.Thread(target=receive_data, name='receive_handler')
receive_handler.start()
thread_open('Поток открыт', receive_handler.name)

disconnect_handler = threading.Thread(target=disconnect_check, name='disconnect_handler')
disconnect_handler.start()
thread_open('Поток открыт', disconnect_handler.name)

while not is_game_started:
    connection()

