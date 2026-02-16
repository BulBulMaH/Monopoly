import os
import json
import pygame as pg


def resolution_definition():
    if os.path.exists('settings.json'):
        f = open('settings.json')
        settings_data = json.load(f)
        resolution_index = settings_data['resolution index']
        fps = settings_data['fps']
        optimized = settings_data['optimized movement']
        debug_mode = settings_data['debug mode']
        background_color = pg.Color(settings_data['background color'])
        fullscreen = settings_data['fullscreen']
        sharp_scale = settings_data['sharp fullscreen']
        name = settings_data['name']
        address = settings_data['address']
        port = settings_data['port']

    else:
        settings_data = {'resolution index': 1,
                         'fps': 60,
                         'optimized movement': False,
                         'background color': [128, 128, 128, 255],
                         'fullscreen': False,
                         'sharp fullscreen': True,
                         'debug mode': False,
                         'name': '',
                         'address': '',
                         'port': ''}

        resolution_index = settings_data['resolution index']
        fps = settings_data['fps']
        optimized = settings_data['optimized movement']
        debug_mode = settings_data['debug mode']
        background_color = pg.Color(settings_data['background color'])
        fullscreen = settings_data['fullscreen']
        sharp_scale = settings_data['sharp fullscreen']
        name = settings_data['name']
        address = settings_data['address']
        port = settings_data['port']

        with open("settings.json", "w") as outfile:
            json.dump(settings_data, outfile, indent=4)

    if resolution_index == 1:
        if fullscreen:
            resolution = (1280, 720)
        else:
            resolution = (1280, 650)
        resolution_folder = '720p'
        fps_coordinates = (652, -5)
        font_size = 25
        settings_font_size = 25

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

        log_textbox_coordinates = {'main_box':                  (95,  95,  459, 426),
                                   'user_input_box':            (95,  519, 350, 35),
                                   'audio_send_button':         (411, 519, 38,  35),
                                   'voice_message_send_button': (446, 519, 38,  35),
                                   'image_send_button':         (481, 519, 38,  35),
                                   'text_send_button':          (516, 519, 38,  35)}

        egg_btns_coordinates = {'egg':  ((953,  310), (52, 38)),
                                'eggs': ((1037, 310), (52, 38))}

        settings_buttons_coordinates = {'dropdown':              (10,  10,  230, 50),
                                        'start_game_button':     (572, 602, 136, 38),
                                        'fps_textbox':           (266, 70,  60,  30),
                                        'optimization_checkbox': (226, 105, 25,  25),
                                        'debug_checkbox':        (120, 137, 25,  25),
                                        'fullscreen_checkbox':   (222, 169, 25,  25),
                                        'sharp_scale_checkbox':  (252, 201, 25,  25),
                                        'pick_color_button':     (10,  240, 180, 38),
                                        'apply_button':          (10,  298, 180, 38),
                                        'color_picker':          (60,  120, 390, 390),
                                        'fps_text':              (10,  70),
                                        'optimization_text':     (10,  102),
                                        'debug_text':            (10,  134),
                                        'fullscreen_text':       (10,  166),
                                        'sharp_scale_text':      (10,  198)}

        margin = [[(0, 0)],
                  [(0,  -14), (0,  14)],
                  [(14,  0), (-14, 14), (-14, -14)],
                  [(14, -14), (14, 14), (-14,  14), (-14, -14)]]

        cubes_coordinates = [(959, 489), (959, 565)]
        avatar_side_size = 100
        tile_size = (55, 55)
        log_image_size = (128, 128)
        egg_card_coordinates = (85, 334)
        egg_card_text_center = (257, 464)
        egg_card_text_width = 342
        egg_card_title_center = (257, 362)
        egg_title_font_size = 25
        tile_info_coordinates = (95,  95)
        speed = 0.003

    elif resolution_index == 2:
        if fullscreen:
            resolution = (1920, 1080)
        else:
            resolution = (1920, 1001)
        resolution_folder = '1080p'
        fps_coordinates = (1006, 0)
        font_size = 25
        settings_font_size = 51

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

        log_textbox_coordinates = {'main_box':                  (138, 138, 721, 688),
                                   'user_input_box':            (138, 819, 640, 40),
                                   'audio_send_button':         (696, 819, 43, 40),
                                   'voice_message_send_button': (736, 819, 43, 40),
                                   'image_send_button':         (776, 819, 43, 40),
                                   'text_send_button':          (816, 819, 43, 40)}

        egg_btns_coordinates = {'egg':  ((1455, 465), (78, 57)),
                                'eggs': ((1581, 465), (78, 57))}

        settings_buttons_coordinates = {'dropdown':              (20,  20,  230, 50),
                                        'start_game_button':     (835, 934, 250, 57),
                                        'fps_textbox':           (534, 81,  120, 55),
                                        'optimization_checkbox': (451, 144, 45,  45),
                                        'debug_checkbox':        (238, 198, 45,  45),
                                        'fullscreen_checkbox':   (443, 252, 45,  45),
                                        'sharp_scale_checkbox':  (507, 306, 45,  45),
                                        'pick_color_button':     (20,  370, 250, 57),
                                        'apply_button':          (20,  457, 250, 57),
                                        'color_picker':          (60,  120, 390, 390),
                                        'fps_text':              (20,  80),
                                        'optimization_text':     (20,  134),
                                        'debug_text':            (20,  188),
                                        'fullscreen_text':       (20,  242),
                                        'sharp_scale_text':      (20,  296)}

        margin = [[[0, 0]],
                  [[0, -21], [0, 21]],
                  [[21, 0], [-21, 21], [-21, -21]],
                  [[21, -21], [21, 21], [-21, 21], [-21, -21]]]

        cubes_coordinates = [(1499, 906), (1594, 906)]
        avatar_side_size = 150
        tile_size = (85, 85)
        log_image_size = (192, 192)
        egg_card_coordinates = (123, 514)
        egg_card_text_center = (393, 720)
        egg_card_text_width = 536
        egg_card_title_center = (393, 555)
        egg_title_font_size = 51
        tile_info_coordinates = (138, 138)
        speed = 0.00182

    elif resolution_index == 3:
        if fullscreen:
            resolution = (2560, 1440)
        else:
            resolution = (2560, 1360)
        resolution_folder = '1440p'
        fps_coordinates = (1360, -10)
        font_size = 51
        settings_font_size = 51

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

        log_textbox_coordinates = {'main_box':                  (197, 197, 961, 911),
                                   'user_input_box':            (197, 1098, 760, 60),
                                   'audio_send_button':         (915, 1098, 63, 60),
                                   'voice_message_send_button': (975, 1098, 63, 60),
                                   'image_send_button':         (1035, 1098, 63, 60),
                                   'text_send_button':          (1095, 1098, 63, 60)}

        settings_buttons_coordinates = {'dropdown': (20, 20, 230, 50),
                                        'start_game_button': (1155, 1273, 250, 57),
                                        'fps_textbox': (534, 81, 120, 55),
                                        'optimization_checkbox': (451, 144, 45, 45),
                                        'debug_checkbox': (238, 198, 45, 45),
                                        'fullscreen_checkbox': (443, 252, 45, 45),
                                        'sharp_scale_checkbox': (507, 306, 45, 45),
                                        'pick_color_button': (20, 370, 250, 57),
                                        'apply_button': (20, 457, 250, 57),
                                        'color_picker': (60, 120, 390, 390),
                                        'fps_text': (20, 80),
                                        'optimization_text': (20, 134),
                                        'debug_text': (20, 188),
                                        'fullscreen_text': (20, 242),
                                        'sharp_scale_text': (20, 296)}

        egg_btns_coordinates = {'egg':  ((1935, 620), (106, 76)),
                                'eggs': ((2101, 620), (106, 76))}

        margin = [[(0, 0)],
                  [(0,  -28), (0,  28)],
                  [(28,  0), (-28, 28), (-28, -28)],
                  [(28, -28), (28, 28), (-28,  28), (-28, -28)]]

        cubes_coordinates = [(1922, 1130), (2074, 1130)]
        avatar_side_size = 203
        tile_size = (115, 115)
        log_image_size = (256, 256)
        egg_card_coordinates = (177, 698)
        egg_card_text_center = (537, 973)
        egg_card_text_width = 714
        egg_card_title_center = (537, 758)
        egg_title_font_size = 51
        tile_info_coordinates = (197, 197)
        speed = 0.0015

    return resolution, resolution_folder, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, fps, auction_coordinates, tile_size, margin, debug_mode, fps_coordinates, font_size, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_title_font_size, egg_card_text_width, egg_btns_coordinates, optimized, background_color, log_textbox_coordinates, tile_info_coordinates, fullscreen, sharp_scale, settings_buttons_coordinates, settings_font_size, log_image_size, name, address, port