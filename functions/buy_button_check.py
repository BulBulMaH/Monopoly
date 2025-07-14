from functions.all_tiles_get import all_tiles_get

def buy_btn_check(color):
    global state, players
    all_tiles = all_tiles_get()
    for player in players:
        if player.main and player.color == color:
            for allPlayer in players:
                if (all_tiles[player.piece_position].buyable == 'True' and
                    player.piece_position not in allPlayer.property and
                    player.money - int(all_tiles[player.piece_position].priceTxt) > 0):
                    state['buy_btn_active'] = True
                else:
                    state['buy_btn_active'] = False