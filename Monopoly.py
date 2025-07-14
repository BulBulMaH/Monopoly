import pygame as pg
import socket as sck
import random
import time
import threading
import math

pg.init()
clock = pg.time.Clock()

print('Введите разрешение экрана:\n1 - 1280x720\n2 - 1920x1080')
resBool = False
while not resBool:
    resNum = int(input())
    if resNum == 1:
        res = (1280,650)
        resFolder = '720p'
        pieceColorCoef = 28
        barsCoords = (582, 2)
        btnCoords = [(953, 20, 136, 38),(953, 78, 136, 38)]
        btnTextCoords = [(963,24),(993,82)]
        btnFont = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)
        profileCoords = [[[669, 20], [830, 46], [674, 48]],
                         [[669, 169], [830, 195], [674, 197]],
                         [[669, 318], [830, 344], [674, 346]],
                         [[669, 467], [830, 493], [674, 495]]]
        resBool = True
    elif resNum == 2:
        res = (1920,1001)
        resFolder = '1080p'
        pieceColorCoef = 42
        barsCoords = (897,3)
        btnCoords = [(1455, 30, 204, 57),(1455, 117, 204, 57)]
        btnTextCoords = [(1475,40),(1514,127)]
        btnFont = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', int(37.5))
        profileCoords = [[[1028, 30], [1262, 66], [1034, 69]],
                         [[1028, 249], [1262, 285], [1034, 288]],
                         [[1028, 468], [1262, 504], [1034, 507]],
                         [[1028, 687], [1262, 723], [1034, 726]]]
        resBool = True
    else:
        print('Введены некорректные данные')

positionsFile = open(f'resources/{resFolder}/text values/positions.txt')
positionsTemp = positionsFile.readlines()
positionsFile.close()
positions = []
for i in range(len(positionsTemp)):
    positions.append(positionsTemp[i].split(','))
    positions[i][1] = positions[i][1][:-1]
positionsTemp = []
for i in range(len(positions)):
    for ii in range(len(positions[i])):
        positions[i][ii] = int(positions[i][ii])

class Player():
    def __init__(self,color):
        self.piecePos = 0
        self.name = ''
        self.property = []
        self.color = color
        self.money = 1500
        self.main = False
        self.x = positions[0][0]
        self.y = positions[0][1]
        self.baseX = positions[0][0]
        self.baseY = positions[0][1]

    def mainColor(self,mainColor):
        self.color = mainColor
        self.main = True
        print('Основной цвет:',self.color)

class Tiles():
    def __init__(self, positionNumber,inf):
        inflist = inf.split(',')
        self.position = int(inflist[0])
        self.buyable = inflist[1]
        self.type = inflist[2]
        self.family = inflist[3]
        self.descr = inflist[4]
        self.xText = int(inflist[5])
        self.yText = int(inflist[6])
        self.priceTxt = inflist[7]
        self.color = inflist[8]
        self.angle = int(inflist[9])

allTiles = []
test = open(f'resources/{resFolder}/text values/kletki.txt', 'r')
inf = test.readlines()
test.close()
for i in range(40):
    allTiles.append(Tiles(i,inf[i]))
inf = []

redPlayer = Player('red')
greenPlayer = Player('green')
yellowPlayer = Player('yellow')
bluePlayer = Player('blue')
global buy_btn_active
buy_btn_active = False

allPlayers = [redPlayer,greenPlayer,yellowPlayer,bluePlayer]
players = []

sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)

connected = False
while not connected:
    try:
        sock.connect(('26.197.29.62', 1247))
        connected = True
    except:
        print('Не удалось подключиться')

screen = pg.display.set_mode(res)
pg.display.set_caption('Monopoly v0.3') #название игры
background = pg.image.load(f'resources/{resFolder}/board.png')
bars = pg.image.load(f'resources/{resFolder}/bars.png')

font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)
buttonTexture = pg.image.load(f'resources/{resFolder}/button.png')
buttonPressed = pg.image.load(f'resources/{resFolder}/buttonPressed.png')
buttonMouseCollided = pg.image.load(f'resources/{resFolder}/buttonMouseCollided.png')
buttonDisabled = pg.image.load(f'resources/{resFolder}/buttonDisabled.png')

profilePicture = pg.image.load(f'resources/{resFolder}/profile/profile.png')

cubeButton = pg.Rect(btnCoords[0][0],btnCoords[0][1],btnCoords[0][2],btnCoords[0][3])
buyButton = pg.Rect(btnCoords[1][0],btnCoords[1][1],btnCoords[1][2],btnCoords[1][3])

global startSpeed
startSpeed = 3
xStart = positions[0][0]
yStart = positions[0][1]
running = True

