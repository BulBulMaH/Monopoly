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
        self.priceTxt = information_list[7]
        self.color = information_list[8]
        self.angle = int(information_list[9])
        self.penises = 0
        self.income = 0
        self.owned = False

    def penis_income_calculation(self):
        coef = 8
        coef2 = 2

        self.income = int(self.priceTxt) / coef
        self.income = math.ceil(self.income * (coef2 ** self.penises))
        return self.income