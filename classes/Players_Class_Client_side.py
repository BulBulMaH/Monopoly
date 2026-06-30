import pygame as pg

class Player:
    def __init__(self, color, positions, resolution_folder, font: pg.Font):
        self.resolution_folder = resolution_folder
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
        self.avatar = pg.image.load(f'resources/{self.resolution_folder}/profile/avatar_placeholder.png').convert()
        self.player_piece = pg.image.load(f'resources/{self.resolution_folder}/pieces/{self.color}_piece.png').convert_alpha()
        self.player_piece_rect = self.player_piece.get_rect(center=(self.x, self.y))
        self.rendered_money = font.render(f'{self.money}¤', False, 'black')
        self.rendered_value = font.render(f'{self.value}¤', False, 'black')
        self.rendered_name = font.render(f'{self.name}', False, 'black')

    def main_color(self, main_color):
        self.color = main_color
        self.main = True

    def change_resolution(self, positions, resolution_folder, avatar_size, font: pg.Font):
        self.x = positions[0]
        self.y = positions[1]
        if self.avatar == pg.image.load(f'resources/{self.resolution_folder}/profile/avatar_placeholder.png').convert():
            self.avatar = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png').convert()
        else:
            self.avatar = pg.transform.smoothscale(self.avatar, avatar_size)
        self.player_piece = pg.image.load(f'resources/{resolution_folder}/pieces/{self.color}_piece.png').convert_alpha()

        self.rendered_money = font.render(f'{self.money}¤', False, 'black')
        self.rendered_value = font.render(f'{self.value}¤', False, 'black')
        self.rendered_name = font.render(f'{self.name}', False, 'black')