def blitItems(screen,background,buttonTexture,font):
    screen.blit(background, (0, 0))  # инициализация поля
    screen.blit(buttonTexture, (btnCoords[0][0],btnCoords[0][1]))  # играть
    screen.blit(buttonTexture, (btnCoords[1][0],btnCoords[1][1]))  # купить

    screen.blit(font.render('Бросить кубы', False, 'black'), (btnTextCoords[0][0],btnTextCoords[0][1]))
    # screen.blit(mainFont.render('позиция: ' + str(piecePos), False, 'white'), (860, 317))
    screen.blit(font.render('Купить', False, 'black'), (btnTextCoords[1][0], btnTextCoords[1][1]))

    # screen.blit(pg.image.load('resources/main imgs/debug/номера клеток.png'),(0, 0))

    for player in players:
        playerNumber = players.index(player)
        screen.blit(profilePicture, (profileCoords[playerNumber][0][0], profileCoords[playerNumber][0][1]))
        screen.blit(pg.image.load(f'resources/{resFolder}/profile/{player.color}Profile.png'),
                    (profileCoords[playerNumber][1][0], profileCoords[playerNumber][1][1]))
        screen.blit(btnFont.render(f'{player.money}~', False, 'black'),
                    (profileCoords[playerNumber][2][0], profileCoords[playerNumber][2][1] - 10))
        positionUpdate(positions, player.color, player.baseX, player.baseY)

        for company in player.property:
            screen.blit(pg.image.load(f'resources/{resFolder}/{player.color}Property.png'),((int(positions[company][0])), int(positions[company][1])))

    screen.blit(bars, barsCoords)


def pricePrinting():
    for tile in allTiles:
        text = font.render(f'{tile.priceTxt}~', False, tile.color)
        text_rect = text.get_rect()
        text_rect.center = (tile.xText,tile.yText)
        priceText = pg.transform.rotate(text,tile.angle)

        screen.blit(priceText, text_rect)

def positionUpdate(positions, color, x, y):
    for player in players:
        if player.color == 'green':
            player.x = x + pieceColorCoef
        elif player.color == 'yellow':
            player.y = y + pieceColorCoef
        elif player.color == 'blue':
            player.x = x + pieceColorCoef
            player.y = y + pieceColorCoef
        screen.blit(pg.image.load(f'resources/{resFolder}/{player.color}Piece.png'), (player.x,player.y))

def move(color, piesePos, cube1, cube2):
    global buy_btn_active
    buyBtnActive = False
    for player in players:
        if player.color == color:
            global startSpeed

            for i in range(int(cube1) + int(cube2)):
                start = [positions[player.piece_position][0], positions[player.piece_position][1]]
                if player.piece_position + 1 <= 39:
                    end = [positions[player.piece_position + 1][0],
                           positions[player.piece_position + 1][1]]
                else:
                    end = [positions[player.piece_position - 39][0],
                           positions[player.piece_position - 39][1]]
                player.piece_position += 1
                if player.piece_position > 39:
                    player.piece_position = 0
                player.baseX = start[0]
                player.baseY = start[1]
                differenceX = end[0] - player.baseX
                differenceY = end[1] - player.baseY
                while abs(differenceX) >= abs(end[0] - player.baseX) and abs(differenceY) >= abs(end[1] - player.baseY):
                    print('\n')
                    print(f'i: {i}, cube 1: {cube1}, cube 2: {cube2}')
                    differenceX = end[0] - player.baseX
                    differenceY = end[1] - player.baseY
                    clock.tick(60)
                    print(f'Скорость: {startSpeed}')

                    xStep = (end[0] - start[0]) / start[0]
                    yStep = (end[1] - start[1]) / start[1]

                    print(f'Coarse steps: {xStep}, {yStep}.')

                    xStep /= max(abs(xStep), abs(yStep))
                    yStep /= max(abs(xStep), abs(yStep))

                    print(f'xStep: {xStep}, yStep: {yStep}, цвет: {player.color}')
                    print(differenceX,differenceY,'РАЗНИЦА')

                    player.baseX += xStep * startSpeed
                    player.baseY += yStep * startSpeed

                    print(f'Старт: {start}, конец: {end}.')
                    positionUpdate(positions, player.color, player.baseX, player.baseY)
                    print(f'Позиция: {player.x, player.y}, X: {player.baseX}, Y: {player.baseY}, ------------------------ позиция: {player.piece_position}')
                player.baseX = positions[player.piece_position][0]
                player.baseY = positions[player.piece_position][1]
                positionUpdate(positions, player.color, player.baseX, player.baseY)
            buyBtnCheck(players)
            print(f'Новая позиция у {player.color}: {player.piece_position}. Координаты: {player.x}, {player.y} / {positions[player.piece_position][0]}, {positions[player.piece_position][1]}')
            for player2 in players:
                print(player2.color, player2.x, player2.y, player2.piece_position)
        # startSpeed = 1.5

