import copy
import random
import sqlite3
import json
import math_class
import numpy

CONST_MAX_WIN = 400000
CONST_BONUS_PAY = [0, 0, 0, 80, 200, 500, 1500, 5000]

class block:
    def __init__(self, ID, block_type="empty", block_value=0):
        self.ID = ID
        self.block_type = block_type
        self.block_value = block_value

    def get_value(self):
        if self.block_type == "coin" or self.block_type == "special_coin":
            return self.block_value
        return 0

    def multiply(self, multiplier):
        if self.block_type == "coin" or self.block_type == "special_coin":
            # print("block value before multiply: " + str(self.block_value)
            # + ", multiplier: " + str(multiplier))
            self.block_value *= multiplier
            if self.block_value > CONST_MAX_WIN:
                self.block_value = CONST_MAX_WIN

    def erase(self):
        self.block_type = "empty"
        self.block_value = 0

    def get_string(self):
        if self.block_type == "empty":
            return "/"
        if self.block_type == "coin":
            return f"{self.block_value:,}"
        if self.block_type == "special_coin":
            return f"[{self.block_value:,}]"
        if self.block_type == "multiplier":
            return f"x{self.block_value}"
        if self.block_type == "collect":
            return f"[ C ]"
        if self.block_type == "bonus":
            return "BONUS"

    def get_display_string(self):
        file_name = "coin_0.png"
        display_string = ""
        if self.block_type == "coin":
            display_string = self.block_value
            if self.block_value >= 1000:
                file_name = "coin_4.png"
            elif self.block_value >= 100:
                file_name = "coin_3.png"
            elif self.block_value >= 10:
                file_name = "coin_2.png"
            else:
                file_name = "coin_1.png"
        elif self.block_type == "multiplier":
            display_string = f"x{self.block_value}"
            file_name = "multiplier.png"

        elif self.block_type == "special_coin":
            display_string = f"[{self.block_value}]"
            file_name = "collect.png"
        elif self.block_type == "collect":
            display_string = "[C]"
            file_name = "collect.png"
        elif self.block_type == "bonus":
            file_name = "bonus.png"
        file_name = "images\\" + file_name
        return file_name, display_string

    def isEmpty(self):
        return self.block_type == "empty"

import csv
import random
seed_name_list = ["SPECIAL", "AAA", "AA", "A", "B", "C", "D", "E", "F"]
def get_seed(RTP_version):
    # Define the valid RTP versions and default to 87 if the input is invalid
    valid_versions = [97, 96, 94, 92, 87]
    if RTP_version not in valid_versions:
        RTP_version = 87

    # Read the CSV file and store the weights for the given RTP version
    weights = []
    with open('rtp_seed.csv', mode='r') as file:
        # print("debug: csv file:")
        # print csv file
        # debug_csv_reader = csv.reader(file)
        # for row in debug_csv_reader:
            # print(row)
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if int(row['rtp_version']) == RTP_version:
                weights = [float(row[f'seed_{i}']) for i in range(9)]
                break

    # Normalize the weights to sum to 1
    total_weight = sum(weights)
    normalized_weights = [weight / total_weight for weight in weights]

    # Randomly select a seed based on the weights
    seed = random.choices(range(9), weights=normalized_weights, k=1)[0]
    # print("your seed is: " + str(seed))
    return seed

def wrap_string(block):
    if block.block_type == "empty":
        return "/"
    if block.block_type == "coin":
        return f"{block.block_value}"
    if block.block_type == "special_coin":
        return f"s{block.block_value}"
    if block.block_type == "multiplier":
        return f"x{block.block_value}"
    if block.block_type == "collect":
        return f"C"
    if block.block_type == "bonus":
        return f"BONUS"


def unwrap_string(wrapped_string):
    if wrapped_string == "/":
        return block(0, "empty", 0)
    if wrapped_string[0] == "s":
        return block(0, "special_coin", int(wrapped_string[1:]))
    if wrapped_string[0] == "C":
        return block(0, "collect")
    if wrapped_string[0] == "x":
        return block(0, "multiplier", int(wrapped_string[1:]))
    if wrapped_string == "BONUS":
        return block(0, "bonus")
    return block(0, "coin", int(wrapped_string))


def unwrap_string_to_board(wrapped_board):
    unwrapped_board_string = []
    for i in range(25):
        unwrapped_board_string.append(unwrap_string(wrapped_board[i]))
    return unwrapped_board_string


