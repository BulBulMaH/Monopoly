import csv

from Tiles_Class import Tiles
from Eggs_Class import Eggs
from PIL import Image
import os


def all_tiles_get(resolution_folder, tile_size):
    all_tiles = []
    all_egg = []
    all_eggs = []

    with open('resources/tiles_data/kletki.csv', 'r', encoding='utf-8') as kletki:
        kletki_reader = csv.DictReader(kletki)
        kletki_list = []
        for i in kletki_reader:
            kletki_list.append(i)

    with open('resources/tiles_data/egg.csv', 'r', encoding='utf-8') as egg:
        egg_reader = csv.DictReader(egg)
        egg_list = []
        for i in egg_reader:
            egg_list.append(i)

    with open('resources/tiles_data/eggs.csv', 'r', encoding='utf-8') as eggs:
        eggs_reader = csv.DictReader(eggs)
        eggs_list = []
        for i in eggs_reader:
            eggs_list.append(i)

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

        first_launch = not os.path.exists(f'resources/temp/images/{resolution_folder}/board image.png')
        if first_launch:
            image_main = Image.new('RGBA', Image.open(f'resources/{resolution_folder}/board grid.png').size, (255, 255, 255))
            image_main.paste(Image.open(f'resources/{resolution_folder}/board grid.png').convert('RGBA'))
        for i in range(40):
            all_tiles.append(Tiles(kletki_list[i], tile_position_list[i]))
            if i not in (0, 10, 20, 30):
                if first_launch:
                    image = Image.open(f'resources/tiles_data/images/{i}.png')
                    image = image.resize(tile_size)
                    image_main.paste(image, (all_tiles[i].x_position, all_tiles[i].y_position))
        if first_launch:
            image_main.save(f'resources/temp/images/{resolution_folder}/board image.png')
                    # image.save(f'resources/temp/images/{resolution_folder}/{i}.png')

        for i in range(len(egg_list)):
            all_egg.append(Eggs(egg_list[i]))

        for i in range(len(eggs_list)):
            all_eggs.append(Eggs(eggs_list[i]))

    positions = []
    for tile in all_tiles:
        positions.append((tile.x_position, tile.y_position))

    return all_tiles, positions, all_egg, all_eggs