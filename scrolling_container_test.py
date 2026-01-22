import pygame

from pygame_gui import UIManager
from pygame_gui.elements import UIScrollingContainer, UILabel


pygame.init()


pygame.display.set_caption('Scrolling Container Test')
window_surface = pygame.display.set_mode((800, 600))
manager = UIManager((800, 600), 'quick_theme.json')

background = pygame.Surface((800, 600))
background.fill(manager.ui_theme.get_colour('dark_bg'))

scrolling_container = UIScrollingContainer(pygame.Rect(50, 50, 700, 500), manager, should_grow_automatically=True)
# scrolling_container.set_scrollable_area_dimensions((1200, 1200))

test_label = UILabel(pygame.Rect((50, 50), (200, 40)), "Hello", manager=manager, object_id="#label_1", container=scrolling_container)
test_label_2 = UILabel(pygame.Rect((900, 1000), (200, 40)), "Hello", manager=manager, object_id="#label_2", container=scrolling_container)

clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            scrolling_container.horiz_scroll_bar.sliding_button.hide()
            scrolling_container.horiz_scroll_bar.left_button.hide()
            scrolling_container.horiz_scroll_bar.right_button.hide()


        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()
