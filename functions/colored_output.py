def thread_open(primarily_text, secondary_text):
    print(f'{"\033[31m{}".format(primarily_text)}{'\033[0m'}: {secondary_text}')


def information_sent(primarily_text, secondary_text):
    print(f'{"\033[36m{}".format(primarily_text)}{'\033[0m'}: {secondary_text}')


def information_sent_to(primarily_text, color, secondary_text):
    if color == 'red':                 # |
                                       # V Цифры цвета меняются
        print(f'{"\033[36m{}".format(primarily_text)} {"\033[31m{}".format(color)}{'\033[0m'}: {secondary_text}')
    elif color == 'green':
        print(f'{"\033[36m{}".format(primarily_text)} {"\033[32m{}".format(color)}{'\033[0m'}: {secondary_text}')
    elif color == 'yellow':
        print(f'{"\033[36m{}".format(primarily_text)} {"\033[33m{}".format(color)}{'\033[0m'}: {secondary_text}')
    elif color == 'blue':
        print(f'{"\033[36m{}".format(primarily_text)} {"\033[34m{}".format(color)}{'\033[0m'}: {secondary_text}')


def information_received(primarily_text, secondary_text):
    print(f'{"\033[32m{}".format(primarily_text)}{'\033[0m'}: {secondary_text}')


def new_connection(primarily_text, secondary_text):
    print(f'{"\033[35m{}".format(primarily_text)}{'\033[0m'}: {secondary_text}')


def info_output():
    thread_open('Красный', 'Поток открыт')
    new_connection('Фиолетовый', 'Новое подключение')
    information_sent('Бирюзовый', 'Информация отправлена (и другие)')
    information_received('Зелёный', 'Информация получена')

# info_output()
