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

            btn_coordinates = {'throw_cubes':   (953, 20, 136, 38),
                                'buy':          (953, 78, 136, 38),
                                'pay':          (953, 136, 136, 38),
                                'shove_penis':  (953, 194, 136, 38),
                                'remove_penis': (953, 252, 136, 38),
                                'exchange':     (1109, 20, 136, 38)}

            btn_font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', 25)

            profile_coordinates = [{'profile': [669, 20], 'avatar': [830, 46], 'money': [674, 38], 'name': [674, 18]},
                                    {'profile': [669, 169], 'avatar':[830, 195] , 'money': [674, 187], 'name': [674, 167]},
                                    {'profile': [669, 318], 'avatar':[830, 344] , 'money': [674, 336], 'name': [674, 316]},
                                    {'profile': [669, 467], 'avatar':[830, 493] , 'money': [674, 485], 'name': [674, 465]}]

            exchange_coordinates = {'exchange_screen': (75, 75),
                                    'text_give': (120, 160),
                                    'text_get': (345, 160)}

            start_btn_textboxes_coordinates = {'name':          (1065, 384, 196, 30),
                                                'IP':            (1065, 430, 134, 30),
                                                'port':          (1202, 430, 59, 30),
                                                'connect':       (1121, 476, 140, 38),
                                                'choose_avatar': (1121, 534, 140, 38),
                                                'ready':         (1121, 592, 140, 38)}
            cubes_coordinates = [(961, 565), (1037, 565)]
            avatar_side_size = 100
            speed = 3
            is_resolution_selected = True

        elif resolution_index == '2':
            resolution = (1920, 1001)
            resolution_folder = '1080p'
            piece_color_coefficient = 42
            btn_radius = 10
            bars_coordinates = (897, 3)

            btn_coordinates = {'throw_cubes':   (1455, 30, 204, 57),
                                'buy':          (1455, 117, 204, 57),
                                'pay':          (1455, 204, 204, 57),
                                'shove_penis':  (1455, 291, 204, 57),
                                'remove_penis': (1455, 378, 204, 57),
                                'exchange':     (1689, 30, 204, 57)}

            btn_font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', 25)

            profile_coordinates = [{'profile': [1028, 30], 'avatar': [1262, 66], 'money': [1034, 62], 'name': [1034, 34]},
                                    {'profile': [1028, 249], 'avatar': [1262, 285], 'money': [1034, 281], 'name': [1034, 253]},
                                    {'profile': [1028, 468], 'avatar': [1262, 504], 'money': [1034, 500], 'name': [1034, 472]},
                                    {'profile': [1028, 687], 'avatar': [1262, 723], 'money': [1034, 719], 'name': [1034, 691]}]

            exchange_coordinates = {'exchange_screen': (108, 108),
                                    'text_give': (177, 240),
                                    'text_get': (530, 240)}

            start_btn_textboxes_coordinates = {'name':          (1689, 660, 134, 30),
                                                'IP':            (1689, 710, 134, 30),
                                                'port':          (1826, 710, 59, 30),
                                                'connect':       (1689, 760, 201, 57),
                                                'choose_avatar': (1689, 837, 201, 57),
                                                'ready':         (1689, 914, 201, 57)}
            cubes_coordinates = [(1499, 906), (1694, 906)]
            avatar_side_size = 150
            speed = 30
            is_resolution_selected = True
        else:
            print('Введены некорректные данные\n')
    return resolution, resolution_folder, piece_color_coefficient, bars_coordinates, btn_coordinates, btn_font, profile_coordinates, start_btn_textboxes_coordinates, btn_radius, cubes_coordinates, speed, avatar_side_size, exchange_coordinates