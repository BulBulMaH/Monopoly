import pygame


class ProgressBar:
    def __init__(self, base_rect: tuple | list, color: tuple | list, percentage: float):
        self.base_rect = pygame.Rect(base_rect)
        self.rect_to_draw = pygame.Rect(base_rect)
        self.color = pygame.Color(color)
        self.percentage = percentage

    def render(self, screen: pygame.Surface, position: tuple | list):
        self.rect_to_draw.x, self.rect_to_draw.y = position
        screen.fill(self.color, self.rect_to_draw)

    def set_percentage(self, percentage):
        self.percentage = percentage
        self.rect_to_draw.width = self.base_rect.width * self.percentage