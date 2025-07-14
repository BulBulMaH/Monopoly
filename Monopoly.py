import pygame as pg
import socket as sck
import threading
import time
import pygame_widgets
from pygame_widgets.button import Button

pg.init()
clock = pg.time.Clock()

is_resolution_selected = False
while not is_resolution_selected:
    resolution_index = int(input('Введите разрешение экрана:\n1 - 1280x720\n2 - 1920x1080\n'))
    if resolution_index == 1:
        resolution = (1280, 650)
        resolution_folder = '720p'
        piece_color_coefficient = 28
        bars_coordinates = (582, 2)
        btn_coordinates = [(953, 20, 136, 38), (953, 78, 136, 38)]
        btn_text_coordinates = [(963, 24), (993, 82)]
        btn_font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', 25)
        profile_coordinates = [[[669, 20], [830, 46], [674, 48]],
                               [[669, 169], [830, 195], [674, 197]],
                               [[669, 318], [830, 344], [674, 346]],
                               [[669, 467], [830, 493], [674, 495]]]
        is_resolution_selected = True
    elif resolution_index == 2:
        resolution = (1920, 1001)
        resolution_folder = '1080p'
        piece_color_coefficient = 42
        bars_coordinates = (897, 3)
        btn_coordinates = [(1455, 30, 204, 57), (1455, 117, 204, 57)]
        btn_text_coordinates = [(1475, 40), (1514, 127)]
        btn_font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', int(37.5))
        profile_coordinates = [[[1028, 30], [1262, 66], [1034, 69]],
                               [[1028, 249], [1262, 285], [1034, 288]],
                               [[1028, 468], [1262, 504], [1034, 507]],
                               [[1028, 687], [1262, 723], [1034, 726]]]
        is_resolution_selected = True
    else:
        print('Введены некорректные данные')

positions_file = open(f'resources/{resolution_folder}/text values/positions.txt')
positions_temporary = positions_file.readlines()
positions_file.close()
positions = []
for i in range(len(positions_temporary)):
    positions.append(positions_temporary[i].split(','))
    positions[i][1] = positions[i][1][:-1]
positions_temporary.clear()
for i in range(len(positions)):
    for ii in range(len(positions[i])):
        positions[i][ii] = int(positions[i][ii])

class Player:
    def __init__(self,color):
        self.piece_position = 0
        self.name = ''
        self.property = []
        self.color = color
        self.money = 1500
        self.main = False
        self.x = positions[0][0]
        self.y = positions[0][1]
        self.baseX = positions[0][0]
        self.baseY = positions[0][1]

    def main_color(self, main_color, name):
        self.color = main_color
        self.name = name
        self.main = True
        print('Основной цвет:',self.color)

class Tiles:
    def __init__(self, inf):
        information_list = inf.split(',')
        self.position = int(information_list[0])
        self.buyable = information_list[1]
        self.type = information_list[2]
        self.family = information_list[3]
        self.descr = information_list[4]
        self.xText = int(information_list[5])
        self.yText = int(information_list[6])
        self.priceTxt = information_list[7]
        self.color = information_list[8]
        self.angle = int(information_list[9])

all_tiles = []
test = open(f'resources/{resolution_folder}/text values/kletki.txt', 'r')
information = test.readlines()
test.close()
for i in range(40):
    all_tiles.append(Tiles(information[i]))
information.clear()

buy_btn_active = False

all_players = [Player('red'), Player('green'), Player('yellow'), Player('blue')]
players = []

sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)

# avatarBool = False
# while not avatarBool:
#     avatar_path = input('Введите путь к аватару:\n')
#     try:
#         avatar = open(avatar_path, 'rb').read()
#         avatar_size = os.path.getsize(avatar_path)
#         print(avatar_size)
#         avatarBool = True
#     except:
#         print('Файл не найден')

named = False
while not named:
    name_temporary = input('Введите имя:\n')
    if name_temporary != '':
        name = name_temporary
        named = True

connected = False
while not connected:
    try:
        sock.connect(('26.190.64.4', 1247))
        connected = True
    except:
        print('Не удалось подключиться')


# sock.send(avatar)

screen = pg.display.set_mode(resolution)
pg.display.set_caption('Monopoly v0.5') # название игры
background = pg.image.load(f'resources/{resolution_folder}/board.png')
bars = pg.image.load(f'resources/{resolution_folder}/bars.png')
font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)
button_texture = pg.image.load(f'resources/{resolution_folder}/button.png')
button_pressed = pg.image.load(f'resources/{resolution_folder}/buttonPressed.png')
button_mouse_collided = pg.image.load(f'resources/{resolution_folder}/buttonMouseCollided.png')
button_disabled = pg.image.load(f'resources/{resolution_folder}/buttonDisabled.png')
profile_picture = pg.image.load(f'resources/{resolution_folder}/profile/profile.png')

