import pygame as pg
import socket as sck
import random
import pygame_textinput as txt_inp
import time

pg.init()
allProperty = [ # [name, family, textX, textY, color, price, buildPrice, tax1, tax2, tax3, tax4, tax5, tax6, tax7]
    ['Начало', 'Угловые локации', 'Отсюда начинается игра. При прохождении этого поля, вам даётся 200G','','','','','','','','','','',''],
    ['Иван 1', 'Иваны', 129, 105, 'black', 60, 50, 2, 4, 10, 30, 90, 160, 250],
    ['Груда вопросительных яиц 1', 'Груды вопросительных яиц', 'Тяните карту!','','','','','','','','','','',''],
    ['Иван 2', 'Иваны', 253, 105, 'black', 60, 50, 4, 8, 20, 60, 180, 320, 450],
    ['Глеб 1', 'Глебы', 311, 105, 'white', -200,'','','','','','','',''],
    ['Егор 1', 'Егоры', 381, 105, 'black', 200,'','','','','','','',''],
    ['Василий 1', 'Василии', 448, 105, 'black', 100, 50, 6, 12, 30, 90, 270, 400, 550],
    ['Вопросительное яйцо 1', 'Вопросительные яйца', 'Тяните карту!','','','','','','','','','','',''],
    ['penis.', 'Василии', 580, 105, 'black', 100, 50, 6, 12, 30, 90, 270, 400, 550],
    ['Василий 3', 'Василии', 640, 105, 'black', 100, 50, 8, 16, 40, 100, 300, 450, 600],
    ['Тюрьма', 'Угловые локации', 'Вы - злобный нарушитель!', 100, 50],
    ['Доминика 1', 'Доминики', 678, 124, 'black', 140, 100, 10, 20, 50, 150, 450, 625, 750],
    ['Данил 1', 'Данилы', 678, 185, 'black', 250,'','','','','','','',''],
    ['Доминика 2', 'Доминики', 678, 249, 'black', 140, 100, 10, 20, 50, 150, 450, 625, 750],
    ['Доминика 3', 'Доминики', 678, 314, 'black', 140, 100, 12, 24, 60, 180, 500, 700, 900],
    ['Егор 2', 'Егоры', 678, 380, 'black', 200,'','','','','','','',''],
    ['Артём 1', 'Артёмы', 678, 446, 'black', 180, 100, 14, 28, 70, 200, 550, 750, 950],
    ['Груда вопросительных яиц 2', 'Груды вопросительных яиц', 'Тяните карту!','','','','','','','','','','',''],
    ['Артём 2', 'Артёмы', 678, 579, 'black', 180, 100, 14, 28, 70, 200, 550, 750, 950],
    ['Артём 3', 'Артёмы', 678, 637, 'black', 180, 100, 16, 32, 80, 220, 600, 800, 1000],
    ['Ничего', 'Угловые локации', 'Самая безопасная локация. Ведь так же?','','','','','','','','','','',''],
    ['Никита 1', 'Никиты', 639, 681, 'black', 220, 150, 22, 44, 110, 330, 800, 975, 1150],
    ['Вопросительное яйцо 1', 'Вопросительные яйца', 'Тяните карту!','','','','','','','','','','',''],
    ['Никита 2', 'Никиты', 514, 681, 'black', 220, 150, 22, 44, 110, 330, 800, 975, 1150],
    ['Никита 3', 'Никиты', 448, 681, 'black', 220, 150, 24, 48, 120, 360, 850, 1025, 1200],
    ['Егор 3', 'Егоры', 382, 681, 'black', 200,'','','','','','','',''],
    ['Василий Киммель 1', 'Киммели', 314, 681, 'black', 260, 150, 18, 36, 90, 250, 700, 875, 1050],
    ['Василий Киммель 2', 'Киммели', 249, 681, 'black', 260, 150, 18, 36, 90, 250, 700, 875, 1050],
    ['Данил 1', 'Данилы', 185, 681, 'black', 250,'','','','','','','',''],
    ['Василий Киммель 3', 'Киммели', 124, 681, 'black', 260, 150, 20, 40, 100, 300, 750, 925, 1100],
    ['Туда', 'Угловые локации', 'Тууудаааа!','','','','','','','','','','',''],
    ['Даниил 1', 'Даниилы', 105, 633, 'black', 300, 200, 26, 52, 130, 390, 900, 1100, 1275],
    ['Даниил 2', 'Даниилы', 105, 578, 'black', 300, 200, 26, 52, 130, 390, 900, 1100, 1275],
    ['Груда вопросительных яиц 1', 'Груды вопросительных яиц', 'Тяните карту!'],
    ['Даниил 3', 'Даниилы', 105, 444, 'black', 300, 200, 28, 56, 150, 450, 1000, 1200, 1400],
    ['Егор 1', 'Егоры', 105, 379, 'black', 200,'','','','','','','',''],
    ['Вопросительное яйцо 1', 'Вопросительные яйца', 'Тяните карту!','','','','','','','','','','',''],
    ['Дмитрий 1', 'Дмитрии', 105, 247, 'black', 350, 200, 35, 70, 175, 500, 1100, 1300, 1500],
    ['Глеб 1', 'Глебы', 105, 178, 'white', -100,'','','','','','','',''],
    ['Дмитрий 2', 'Дмитрии', 105, 124, 'black', 350, 200, 50, 100, 200, 600, 1400, 1700, 1200]
    ]
