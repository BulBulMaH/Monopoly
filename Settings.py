import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.dropdown import Dropdown
pg.init()

TITLE = 'Settings'
icon = pg.image.load(f'resources/icon.png')
pg.display.set_icon(icon)
screen = pg.display.set_mode((500, 650))
pg.display.set_caption(TITLE)

font = pg.font.Font('resources/fonts/bulbulpoly-3.ttf',25)


def save():
    print(dropdown.getSelected())


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
    global save_button, dropdown
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
                        120,
                        10,
                        230,
                        50,
                        name='Выберите разрешение',
                        choices=['1280x720', '1920x1080'],
                        # radius=2,
                        borderRadius=100,
                        inactiveColour=(255, 255, 255),
                        inactiveBorderColour=(0, 0, 0),
                        hoverColour=(255, 255, 255),
                        hoverBorderColour=(105, 105, 105),
                        pressedColour=(191, 191, 191),
                        pressedBorderColour=(0, 0, 0),
                        borderThickness=300,
                        font=font,
                        values=[1, 2],
                        direction='down')


buttons()

running = True
while running:
    screen.fill((128, 128, 128))
    event_handler()
    pg.display.flip()
pg.quit()
