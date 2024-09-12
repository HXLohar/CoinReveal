import random
import time
import numpy as np
MIN_C_CHANCE_PER_BLOCK = 0.0015
C_CHANCE_DECREASE_SPEED = 0.55
C_CHANCE_PER_BLOCK = 0.0135
EMPTY_BLOCK = '/'
random.seed(time.time())

def call_model_A(wrapped_board_array, c_activated, seed):
    # print("Previous state\n", wrapped_board_state)
    wrapped_board_array = np.array(wrapped_board_array, dtype='<U10')
    empty_blocks = len(np.where(wrapped_board_array == '/')[0])

    # print("Empty blocks:", empty_blocks)
    # if empty_blocks == 0:
        # print(wrapped_board_array)

    offset_factor = (1-C_CHANCE_DECREASE_SPEED) ** c_activated
    chance_c = max(C_CHANCE_PER_BLOCK * empty_blocks * offset_factor, MIN_C_CHANCE_PER_BLOCK * empty_blocks)

    # print("chance_c is:", chance_c)

    if np.random.uniform(0, 1) < chance_c:

        empty_block_indices = np.where(wrapped_board_array == '/')[0]
        if empty_block_indices.size > 0:
            c_block = np.random.choice(empty_block_indices)
            wrapped_board_array[c_block] = 'C'

    coin_chances = [3, 117, 480, 2250, 16000, 39900, 85000, 130000, 325000, 475000, 1450000, 3000000, 4306250]
    coin_values = [10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10, 5, 2, 1]

    multiplier_chances = [10, 115, 1200, 9225, 36450, 123000]
    multiplier_values = [100, 20, 10, 5, 3, 2]
    coin_chance_total = sum(coin_chances) / (sum(coin_chances) + sum(multiplier_chances))
    # bonus_chances = {0: 0.04, 1: 0.035, 2: 0.03, 3: 0.025, 4: 0.015, 5: 0.0}
    bonus_chances = [0.04, 0.035, 0.03, 0.025, 0.015, 0.0]

    for i in range(len(wrapped_board_array)):
        # use np.where to get the bonus count
        bonus_count = len(np.where(wrapped_board_array == "BONUS")[0])
        # if bonus_count == 5:
            # print("chance of additional scatter per block at 5S: ", bonus_chances[bonus_count])
        # Calculate the chance of getting a BONUS symbol
        chance_bonus = bonus_chances[bonus_count]

        if wrapped_board_array[i] == EMPTY_BLOCK:
            if random.uniform(0, 1) < chance_bonus:
                wrapped_board_array[i] = "BONUS"
                continue
            if random.uniform(0, 1) < coin_chance_total:
                coin = random.choices(coin_values, weights=coin_chances, k=1)[0]
                wrapped_board_array[i] = f"{coin}"
            else:
                multiplier = random.choices(multiplier_values, weights=multiplier_chances, k=1)[0]
                wrapped_board_array[i] = f"x{multiplier}"
    # print("Board:\n", wrapped_board_array)
    return wrapped_board_array.tolist()