import socket as sck
import time
import random
import threading

class Player():
    def __init__(self,conn,address,color):
        self.conn = conn
        self.address = address
        self.piece_position = 0
        self.name = ''
        self.property = []
        self.color = color
        self.imprisoned = False
        self.money = 1500

    def connect(self, colors):
        new_sck, address = main_sck.accept()
        print('Новое подключение:', address)
        new_sck.setblocking(False)
        self.conn = new_sck
        self.address = address
        colors.pop(0)
        color_data_main = 'color main|' + self.color
        self.conn.send(color_data_main.encode())
        print('Игроку', self.address, 'назначен', self.color, 'цвет')
        print('Информация отправлена:',color_data_main)

    def clear(self):
        self.conn = ''
        self.address = ''
        self.piece_position = 0
        self.name = ''
        self.property = []
        self.imprisoned = False
        self.money = 1500

class Tiles():
    def __init__(self, inf):
        information_list = inf.split(',')
        self.position = int(information_list[0])
        self.type = information_list[2]
        self.family = information_list[3]
        self.priceTxt = information_list[7]

all_tiles = []
test = open(f'resources/720p/text values/kletki.txt', 'r')
information = test.readlines()
test.close()
for i in range(40):
    all_tiles.append(Tiles(information[i]))
information.clear()

main_sck = sck.socket(sck.AF_INET,sck.SOCK_STREAM)
main_sck.setsockopt(sck.IPPROTO_TCP,sck.TCP_NODELAY,1)
main_sck.bind(('26.190.64.4',1247))
main_sck.setblocking(False)
main_sck.listen(4) # количество доступных подключений
print('Сервер открыт')

red_player = Player('', '', 'red')
green_player = Player('', '', 'green')
yellow_player = Player('', '', 'yellow')
blue_player = Player('', '', 'blue')

all_players = [Player('', '', 'red'),
               Player('', '', 'green'),
               Player('', '', 'yellow'),
               Player('', '', 'blue')]
players = []
colors = ['red','blue','yellow','green']
random.shuffle(colors)

def receive_data():
    while True:
        try:
            for player in players:
                data_temp = player.conn.recv(1024).decode()
                data = data_temp.split('|')
                if data != '':
                    print('Информация получена:', data)


                if data[0] == 'move':
                    cube1 = random.randint(1,6)
                    cube2 = random.randint(1,6)
                    cube_sum = cube1 + cube2
                    double = cube1 == cube2
                    player.piece_position += cube_sum
                    if player.piece_position > 39:
                        player.piece_position -= 39
                        player.money += 200
                        money_data = f'money|{player.color}|{player.money}'
                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            print('Информация отправлена:', money_data)
                    if player.piece_position == 0:
                        player.money += 100
                        money_data = f'money|{player.color}|{player.money}'
                        for player2 in players:
                            player2.conn.send(money_data.encode())
                            print('Информация отправлена:', money_data)
                    move_data = f'move|{player.color}|{player.piece_position}|{cube1}|{cube2}'
                    for player2 in players:
                        player2.conn.send(move_data.encode())
                        print('Информация отправлена:',move_data)

                if data[0] == 'buy':
                    player.property.append(data[1])
                    player.money -= int(all_tiles[int(data[1])].priceTxt)
                    for company in player.property:
                        property_data = company + '|'
                    property_data = 'property|' + property_data[:-1] + '|' + player.color
                    money_data = f'money|{player.color}|{player.money}'
                    for player2 in players:
                        player2.conn.send(property_data.encode())
                        player2.conn.send(money_data.encode())
                        print(f'Информация отправлена: {property_data}, {money_data}')

                if data[0] == 'moved':
                    print(f'Игрок {player.color} переместился.')
        except:
            pass

def players_send():
    players_data = ''
    property_data = ''
    for player in players:
        players_data += f'playersData|{player.color}|{player.money}|{player.piece_position}|_'
        print(players_data)
        if player.property:
            for company in player.property:
                property_data = company + '|'
            property_data = 'property|' + property_data[:-1] + '|' + player.color

    players_data = players_data[:-2]
    players_data = players_data.split('_')
    for player2 in players:
        players_data_temp = list(players_data)
        print(players_data_temp, players_data)
        player2.conn.send(property_data.encode())
        print(f'Информация отправлена к {player2.color} цвету: {property_data}')
        for i in range(len(players_data_temp)):
            time.sleep(0.12)
            player2.conn.send(players_data_temp[0].encode())
            print(f'Информация отправлена к {player2.color} цвету: {players_data_temp[0]}')
            players_data_temp.pop(0)


def connection():
    for player in all_players:
        if player.color == colors[0]:
            try:
                player.connect(colors)
                players.append(player)
                print(f'Игрок с цветом {player.color} добавлен в список')
                time.sleep(1)
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
                    print(f'Информация отправлена к {player2.color} цвету: {deletion_player_data}')
            time.sleep(1)



receiveHandler = threading.Thread(target=receive_data, name='receiveHandler')
receiveHandler.start()
print('Поток открыт:', receiveHandler.name)

disconnectHandler = threading.Thread(target=disconnect_check, name='disconnectHandler')
disconnectHandler.start()
print('Поток открыт:', disconnectHandler.name)

running = True
while running:
    connection()
