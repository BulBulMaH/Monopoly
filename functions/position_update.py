import pygame as pg
from functions.resolution_choice import resolution_definition

def position_update(color, players, piece_color_coefficient, screen):
    resolution_folder = resolution_definition()[1]
    for player in players:
        if player.color == color:
            if color == 'red':
                player.x = player.baseX
                player.y = player.baseY
            elif color == 'green':
                player.x = player.baseX + piece_color_coefficient
                player.y = player.baseY
            elif color == 'yellow':
                player.x = player.baseX
                player.y = player.baseY + piece_color_coefficient
            elif color == 'blue':
                player.x = player.baseX + piece_color_coefficient
                player.y = player.baseY + piece_color_coefficient
            screen.blit(pg.image.load(f'resources/{resolution_folder}/{player.color}Piece.png'), (player.x, player.y))