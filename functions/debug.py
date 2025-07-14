def debug_output():
    global players, state
    print(f'\nPlayers: {players}'
          f'\nState: buy_btn_active: {state['buy_btn_active']}'
          f'\n       is_game_started: {state['is_game_started']}'
          f'\n       ready: {state['ready']}')