import pygame as pg

class Player:
    def __init__(self, color, positions, resolution_folder, font: pg.Font):
        self.piece_position = 0
        self.name = ''
        self.color = color
        self.money = 1500
        self.value = self.money
        self.main = False
        self.x = positions[0]
        self.y = positions[1]
        self.imprisoned = False
        self.egg_prison_exit_card = False
        self.eggs_prison_exit_card = False
        self.dn_card = False
        self.bankrupt = False
        self.timer_bar = None
        self.time_left = 10800
        self.max_time = 10800
        self.pay_multiplier = 1
        self.avatar = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png').convert()
        self.player_piece = pg.image.load(f'resources/{resolution_folder}/pieces/{self.color}_piece.png').convert_alpha()
        self.player_piece_rect = self.player_piece.get_rect(center=(self.x, self.y))
        self.font = font
        self.rendered_money = self.font.render(f'{self.money}~', False, 'black')
        self.rendered_value = self.font.render(f'{self.value}~', False, 'black')
        self.rendered_name = self.font.render(f'{self.name}~', False, 'black')

    def main_color(self, main_color):
        self.color = main_color
        self.main = True
