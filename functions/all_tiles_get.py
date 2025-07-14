from functions.Tiles_Class import Tiles
from functions.resolution_choice import resolution_definition

def all_tiles_get():
    all_tiles = []
    resolution_folder = resolution_definition()[1]
    test = open(f'resources/{resolution_folder}/text values/kletki.txt', 'r')
    information = test.readlines()
    test.close()
    for i in range(40):
        all_tiles.append(Tiles(information[i]))
    information.clear()