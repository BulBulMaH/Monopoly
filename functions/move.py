import time
from functions.position_update import position_update
from functions.buy_button_check import buy_btn_check

def move(color, cube1, cube2, positions, sock):
    global players
    for player in players:
        if player.color == color:
            if player.main:
                global state
                state['buy_btn_active'] = False
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