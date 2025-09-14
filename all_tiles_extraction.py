import csv
from PIL import Image
from Tiles_Class import Tiles

def all_tiles_get(resolution_folder, tile_size, platform):
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
        for i in range(40):
            all_tiles.append(Tiles(kletki_list[i], tile_position_list[i]))
            if i not in (0, 10, 20, 30):
                image = Image.open(f'resources/tiles_data/images/{i}.png')
                image = image.resize(tile_size)
                image.save(f'resources/temp/{platform}/images/{i}.png')

    positions = []
    for tile in all_tiles:
        positions.append((tile.x_position, tile.y_position))

    return all_tiles, positions