class Eggs:
    def __init__(self, information_list):
        self.position = int(information_list['position'])
        self.command = information_list['command']
        if self.command == 'go to next':
            self.value = information_list['value']
        else:
            self.value = int(information_list['value'])
        self.description = information_list['description']
