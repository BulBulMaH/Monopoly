import csv
from classes.Tiles_Class import Tiles
from classes.Eggs_Class import Eggs
from classes.Questions_Class import Questions
from PIL import Image
import os


def all_tiles_get(resolution_folder, tile_size):
    all_tiles = []
    all_egg = []
    all_eggs = []
    all_question = []

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

    with open('resources/tiles_data/question.csv', 'r', encoding='utf-8') as question:
        question_reader = csv.DictReader(question)
        question_list = []
        for i in question_reader:
            question_list.append(i)

    with open(f'resources/{resolution_folder}/tiles_positions.csv', 'r', encoding='utf-8') as tile_position:
        tile_position_reader = csv.DictReader(tile_position)
        tile_position_list = []
        for i in tile_position_reader:
            tile_position_list.append(i)

    os.makedirs(f'resources/temp/images/{resolution_folder}', exist_ok=True)
    first_launch = not os.path.exists(f'resources/temp/images/{resolution_folder}/board image.png')

    if first_launch:
        image_main = Image.new('RGB', Image.open(f'resources/{resolution_folder}/board grid.png').size, (255, 255, 255))

        image_main.paste(Image.open(f'resources/{resolution_folder}/board grid.png').convert('RGB'))

    for i in range(40):
        all_tiles.append(Tiles(kletki_list[i], tile_position_list[i], tile_size))
        if first_launch:
            if i not in (0, 10, 20, 30):
                image = Image.open(f'resources/tiles_data/images/{i}.webp')
                image = image.resize(tile_size)
                image_main.paste(image, (all_tiles[i].rect.x, all_tiles[i].rect.y))

    if first_launch:
        image_main.save(f'resources/temp/images/{resolution_folder}/board image.png')

    for i in range(len(egg_list)):
        all_egg.append(Eggs(egg_list[i]))

    for i in range(len(eggs_list)):
        all_eggs.append(Eggs(eggs_list[i]))

    for i in range(len(question_list)):
        all_question.append(Questions(question_list[i]))

    return all_tiles, all_egg, all_eggs, all_question

def all_tiles_change_resolution(all_tiles: list[Tiles], resolution_folder, tile_size):
    with open(f'resources/{resolution_folder}/tiles_positions.csv', 'r', encoding='utf-8') as tile_position:
        tile_position_reader = csv.DictReader(tile_position)
        tile_position_list = []
        for i in tile_position_reader:
            tile_position_list.append(i)

    first_launch = not os.path.exists(f'resources/temp/images/{resolution_folder}/board image.png')

    if first_launch:
        image_main = Image.new('RGB', Image.open(f'resources/{resolution_folder}/board grid.png').size, (255, 255, 255))

        image_main.paste(Image.open(f'resources/{resolution_folder}/board grid.png').convert('RGB'))

    for i, tile in enumerate(all_tiles):
        tile.change_resolution(tile_position_list[i], tile_size)
        if first_launch:
            if i not in (0, 10, 20, 30):
                image = Image.open(f'resources/tiles_data/images/{i}.webp')
                image = image.resize(tile_size)
                image_main.paste(image, (all_tiles[i].rect.x, all_tiles[i].rect.y))

    if first_launch:
        os.makedirs(f'resources/temp/images/{resolution_folder}', exist_ok=True)
        image_main.save(f'resources/temp/images/{resolution_folder}/board image.png')