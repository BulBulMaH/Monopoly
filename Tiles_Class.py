import math
import pygame

class Tiles:
    def __init__(self, information_list, positions):
        self.position = int(information_list['position'])
        if information_list['buyable'] == 'True':
            self.buyable = True
        else:
            self.buyable = False
        self.type = information_list['type']
        self.family = information_list['family']
        self.name = information_list['name']
        self.price = int(information_list['price'])
        self.color = information_list['color']
        self.angle = int(information_list['angle'])
        self.max_family_members = int(information_list['max_family_members'])
        self.x_position = int(positions['tile position x'])
        self.y_position = int(positions['tile position y'])
        self.xText = int(positions['price text center x'])
        self.yText = int(positions['price text center y'])
        self.x_center = int(positions['tile center x'])
        self.y_center = int(positions['tile center y'])
        self.family_members = 0
        if self.type == 'buildable':
            self.penis_price = round(int(self.price) * 0.63 / 50) * 50
        else:
            self.penis_price = 0
        self.penises = 0
        self.income = 0
        self.owned = False
        self.owner = ''
        self.full_family = False
        self.prerendered_text = ''
        self.text_rect = ''
        self.mortgaged = False
        self.mortgaged_moves_count = 0

    def penis_income_calculation(self):
        if self.family_members == self.max_family_members and not self.mortgaged:
            self.full_family = True
        else:
            self.full_family = False

        if self.owned:
            if self.type == 'buildable':
                if self.full_family:
                    coef = 8
                    coef2 = 2

                    self.income = self.price / coef
                    self.income = math.ceil(self.income * (coef2 ** self.penises))
                else:
                    self.income = math.ceil(self.price / 16)

            elif self.type == 'train':
                coef = 8
                coef2 = 2

                self.income = self.price / coef
                self.income = math.ceil(self.income * (coef2 ** (self.family_members - 1)))
        else:
            self.income = self.price
        return self.income

    def text_defining(self, font):
        self.penis_income_calculation()
        if self.type == 'buildable' or self.type == 'train' or self.type == 'minus':
            if not self.mortgaged:
                text = f'{self.income}~'
            else:
                text = ''

        elif self.type == 'infrastructure':
            if self.owned:
                if not self.full_family:
                    text = 'куб*4'
                else:
                    text = 'куб*10'
            else:
                text = f'{self.income}~'

        else:
            text = ''

        if font.get_point_size() == 25:
            offset_coefficients = (31, 29)
        else:
            offset_coefficients = (64, 60)

        if self.angle == -90:
            offset = (font.size(text)[0] - offset_coefficients[0]) / 2
            # offset = round((font.size(text)[0] - font.get_point_size() * (31 / 25)) / 2)
            # offset = 0
        elif self.angle == 90:
            offset = (font.size(text)[0] - offset_coefficients[1]) / 2
            # offset = round((font.size(text)[0] - font.get_point_size() * (29 / 25)) / 2)
            # offset = 0
        else:
            offset = 0
        # print(offset, math.ceil(offset), font.size(text)[0], self.name)
        text = font.render(text, False, self.color)
        self.prerendered_text = pygame.transform.rotate(text, self.angle).convert()

        self.text_rect = text.get_rect(center=(self.xText + math.ceil(offset), self.yText - math.ceil(offset))) # + round(offset) - round(offset) math.ceil

