import os
import pygame as pg

def resolution_definition(do_choose):
    if do_choose:
        if os.path.exists('settings.txt'):
            print('Выберите настройки. Вы можете поменять настройки позже, открыв файл settings.py')
            lines = open('settings.txt', 'r').readlines()
            resolution_index = lines[0][:-1]
            if '.' in lines[1]:
                fps = float(lines[1])
            else:
                fps = int(lines[1])
            if lines[2][:-1] == 'ultra optimization':
                optimized = True
            else:
                optimized = False
            if lines[3][:-1] == 'bdb':
                debug_mode = True
            else:
                debug_mode = False
            color_values = lines[4][:-1].split(',')
            color = []
            for value in color_values:
                color.append(int(value))
            background_color = pg.Color(color)
        else:
            is_resolution_selected = False
            while not is_resolution_selected:
                resolution_index = input('Выберите разрешение экрана:\n'
                                         '1 - 1280x720\n'
                                         '2 - 1920x1080\n'
                                         '3 - 2560x1440\n')
                if resolution_index in '123':
                    is_resolution_selected = True

            is_fps_selected = False
            while not is_fps_selected:
                fps = input('Введите максимальный FPS:\n')
                try:
                    if '.' in fps:
                        fps = float(fps)
                    else:
                        fps = int(fps)
                    is_fps_selected = True
                except:
                    pass

            is_optimization_selected = False
            while not is_optimization_selected:
                is_optimized = input('Выберите наличие "ультраоптимизации":\n'
                                     '[y / +] - есть\n'
                                     '[n / -] - нет\n')
                if is_optimized in 'y+':
                    optimized = True
                    is_optimization_selected = True
                elif is_optimized in 'n-':
                    optimized = False
                    is_optimization_selected = True

            is_debug_selected = False
            while not is_debug_selected:
                is_debug = input('debug?:\n'
                                     '[y / +] - есть\n'
                                     '[n / -] - нет\n')
                if is_debug in 'y+':
                    debug_mode = True
                    is_debug_selected = True
                elif is_debug in 'n-':
                    debug_mode = False
                    is_debug_selected = True
            # debug_mode = False
            background_color = pg.Color(128, 128, 128)


            with open('settings.txt', 'w+') as settings_file:
                if debug_mode:
                    debug_text = 'bdb'
                else:
                    debug_text = ''

                if optimized:
                    optimization_text = 'ultra optimization'
                else:
                    optimization_text = ''
                settings_file.write(f'{resolution_index}\n{fps}\n{optimization_text}\n{debug_text}\n\n')
                print('Настройки сохранены')

    else:
        debug_mode = False
        optimized = True
        resolution_index = '1'
        fps = 30
        background_color = pg.Color(128, 128, 128)
    if resolution_index == '1':
        resolution = (1280, 650)
        resolution_folder = '720p'
        fps_coordinates = (657, 0)
        font_size = 25

        btn_coordinates = {'throw_cubes':   ((953,  20 ), (136, 38)),
                            'buy':          ((953,  78,), (136, 38)),
                            'pay':          ((953,  136), (136, 38)),
                            'shove_penis':  ((953,  194), (136, 38)),
                            'remove_penis': ((953,  252), (136, 38)),
                            'exchange':     ((1109, 20 ), (136, 38)),
                            'auction':      ((1109, 78 ), (136, 38)),
                            'mortgage':     ((1109, 136), (136, 38)),
                            'redeem':       ((1109, 194), (136, 38))}

        profile_coordinates = [{'profile': (669, 20 ),  'avatar': (830, 46 ),  'money': (674, 38 ), 'name': (674, 18 )},
                               {'profile': (669, 169),  'avatar': (830, 195),  'money': (674, 187), 'name': (674, 167)},
                               {'profile': (669, 318),  'avatar': (830, 344),  'money': (674, 336), 'name': (674, 316)},
                               {'profile': (669, 467),  'avatar': (830, 493),  'money': (674, 485), 'name': (674, 465)}]

        exchange_coordinates = {'exchange_screen':  (75,  75),
                                'textbox_give':     (120, 160, 183, 30),
                                'textbox_get':      (345, 160, 183, 30),
                                'text_give':        (120, 196),
                                'text_get':         (345, 196),
                                'button':          ((256, 492), (136, 38)),
                                'value':            (324, 173),
                                'confirm':         ((144, 492), (136, 38)),
                                'reject':          ((369, 492), (136, 38))}

        auction_coordinates = {'auction_screen':  (75,  75),
                               'price_text':      (144, 465),
                               'confirm':        ((144, 492), (136, 38)),
                               'reject':         ((369, 492), (136, 38)),
                               'company_text':    (120, 160)}

        start_btn_textboxes_coordinates = {'name':           ((1040, 442), (217, 35)),
                                            'IP':            ((1040, 483), (150, 35)),
                                            'port':          ((1196, 483), (65,  35)),
                                            'connect':       ((1040, 534), (217, 38)),
                                            'choose_avatar': ((1040, 592), (217, 38)),
                                            'debug':         ((1040, 384), (140, 38))}

        egg_btns_coordinates = {'egg':  ((953,  310), (52, 38)),
                                'eggs': ((1037, 310), (52, 38))}

        margin = [[(0, 0)],
                  [(0,  -14), (0,  14)],
                  [(14,  0), (-14, 14), (-14, -14)],
                  [(14, -14), (14, 14), (-14,  14), (-14, -14)]]

        cubes_coordinates = [(959, 489), (959, 565)]
        avatar_side_size = 100
        tile_size = (55, 55)
        egg_card_coordinates = (85, 334)
        egg_card_text_center = (257, 464)
        egg_card_text_width = 342
        egg_card_title_center = (257, 362)
        egg_title_font_size = 25
        speed = 0.003
        if do_choose:
            print(f'Выбрано разрешение 1280x720 и FPS равен {fps}. Вы можете поменять настройки, открыв файл settings.py\n')

    elif resolution_index == '2':
        resolution = (1920, 1001)
        resolution_folder = '1080p'
        fps_coordinates = (1006, 0)
        font_size = 25

        btn_coordinates = {'throw_cubes':   ((1455, 30 ), (204, 57)),
                            'buy':          ((1455, 117), (204, 57)),
                            'pay':          ((1455, 204), (204, 57)),
                            'shove_penis':  ((1455, 291), (204, 57)),
                            'remove_penis': ((1455, 378), (204, 57)),
                            'exchange':     ((1689, 30 ), (204, 57)),
                            'auction':      ((1689, 117), (204, 57)),
                            'mortgage':     ((1689, 204), (204, 57)),
                            'redeem':       ((1689, 291), (204, 57))}

        profile_coordinates = [{'profile': [1028, 30],  'avatar': [1262, 66],  'money': [1034, 62],  'name': [1034, 34]},
                               {'profile': [1028, 249], 'avatar': [1262, 285], 'money': [1034, 281], 'name': [1034, 253]},
                               {'profile': [1028, 468], 'avatar': [1262, 504], 'money': [1034, 500], 'name': [1034, 472]},
                               {'profile': [1028, 687], 'avatar': [1262, 723], 'money': [1034, 719], 'name': [1034, 691]}]

        exchange_coordinates = {'exchange_screen':  (108, 108),
                                'textbox_give':     (177, 240, 290, 30),
                                'textbox_get':      (530, 240, 290, 30),
                                'text_give':        (177, 290),
                                'text_get':         (530, 290),
                                'button':          ((398, 765), (201, 57)),
                                'value':            (498, 254),
                                'confirm':         ((221, 765), (201, 57)),
                                'reject':          ((576, 765), (201, 57))}

        auction_coordinates = {'auction_screen':  (108, 108),
                               'price_text':      (221, 738),
                               'confirm':        ((221, 765), (201, 57)),
                               'reject':         ((576, 765), (201, 57)),
                               'company_text':    (177, 240)}

        start_btn_textboxes_coordinates = {'name':           ((1683, 733), (208, 40)),
                                            'IP':            ((1683, 787), (134, 40)),
                                            'port':          ((1820, 787), (65,  40)),
                                            'connect':       ((1683, 842), (208, 57)),
                                            'choose_avatar': ((1683, 914), (208, 57)),
                                            'debug':         ((1683, 660), (208, 57))}

        egg_btns_coordinates = {'egg':  ((1455, 465), (78, 57)),
                                'eggs': ((1581, 465), (78, 57))}

        margin = [[[0, 0]],
                  [[0, -21], [0, 21]],
                  [[21, 0], [-21, 21], [-21, -21]],
                  [[21, -21], [21, 21], [-21, 21], [-21, -21]]]

        cubes_coordinates = [(1499, 906), (1594, 906)]
        avatar_side_size = 150
        tile_size = (85, 85)
        egg_card_coordinates = (123, 514)
        egg_card_text_center = (393, 720)
        egg_card_text_width = 536
        egg_card_title_center = (393, 555)
        egg_title_font_size = 51
        speed = 0.00182

        print(f'Выбрано разрешение 1920x1080 и FPS равен {fps}. Вы можете поменять настройки, открыв файл settings.py\n')

    elif resolution_index == '3':
        resolution = (2560, 1360)
        resolution_folder = '1440p'
        fps_coordinates = (1360, -10)
        font_size = 51

        btn_coordinates = {'throw_cubes':  ((1935, 40 ), (272, 76)),
                           'buy':          ((1935, 156), (272, 76)),
                           'pay':          ((1935, 272), (272, 76)),
                           'shove_penis':  ((1935, 388), (272, 76)),
                           'remove_penis': ((1935, 504), (272, 76)),
                           'exchange':     ((2247, 40 ), (272, 76)),
                           'auction':      ((2247, 156), (272, 76)),
                           'mortgage':     ((2247, 272), (272, 76)),
                           'redeem':       ((2247, 388), (272, 76))}

        profile_coordinates = [{'profile': [1381, 40],  'avatar': [1703, 92],  'money': [1391, 76],  'name': [1391, 36]},
                               {'profile': [1381, 338], 'avatar': [1703, 390], 'money': [1391, 374], 'name': [1391, 334]},
                               {'profile': [1381, 636], 'avatar': [1703, 688], 'money': [1391, 672], 'name': [1391, 632]},
                               {'profile': [1381, 934], 'avatar': [1703, 986], 'money': [1391, 970], 'name': [1391, 930]}]

        exchange_coordinates = {'exchange_screen':  (150, 150),
                                'textbox_give':     (240, 320, 366, 60),
                                'textbox_get':      (690, 320, 366, 30),
                                'text_give':        (240, 392),
                                'text_get':         (690, 392),
                                'button':          ((512, 984), (272, 76)),
                                'value':            (648, 346),
                                'confirm':         ((288, 984), (272, 76)),
                                'reject':          ((738, 984), (272, 76))}

        auction_coordinates = {'auction_screen':  (150, 150),
                               'price_text':      (288, 930),
                               'confirm':        ((288, 984), (272, 76)),
                               'reject':         ((738, 984), (272, 76)),
                               'company_text':    (240, 320)}

        start_btn_textboxes_coordinates = {'debug':         ((2127, 827 ), (392, 76)),
                                           'name':          ((2127, 943 ), (392, 60)),
                                           'IP':            ((2127, 1035), (265, 60)),
                                           'port':          ((2401, 1035), (118, 60)),
                                           'connect':       ((2127, 1127), (392, 76)),
                                           'choose_avatar': ((2127, 1243), (392, 76))}

        egg_btns_coordinates = {'egg':  ((1935, 620), (106, 76)),
                                'eggs': ((2101, 620), (106, 76))}

        margin = [[(0, 0)],
                  [(0,  -28), (0,  28)],
                  [(28,  0), (-28, 28), (-28, -28)],
                  [(28, -28), (28, 28), (-28,  28), (-28, -28)]]

        cubes_coordinates = [(1922, 1130), (2074, 1130)]
        avatar_side_size = 203
        tile_size = (115, 115)
        egg_card_coordinates = (177, 698)
        egg_card_text_center = (537, 973)
        egg_card_text_width = 714
        egg_card_title_center = (537, 758)
        egg_title_font_size = 51
        speed = 0.0015
        if do_choose:
            print(f'Выбрано разрешение 2560x1440 и FPS равен {fps}. Вы можете поменять настройки, открыв файл settings.py\n')

    return resolution, resolution_folder, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, fps, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates, font_size, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_title_font_size, egg_card_text_width, egg_btns_coordinates, optimized, background_color