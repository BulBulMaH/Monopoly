import socket as sck
import time
import random

main_sck = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
main_sck.setsockopt(sck.IPPROTO_TCP,sck.TCP_NODELAY,1)
main_sck.bind(('26.197.29.62',1247))
main_sck.setblocking(0)
main_sck.listen(4) #количество доступных подключений
print('Sck создан')
players = []
colors = ['color red','color blue','color yellow','color green']
random.shuffle(colors)
while True:
    #проверка наличия желающих войти в игру
    try:
        new_sck, address = main_sck.accept()
        print('Новое подключение: ',address)
        new_sck.setblocking(0)
        player = new_sck
        players.append(player)
    except:
        pass
    #считывание команд игроков
    for player in players:
        try:
            player.send(colors[0].encode())
            colors.remove(0)
            random.shuffle(colors)
            print('Цвет назначен: ', colors[0])
            print(colors[player])
        except:
            pass
    for player in players:
        try:
            data = player.recv(1024).decode()
            print('Получение',data)
        except:
            pass
        # отправление нового состояния поля
        for player in players:
            try:
                player.send(' '.encode())
                player.errors = 0
            except:
                player.close()
                players.remove(player)
        time.sleep(1)