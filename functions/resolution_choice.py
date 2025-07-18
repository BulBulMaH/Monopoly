import pygame as pg

def resolution_definition():
    is_resolution_selected = False
    while not is_resolution_selected:
        resolution_index = input('Введите разрешение экрана:\n1 - 1280x720\n2 - 1920x1080\n')
        if resolution_index == '1':
            resolution = (1280, 650)
            resolution_folder = '720p'
            piece_color_coefficient = 28
            btn_radius = 2
            bars_coordinates = (582, 2)
            btn_coordinates = [(953, 20, 136, 38),  # Бросить кубы
                               (953, 78, 136, 38),  # Купить
                               (953, 136, 136, 38), # Оплатить
                               (953, 78, 136, 38),  # На аукцион
                               (953, 78, 136, 38)]
            btn_text_coordinates = [(963, 24),
                                    (993, 82)]
            btn_font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', 25)
            #                        профиль      цвет      деньги      имя
            profile_coordinates = [[[669, 20], [830, 46], [674, 38], [674, 18]],
                                   [[669, 169], [830, 195], [674, 187], [674, 167]],
                                   [[669, 318], [830, 344], [674, 336], [674, 316]],
                                   [[669, 467], [830, 493], [674, 485], [674, 465]]]
            start_btn_textboxes_coordinates = [(1065, 442, 196, 30), # имя
                                               (1065, 488, 134, 30), # IP
                                               (1202, 488, 59, 30),  # порт
                                               (1110, 534, 136, 38), # кнопка "Подключиться"
                                               (1110, 592, 136, 38)] # кнопка "Начать игру"
            cubes_coordinates = [(1109, 20), (1195, 20)]
            speed = 15
            is_resolution_selected = True

        elif resolution_index == '2':
            resolution = (1920, 1001)
            resolution_folder = '1080p'
            piece_color_coefficient = 42
            btn_radius = 10
            bars_coordinates = (897, 3)
            btn_coordinates = [(1455, 30, 204, 57),  # Бросить кубы
                               (1455, 117, 204, 57), # Купить
                               (1455, 204, 204, 57), # Оплатить
                               (1455, 291, 204, 57)] # На аукцион
            btn_text_coordinates = [(1475, 40), (1514, 127)]
            btn_font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', 25)
            #                         профиль      цвет       деньги        имя
            profile_coordinates = [[[1028, 30], [1262, 66], [1034, 62], [1034, 32]],
                                   [[1028, 249], [1262, 285], [1034, 281], [1034, 251]],
                                   [[1028, 468], [1262, 504], [1034, 500], [1034, 470]],
                                   [[1028, 687], [1262, 723], [1034, 719], [1034, 689]]]
            start_btn_textboxes_coordinates = [(1689, 737, 134, 30),  # имя
                                               (1689, 787, 134, 30),  # IP
                                               (1826, 787, 59, 30),   # порт
                                               (1689, 837, 201, 57),  # кнопка "Подключиться"
                                               (1689, 914, 201, 57)]  # кнопка "Начать игру"
            cubes_coordinates = [(1689, 30), (1784, 30)]
            speed = 30
            is_resolution_selected = True
        else:
            print('Введены некорректные данные\n')
    return resolution, resolution_folder, piece_color_coefficient, bars_coordinates, btn_coordinates, btn_text_coordinates, btn_font, profile_coordinates, start_btn_textboxes_coordinates, btn_radius, cubes_coordinates, speed