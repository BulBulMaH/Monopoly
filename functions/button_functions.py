import socket as sck

def throw_cubes(players, sock, state):
    if state['is_game_started']:
        print('Кнопка "Бросить кубы" нажата')
        for player in players:
            if player.main:
                move_command = 'move'
                sock.send(move_command.encode())
                print('Команда отправлена:', move_command)


def buy(state, players, sock):
    if state['is_game_started'] and state['buy_btn_active']:
        print('Кнопка "Купить" нажата')
        for player in players:
            if player.main:
                buy_command = 'buy|' + str(player.piece_position)
                sock.send(buy_command.encode())
                print('Команда отправлена:', buy_command)


def start(state):
    if not state['is_game_started']:
        sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        sock.setsockopt(sck.IPPROTO_TCP, sck.TCP_NODELAY, 1)

        connected = False
        while not connected:
            try:
                sock.connect(('26.190.64.4', 1247))
                connected = True
            except:
                print('Не удалось подключиться')