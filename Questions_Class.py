class Questions:
    def __init__(self, information_list):
        self.position = int(information_list['position'])
        self.weight = int(information_list['weight'])
        self.all_weights = []
        self.command = information_list['command']
        self.value_range = []
        value_range = information_list['value_range'].split('-')
        for i in value_range:
            self.value_range.append(int(i))
        self.description = information_list['description']