running = True

def throw_cubes():
    print('Кнопка "Бросить кубы" нажата')
    for player in players:
        if player.main:
            move_command = 'move'
            sock.send(move_command.encode())
            print('Команда отправлена:', move_command)

def buy():
    if buy_btn_active:
        print('Кнопка "Купить" нажата')
        for player in players:
            if player.main:
                buy_command = 'buy|' + str(player.piece_position)
                sock.send(buy_command.encode())
                print('Команда отправлена:', buy_command)
    else:
        print('Кнопка "Купить" нажата, но она отключена')


cube_button = Button(screen,
                     btn_coordinates[0][0],
                     btn_coordinates[0][1],
                     btn_coordinates[0][2],
                     btn_coordinates[0][3],
                     inactiveColour=(255, 255, 255),
                     inactiveBorderColour=(0, 0, 0),
                     hoverColour=(255, 255, 255),
                     hoverBorderColour=(105, 105, 105),
                     pressedColour=(191, 191, 191),
                     pressedBorderColour=(0, 0, 0),
                     borderThickness=3,
                     radius=2,
                     font=font,
                     text='Бросить кубы',
                     onClick=throw_cubes)
buy_button = Button(screen,
                     btn_coordinates[1][0],
                     btn_coordinates[1][1],
                     btn_coordinates[1][2],
                     btn_coordinates[1][3],
                     inactiveColour=(255, 255, 255),
                     inactiveBorderColour=(0, 0, 0),
                     hoverColour=(255, 255, 255),
                     hoverBorderColour=(105, 105, 105),
                     pressedColour=(191, 191, 191),
                     pressedBorderColour=(0, 0, 0),
                     borderThickness=3,
                     radius=2,
                     font=font,
                     text='Купить',
                     onClick=buy)


def blit_items():
    screen.blit(background, (0, 0))  # инициализация поля
    for player in players:
        player_index = players.index(player)
        screen.blit(profile_picture, (profile_coordinates[player_index][0][0], profile_coordinates[player_index][0][1]))
        screen.blit(pg.image.load(f'resources/{resolution_folder}/profile/{player.color}Profile.png'),
                    (profile_coordinates[player_index][1][0], profile_coordinates[player_index][1][1]))
        screen.blit(btn_font.render(f'{player.money}~', False, 'black'),
                    (profile_coordinates[player_index][2][0], profile_coordinates[player_index][2][1] - 10))
        position_update(player.color, player.baseX, player.baseY)

        for company in player.property:
            screen.blit(pg.image.load(f'resources/{resolution_folder}/{player.color}Property.png'), ((int(positions[company][0])), int(positions[company][1])))

    screen.blit(bars, bars_coordinates)

def price_printing():
    for tile in all_tiles:
        if tile.priceTxt != '':
            text = font.render(f'{tile.priceTxt}~', False, tile.color)
            text_rect = text.get_rect()
            text_rect.center = (tile.xText,tile.yText)
            price_text = pg.transform.rotate(text,tile.angle)

            screen.blit(price_text, text_rect)

def position_update(color, x, y):
    for player in players:
        if player.color == color:
            if color == 'red':
                player.x = x
                player.y = y
            elif color == 'green':
                player.x = x + piece_color_coefficient
                player.y = y
            elif color == 'yellow':
                player.x = x
                player.y = y + piece_color_coefficient
            elif color == 'blue':
                player.x = x + piece_color_coefficient
                player.y = y + piece_color_coefficient
            screen.blit(pg.image.load(f'resources/{resolution_folder}/{player.color}Piece.png'), (player.x, player.y))

