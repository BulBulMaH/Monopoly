import math

class Tiles:
    def __init__(self, inf):
        information_list = inf.split(',')
        self.position = int(information_list[0])
        if information_list[1] == 'True':
            self.buyable = True
        else:
            self.buyable = False
        self.type = information_list[2]
        self.family = information_list[3]
        self.descr = information_list[4]
        self.xText = int(information_list[5])
        self.yText = int(information_list[6])
        self.price = information_list[7]
        self.color = information_list[8]
        self.angle = int(information_list[9])
        self.max_family_members = int(information_list[10])
        self.family_members = 0
        self.penises = 0
        self.income = 0
        self.owned = False
        self.owner = ''
        self.full_family = False
        self.text = ''

    def penis_income_calculation(self):
        if self.family_members == self.max_family_members:
            self.full_family = True

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
                self.income = math.ceil(self.income * (coef2 ** self.family_members))
        else:
            self.income = int(self.price)
        return self.income

    def text_defining(self):
        self.penis_income_calculation()
        if self.type == 'buildable' or self.type == 'train' or self.type == 'minus':
            self.text = f'{self.income}~'

        elif self.type == 'infrastructure':
            if self.owned:
                if not self.full_family:
                    self.text = 'куб*4'
                else:
                    self.text = 'куб*10'
            else:
                self.text = f'{self.income}~'