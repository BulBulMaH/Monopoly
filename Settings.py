import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle
pg.init()

TITLE = 'Settings'
icon = pg.image.load(f'resources/icon.png')
pg.display.set_icon(icon)
screen = pg.display.set_mode((500, 650))
pg.display.set_caption(TITLE)

font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)


def save():
    resolution_index = dropdown.getSelected()
    fps = fps_textbox.getText()
    if resolution_index and fps:
        with open('settings.txt', 'w+') as settings_file:
            if debug_toggle.getValue():
                debug_text = 'bdb'
            else:
                debug_text = ''
            settings_file.write(f'{resolution_index}\n{fps}\n{debug_text}\n')
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
        if event.type == pg.QUIT:
            global running
            running = False
    try:
        pygame_widgets.update(events)
    except AttributeError:
        print(
            f'{"\033[31m{}".format('Снова вылезла эта поганая ошибка. Я надеюсь, что игра не зависла на этот раз.')}{'\033[0m'}\n')


def buttons():
    global save_button, dropdown, fps_textbox, dropdown_choice, debug_toggle
    save_button = Button(screen,
                         182,
                         592,
                         136,
                         38,
                         inactiveColour=(255, 255, 255),
                         inactiveBorderColour=(0, 0, 0),
                         hoverColour=(255, 255, 255),
                         hoverBorderColour=(105, 105, 105),
                         pressedColour=(191, 191, 191),
                         pressedBorderColour=(0, 0, 0),
                         borderThickness=3,
                         radius=2,
                         font=font,
                         text='Сохранить',
                         onClick=save)

    dropdown = Dropdown(screen,
                        10,
                        10,
                        230,
                        50,
                        name='Выберите разрешение',
                        choices=['1280x720', '1920x1080', '2560x1440'],
                        radius=2,
                        borderRadius=2,
                        inactiveColour=(255, 255, 255),
                        inactiveBorderColour=(0, 0, 0),
                        hoverColour=(255, 255, 255),
                        hoverBorderColour=(105, 105, 105),
                        pressedColour=(191, 191, 191),
                        pressedBorderColour=(0, 0, 0),
                        font=font,
                        values=[1, 2, 3],
                        direction='down')

    fps_textbox = TextBox(screen,
                           270,
                           70,
                           50,
                           30,
                           colour=(200, 200, 200),
                           textColour=(0, 0, 0),
                           borderThickness=2,
                           borderColour=(0, 0, 0),
                           font=font,
                           radius=2,
                           placeholderTextColour=(128, 128, 128),
                           onTextChanged=fps_check)

    debug_toggle = Toggle(screen,
                       130,
                       110,
                       30,
                       15,
                       startOn=False)


buttons()

running = True
while running:
    screen.fill((128, 128, 128))
    screen.blit(font.render('Введите максимальный FPS:', False, 'black'), (10, 70))
    screen.blit(font.render('debug mode:', False, 'black'), (10, 103))
    event_handler()
    pg.display.flip()
pg.quit()
