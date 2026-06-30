import pygame


class CurrencyDrawingButton:
    def __init__(self, base_rect, state):
        self.element_type = 'button'
        self.hidden = False

        self.border_rect = pygame.Rect(base_rect)

        self.border_size = 1

        self.white = pygame.Color(255, 255, 255)
        self.black = pygame.Color(0, 0, 0)
        self.state = bool(state)

        if self.state:
            self.background_color = self.black
            self.border_color = self.white
        else:
            self.background_color = self.white
            self.border_color = self.black

        self.background_rect = pygame.Rect(
            self.border_rect.x + self.border_size,
            self.border_rect.y + self.border_size,
            self.border_rect.width - self.border_size * 2,
            self.border_rect.height - self.border_size * 2
        )
        self.mouse_position = ()

    def render(self, screen):
        if self.hidden:
            return

        pygame.draw.rect(screen, self.background_color, self.background_rect, )
        pygame.draw.rect(screen, self.border_color, self.border_rect, width=self.border_size)

    def process_events(self, event: pygame.event.Event, action): # action in {'blacking', 'whitening', None}
        if not self.hidden:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.border_rect.collidepoint(self.mouse_position):
                    if self.state:
                        action = 'whitening'
                    else:
                        action = 'blacking'

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                action = None

            if event.type == pygame.MOUSEMOTION:
                self.mouse_position = event.pos
                if self.border_rect.collidepoint(self.mouse_position):

                    if action == 'blacking':
                        self.background_color = self.black
                        self.border_color = self.white
                        self.state = True
                    elif action == 'whitening':
                        self.background_color = self.white
                        self.border_color = self.black
                        self.state = False

        return action

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def get_state(self) -> int:
        return int(self.state)