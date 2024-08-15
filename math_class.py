import random

def call_model_A(wrapped_board_state, c_activated, seed):
    print("Previous state\n", wrapped_board_state)
    random.seed(seed)
    empty_blocks = wrapped_board_state.count("")
    offset_factor = max(0.7 ** c_activated, 0.15)
    chance_c = 0.0175 * empty_blocks * offset_factor
    RNG = random.random()
    print("Chance to place a collect block:", chance_c)
    print("RNG:", RNG)
    if RNG < chance_c:
        empty_block_indices = [i for i, x in enumerate(wrapped_board_state) if x == ""]
        if empty_block_indices:  # Check if there are empty blocks
            c_block = random.choice(empty_block_indices)
            wrapped_board_state[c_block] = 'C'

    coin_chances = [0.000001, 0.000019, 0.0002, 0.0015, 0.0035, 0.008, 0.015, 0.02, 0.04, 0.08, 0.095, 0.22, 0.481]
    coin_values = [10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10, 5, 2, 1]
    coin_chance_total = sum(coin_chances)
    multiplier_chances = [0.000001, 0.000029, 0.0007, 0.00445, 0.0126, 0.028]
    multiplier_values = [100, 20, 10, 5, 3, 2]

    for i in range(len(wrapped_board_state)):
        if wrapped_board_state[i] == "":
            if random.random() < coin_chance_total:
                coin = random.choices(coin_values, weights=coin_chances, k=1)[0]
                wrapped_board_state[i] = f"{coin}"
            else:  # 50% chance to place a multiplier
                multiplier = random.choices(multiplier_values, weights=multiplier_chances, k=1)[0]
                wrapped_board_state[i] = f"x{multiplier}"
    print("State after the spin:\n", wrapped_board_state)
    return wrapped_board_state