quesEgg = [
    'Вам надо к Егору',
    'Вам надо к Егору',
    'Вам надо к Егору',
    'Вы - злобный нарушитель и вам надо в тюрьму',
    'Артём отдаёт вам часть долга в размере 50~. (но Артём переложил ответственность на банк)',
    'Вам надо к Данилу', #?
    'Вам к щедрому Дмитрию',
    'Вам надо к первой Доминике',
    'Вам надо пройти к началу',
    'Артём заставляет Вас дать ему в долг 15~.',
    'Вам нужно к опасному Никите',
    'Артём сегодня очень щедрый и отдаёт Вам 150~. (но Артём переложил ответственность на банк)',
    'Впереди страшные вещи. Вернитесь на три клетки назад',
    'Вы сможете выйти из тюрьмы' #придумать механику
]
quesEggs = [
    'Артём отдаёт Вам 20~',
    'Артём отдаёт Вам 25~. (но Артём переложил ответственность на банк)',
    'Артём щедрый и отдаёт Вам 100~. (но Артём переложил ответственность на банк)',
    'Вам нужно заплатить налог на звёзды. За одну звезду - 50~',
    'все платят Вам 10~',
    'Артём насильно забирает у Вас в долг 100~',
    'Вам надо пройти к началу',
    'Артём никогда не был таким щедрым и отдаёт Вам 200~. (но Артём переложил ответственность на банк)',
    'Вы - злобный нарушитель и вам надо в тюрьму',
    'Артём выплачивает часть долга в размере 100~. (но Артём переложил ответственность на банк)',
    'Артём выплачивает часть долга в размере 100~. (но Артём переложил ответственность на банк)',
    'Артём отдаёт Вам часть долга в размере 50~. (но Артём переложил ответственность на банк)',
    'Артём умоляет Вас дать ему в долг 50~. Вы соглашаетесь. Я сказал соглашаетесь!',
    'Артём обворовывает Вас на 50~. Вы записали эту сумму в счёт долга',
    'Артём случайно уронил 10~ и сказал, что это плата по долгу. Вы получили 10~',
    'Вы сможете выйти из тюрьмы'  # придумать механику
]

screen = pg.display.set_mode((1280,797))
pg.display.set_caption('Monopoly v0.1') #название игры
background = pg.image.load('resources/images/board/board.png') #объявление поля
font = pg.font.Font('resources/fonts/bulbulpoly.ttf',int(15.8090625))
mainFont = pg.font.Font('resources/fonts/cardsfont.ttf',int(14))
priceFont = pg.font.Font('resources/fonts/bulbulpoly-2.ttf',int(7))
red = pg.image.load('resources/images/players/redPlayer.png')
buttonTexture = pg.image.load('resources/images/interactive/button.png')
buttonPressed = pg.image.load('resources/images/interactive/buttonPressed.png')
buttonMouseCollided = pg.image.load('resources/images/interactive/buttonMouseCollided.png')
connectButton = pg.Rect(860,129,134,36)
playButton = pg.Rect(860,194,134,36)
buyButton = pg.Rect(860,373,134,36)
ipInput = pg.Rect(861,24,134,36)
nameInput = pg.Rect(861,64,134,36)
manager = txt_inp.TextInputManager(validator = lambda input: len(input) <= 12)
nameTxtInp = txt_inp.TextInputVisualizer(manager = manager,font_object = font,font_color = 'white',cursor_color = 'white')
ipTxtInp = txt_inp.TextInputVisualizer(manager = manager,font_object = font,font_color = 'white',cursor_color = 'white')
piecesImg = ['resources/images/players/bluePlayer.png',
             'resources/images/players/greenPlayer.png',
             'resources/images/players/redPlayer.png',
             'resources/images/players/yellowPlayer.png']
