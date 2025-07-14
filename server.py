import socket as sck
import time
import random
import threading

class Player():
    def __init__(self,conn,address,color):
        self.conn = conn
        self.address = address
        self.piecePos = 0
        self.name = ''
        self.property = []
        self.color = color
        self.imprisoned = False
        self.money = 1500

    def connect(self,colors):
        new_sck, address = main_sck.accept()
        print('Новое подключение:', address)
        new_sck.setblocking(0)
        self.conn = new_sck
        self.address = address
        colors.pop(0)
        colorDataMain = 'color main|' + self.color
        self.conn.send(colorDataMain.encode())
        print('Игроку', self.address, 'назначен', self.color, 'цвет')
        print('Информация отправлена:',colorDataMain)

    def clear(self):
        self.conn = ''
        self.address = ''
        self.piecePos = 0
        self.name = ''
        self.property = []
        self.imprisoned = False
        self.money = 1500

class Tiles():
    def __init__(self, positionNumber,inf):
        inflist = inf.split(',')
        self.position = int(inflist[0])
        self.type = inflist[2]
        self.family = inflist[3]
        self.priceTxt = inflist[7]

allTiles = []
test = open(f'resources/720p/text values/kletki.txt', 'r')
inf = test.readlines()
test.close()
for i in range(40):
    allTiles.append(Tiles(i,inf[i]))
inf = []

main_sck = sck.socket(sck.AF_INET,sck.SOCK_STREAM)
main_sck.setsockopt(sck.IPPROTO_TCP,sck.TCP_NODELAY,1)
main_sck.bind(('26.190.64.4',1247))
main_sck.setblocking(0)
main_sck.listen(4) # количество доступных подключений
print('Сервер открыт')

redPlayer = Player('','','red')
greenPlayer = Player('','','green')
yellowPlayer = Player('','','yellow')
bluePlayer = Player('','','blue')

players = []
all_players = [redPlayer, greenPlayer, yellowPlayer, bluePlayer]
colors = ['red','blue','yellow','green']
random.shuffle(colors)

def receiveData():
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
                    cubeSum = cube1 + cube2
                    double = cube1 == cube2
                    player.piece_position += cubeSum
                    if player.piece_position > 39:
                        player.piece_position -= 39
                        player.money += 200
                        moneyData = f'money|{player.color}|{player.money}'
                        for player2 in players:
                            player2.conn.send(moneyData.encode())
                            print('Информация отправлена:', moneyData)
                    if player.piece_position == 0:
                        player.money += 100
                        moneyData = f'money|{player.color}|{player.money}'
                        for player2 in players:
                            player2.conn.send(moneyData.encode())
                            print('Информация отправлена:', moneyData)
                    moveData = f'move|{player.color}|{player.piece_position}|{cube1}|{cube2}'
                    for player2 in players:
                        player2.conn.send(moveData.encode())
                        print('Информация отправлена:',moveData)

                if data[0] == 'buy':
                    player.property.append(data[1])
                    player.money -= int(allTiles[int(data[1])].priceTxt)
                    for company in player.property:
                        propertyData = company + '|'
                    propertyData = 'property|' + propertyData[:-1] + '|' + player.color
                    moneyData = f'money|{player.color}|{player.money}'
                    for player2 in players:
                        player2.conn.send(propertyData.encode())
                        player2.conn.send(moneyData.encode())
                        print(f'Информация отправлена: {propertyData}, {moneyData}')

                if data[0] == 'moved':
                    print(f'Игрок {player.color} переместился.')
        except:
            pass

def playersSend():
    playersData = ''
    propertyData = ''
    for player in players:
        playersData += f'playersData|{player.color}|{player.money}|{player.piece_position}|_'
        print(playersData)
        if player.property != []:
            for company in player.property:
                propertyData = company + '|'
            propertyData = 'property|' + propertyData[:-1] + '|' + player.color

    playersData = playersData[:-2]
    playersData = playersData.split('_')
    for player2 in players:
        playersDataTemp = list(playersData)
        print(playersDataTemp, playersData)
        player2.conn.send(propertyData.encode())
        print(f'Информация отправлена к {player2.color} цвету: {propertyData}')
        for i in range(len(playersDataTemp)):
            time.sleep(0.12)
            player2.conn.send(playersDataTemp[0].encode())
            print(f'Информация отправлена к {player2.color} цвету: {playersDataTemp[0]}')
            playersDataTemp.pop(0)

def connectCheck(colors,redPlayer,greenPlayer,yellowPlayer,bluePlayer):
    try:
        if colors[0] == 'red':
            redPlayer.connect(colors)
            players.append(redPlayer)
        elif colors[0] == 'green':
            greenPlayer.connect(colors)
            players.append(greenPlayer)
        elif colors[0] == 'yellow':
            yellowPlayer.connect(colors)
            players.append(yellowPlayer)
        elif colors[0] == 'blue':
            bluePlayer.connect(colors)
            players.append(bluePlayer)
        print(f'Игрок с цветом {colors[0]} добавлен в список')
        time.sleep(1)
        playersSend()
    except:
        pass

def disconnectCheck():
    while True:
        for player in players:
            try:
                player.conn.send('test'.encode())
            except:
                colors.append(player.color)
                deleted_color = player.color
                print(f'Игрок {player.color} отключился.\nЦвет {player.color} возвращён')
                player.piece_position = 0
                player.money = 1500
                player.property = []
                player.name = ''
                players.remove(player)
                playersSend()
                for player2 in players:
                    deletion_playerData = 'playerDeleted|' + deleted_color
                    player2.conn.send(deletion_playerData.encode())
                    print(f'Информация отправлена к {player2.color} цвету: {deletion_playerData}')
            time.sleep(1)



receiveHandler = threading.Thread(target=receiveData,name='receiveHandler')
receiveHandler.start()
print('Поток открыт:', receiveHandler.name)

disconnectHandler = threading.Thread(target=disconnectCheck,name='disconnectHandler')
disconnectHandler.start()
print('Поток открыт:', disconnectHandler.name)

running = True
while running:
    connectCheck(colors, redPlayer, greenPlayer, yellowPlayer, bluePlayer)
