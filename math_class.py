import random
import time

random.seed(time.time())
def call_model_A(wrapped_board_state, c_activated, seed):
    # print("Previous state\n", wrapped_board_state)

    empty_blocks = wrapped_board_state.count("")
    offset_factor = max(0.625 ** c_activated, 0.15)
    chance_c = 0.0175 * empty_blocks * offset_factor
    RNG = random.random()
    # print("Chance to place a collect block:", chance_c)
    # print("RNG:", RNG)
    if RNG < chance_c:
        empty_block_indices = [i for i, x in enumerate(wrapped_board_state) if x == ""]
        if empty_block_indices:  # Check if there are empty blocks
            c_block = random.choice(empty_block_indices)
            wrapped_board_state[c_block] = 'C'

    coin_chances = [3, 47, 300, 1250, 5000, 15000, 45000, 140000, 400000, 800000, 1500000, 2350000, 4300000]
    coin_values = [10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10, 5, 2, 1]
    coin_chance_total = sum(coin_chances)
    multiplier_chances = [2, 28, 1270, 127000, 96000, 333400]
    multiplier_values = [100, 20, 10, 5, 3, 2]

    for i in range(len(wrapped_board_state)):
        if wrapped_board_state[i] == "":
            if random.random() < coin_chance_total:
                coin = random.choices(coin_values, weights=coin_chances, k=1)[0]
                wrapped_board_state[i] = f"{coin}"
            else:
                multiplier = random.choices(multiplier_values, weights=multiplier_chances, k=1)[0]
                wrapped_board_state[i] = f"x{multiplier}"
    # print("State after the spin:\n", wrapped_board_state)
    return wrapped_board_state