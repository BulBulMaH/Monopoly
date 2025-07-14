class Tiles:
    def __init__(self, inf):
        information_list = inf.split(',')
        self.position = int(information_list[0])
        self.buyable = information_list[1]
        self.type = information_list[2]
        self.family = information_list[3]
        self.descr = information_list[4]
        self.xText = int(information_list[5])
        self.yText = int(information_list[6])
        self.priceTxt = information_list[7]
        self.color = information_list[8]
        self.angle = int(information_list[9])