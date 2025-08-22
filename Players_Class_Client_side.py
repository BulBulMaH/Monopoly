import pygame as pg

class Player:
    def __init__(self, color, positions, resolution_folder, property_family_count):
        self.piece_position = 0
        self.name = ''
        self.property = []
        self.property_family_count = property_family_count.copy()
        self.color = color
        self.money = 1500
        self.main = False
        self.x = positions[0][0]
        self.y = positions[0][1]
        self.baseX = positions[0][0]
        self.baseY = positions[0][1]
        self.on_move = False
        self.imprisoned = False
        self.avatar = pg.image.load(f'resources/{resolution_folder}/profile/avatar_placeholder.png')

    def main_color(self, main_color):
        self.color = main_color
        self.main = True
        print('Основной цвет:',self.color)