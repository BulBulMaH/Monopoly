import pygame as pg
import csv
from Tiles_Class import Tiles
from PIL import Image

def resolution_definition(do_choose):
    is_resolution_selected = False
    while not is_resolution_selected:
        if do_choose:
            lines = open('settings.txt', 'r').readlines()
            resolution_index = lines[0][:-1]
            fps = int(lines[1])
            if lines[2] == 'big dumb debug':
                debug_mode = True
            else:
                debug_mode = False
        else:
            debug_mode = False
            resolution_index = '1'
            fps = 30
        if resolution_index == '1':
            resolution = (1280, 650)
            resolution_folder = '720p'
            piece_color_coefficient = 28
            btn_radius = 2
            bars_coordinates = (582, 2)
            fps_coordinates = (657, 0)

            btn_coordinates = {'throw_cubes':   (953,  20,  136, 38),
                                'buy':          (953,  78,  136, 38),
                                'pay':          (953,  136, 136, 38),
                                'shove_penis':  (953,  194, 136, 38),
                                'remove_penis': (953,  252, 136, 38),
                                'exchange':     (1109, 20,  136, 38),
                                'auction':      (1109, 78,  136, 38),
                                'mortgage':     (1109, 136, 136, 38),
                                'redeem':       (1109, 194, 136, 38)}

            btn_font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', 25)

            profile_coordinates = [{'profile': [669, 20],  'avatar':[830, 46],  'money': [674, 38],  'name': [674, 18]},
                                   {'profile': [669, 169], 'avatar':[830, 195], 'money': [674, 187], 'name': [674, 167]},
                                   {'profile': [669, 318], 'avatar':[830, 344], 'money': [674, 336], 'name': [674, 316]},
                                   {'profile': [669, 467], 'avatar':[830, 493], 'money': [674, 485], 'name': [674, 465]}]

            exchange_coordinates = {'exchange_screen': (75, 75),
                                    'textbox_give':    (120, 160, 183, 30),
                                    'textbox_get':     (345, 160, 183, 30),
                                    'text_give':       (120, 196),
                                    'text_get':        (345, 196),
                                    'button':          (256, 492, 136, 38),
                                    'value':           (324, 173),
                                    'confirm':         (144, 492, 136, 38),
                                    'reject':          (369, 492, 136, 38)}

            auction_coordinates = {'auction_screen': (75, 75),
                                   'price_text':     (144, 465),
                                   'confirm':        (144, 492, 136, 38),
                                   'reject':         (369, 492, 136, 38),
                                   'company_text':   (120, 160)}

            start_btn_textboxes_coordinates = {'name':           (1065, 442, 196, 30),
                                                'IP':            (1065, 488, 134, 30),
                                                'port':          (1202, 488, 59,  30),
                                                'connect':       (1121, 534, 140, 38),
                                                'choose_avatar': (1121, 592, 140, 38),
                                                'debug':         (1121, 384, 140, 38)}

            margin = [[(14, 14)],
                      [(14, 0),  (14, 28)],
                      [(28, 14), (0, 28),  (0, 0)],
                      [(28, 0),  (28, 28), (0, 28), (0, 0)]]

            cubes_coordinates = [(961, 565), (1037, 565)]
            avatar_side_size = 100
            tile_size = (55, 55)
            speed = 10
            is_resolution_selected = True
            if do_choose:
                print(f'Выбрано разрешение 1280x720 и FPS равен {fps}. Вы можете поменять настройки, открыв файл settings.py')

        elif resolution_index == '2':
            resolution = (1920, 1001)
            resolution_folder = '1080p'
            piece_color_coefficient = 42
            btn_radius = 10
            bars_coordinates = (896, 3)
            fps_coordinates = (1006, 0)

            btn_coordinates = {'throw_cubes':   (1455, 30,  204, 57),
                                'buy':          (1455, 117, 204, 57),
                                'pay':          (1455, 204, 204, 57),
                                'shove_penis':  (1455, 291, 204, 57),
                                'remove_penis': (1455, 378, 204, 57),
                                'exchange':     (1689, 30,  204, 57),
                                'auction':      (1689, 117, 204, 57),
                                'mortgage':     (1689, 204, 204, 57),
                                'redeem':       (1689, 291, 204, 57)}

            btn_font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf', 25)

            profile_coordinates = [{'profile': [1028, 30],  'avatar': [1262, 66],  'money': [1034, 62],  'name': [1034, 34]},
                                   {'profile': [1028, 249], 'avatar': [1262, 285], 'money': [1034, 281], 'name': [1034, 253]},
                                   {'profile': [1028, 468], 'avatar': [1262, 504], 'money': [1034, 500], 'name': [1034, 472]},
                                   {'profile': [1028, 687], 'avatar': [1262, 723], 'money': [1034, 719], 'name': [1034, 691]}]

            exchange_coordinates = {'exchange_screen': (108, 108),
                                    'textbox_give':    (177, 240, 290, 30),
                                    'textbox_get':     (530, 240, 290, 30),
                                    'text_give':       (177, 290),
                                    'text_get':        (530, 290),
                                    'button':          (398, 765, 201, 57),
                                    'value':           (498, 254),
                                    'confirm':         (221, 765, 201, 57),
                                    'reject':          (576, 765, 201, 57)}

            auction_coordinates = {'auction_screen': (108, 108),
                                   'price_text':     (221, 738),
                                   'confirm':        (221, 765, 201, 57),
                                   'reject':         (576, 765, 201, 57),
                                   'company_text':   (177, 240)}

            start_btn_textboxes_coordinates = {'name':           (1689, 737, 134, 30),
                                                'IP':            (1689, 787, 134, 30),
                                                'port':          (1826, 787, 59,  30),
                                                'connect':       (1689, 837, 201, 57),
                                                'choose_avatar': (1689, 914, 201, 57),
                                                'debug':         (1689, 660, 201, 57)}

            margin = [[(21, 21)],
                      [(21, 0),  (21, 42)],
                      [(42, 21), (0, 42),  (0, 0)],
                      [(42, 0),  (42, 42), (0, 42), (0, 0)]]

            cubes_coordinates = [(1499, 906), (1594, 906)]
            avatar_side_size = 150
            tile_size = (85, 85)
            speed = 4
            is_resolution_selected = True
            print(f'Выбрано разрешение 1920x1080 и FPS равен {fps}. Вы можете поменять настройки, открыв файл settings.py')
        else:
            print(f'{"\033[31m{}".format('Введены некорректные данные.')}{'\033[0m'}\n')

    return resolution, resolution_folder, piece_color_coefficient, bars_coordinates, btn_coordinates, btn_font, profile_coordinates, start_btn_textboxes_coordinates, btn_radius, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, fps, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates