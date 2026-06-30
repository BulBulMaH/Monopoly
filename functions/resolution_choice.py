import os
from classes.Settings_Class import Settings
import pygame
from screeninfo import get_monitors


def get_current_monitor_resolution():
    try:
        win_x, win_y = pygame.display.get_window_position()
    except pygame.error: # если окно ещё не инициализировано
        return pygame.display.get_desktop_sizes()[0]

    center_x = win_x + pygame.display.get_window_size()[0] // 2
    center_y = win_y + pygame.display.get_window_size()[1] // 2

    monitors = get_monitors()

    for mon in monitors:
        if (mon.x <= center_x < mon.x + mon.width and
            mon.y <= center_y < mon.y + mon.height):
            return mon.width, mon.height
    # в случае неудачи берём основной монитор
    return monitors[0].width, monitors[0].height


def resolution_definition(settings: Settings):
    default_offsets = {
        '720p':
            {
                'settings topleft': (10, 10),
                'currency drawing topleft': (10, 10),
                'board offset topleft': (0, 0),
                'profiles offset topleft': (669, 10),
                'action buttons offset topright': (20, 20),
                'connection buttons offset bottomright': (20, 20)
            },
        '1080p':
            {
                'settings topleft': (10, 10),
                'currency drawing topleft': (10, 10),
                'board offset topleft': (0, 0),
                'profiles offset topleft': (1028, 30),
                'action buttons offset topright': (30, 30),
                'connection buttons offset bottomright': (30, 30)
            },
        '1440p':
            {
                'settings topleft': (20, 20),
                'currency drawing topleft': (20, 20),
                'board offset topleft': (0, 0),
                'profiles offset topleft': (1381, 40),
                'action buttons offset topright': (40, 40),
                'connection buttons offset bottomright': (40, 40)
            }
    }

    if settings.resolution_index == 1:
        if settings.fullscreen:
            if settings.scaled:
                resolution = (1280, 720)
            else:
                resolution = get_current_monitor_resolution()
        else:
            resolution = (1280, 650)

        fps_coordinates = (652, -5)
        if os.path.exists(f'resources/temp/fonts/{settings.resolution_folder}/BulBulPoly.bdf'):
            os.replace(f'resources/temp/fonts/{settings.resolution_folder}/BulBulPoly.bdf', 'resources/fonts/BulBulPoly 4 1x.bdf')
        font_path = 'resources/fonts/BulBulPoly 4 1x.bdf'

        btn_coordinates = {'throw_cubes':   (953,  20 , 136, 38),
                            'buy':          (953,  78,  136, 38),
                            'pay':          (953,  136, 136, 38),
                            'shove_penis':  (953,  194, 136, 38),
                            'remove_penis': (953,  252, 136, 38),
                            'exchange':     (1109, 20 , 136, 38),
                            'auction':      (1109, 78 , 136, 38),
                            'mortgage':     (1109, 136, 136, 38),
                            'redeem':       (1109, 194, 136, 38),
                            'surrender':    (1109, 252, 136, 38)}

        profile_coordinates = [{'profile': (669, 20 ),  'avatar': (830, 46 ),  'money': (692, 40 ), 'value': (692, 58 ), 'name': (674, 22 ), 'timer_bar': (677, 85,  146, 10)},
                               {'profile': (669, 169),  'avatar': (830, 195),  'money': (692, 189), 'value': (692, 207), 'name': (674, 171), 'timer_bar': (677, 234, 146, 10)},
                               {'profile': (669, 318),  'avatar': (830, 344),  'money': (692, 338), 'value': (692, 356), 'name': (674, 320), 'timer_bar': (677, 383, 146, 10)},
                               {'profile': (669, 467),  'avatar': (830, 493),  'money': (692, 487), 'value': (692, 505), 'name': (674, 469), 'timer_bar': (677, 532, 146, 10)}]

        exchange_coordinates = {'exchange_screen':  (75,  75),
                                'textbox_give':     (120, 160, 183, 30),
                                'textbox_get':      (345, 160, 183, 30),
                                'text_give':        (120, 196),
                                'text_get':         (345, 196),
                                'button':           (256, 492, 136, 38),
                                'value':            (324, 173),
                                'confirm':          (144, 492, 136, 38),
                                'reject':           (369, 492, 136, 38)}

        auction_coordinates = {'auction_screen':  (75,  75),
                               'price_text':      (144, 465),
                               'confirm':         (144, 492, 136, 38),
                               'reject':          (369, 492, 136, 38),
                               'company_text':    (120, 160)}

        start_btn_textboxes_coordinates = {'name':          (1040, 442, 217, 35),
                                           'IP':            (1040, 483, 150, 35),
                                           'port':          (1196, 483, 65,  35),
                                           'connect':       (1040, 534, 217, 38),
                                           'choose_avatar': (1040, 592, 217, 38),
                                           'settings':      (1040, 384, 217, 38)}

        log_textbox_coordinates = {'main_box':                  (95,  95,  459, 426),
                                   'user_input_box':            (95,  519, 350, 35),
                                   'audio_send_button':         (411, 519, 38,  35),
                                   'voice_message_send_button': (446, 519, 38,  35),
                                   'image_send_button':         (481, 519, 38,  35),
                                   'text_send_button':          (516, 519, 38,  35)}

        egg_btns_coordinates = ((953,  310, 52, 38),
                                (1037, 310, 52, 38),
                                (1121, 310, 52, 38))

        settings_buttons_coordinates = {
            'label_widget_gap': 10,
            'widget_widget_gap': 10,
            'row_vertical_padding': 4,
            'label_vertical_offset': 0,
            'widget_vertical_offset': 0,

            'message': (200, 10),
            'dropdown': (0, 0, 230, 50),
            'start_game_button': (0, 0,  136, 38),
            'fps_textbox': (0, 0, 60, 30),
            'minimize_window_fps_optimization_checkbox': (0, 0, 25, 25),
            'minimize_window_fps_optimization_textbox': (0, 0, 60, 30),
            'inactivity_fps_optimization_checkbox': (0, 0, 25, 25),
            'inactivity_fps_optimization_textbox': (0, 0, 60, 30),
            'debug_checkbox': (0, 0, 25, 25),
            'fullscreen_checkbox': (0, 0, 25, 25),
            'scale_checkbox': (0, 0, 25, 25),
            'pick_color_button': (0, 0, 180, 38),
            'apply_button': (0, 0, 180, 38),
            'currency_draw_button': (0, 0, 180, 38),
            'color_picker': (0, 0, 390, 390)
        }

        currency_drawing_coordinates = {
            'save char': (0, 0, 300, 38),
            'back': (0, 0, 180, 38),
            'set char': (0, 0, 230, 38),
            'dropdown load': (0, 0, 300, 50),
            'dropdown save': (0, 0, 230, 50),
            'char name textbox': (0, 0, 300, 30),
            'restart': (0, 0, 230, 38),
            'gap': 10
        }

        currency_drawing_tile_size = (30, 30)

        offset_horizontal = [[(0, 0)],
                            [(0,  -14), (0,  14)],
                            [(14,  0), (-14, 14), (-14, -14)],
                            [(14, -14), (14, 14), (-14,  14), (-14, -14)]]

        offset_vertical = [[(0, 0)],
                          [(-14, 0), (14, 0)],
                          [(0, 14), (14, -14), (-14, -14)],
                          [(-14, 14), (14, 14), (14, -14), (-14, -14)]]

        cubes_coordinates = [(959, 489), (959, 565)]
        avatar_side_size = 100
        tile_size = (55, 55)
        max_log_image_size = (423, 211)
        egg_card_coordinates = (85, 334)
        egg_card_text_center = (257, 464)
        egg_card_text_width = 342
        egg_card_title_center = (257, 362)
        tile_info_coordinates = (95,  95)
        speed = 0.003

    elif settings.resolution_index == 2:
        if settings.fullscreen:
            if settings.scaled:
                resolution = (1920, 1080)
            else:
                resolution = get_current_monitor_resolution()
        else:
            resolution = (1920, 1001)
        fps_coordinates = (1006, 0)
        if os.path.exists(f'resources/temp/fonts/{settings.resolution_folder}/BulBulPoly.bdf'):
            os.replace(f'resources/temp/fonts/{settings.resolution_folder}/BulBulPoly.bdf', 'resources/fonts/BulBulPoly 4 1x_2.bdf')
        font_path = 'resources/fonts/BulBulPoly 4 1x_2.bdf'

        btn_coordinates = {'throw_cubes':   (1455, 30 , 204, 57),
                            'buy':          (1455, 117, 204, 57),
                            'pay':          (1455, 204, 204, 57),
                            'shove_penis':  (1455, 291, 204, 57),
                            'remove_penis': (1455, 378, 204, 57),
                            'exchange':     (1689, 30 , 204, 57),
                            'auction':      (1689, 117, 204, 57),
                            'mortgage':     (1689, 204, 204, 57),
                            'redeem':       (1689, 291, 204, 57),
                            'surrender':    (1689, 378, 204, 57)}

        profile_coordinates = [{'profile': (1028, 30),  'avatar': (1262, 66),  'money': (1057, 64),  'value': (1057, 90),  'name': (1034, 37),  'timer_bar': (1035, 122, 221, 16)},
                               {'profile': (1028, 249), 'avatar': (1262, 285), 'money': (1057, 282), 'value': (1057, 309), 'name': (1034, 256), 'timer_bar': (1035, 341, 221, 16)},
                               {'profile': (1028, 468), 'avatar': (1262, 504), 'money': (1057, 502), 'value': (1057, 528), 'name': (1034, 475), 'timer_bar': (1035, 560, 221, 16)},
                               {'profile': (1028, 687), 'avatar': (1262, 723), 'money': (1057, 721), 'value': (1057, 737), 'name': (1034, 694), 'timer_bar': (1035, 779, 221, 16)}]

        exchange_coordinates = {'exchange_screen':  (108, 108),
                                'textbox_give':     (177, 240, 290, 30),
                                'textbox_get':      (530, 240, 290, 30),
                                'text_give':        (177, 290),
                                'text_get':         (530, 290),
                                'button':           (398, 765, 201, 57),
                                'value':            (498, 254),
                                'confirm':          (221, 765, 201, 57),
                                'reject':           (576, 765, 201, 57)}

        auction_coordinates = {'auction_screen':  (108, 108),
                               'price_text':      (221, 738),
                               'confirm':         (221, 765, 201, 57),
                               'reject':          (576, 765, 201, 57),
                               'company_text':    (177, 240)}

        start_btn_textboxes_coordinates = {'name':           (1683, 733, 208, 40),
                                            'IP':            (1683, 787, 134, 40),
                                            'port':          (1820, 787, 65,  40),
                                            'connect':       (1683, 842, 208, 57),
                                            'choose_avatar': (1683, 914, 208, 57),
                                            'settings':      (1683, 660, 208, 57)}

        log_textbox_coordinates = {'main_box':                  (138, 138, 721, 688),
                                   'user_input_box':            (138, 819, 640, 40),
                                   'audio_send_button':         (696, 819, 43, 40),
                                   'voice_message_send_button': (736, 819, 43, 40),
                                   'image_send_button':         (776, 819, 43, 40),
                                   'text_send_button':          (816, 819, 43, 40)}

        egg_btns_coordinates = ((1455, 465, 78, 57),
                                (1581, 465, 78, 57),
                                (1707, 465, 78, 57))

        settings_buttons_coordinates = {
            'label_widget_gap': 10,
            'widget_widget_gap': 10,
            'row_vertical_padding': 4,
            'label_vertical_offset': 0,
            'widget_vertical_offset': 0,

            'message': (200, 10),
            'dropdown': (0, 0, 230, 50),
            'start_game_button': (0, 0, 250, 57),
            'fps_textbox': (0, 0, 60, 30),
            'minimize_window_fps_optimization_checkbox': (0, 0, 25, 25),
            'minimize_window_fps_optimization_textbox': (0, 0, 60, 30),
            'inactivity_fps_optimization_checkbox': (0, 0, 25, 25),
            'inactivity_fps_optimization_textbox': (0, 0, 60, 30),
            'debug_checkbox': (0, 0, 25, 25),
            'fullscreen_checkbox': (0, 0, 25, 25),
            'scale_checkbox': (0, 0, 25, 25),
            'pick_color_button': (0, 0, 180, 38),
            'apply_button': (0, 0, 180, 38),
            'currency_draw_button': (0, 0, 180, 38),
            'color_picker': (0, 0, 390, 390)
        }

        currency_drawing_coordinates = {
            'save char': (0, 0, 400, 38),
            'back': (0, 0, 180, 38),
            'set char': (0, 0, 400, 38),
            'dropdown load': (0, 0, 400, 50),
            'dropdown save': (0, 0, 400, 50),
            'char name textbox': (0, 0, 400, 30),
            'restart': (0, 0, 400, 38),
            'gap': 10
        }

        currency_drawing_tile_size = (45, 45)

        offset_horizontal = [[(0, 0)],
                             [(0, -21),  (0, 21)],
                             [(21, 0),   (-21, 21), (-21, -21)],
                             [(21, -21),  (21, 21), (-21,  21), (-21, -21)]]

        offset_vertical = [[(0, 0)],
                           [(-21, 0),  (21, 0)],
                           [(0, 21),   (21, -21), (-21, -21)],
                           [(-21, 21), (21, 21),   (21, -21), (-21, -21)]]

        cubes_coordinates = [(1499, 906), (1594, 906)]
        avatar_side_size = 150
        tile_size = (85, 85)
        max_log_image_size = (685, 342)
        egg_card_coordinates = (123, 514)
        egg_card_text_center = (393, 720)
        egg_card_text_width = 536
        egg_card_title_center = (393, 555)
        tile_info_coordinates = (138, 138)
        speed = 0.00182

    elif settings.resolution_index == 3:
        if settings.fullscreen:
            if settings.scaled:
                resolution = (2560, 1440)
            else:
                resolution = get_current_monitor_resolution()
        else:
            resolution = (2560, 1360)
        fps_coordinates = (1360, -10)
        if os.path.exists(f'resources/temp/fonts/{settings.resolution_folder}/BulBulPoly.bdf'):
            os.replace(f'resources/temp/fonts/{settings.resolution_folder}/BulBulPoly.bdf', 'resources/fonts/BulBulPoly 4 2x.bdf')
        font_path = 'resources/fonts/BulBulPoly 4 2x.bdf'

        btn_coordinates = {'throw_cubes':  (1935, 40 , 272, 76),
                           'buy':          (1935, 156, 272, 76),
                           'pay':          (1935, 272, 272, 76),
                           'shove_penis':  (1935, 388, 272, 76),
                           'remove_penis': (1935, 504, 272, 76),
                           'exchange':     (2247, 40 , 272, 76),
                           'auction':      (2247, 156, 272, 76),
                           'mortgage':     (2247, 272, 272, 76),
                           'redeem':       (2247, 388, 272, 76),
                           'surrender':    (2247, 504, 272, 76)}

        profile_coordinates = [{'profile': (1381, 40),  'avatar': (1703, 92),  'money': (1422, 81),  'value': (1422, 117),  'name': (1391, 42),  'timer_bar': (1397, 171,  290, 18)},
                               {'profile': (1381, 338), 'avatar': (1703, 390), 'money': (1422, 379), 'value': (1422, 415),  'name': (1391, 340), 'timer_bar': (1397, 469,  290, 18)},
                               {'profile': (1381, 636), 'avatar': (1703, 688), 'money': (1422, 677), 'value': (1422, 713),  'name': (1391, 638), 'timer_bar': (1397, 767,  290, 18)},
                               {'profile': (1381, 934), 'avatar': (1703, 986), 'money': (1422, 975), 'value': (1422, 1011), 'name': (1391, 936), 'timer_bar': (1397, 1065, 290, 18)}]

        exchange_coordinates = {'exchange_screen':  (150, 150),
                                'textbox_give':     (240, 320, 366, 60),
                                'textbox_get':      (690, 320, 366, 30),
                                'text_give':        (240, 392),
                                'text_get':         (690, 392),
                                'button':           (512, 984, 272, 76),
                                'value':            (648, 346),
                                'confirm':          (288, 984, 272, 76),
                                'reject':           (738, 984, 272, 76)}

        auction_coordinates = {'auction_screen':  (150, 150),
                               'price_text':      (288, 930),
                               'confirm':         (288, 984, 272, 76),
                               'reject':          (738, 984, 272, 76),
                               'company_text':    (240, 320)}

        start_btn_textboxes_coordinates = {'settings':      (2127, 827,  392, 76),
                                           'name':          (2127, 943,  392, 60),
                                           'IP':            (2127, 1035, 265, 60),
                                           'port':          (2401, 1035, 118, 60),
                                           'connect':       (2127, 1127, 392, 76),
                                           'choose_avatar': (2127, 1243, 392, 76)}

        log_textbox_coordinates = {'main_box':                  (197,  197,  961, 911),
                                   'user_input_box':            (197,  1098, 760, 60),
                                   'audio_send_button':         (915,  1098, 63, 60),
                                   'voice_message_send_button': (975,  1098, 63, 60),
                                   'image_send_button':         (1035, 1098, 63, 60),
                                   'text_send_button':          (1095, 1098, 63, 60)}

        settings_buttons_coordinates = {
            'label_widget_gap': 20,
            'widget_widget_gap': 20,
            'row_vertical_padding': 8,
            'label_vertical_offset': 0,
            'widget_vertical_offset': 0,

            'message': (200, 10),
            'dropdown': (0, 0, 230, 50),
            'start_game_button': (0, 0, 250, 57),
            'fps_textbox': (0, 0, 120, 55),
            'minimize_window_fps_optimization_checkbox': (0, 0, 45, 45),
            'minimize_window_fps_optimization_textbox': (0, 0, 120, 55),
            'inactivity_fps_optimization_checkbox': (0, 0, 45, 45),
            'inactivity_fps_optimization_textbox': (0, 0, 120, 55),
            'debug_checkbox': (0, 0, 45, 45),
            'fullscreen_checkbox': (0, 0, 45, 45),
            'scale_checkbox': (0, 0, 45, 45),
            'pick_color_button': (0, 0, 250, 57),
            'apply_button': (0, 0, 250, 57),
            'currency_draw_button': (0, 0, 250, 57),
            'color_picker': (0, 0, 390, 390)
        }

        currency_drawing_coordinates = {
            'save char': (0, 0, 250, 57),
            'back': (0, 0, 250, 57),
            'set char': (0, 0, 250, 57),
            'dropdown load': (0, 0, 230, 50),
            'dropdown save': (0, 0, 230, 50),
            'char name textbox': (0, 0, 230, 55),
            'restart': (0, 0, 250, 57),
            'gap': 20
        }

        currency_drawing_tile_size = (30, 30)

        egg_btns_coordinates = ((1935, 620, 106, 76),
                                (2101, 620, 106, 76),
                                (2267, 620, 106, 76))

        offset_horizontal = [[(0, 0)],
                             [(0,  -28), (0,  28)],
                             [(28,  0), (-28, 28), (-28, -28)],
                             [(28, -28), (28, 28), (-28,  28), (-28, -28)]]

        offset_vertical = [[(0, 0)],
                           [(-28, 0), (28, 0)],
                           [(0, 28), (28, -28), (-28, -28)],
                           [(-28, 28), (28, 28), (28, -28), (-28, -28)]]

        cubes_coordinates = [(1953, 1034), (1953, 1186)]
        avatar_side_size = 203
        tile_size = (115, 115)
        max_log_image_size = (925, 462)
        egg_card_coordinates = (177, 698)
        egg_card_text_center = (537, 973)
        egg_card_text_width = 714
        egg_card_title_center = (537, 758)
        tile_info_coordinates = (197, 197)
        speed = 0.0015

    return resolution, btn_coordinates, profile_coordinates, start_btn_textboxes_coordinates, cubes_coordinates, speed, avatar_side_size, exchange_coordinates, auction_coordinates, tile_size, offset_horizontal, offset_vertical, fps_coordinates, font_path, egg_card_coordinates, egg_card_text_center, egg_card_title_center, egg_card_text_width, egg_btns_coordinates, log_textbox_coordinates, tile_info_coordinates, settings_buttons_coordinates, max_log_image_size, default_offsets, currency_drawing_tile_size, currency_drawing_coordinates