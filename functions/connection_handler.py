from functions.position_update import position_update
from functions.move import move
from functions.buy_button_check import buy_btn_check

def handle_connection(sock, positions, name, running, screen):
    global all_players, players, state
    while True:
        try:
            data_temp = sock.recv(1024).decode()
            data = data_temp.replace('test','').split('|')
            if data[0] != '':
                print('Информация получена:', data)
            if data[0] == 'color main':
                for allPlayer in all_players:
                    if allPlayer.color == data[1]:
                        allPlayer.main_color(data[1], name)

            elif data[0] == 'move':
                move(data[1], int(data[3]), int(data[4]), positions, sock)

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
                        position_update(player.color, player.baseX, player.baseY, screen)

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

            elif data[0] == 'gameStarted':
                state['is_game_started'] = True

            if not running:
                break
        except:
            pass