pos1, pos2 = 0, 0
name = ''
color = ''
property = []
inPrison = False
piecePos = 0
allData = []
oldAllData = ['1']
isConnPressed = False
pieceCol_defined = False
piece = ''
piec = 0
pieceX, pieceY = 23, 23
q = 0
angle = 0 - 90
true = True
while true:
    screen.fill((64,64,64))
    screen.blit(background,(0,0)) #инициализация поля
    screen.blit(buttonTexture,(859,128)) #подключиться
    screen.blit(buttonTexture,(859,194)) #играть
    screen.blit(buttonTexture,(859,372)) #купить
    screen.blit(mainFont.render('подключиться',False,'black'), (864, 127))
    screen.blit(mainFont.render('играть', False, 'black'), (900, 194))
    screen.blit(mainFont.render('позиция: ' + str(piecePos), False, 'white'), (860, 317))
    screen.blit(mainFont.render('купить', False, 'black'), (900, 372))

    # отрисовка цен
    for face in range(len(allProperty)):
        for pos1 in range(12):
            for pos2 in range(face + 1): # иначе он не видит посл. клетку
                pass
        if type(allProperty[pos2][2]) is not str:
            priceTextVal = str(allProperty[pos2][5]) + '~'
            if pos2 > 10 and pos2 < 20:
                priceText = pg.transform.rotate(priceFont.render(priceTextVal, False, (allProperty[pos2][4])), angle)
            elif pos2 > 30 and pos2 < 40:
                priceText = pg.transform.rotate(priceFont.render(priceTextVal, False, (allProperty[pos2][4])), 90)
            else:
                priceText = priceFont.render(priceTextVal, False, (allProperty[pos2][4]))
            screen.blit(priceText,(allProperty[pos2][2], allProperty[pos2][3]))


    events = pg.event.get()
    for event in events:
        if event.type == pg.MOUSEBUTTONDOWN and playButton.collidepoint(event.pos):
            firCube = random.randint(1, 6)
            secCube = random.randint(1, 6)
            sumCubes = firCube + secCube
            piecePosX = sumCubes * 66
            print('Первый куб:',firCube,', второй куб:',secCube,', сумма:',sumCubes)
            for ee in range(sumCubes):
                for piecePosX in range(66):
                    q += 1
                    if q/66 >= 1:
                        piecePos +=1
                        q = 0
                        #print(piecePos)
                        if piecePos == 1:
                            pieceX = 107
                        elif piecePos == 10:
                            pieceX = 720
                        elif piecePos == 11:
                            pieceY = 107
                        elif piecePos == 20:
                            pieceY = pieceX
                        elif piecePos == 21:
                            pieceX = 635
                        elif piecePos == 30:
                            pieceX = 23
                        elif piecePos == 31:
                            pieceY = 635
                        elif piecePos == 40:
                            pieceY = 23
                            pieceX = pieceY
                            piecePos = 0
                    if pieceX <= 720 and pieceY <= 100:
                        pieceX += 1
                    elif pieceX > 720 and pieceY < 720:
                        pieceY += 1
                    elif pieceX > 23 and pieceY > 720:
                        pieceX -= 1
                    elif pieceX >= 23 and pieceY <= 721:
                        pieceY -= 1

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and connectButton.collidepoint(event.pos) and not isConnPressed:
            isConnPressed = True
            name = (f'{nameTxtInp.value}')
            screen.blit(buttonPressed,(859, 128))
            # print(f'Подтверждён IP: {ipTxtInp.value}')
            print('Подтверждён ник:', name)
            sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
            sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)
            sock.connect(('26.197.29.62', 1247))
            sock.send(f'name {nameTxtInp.value}'.encode())
            data = sock.recv(1024).decode()  # получение состояния поля
            if 'color' in data:
                color = data[6:]
                print('Цвет получен:', color)
                for piec in range(len(piecesImg)):
                    if color in piecesImg[piec]:
                        print('Отрисован',piecesImg[piec])
                        piece = pg.image.load(piecesImg[piec])
                        pieceCol_defined = True
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and buyButton.collidepoint(event.pos):
            print('buy')
        if event.type == pg.QUIT:
            true = False
            pg.quit()
    try:
        screen.blit(mainFont.render('значения кубов: ' + str(firCube) + ', ' + str(secCube), False, 'white'), (860, 259))
    except:
        pass
    nameTxtInp.update(events)
    screen.blit(nameTxtInp.surface, (861, 64))
    if pieceCol_defined:
        screen.blit(piece,(pieceX,pieceY))
    if playButton.collidepoint(pg.mouse.get_pos()):
        screen.blit(buttonMouseCollided, (859,194))
        screen.blit(mainFont.render('играть', False, (105,105,105)), (900, 194))
    if connectButton.collidepoint(pg.mouse.get_pos()) and not isConnPressed:
        screen.blit(buttonMouseCollided,(859,128))
        screen.blit(mainFont.render('подключиться', False, (105,105,105)), (864, 127))
    if buyButton.collidepoint(pg.mouse.get_pos()):
        screen.blit(buttonMouseCollided, (859,372))
        screen.blit(mainFont.render('купить', False, (105,105,105)), (900, 372))
    if isConnPressed:
        allData = [name, color, piecePos, inPrison, property]
        if allData != oldAllData:
            oldAllData = allData
            y = str(allData)
            sock.send(y.encode())
            print('Информация отправлена:', allData)

    pg.display.update()
    time.sleep(0.01)