import math

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
        self.text = ''
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

                    self.income = int(self.price) / coef
                    self.income = math.ceil(self.income * (coef2 ** self.penises))
                else:
                    self.income = math.ceil(int(self.price) / 16)

            elif self.type == 'train':
                coef = 8
                coef2 = 2

                self.income = int(self.price) / coef
                self.income = math.ceil(self.income * (coef2 ** (self.family_members - 1)))
        else:
            self.income = int(self.price)
        return self.income

    def text_defining(self):
        self.penis_income_calculation()
        if self.type == 'buildable' or self.type == 'train' or self.type == 'minus':
            if not self.mortgaged:
                self.text = f'{self.income}~'
            else:
                self.text = ''

        elif self.type == 'infrastructure':
            if self.owned:
                if not self.full_family:
                    self.text = 'куб*4'
                else:
                    self.text = 'куб*10'
            else:
                self.text = f'{self.income}~'