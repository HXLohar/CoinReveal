import random
import time

random.seed(time.time())
def call_model_A(wrapped_board_state, c_activated, seed):
    # print("Previous state\n", wrapped_board_state)

    empty_blocks = wrapped_board_state.count("/")
    # print("Empty blocks:", empty_blocks)
    offset_factor = max(0.625 ** c_activated, 0.15)
    chance_c = 0.0175 * empty_blocks * offset_factor
    RNG = random.random()
    # print("chance_c is:", chance_c)
    # print("RNG is:", RNG)
    # print("Chance to place a collect block:", chance_c)
    # print("RNG:", RNG)
    if RNG < chance_c:
        empty_block_indices = [i for i, x in enumerate(wrapped_board_state) if x == "/"]
        if empty_block_indices:  # Check if there are empty blocks
            c_block = random.choice(empty_block_indices)
            # print("chosen block index:", c_block)
            wrapped_board_state[c_block] = 'C'

    coin_chances = [3, 117, 480, 2250, 11000, 27900, 67000, 170000, 370000, 770000, 1350000, 2400000, 4591250]
    coin_values = [10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10, 5, 2, 1]

    multiplier_chances = [15, 185, 1800, 9500, 57500, 171000]
    multiplier_values = [100, 20, 10, 5, 3, 2]
    coin_chance_total = sum(coin_chances) / (sum(coin_chances) + sum(multiplier_chances))
    for i in range(len(wrapped_board_state)):
        bonus_count = wrapped_board_state.count("BONUS")

        # Calculate the chance of getting a BONUS symbol
        bonus_chances = {0: 0.04, 1: 0.035, 2: 0.03, 3: 0.025, 4: 0.015, 5: 0.0}
        chance_bonus = bonus_chances.get(bonus_count, 0.0)
        RNG = random.random()
        if RNG < chance_bonus:
            wrapped_board_state[i] = "BONUS"
            continue
        if wrapped_board_state[i] == "/":
            if random.random() < coin_chance_total:
                coin = random.choices(coin_values, weights=coin_chances, k=1)[0]
                wrapped_board_state[i] = f"{coin}"
            else:
                multiplier = random.choices(multiplier_values, weights=multiplier_chances, k=1)[0]
                wrapped_board_state[i] = f"x{multiplier}"
    # print("State after the spin:\n", wrapped_board_state)
    return wrapped_board_state