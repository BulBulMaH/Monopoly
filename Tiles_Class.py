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
        if information_list['special_price'] == 'True':
            self.special_price = True
        else:
            self.special_price = False
        self.x_position = int(positions['tile position x'])
        self.y_position = int(positions['tile position y'])
        self.xText = int(positions['price text center x'])
        self.yText = int(positions['price text center y'])
        self.x_center = int(positions['tile center x'])
        self.y_center = int(positions['tile center y'])
        self.family_members = 0
        if self.type == 'buildable':
            if self.special_price:
                self.penis_price = round(int(self.price) * 0.55 / 50) * 50
            else:
                self.penis_price = round(int(self.price) * 0.63 / 50) * 50
        else:
            self.penis_price = 0
        self.penises = 0
        self.penised_family = False # запЭнисованная семья, если семья имеет хотя бы один пЭнис
        self.recently_built = False
        self.income = 0
        self.owned = False
        self.owner = ''
        self.full_family = False
        self.prerendered_text = None
        self.text_rect = None
        self.mortgaged = False
        self.mortgaged_moves_count = 0


    def penis_income_calculation(self):
        if self.family_members == self.max_family_members and not self.mortgaged:
            self.full_family = True
        else:
            self.full_family = False

        if self.owned and not self.mortgaged:
            if self.type == 'buildable':
                if self.special_price:
                    coef = 6.4
                    coef2 = 2
                else:
                    coef = 8
                    coef2 = 2
                if self.full_family:
                    self.income = math.ceil(self.price / coef * (coef2 ** self.penises))
                else:
                    self.income = math.ceil(self.price / coef * (coef2 ** -1))

            elif self.type == 'train':
                coef = 8
                coef2 = 2

                self.income = math.ceil(self.price / coef * (coef2 ** (self.family_members - 1)))
        else:
            self.income = self.price
        return self.income

    def text_defining(self, font: pygame.Font):
        self.penis_income_calculation()
        if self.type == 'buildable' or self.type == 'train' or self.type == 'minus':
            text = f'{self.income}~'

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


        text = font.render(text, False, self.color)
        self.prerendered_text = pygame.transform.rotate(text, self.angle).convert()

        self.text_rect = self.prerendered_text.get_rect(center=(self.xText, self.yText))


    def reset_tile(self):
        self.family_members = 0
        self.penises = 0
        self.penised_family = False
        self.recently_built = False
        self.income = 0
        self.owned = False
        self.owner = ''
        self.full_family = False
        self.mortgaged = False
        self.mortgaged_moves_count = 0
