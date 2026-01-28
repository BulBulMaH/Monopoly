import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import pygame_gui
import traceback
import time

pg.init()

TITLE = 'Settings'
icon = pg.image.load(f'resources/icon.png')
pg.display.set_icon(icon)
screen = pg.display.set_mode((500, 650))
pg.display.set_caption(TITLE)

font = pg.font.Font('resources/fonts/bulbulpoly-4.ttf',25)
manager = pygame_gui.UIManager((500, 650), theme_path=f'resources/720p/gui_theme.json', starting_language='ru')

if os.path.exists('settings.txt'):
    lines = open('settings.txt', 'r').readlines()
    previous_values = []
    resolution_index = lines[0][:-1]
    if lines[0][:-1] == '1':
        previous_values.append('1280x720')
    elif lines[0][:-1] == '2':
        previous_values.append('1920x1080')
    elif lines[0][:-1] == '3':
        previous_values.append('2560x1440')

    previous_values.append(lines[1][:-1]) # fps

    if lines[2][:-1] == 'ultra optimization':
        previous_values.append(True)
    else:
        previous_values.append(False)

    if lines[3][:-1] == 'bdb':
        previous_values.append(True)
    else:
        previous_values.append(False)

    color_values = lines[4][:-1].split(',')
    color = []
    for value in color_values:
        color.append(int(value))
    previous_values.append(pg.Color(color))
    picked_color = pg.Color(color)

    fullscreen_data = lines[5][:-1].split(',')
    if fullscreen_data[0] == 'True':
        fullscreen = True
        if fullscreen_data[1] == 'True':
            smooth_scale = True
        else:
            smooth_scale = False
    else:
        fullscreen = False
        smooth_scale = False
    previous_values.append((fullscreen, smooth_scale))
else:
    previous_values = []
    resolution_index = '1'
    previous_values.append('1280x720')
    previous_values.append('')
    previous_values.append(False)
    previous_values.append(False)
    previous_values.append(pg.Color(128, 128, 128))
    previous_values.append((False, False))


def delta_time(old_time):
    now = time.time()
    dt = now - old_time
    old_time = now
    return dt, old_time


def save():
    fps = fps_textbox.get_text()
    if resolution_index and fps:
        with open('settings.txt', 'w+') as settings_file:
            if debug_checkbox.get_state():
                debug_text = 'bdb'
            else:
                debug_text = ''
            if optimization_checkbox.get_state():
                optimization_text = 'ultra optimization'
            else:
                optimization_text = ''
            color_text = ''
            for i in picked_color:
                color_text += f'{i},'
            color_text = color_text[:-1]
            fullscreen = fullscreen_checkbox.get_state()
            sharp_scale = not smooth_scale_checkbox.get_state()

            settings_file.write(f'{resolution_index}\n{fps}\n{optimization_text}\n{debug_text}\n{color_text}\n{fullscreen},{sharp_scale}\n')
            print('Настройки сохранены')
            global running
            running = False
    else:
        print('Выберите правильные настройки')


def fps_check():
    text = fps_textbox.getText()
    new_text = text
    for character in text:
        if character not in '0123456789':
            new_text = new_text.replace(character, '')
    if fps_textbox.getText() != new_text:
        fps_textbox.setText(new_text)


def event_handler():
    events = pg.event.get()
    for event in events:

        manager_initiated = False
        while not manager_initiated:
            try:
                manager.process_events(event)
                manager_initiated = True
            except:
                print(
                    f'{"\033[32m{}".format(f'Не беспокойтесь. Эта ошибка не вредит игре:\n{traceback.format_exc()}')}{'\033[0m'}')

        if event.type == pg.QUIT:
            global running
            running = False

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == save_button:
                save()
            elif event.ui_element == pick_color_button:
                color_picker.show()

        elif event.type == pygame_gui.UI_CHECK_BOX_CHECKED:
            if event.ui_element == fullscreen_checkbox:
                smooth_scale_checkbox.enable()

        elif event.type == pygame_gui.UI_CHECK_BOX_UNCHECKED:
            if event.ui_element == fullscreen_checkbox:
                smooth_scale_checkbox.disable()
                smooth_scale_checkbox.set_state(False)

        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            global resolution_index
            if event.text == '1280x720':
                resolution_index = '1'
            elif event.text == '1920x1080':
                resolution_index = '2'
            elif event.text == '2560x1440':
                resolution_index = '3'
        elif event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            if event.ui_element == color_picker:
                color_picker.hide()
                global picked_color
                picked_color = event.colour


def buttons():
    global save_button, dropdown, fps_textbox, dropdown_choice, optimization_checkbox, debug_checkbox, pick_color_button, color_picker, fullscreen_checkbox, smooth_scale_checkbox
    save_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(182, 592, 136, 38),
        text='Сохранить',
        manager=manager)

    dropdown = pygame_gui.elements.UIDropDownMenu(
        relative_rect=pg.Rect(10, 10, 230, 50),
        starting_option=previous_values[0],
        options_list=['1280x720', '1920x1080', '2560x1440'],
        manager=manager)

    fps_textbox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pg.Rect(266, 70, 50, 30),
        placeholder_text='',
        initial_text=previous_values[1],
        manager=manager)

    optimization_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(226, 105, 25, 25),
        text='',
        initial_state=previous_values[2],
        manager=manager)

    debug_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(120, 137, 25, 25),
        text='',
        initial_state=previous_values[3],
        manager=manager)

    fullscreen_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(222, 169, 25, 25),
        text='',
        initial_state=previous_values[5][0],
        manager=manager)

    smooth_scale_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pg.Rect(339, 201, 25, 25),
        text='',
        initial_state=previous_values[5][1],
        manager=manager)
    if not fullscreen_checkbox.get_state():
        smooth_scale_checkbox.disable()

    pick_color_button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect(10, 240, 180, 38),
        text='Выбрать цвет фона',
        manager=manager)

    color_picker = pygame_gui.windows.UIColourPickerDialog(
        rect=pg.Rect(60, 120, 390, 390),
        initial_colour=previous_values[4],
        manager=manager,
        visible=False)

    theme = manager.create_new_theme(f'resources/720p/gui_theme.json')
    manager.set_ui_theme(theme)

buttons()

prev_time = time.time()

running = True
while running:
    dt, prev_time = delta_time(prev_time)
    screen.fill(previous_values[4])
    screen.blit(font.render('Введите максимальный FPS:', False, 'black'), (10, 70))
    screen.blit(font.render('Оптимизация движения:', False, 'black'), (10, 102))
    screen.blit(font.render('debug mode:', False, 'black'), (10, 134))
    screen.blit(font.render('Полноэкранный режим:', False, 'black'), (10, 166))
    screen.blit(font.render('Сглаживание при растяжении экрана:', False, 'black'), (10, 198))
    event_handler()
    manager.update(dt)
    manager.draw_ui(screen)
    pg.display.flip()
pg.quit()