def handle_connection(sock, positions):
    while True:
        data_temp = sock.recv(1024).decode()
        data = data_temp.replace('test','').split('|')
        if data[0] != '':
            print('Информация получена:', data)
        if data[0] == 'color main':
            if data[1] == 'red':
                redPlayer.mainColor(data[1])
            elif data[1] == 'green':
                greenPlayer.mainColor(data[1])
            elif data[1] == 'yellow':
                yellowPlayer.mainColor(data[1])
            elif data[1] == 'blue':
                bluePlayer.mainColor(data[1])

        elif data[0] == 'move':
            move(data[1], data[2], data[3], data[4])

        elif data[0] == 'playersData':
            data.remove('playersData')
            for allPlayer in allPlayers:
                for i in data:
                    if i == allPlayer.color:
                        if allPlayer not in players:
                            players.append(allPlayer)
            for player in players:
                if player.color == data[0]:
                    player.money = int(data[1])
                    player.piece_position = int(data[2])
                    player.x = positions[player.piece_position][0]
                    player.y = positions[player.piece_position][1]

        elif data[0] == 'property':
            for player in players:
                if data[2] == player.color:
                    player.property.append(int(data[1]))
                    print('У',player.color,'есть',player.property)
                    buyBtnCheck(players)

        elif data[0] == 'money':
            for player in players:
                if data[1] == player.color:
                    player.money = int(data[2])

        if not running:
            break

def eventsCheck(players):
    events = pg.event.get()
    for event in events:
        if event.type == pg.MOUSEBUTTONDOWN and cubeButton.collidepoint(pg.mouse.get_pos()):
            print('Кнопка "Бросить кубы" нажата')
            screen.blit(buttonPressed, (btnCoords[0][0], btnCoords[0][1]))
            screen.blit(font.render('Бросить кубы', False, 'black'), (btnTextCoords[0][0],btnTextCoords[0][1]))
            for player in players:
                if player.main:
                    moveCommand = f'move|{player.color}'
                    sock.send(moveCommand.encode())
                    print('Команда отправлена:',moveCommand)
        if event.type == pg.MOUSEBUTTONDOWN and buyButton.collidepoint(pg.mouse.get_pos()) and buy_btn_active:
            print('Кнопка "Купить" нажата')
            screen.blit(buttonPressed, (btnCoords[1][0], btnCoords[1][1]))
            screen.blit(font.render('Купить', False, 'black'), (btnTextCoords[1][0],btnTextCoords[1][1]))
            for player in players:
                if player.main:
                    buyCommand = 'buy|' + str(player.piece_position)
                    sock.send(buyCommand.encode())
                    print('Команда отправлена:', buyCommand)
        if not buy_btn_active:
            screen.blit(buttonDisabled, (btnCoords[1][0], btnCoords[1][1]))
            screen.blit(font.render('Купить', False, 'black'), (btnTextCoords[1][0], btnTextCoords[1][1]))
        if event.type == pg.QUIT:
            running = False

def buyBtnCheck(players):
    global buy_btn_active
    for player in players:
        if player.main and allTiles[player.piece_position].buyable == 'True' and player.piece_position not in player.property:
            if player.money - int(allTiles[player.piece_position].priceTxt) > 0:
                buyBtnActive = True
            else:
                buyBtnActive = False
        else:
            buyBtnActive = False

def buttonAnim(buttonMouseCollided,buttonDisabled):
    if cubeButton.collidepoint(pg.mouse.get_pos()):
        screen.blit(buttonMouseCollided, (btnCoords[0][0],btnCoords[0][1]))
        screen.blit(btnFont.render('Бросить кубы', False, (128,128,128)), (btnTextCoords[0][0],btnTextCoords[0][1]))
    if buyButton.collidepoint(pg.mouse.get_pos()) and buy_btn_active:
        screen.blit(buttonMouseCollided, (btnCoords[1][0],btnCoords[1][1]))
        screen.blit(btnFont.render('Купить', False, (128,128,128)), (btnTextCoords[1][0],btnTextCoords[1][1]))
    if not buy_btn_active:
        screen.blit(buttonDisabled, (btnCoords[1][0], btnCoords[1][1]))
        screen.blit(btnFont.render('Купить', False, (128, 128, 128)), (btnTextCoords[1][0], btnTextCoords[1][1]))



connHandler = threading.Thread(target = handle_connection, args=(sock,positions,), name='ConnectionHandler')
connHandler.start()

while running:
    blitItems(screen,background,buttonTexture,btnFont)
    pricePrinting()
    eventsCheck(players)
    buttonAnim(buttonMouseCollided,buttonDisabled)
    pg.display.update()
    clock.tick(60)
pg.quit()
