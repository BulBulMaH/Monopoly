import csv
from Tiles_Class import Tiles
from PIL import Image
import os

def all_tiles_get(resolution_folder, tile_size):
    all_tiles = []
    with open('resources/tiles_data/kletki.csv', 'r', encoding='utf-8') as kletki:
        kletki_reader = csv.DictReader(kletki)
        kletki_list = []
        for i in kletki_reader:
            kletki_list.append(i)

    with open(f'resources/{resolution_folder}/tiles_positions.csv', 'r', encoding='utf-8') as tile_position:
        tile_position_reader = csv.DictReader(tile_position)
        tile_position_list = []
        for i in tile_position_reader:
            tile_position_list.append(i)

        if not os.path.exists(f'resources/temp/images/{resolution_folder}'):
            if not os.path.exists('resources/temp/images'):
                if not os.path.exists('resources/temp'):
                    os.mkdir('resources/temp')
                os.mkdir('resources/temp/images')
            os.mkdir(f'resources/temp/images/{resolution_folder}')

        for i in range(40):
            all_tiles.append(Tiles(kletki_list[i], tile_position_list[i]))
            if i not in (0, 10, 20, 30):
                if not os.path.exists(f'resources/temp/images/{resolution_folder}/{i}.png'):
                    image = Image.open(f'resources/tiles_data/images/{i}.png')
                    image = image.resize(tile_size)
                    image.save(f'resources/temp/images/{resolution_folder}/{i}.png')

    positions = []
    for tile in all_tiles:
        positions.append((tile.x_position, tile.y_position))

    return all_tiles, positions