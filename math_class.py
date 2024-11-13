import random
import time
import numpy as np
import csv

EMPTY_BLOCK = '/'
random.seed(time.time())
MIN_C_CHANCE_PER_BLOCK = 0.0015
C_CHANCE_DECREASE_SPEED = 0.55
C_CHANCE_PER_BLOCK = 0.0135
coin_chances = [3, 117, 480, 2250, 16000, 39900, 85000, 125000, 304800, 491000, 1400000, 2853200, 4492550]
multiplier_chances = [7, 95, 1200, 8725, 40150, 139523]
bonus_chances = [0.06, 0.05, 0.04, 0.035, 0.03, 0.025, 0.02, 0.0]
coin_values = [10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10, 5, 2, 1]
multiplier_values = [100, 20, 10, 5, 3, 2]

previous_seed = -1
seed_configs = None
premium_coin_configs = None
def init_model_A_params():
    # reset all chance values to default value
    global coin_chances, multiplier_chances, bonus_chances, C_CHANCE_PER_BLOCK, C_CHANCE_DECREASE_SPEED, \
        MIN_C_CHANCE_PER_BLOCK
    MIN_C_CHANCE_PER_BLOCK = 0.0015
    C_CHANCE_DECREASE_SPEED = 0.55
    C_CHANCE_PER_BLOCK = 0.0135
    coin_chances = [3, 117, 480, 2250, 16000, 39900, 85000, 125000, 304800, 491000, 1400000, 2853200, 4492550]
    multiplier_chances = [7, 95, 1200, 8725, 40150, 139523]
    bonus_chances = [0.06, 0.05, 0.04, 0.035, 0.03, 0.025, 0.02, 0.0]


def call_model_A(wrapped_board_array, c_activated, seed):
    # print(wrapped_board_array)
    # print("Previous state\n", wrapped_board_state)
    wrapped_board_array = np.array(wrapped_board_array, dtype='<U10')
    empty_block_count = len(np.where(wrapped_board_array == EMPTY_BLOCK)[0])
    # print(C_CHANCE_DECREASE_SPEED)
    offset_factor = (1 - C_CHANCE_DECREASE_SPEED) ** c_activated
    chance_c = max(C_CHANCE_PER_BLOCK * empty_block_count * offset_factor, MIN_C_CHANCE_PER_BLOCK * empty_block_count)

    if np.random.uniform(0, 1) < chance_c:
        flag_existing_C = "C" in wrapped_board_array
        empty_block_indices = np.where(wrapped_board_array == EMPTY_BLOCK)[0]
        if empty_block_indices.size > 0 and not flag_existing_C:
            c_block = np.random.choice(empty_block_indices)
            wrapped_board_array[c_block] = 'C'

    coin_chance_total = sum(coin_chances) / (sum(coin_chances) + sum(multiplier_chances))

    bonus_count = len(np.where(wrapped_board_array == "BONUS")[0])
    chance_bonus = bonus_chances[bonus_count]

    for i in range(len(wrapped_board_array)):

        if wrapped_board_array[i] == EMPTY_BLOCK:
            if random.uniform(0, 1) < chance_bonus:
                wrapped_board_array[i] = "BONUS"
                bonus_count += 1
                chance_bonus = bonus_chances[bonus_count]

                continue
            if random.uniform(0, 1) < coin_chance_total:
                coin = random.choices(coin_values, weights=coin_chances, k=1)[0]
                wrapped_board_array[i] = f"{coin}"
            else:
                multiplier = random.choices(multiplier_values, weights=multiplier_chances, k=1)[0]
                wrapped_board_array[i] = f"x{multiplier}"
    # print("Board:\n", wrapped_board_array)
    return wrapped_board_array.tolist(), bonus_count

def call_model_B(wrapped_board_array, c_activated, seed_id):
    global coin_chances, multiplier_chances, bonus_chances, C_CHANCE_PER_BLOCK, C_CHANCE_DECREASE_SPEED, MIN_C_CHANCE_PER_BLOCK
    global previous_seed, premium_coin_configs

    if seed_id != previous_seed:
        previous_seed = seed_id
        seed_config = seed_configs[seed_id]
        coin_chances = seed_config['coin_chances']
        multiplier_chances = seed_config['multiplier_chances']
        bonus_chances = seed_config['bonus_chances']
        C_CHANCE_PER_BLOCK = seed_config['c_chance_per_block']
        C_CHANCE_DECREASE_SPEED = seed_config['c_chance_decrease_speed']
        MIN_C_CHANCE_PER_BLOCK = seed_config['min_c_chance_per_block']
    # print("SEED INFO DEBUG:")
    # print(seed_id)
    # print(coin_chances)
    # print(multiplier_chances)
    # print(bonus_chances)
    if is_empty_board(wrapped_board_array):
        if seed_id <= 3 and seed_id > 0:
            good_symbols = ["coin", "multiplier", "collect"]
            random.shuffle(good_symbols)
            good_symbol_types = 4 - seed_id
            good_symbol_indexes = random.sample(range(25), good_symbol_types)
            for i in range(good_symbol_types):
                if good_symbols[i] == "collect":
                    wrapped_board_array[good_symbol_indexes[i]] = "C"
                elif good_symbols[i] == "multiplier":
                    # print(seed_id)
                    # print(multiplier_values)
                    # print(multiplier_chances)
                    multiplier = random.choices(multiplier_values, weights=multiplier_chances, k=1)[0]
                    wrapped_board_array[good_symbol_indexes[i]] = f"x{multiplier}"
                else:
                    coin = random.choices(premium_coin_configs['coin_values'], weights=premium_coin_configs['weights'], k=1)[0]
                    wrapped_board_array[good_symbol_indexes[i]] = f"{coin}"

    return call_model_A(wrapped_board_array, c_activated, seed_id)

def init_seed_configs():
    global seed_configs, premium_coin_configs
    seed_configs = []
    premium_coin_configs = {'coin_values': [], 'weights': []}
    with open('seed.csv', mode='r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            row = {k.strip(): v for k, v in row.items()}  # Strip spaces from keys
            seed_configs.append({
                'coin_chances': list(map(int, row['coin_chances'].split(', '))) if row['coin_chances'] else [],
                'multiplier_chances': list(map(int, row['multiplier_chances'].split(', '))) if row['multiplier_chances'] else [],
                'bonus_chances': list(map(float, row['bonus_chances'].split(', '))) if row['bonus_chances'] else [],
                'c_chance_per_block': float(row['c_chance_per_block']) if row['c_chance_per_block'] else None,
                'c_chance_decrease_speed': float(row['c_chance_decrease_speed']) if row['c_chance_decrease_speed'] else None,
                'min_c_chance_per_block': float(row['min_c_chance_per_block']) if row['min_c_chance_per_block'] else None
            })

    with open('premium_coins.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            premium_coin_configs['coin_values'].append(int(row['coin_value']))
            premium_coin_configs['weights'].append(int(row['weight']))
def is_empty_board(wrapped_array):
    # example
    # ['/', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/',
    # '/', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/'] is empty board
    return wrapped_array == [EMPTY_BLOCK] * 25