class board_state:
    def __init__(self, math_model, seed, copy_from_board=None, event="spin"):
        # if copy_from_board is not None, deep copy it
        self.math_model = math_model
        self.seed = seed
        # begin with 25 empty blocks
        self.blocks = []
        for i in range(25):
            self.blocks.append(block(i))
        self.c_activated = 0
        if copy_from_board is not None:
            self.blocks = copy.deepcopy(copy_from_board.blocks)
        self.multi_activated = 0
        self.total_multi = 1
        self.BONUS_symbol_count = 0

    def is_finished_state(self):
        # if the sum of all block's value is no less than MAX_WIN, return True
        sum = self.get_total_value()
        if sum >= CONST_MAX_WIN:
            # if every block is either coin or special_coin or empty, return True
            for block in self.blocks:
                if block.block_type != "coin" and block.block_type != "special_coin" and block.block_type != "bonus" \
                        and block.block_type != "empty":
                    return False

            return True
        # if every block is either coin or special_coin, return True
        for block in self.blocks:
            if block.block_type != "coin" and block.block_type != "special_coin" and block.block_type != "bonus":
                return False

        return True

    def get_total_value(self):
        sum = 0
        for block in self.blocks:
            sum += block.get_value()


        self.BONUS_symbol_count = 0
        for block in self.blocks:
            if block.block_type == "bonus":
                self.BONUS_symbol_count += 1

        sum += CONST_BONUS_PAY[self.BONUS_symbol_count]

        if sum > CONST_MAX_WIN:
            sum = CONST_MAX_WIN
        return sum

    def next_step(self):

        if self.is_finished_state():
            return "already_finished_state"
        # 1. 如果存在type为multiplier的block, 则对于每个block, 调用其multiply方法, 参数为type为multiplier的block的value. 然后对于type为multiplier的block, 调用erase方法
        flag_event = False
        for block in self.blocks:
            if block.block_type == "multiplier":
                self.multi_activated += 1
                self.total_multi *= block.block_value
                for block2 in self.blocks:
                    block2.multiply(block.block_value)
                block.erase()
                flag_event = True
                return
        if flag_event:
            return "activated_multiplier"
        # 2. 如果存在type为collect的block, 则对于每个type为coin或special_coin的block,
        # 将其value加到这个(type为collect的block)上, 然后将自己的type从collect转为special_coin, 并对于每个其他不是special_coin的block, 调用erase方法.
        for block in self.blocks:
            if block.block_type == "collect":
                self.c_activated += 1
                for block2 in self.blocks:
                    if block2.block_type == "coin" or block2.block_type == "special_coin":
                        block.block_value += block2.block_value
                        if block2.block_type != "special_coin":
                            block2.erase()
                block.block_type = "special_coin"
                if block.block_value > CONST_MAX_WIN:
                    block.block_value = CONST_MAX_WIN
                flag_event = True
        if flag_event:
            return "activated_collect"
        # 3. 如果仍有至少1个空格(type为empty)的block, 调用spin方法, 参数为self.math_model
        for block in self.blocks:
            if block.block_type == "empty":
                self.spin(self.math_model, self.c_activated, self.seed)
                return "activated_spin"

        return "ERROR: nothing happened"

    def spin(self, math_model, c_activated, seed):
        wrapped_board = self.wrap_board()
        result, self.BONUS_symbol_count = math_class.call_model_B(wrapped_board, c_activated, seed)
        self.blocks = unwrap_string_to_board(result)

    def wrap_board(self):
        wrapped_board = []
        for block_instance in self.blocks:
            wrapped_board.append(wrap_string(block_instance))
        return wrapped_board


class Round:
    def __init__(self, math_model="B", assigned_seed=-1):
        self.math_model = math_model
        self.seed = assigned_seed
        self.RTP_version = 94
        # seed_name_list = ["SPECIAL", "AAA", "AA", "A", "B", "C", "D", "E", "F"]

        if assigned_seed < 0:
            self.seed = random.randint(0, 10000)
        self.current_board = board_state(self.math_model, self.seed)

        self.board_history = [self.current_board.wrap_board()]
        # self.result = 0

    def batch_spin(self, num_spins):
        results = []
        for _ in range(num_spins):
            results.append(self.spin())
        return results

    def get_latest_board(self):
        latest_board_string = self.board_history[-1]
        # unwrap string to board
        latest_board = board_state(self.math_model, self.seed)
        index = 0
        for wrapped_string in latest_board_string:
            latest_board.blocks[index] = unwrap_string(wrapped_string)
            index += 1
        return latest_board

    def spin(self, seed=-1, RTP_version=94, action_spin=False):

        if not (RTP_version in [97, 96, 94, 92, 87]):
            RTP_version = 87
        self.RTP_version = RTP_version
        if not seed == -1:
            self.seed = seed
        else:
            self.seed = get_seed(self.RTP_version)
            if not action_spin:
                print(f"您得到的種子ID:{self.seed}")
                print(f"對應級別:{seed_name_list[self.seed]}")


        self.current_board.seed = self.seed
        # print("seed id in class round: " + str(self.seed))
        self.current_board.spin(self.math_model, self.current_board.c_activated, self.seed)
        self.board_history.append(self.current_board.wrap_board())

    def next_step(self):
        if self.current_board.is_finished_state():
            self.result = self.current_board.get_total_value()
        else:
            self.current_board.next_step()
            self.board_history.append(self.current_board.wrap_board())


def add_to_database(rounds, db_file_name="data.db", db_table_name="default_table"):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()
    table_name = db_table_name
    # Create the table if it doesn't exist
    c.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    board_history TEXT,
                    result INTEGER,
                    c_activated INTEGER,
                    multi_count INTEGER,
                    multi_total INTEGER,
                    bonus_symbol_count INTEGER,
                    bonus_pay INTEGER
                )
            ''')

    for round in rounds:
        # Convert the board history to a string
        wrapped_boards = []
        for board in round.board_history:
            wrapped_boards.append(' '.join(board))
        board_history_str = '\n'.join(wrapped_boards)

        # Calculate bonus_symbol_count and BONUS_pay
        bonus_symbol_count = round.current_board.BONUS_symbol_count
        # print(bonus_symbol_count)
        bonus_pay = CONST_BONUS_PAY[bonus_symbol_count]
        result = round.current_board.get_total_value()

        # Insert the current round's data into the table
        c.execute(f'''
                    INSERT INTO {table_name} (board_history, result, c_activated, multi_count, multi_total, bonus_symbol_count, bonus_pay)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (board_history_str, result, round.current_board.c_activated, round.current_board.multi_activated,
                      round.current_board.total_multi,
                      bonus_symbol_count, bonus_pay))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
