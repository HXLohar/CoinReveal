import copy
import random
import sqlite3
import json
import math_class

db_Table_Name = "test_A2_4"
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
            self.block_value *= multiplier
    def erase(self):
        self.block_type = "empty"
        self.block_value = 0
    def get_string(self):
        if self.block_type == "empty":
            return ""
        if self.block_type == "coin":
            return f"{self.block_value:,}"
        if self.block_type == "special_coin":
            return f"[{self.block_value:,}]"
        if self.block_type == "multiplier":
            return f"x{self.block_value}"
        if self.block_type == "collect":
            return f"[ C ]"

def wrap_string(block):
    if block.block_type == "empty":
        return ""
    if block.block_type == "coin":
        return f"{block.block_value}"
    if block.block_type == "special_coin":
        return f"s{block.block_value}"
    if block.block_type == "multiplier":
        return f"x{block.block_value}"
    if block.block_type == "collect":
        return f"C"
def unwrap_string(wrapped_string):
    if wrapped_string == "":
        return block(0)
    if wrapped_string[0] == "s":
        return block(0, "special_coin", int(wrapped_string[1:]))
    if wrapped_string[0] == "C":
        return block(0, "collect")
    if wrapped_string[0] == "x":
        return block(0, "multiplier", int(wrapped_string[1:]))
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
    def is_finished_state(self):
        # if the sum of all block's value is no less than MAX_WIN, return True
        sum = self.get_total_value()
        if sum >= MAX_WIN:
            return True
        # if every block is either coin or special_coin, return True
        for block in self.board:
            if block.block_type != "coin" and block.block_type != "special_coin":
                return False
        return True
    def get_total_value(self):
        sum = 0
        for block in self.board:
            sum += block.get_value()
        return sum
    def next_step(self):

        if self.is_finished_state():
            return "already_finished_state"
        # 1. 如果存在type为multiplier的block, 则对于每个block, 调用其multiply方法, 参数为type为multiplier的block的value. 然后对于type为multiplier的block, 调用erase方法
        flag_event = False
        for block in self.board:
            if block.block_type == "multiplier":
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
        wrapped_board = []
        for block_instance in self.board:
            wrapped_board.append(wrap_string(block_instance))
        result = math_class.call_model_A(wrapped_board, c_activated, seed)
        for i in range(25):
            self.board[i] = unwrap_string(result[i])
        return 0

class Round:
    def __init__(self, math_model=1, assigned_seed=-1):
        self.math_model = math_model
        self.seed = assigned_seed
        if assigned_seed < 0:
            self.seed = random.randint(0, 10000)
        self.current_board = board_state(self.math_model, self.seed)
        self.board_history = []
        self.result = 0
    def get_latest_board(self):
        return self.board_history[-1]
    def spin(self):
        self.current_board.spin(self.math_model, self.current_board.c_activated, self.seed)
        self.board_history.append(copy.deepcopy(self.current_board))

    def next_step(self):
        if self.current_board.is_finished_state():
            self.result = self.current_board.get_total_value()
        else:
            self.current_board.next_step()
            self.board_history.append(copy.deepcopy(self.current_board))


    def add_to_database(self):
        self.result = self.current_board.get_total_value()

        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        table_name = db_Table_Name
        # Create the table if it doesn't exist
        table_name = db_Table_Name
        c.execute(f'''
                            CREATE TABLE IF NOT EXISTS {table_name} (
                                id INTEGER PRIMARY KEY,
                                board_history TEXT,
                                result INTEGER,
                                c_activated INTEGER
                            )
                        ''')

        # Convert the board history to a string
        wrapped_boards = []
        for board in self.board_history:
            wrapped_board = []
            for block_instance in board.board:
                wrapped_board.append(wrap_string(block_instance))
            wrapped_boards.append(json.dumps(wrapped_board))
        board_history_str = '\n'.join(wrapped_boards)

        # Insert the current round's data into the table
        c.execute(f'''
                                        INSERT INTO {table_name} (board_history, result, c_activated)
                                        VALUES (?, ?, ?)
                                    ''', (board_history_str, self.result, self.current_board.c_activated))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
