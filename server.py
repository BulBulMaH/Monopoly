import socket as sck
import time
import random

property = []
colors = ['color red','color blue','color yellow','color green']
random.shuffle(colors)
class Player():
    def __init__(self,conn,address,piecePos,color):
        self.conn = conn
        self.address = address
        self.piecePos = piecePos
        self.name = ''
        self.property = property
        self.errors = 0
        self.color = color

main_sck = sck.socket(sck.AF_INET,sck.SOCK_STREAM)
main_sck.setsockopt(sck.IPPROTO_TCP,sck.TCP_NODELAY,1)
main_sck.bind(('26.197.29.62',1247))
main_sck.setblocking(0)
main_sck.listen(4) #количество доступных подключений
print('Sck создан')
startPos = 0
players = []
dataList = []
data = ''
allPlayersData = [[],[],[],[]]

while True:
    #проверка наличия желающих войти в игру
    try:
        new_sck, address = main_sck.accept()
        print('Новое подключение:',address)
        new_sck.setblocking(0)
        new_player = Player(new_sck,address,startPos,colors[0])
        data = new_player.conn.recv(1024).decode()
        print('Получение:', data)
        if 'name' in data:
            new_player.name = data[5:]
        print('Имя:', new_player.name)
        colors.pop(0)
        new_player.conn.send(new_player.color.encode())
        print('Игроку',new_player.name,'назначен цвет',new_player.color)
        players.append(new_player)
    except:
        pass
    try:
        data = new_player.conn.recv(1024).decode()
        data1 = data[:-1]
        print('Data =', data1)
        for i in range(6):
            dataList.append(data1.split(','))
            print('Получение списка:', dataList)
        for i in range(4):
            
            print(allPlayersData)
            new_player.conn.send(allPlayersData.encode())
    except:
        pass
    #считывание команд игроков
    #отправление нового состояния поля
    for player in players:
        try:
            player.conn.send('ТеСт'.encode())
            player.errors = 0
        except:
            player.errors += 1
            if player.errors == 1 or player.errors == 100 or player.errors == 200 or player.errors == 300 or player.errors == 400:
                print('У игрока',player.name,'проблемы...')
        if player.errors == 500:
            colors.append(player.color)
            random.shuffle(colors)
            print('Цвет возвращён в список:',player.color)
            print('Отключение игрока:',player.name)
            player.conn.close()
            players.remove(player)
    time.sleep(0.01)