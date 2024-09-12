import copy
import random
import sqlite3
import json
import math_class
import numpy

db_Table_Name = "test_A4_1"
MAX_WIN = 250000
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

class board_state:
    def __init__(self, math_model, seed, copy_from_board=None, event="spin"):
        # if copy_from_board is not None, deep copy it
        self.math_model = math_model
        self.seed = seed
        # begin with 25 empty blocks
        self.board = []
        for i in range(25):
            self.board.append(block(i))
        self.c_activated = 0
        if copy_from_board is not None:
            self.board = copy.deepcopy(copy_from_board.board)
        self.multi_activated = 0
        self.total_multi = 1
    def is_finished_state(self):
        # if the sum of all block's value is no less than MAX_WIN, return True
        sum = self.get_total_value()
        if sum >= MAX_WIN:
            return True
        # if every block is either coin or special_coin, return True
        for block in self.board:
            if block.block_type != "coin" and block.block_type != "special_coin" and block.block_type != "bonus":
                return False
        return True
    def get_total_value(self):
        sum = 0
        for block in self.board:
            sum += block.get_value()
        bonus_count = numpy.where(self.board == "BONUS")[0].size
        bonus_pay = [0, 0, 0, 80, 200, 500]
        # print("BONUS: " + str(bonus_count))
        sum += bonus_pay[bonus_count]
        # print(f"BONUS pay: {bonus_pay[bonus_count]}")
        if sum > MAX_WIN:
            sum = MAX_WIN
        return sum
    def next_step(self):

        if self.is_finished_state():
            return "already_finished_state"
        # 1. 如果存在type为multiplier的block, 则对于每个block, 调用其multiply方法, 参数为type为multiplier的block的value. 然后对于type为multiplier的block, 调用erase方法
        flag_event = False
        for block in self.board:
            if block.block_type == "multiplier":
                self.multi_activated += 1
                self.total_multi *= block.block_value
                for block2 in self.board:
                    block2.multiply(block.block_value)
                block.erase()
                flag_event = True
        if flag_event:
            return "activated_multiplier"
        # 2. 如果存在type为collect的block, 则对于每个type为coin或special_coin的block,
        # 将其value加到这个(type为collect的block)上, 然后将自己的type从collect转为special_coin, 并对于每个其他不是special_coin的block, 调用erase方法.
        for block in self.board:
            if block.block_type == "collect":
                self.c_activated += 1
                for block2 in self.board:
                    if block2.block_type == "coin" or block2.block_type == "special_coin":
                        block.block_value += block2.block_value
                        if block2.block_type != "special_coin":
                            block2.erase()
                block.block_type = "special_coin"
                flag_event = True
        if flag_event:
            return "activated_collect"
        # 3. 如果仍有至少1个空格(type为empty)的block, 调用spin方法, 参数为self.math_model
        for block in self.board:
            if block.block_type == "empty":
                self.spin(self.math_model, self.c_activated, self.seed)
                return "activated_spin"

        return "ERROR: nothing happened"

    def spin(self, math_model, c_activated, seed):
        wrapped_board = self.wrap_board()
        result = math_class.call_model_A(wrapped_board, c_activated, seed)
        for i in range(25):
            self.board[i] = unwrap_string(result[i])
        return 0
    def wrap_board(self):
        wrapped_board = []
        for block_instance in self.board:
            wrapped_board.append(wrap_string(block_instance))
        return wrapped_board


class Round:
    def __init__(self, math_model=1, assigned_seed=-1):
        self.math_model = math_model
        self.seed = assigned_seed
        if assigned_seed < 0:
            self.seed = random.randint(0, 10000)
        self.current_board = board_state(self.math_model, self.seed)
        self.board_history = []
        self.result = 0

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
            latest_board.board[index] = unwrap_string(wrapped_string)
            index += 1
        return latest_board
    def spin(self):
        self.current_board.spin(self.math_model, self.current_board.c_activated, self.seed)
        self.board_history.append(self.current_board.wrap_board())

    def next_step(self):
        if self.current_board.is_finished_state():
            self.result = self.current_board.get_total_value()
        else:
            self.current_board.next_step()

            self.board_history.append(self.current_board.wrap_board())


def add_to_database(rounds):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    table_name = db_Table_Name
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
                    BONUS_pay INTEGER
                )
            ''')

    for round in rounds:
        # Convert the board history to a string
        wrapped_boards = []
        for board in round.board_history:
            wrapped_boards.append(' '.join(board))
        board_history_str = '\n'.join(wrapped_boards)

        # Calculate bonus_symbol_count and BONUS_pay
        bonus_symbol_count = numpy.where(numpy.array(round.current_board.board) == "BONUS")[0].size
        bonus_pay = [0, 0, 0, 80, 200, 500][bonus_symbol_count]

        # Insert the current round's data into the table
        c.execute(f'''
                    INSERT INTO {table_name} (board_history, result, c_activated, multi_count, multi_total, bonus_symbol_count, BONUS_pay)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (board_history_str, round.result, round.current_board.c_activated, round.current_board.multi_activated, round.current_board.total_multi,
                      bonus_symbol_count, bonus_pay))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()