def move(color, cube1, cube2):
    for player in players:
        if player.color == color:
            if player.main:
                global buy_btn_active
                buy_btn_active = False
            for i in range(cube1 + cube2):
                start = [positions[player.piece_position][0], positions[player.piece_position][1]]
                player.piece_position += 1
                if player.piece_position > 39:
                    player.piece_position = 0
                end = [positions[player.piece_position][0], positions[player.piece_position][1]]
                tile_width = max(abs(positions[player.piece_position][0] - positions[player.piece_position - 1][0]),
                                 abs(positions[player.piece_position][1] - positions[player.piece_position - 1][1]))
                diff_x = end[0] - start[0]
                diff_y = end[1] - start[1]

                if min(diff_x, diff_y) != 0:
                    x_step = diff_x / min(diff_x, diff_y)
                    y_step = diff_y / min(diff_x, diff_y)
                else:
                    x_step = diff_x / max(diff_x, diff_y)
                    y_step = diff_y / max(diff_x, diff_y)

                for ii in range(tile_width):
                    time.sleep(1/120)

                    x_sign = 1
                    y_sign = 1

                    if 0 < player.piece_position <= 20:
                        x_sign = 1
                        y_sign = 1
                    elif 20 < player.piece_position <= 30:
                        x_sign = -1
                        y_sign = 1
                    elif player.piece_position > 30 or player.piece_position == 0:
                        x_sign = -1
                        y_sign = -1

                    player.baseX += x_step * x_sign
                    player.baseY += y_step * y_sign
                    position_update(player.color, player.baseX, player.baseY)

                    print(f'\nЦвет: {player.color}\nСтарт: {start}\nКонец: {end}\nРазница: {diff_x}, {diff_y}\nШаги: {x_step}, {y_step}\nКоординаты игрока: {player.baseX}, {player.baseY}\nПозиция игрока: {player.piece_position}\nШирина клетки: {tile_width}\nЗнаки: {x_sign}, {y_sign}\nПуть (в клетках): {i}')
                print(f'\nИГРОК {player.color} НА НОВОЙ КЛЕТКЕ {player.piece_position}!')
            player.baseX = positions[player.piece_position][0]
            player.baseY = positions[player.piece_position][1]
            buy_btn_check(player.color)
            if player.main:
                sock.send('moved'.encode())


def handle_connection(sock, positions):
    while True:
        data_temp = sock.recv(1024).decode()
        data = data_temp.replace('test','').split('|')
        if data[0] != '':
            print('Информация получена:', data)
        if data[0] == 'color main':
            for allPlayer in all_players:
                if allPlayer.color == data[1]:
                    allPlayer.main_color(data[1], name)

        elif data[0] == 'move':
            move(data[1], int(data[3]), int(data[4]))

        elif data[0] == 'playersData':
            data.remove('playersData')
            for allPlayer in all_players:
                for i in data:
                    if i == allPlayer.color:
                        if allPlayer not in players:
                            players.append(allPlayer)
            for player in players:
                if player.color == data[0]:
                    player.money = int(data[1])
                    player.piece_position = int(data[2])
                    player.baseX = positions[player.piece_position][0]
                    player.baseY = positions[player.piece_position][1]
                    position_update(player.color, player.baseX, player.baseY)

        elif data[0] == 'property':
            for player in players:
                if data[2] == player.color:
                    player.property.append(int(data[1]))
                    print(f'У {player.color} есть {player.property}')
                    buy_btn_check(data[2])

        elif data[0] == 'money':
            for player in players:
                if data[1] == player.color:
                    player.money = int(data[2])

        elif data[0] == 'playerDeleted':
            for player in players:
                if player.color == data[1]:
                    players.remove(player)

        if not running:
            break

def events_check():
    events = pg.event.get()
    pygame_widgets.update(events)
    for event in events:
        if event.type == pg.QUIT:
            global running
            running = False

def buy_btn_check(color):
    global buy_btn_active
    for player in players:
        if player.main and player.color == color:
            for allPlayer in players:
                if (all_tiles[player.piece_position].buyable == 'True' and
                        player.piece_position not in allPlayer.property and
                        player.money - int(all_tiles[player.piece_position].priceTxt) > 0):

                    buy_btn_active = True
                else:
                    buy_btn_active = False


    if not buy_btn_active:
        screen.blit(button_disabled, (btn_coordinates[1][0], btn_coordinates[1][1]))
        screen.blit(font.render('Купить', False, 'black'), (btn_text_coordinates[1][0], btn_text_coordinates[1][1]))
    print(f'\nКнопка покупки объявлена {buy_btn_active}')

def button_anim():
    global button_disabled
    if not buy_btn_active:
        screen.blit(button_disabled, (btn_coordinates[1][0], btn_coordinates[1][1]))
        screen.blit(btn_font.render('Купить', False, (128, 128, 128)), (btn_text_coordinates[1][0], btn_text_coordinates[1][1]))



connHandler = threading.Thread(target = handle_connection, args=(sock,positions,), name='ConnectionHandler')
connHandler.start()

while running:
    blit_items()
    price_printing()
    events_check()
    button_anim()
    pg.display.update()
    clock.tick(60)
pg.quit()
