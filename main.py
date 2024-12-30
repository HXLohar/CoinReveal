import tkinter as tk
from time import sleep
import threading
from tkinter import messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
import asyncio

import cProfile
import pstats
import time

import round_class, math_class

CONST_SLEEP_TIME = 50
DATABASE_UPDATE_INTERVAL = 1000

CONST_CURRENCY_UNIT = "EUR"
CONST_BASE_BET = 1
CONST_INITIAL_BALANCE = 10000

CONST_BONUS_BUY_COST = 500
class profile:
    def __init__(self):
        self.balance = CONST_INITIAL_BALANCE
        self.rounds_played = 0
        self.total_wagered = 0
        self.total_win = 0
        self.win_leaderboard = []
        self.multi_leaderboard = []
        self.biggest_win = 0
        self.highest_multi = 0
        self.speed_preference = 6

    def add_round(self, result_multi, base_bet=CONST_BASE_BET, cost_multi=CONST_BONUS_BUY_COST):
        total_cost = base_bet * cost_multi
        win_amount = base_bet * result_multi
        # self.total_wagered += total_cost
        # moved to the init spin part
        self.total_win += win_amount
        self.balance += (win_amount - total_cost)

        if result_multi >= round_class.CONST_MAX_WIN:
            print("Limit reached: Congratulations on hitting the Max Win!\n限額已達到: 感謝您 中得 最大獎!")

        self.biggest_win = max(self.biggest_win, win_amount)
        self.highest_multi = max(self.highest_multi, result_multi)
        if result_multi < 1000:
            return
        # if leaderboard is empty or last element is smaller than the current result
        if len(self.win_leaderboard) == 0 or self.win_leaderboard[-1] < win_amount:
            self.win_leaderboard.append(win_amount)
            self.win_leaderboard.sort(reverse=True)
            if len(self.win_leaderboard) > 10:
                self.win_leaderboard.pop()
        # same for multi leaderboard
        if len(self.multi_leaderboard) == 0 or self.multi_leaderboard[-1] < result_multi:
            self.multi_leaderboard.append(result_multi)
            self.multi_leaderboard.sort(reverse=True)
            if len(self.multi_leaderboard) > 10:
                self.multi_leaderboard.pop()

    def get_info(self, ongoing_round=False):
        info_string = f"Balance: {self.balance:,.6f} {CONST_CURRENCY_UNIT}\n"
        info_string += "Rounds played: " + str(self.rounds_played) + "\n"
        info_string += f"Total wagered: {self.total_wagered:,.6f} {CONST_CURRENCY_UNIT}\n"
        info_string += f"Total win: {self.total_win:,.6f} {CONST_CURRENCY_UNIT}\n"
        if self.rounds_played >= 5 and not ongoing_round:
            info_string += f"RTP: {(self.total_win/self.total_wagered)*100:06.2f} % / 096.53 %\n"
        else:
            info_string += f"RTP: ???.?? % / 096.53 %\n"
        info_string += f"Biggest win: {self.biggest_win:,.6f} {CONST_CURRENCY_UNIT}\n"
        info_string += f"Highest multiplier: {self.highest_multi:,}x\n"
        info_string += f"(Base bet: {CONST_BASE_BET:.6f} {CONST_CURRENCY_UNIT})\n"
        info_string += "(Cost per round: " + str(CONST_BASE_BET*CONST_BONUS_BUY_COST) + " " + CONST_CURRENCY_UNIT + ")\n"

        return info_string

    def get_interval_between_coins(self):
        interval = [240, 180, 135, 90, 60, 30, 15]
        return interval[self.speed_preference]

    def get_interval_between_steps(self):
        interval = [1000, 800, 600, 400, 300, 200, 100]
        return interval[self.speed_preference]


class visualized_window:
    def __init__(self, round_class=None):
        self.start_time = None
        self.finish_time = None
        self.round_count = 0
        # SET THE SEED HERE
        self.seed = 8
        # SET THE SEED HERE

        self.PlayerProfile = profile()
        self.Round = round_class
        self.Round_list = []

        if round_class is None:
            self.Round = round_class.Round()
        # self.Round.spin()
        self.board_state = self.Round.current_board
        # window size 800x600 with disabled minimize and maximize buttons and not allowing size change
        self.window = tk.Tk()
        self.window.title("CoinReveal.exe")
        self.window.geometry("900x600")
        self.window.resizable(False, False)
        self.action_spin = False
        self.block_display_images = []
        # profile info is at top right
        # text align to left
        self.profile_info_label = tk.Label(self.window, text=self.PlayerProfile.get_info(), font=("Helvetica", 14),
                                           anchor="w", justify="left")
        self.profile_info_label.place(x=525, y=10, width=375, height=275)
        # round result label at bottom right
        self.round_result_label = tk.Label(self.window, text="Round result:\n\n", font=("Helvetica", 16))
        self.round_result_label.place(x=510, y=450, width=300, height=150)
        self.empty_block_index = []
        self.ONGOING_ROUND = False
        # self.block_display_labels = []
        block_size = 90  # size of each block in pixels
        for i in range(5):
            for j in range(5):
                index = i * 5 + j
                y = 30 + j * block_size
                x = 30 + i * block_size
                file_name, display_string = self.board_state.blocks[i * 5 + j].get_display_string()
                image = Image.open(file_name)
                photo = ImageTk.PhotoImage(image)
                font_color = 'white' if 'coin_1.png' in file_name else 'black'

                if file_name == "coin_0.png":
                    self.empty_block_index.append(index)
                font_size = 16
                if "[C]" == display_string:
                    font_size = 24
                elif "multiplier.png" in file_name:
                    font_size = 20
                label = tk.Label(self.window, image=photo, text=display_string, compound='center', borderwidth=2,
                                 relief="groove", font=("Helvetica", font_size), fg=font_color)
                label.image = photo  # keep a reference to the image
                label.place(x=x, y=y, width=block_size, height=block_size)
                self.block_display_images.append(label)
        self.spin_button = tk.Button(self.window, text="Spin", command=self.init_regular_spin)
        self.spin_button.place(x=550, y=300, width=100, height=50)
        self.rounds_entry = tk.Entry(self.window)
        DEFAULT_ACTION_SPINS_AMOUNT = '100000'
        self.rounds_entry.insert(0, DEFAULT_ACTION_SPINS_AMOUNT)  # Default value
        self.rounds_entry.place(x=550, y=360, width=100, height=20)

        # Add a button to perform the rounds
        self.rounds_button = tk.Button(self.window, text="Action Spins", command=self.action_spins)
        self.rounds_button.place(x=550, y=390, width=100, height=50)

        # display the interface
        self.window.mainloop()

    def ask_string(self, title, prompt, default_value):
        result = simpledialog.askstring(title, prompt, initialvalue=default_value, parent=self.window)
        while result is None:
            self.window.after(100)  # Wait for 100 ms
            result = simpledialog.askstring(title, prompt, initialvalue=default_value, parent=self.window)
        return result

    def action_spins(self):
        # messagebox.showinfo("出錯了", "無法使用特快.")
        # return -1
        self.start_time = time.time()

        def profiled_code():

            Round_results = []
            alert_threshold = [1, 2, 5]
            # print("alert_threshold", alert_threshold)
            num_rounds = int(self.rounds_entry.get())
            if messagebox.askokcancel("Action Spins", f"Are you sure you want to perform {num_rounds} rounds?"):
                # ask to input db file name
                # use tkinter to create a popup window, not using the input command line

                db_file_name = self.ask_string("Input", "Please input the db file name\nOr leave blank for data.db:",
                                               "data.db")
                db_table_name = self.ask_string("Input",
                                                "Please input the table name\nOr leave blank for default_table: ",
                                                "default_table")

                # print("called action spins")
                for i in range(num_rounds):
                    self.Round = round_class.Round()
                    self.action_spin = True
                    self.Round.spin(seed=self.seed)
                    while not self.Round.get_latest_board().is_finished_state():
                        self.next_step()
                    # only interact with the database once every DATABASE_UPDATE_INTERVAL rounds
                    self.Round_list.append(self.Round)
                    if i % DATABASE_UPDATE_INTERVAL == (DATABASE_UPDATE_INTERVAL - 1) or i == num_rounds - 1:
                        round_class.add_to_database(self.Round_list, db_file_name, db_table_name)
                        self.Round_list = []

                    Round_results.append(self.Round.current_board.get_total_value())
                    if i in alert_threshold:
                        output_string = "Current Time: " + str(
                            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ", "
                        output_string += f"Progress: Round {i} finished"
                        print(output_string)
                    if i > alert_threshold[0] * 5:
                        for j in range(len(alert_threshold)):
                            alert_threshold[j] *= 10
            else:
                return -1
            self.round_count = num_rounds
            print("--------\nLeaderboard\n")
            print(f"# 1: ", sorted(Round_results)[-1])
            print(f"# 2: ", sorted(Round_results)[-2])
            print(f"# 3: ", sorted(Round_results)[-3])
            print("--------\nTop percentile\n")
            print("Top 1% percentile: ", sorted(Round_results)[-num_rounds // 100])
            print("Top 2% percentile: ", sorted(Round_results)[-num_rounds // 50])
            print("Top 5% percentile: ", sorted(Round_results)[-num_rounds // 20])
            print("Top 10% percentile: ", sorted(Round_results)[-num_rounds // 10])
            print("Top 25% percentile: ", sorted(Round_results)[-num_rounds // 4])
            print("--------\nBottom percentile\n")
            print("Bottom 25% percentile: ", sorted(Round_results)[num_rounds // 4])
            print("Bottom 10% percentile: ", sorted(Round_results)[num_rounds // 10])
            print("Bottom 5% percentile: ", sorted(Round_results)[num_rounds // 20])
            print("Bottom 2% percentile: ", sorted(Round_results)[num_rounds // 50])
            print("Bottom 1% percentile: ", sorted(Round_results)[num_rounds // 100])
            thresholds = [500, 600, 1000, 2500, 5000, 10000, 20000, 50000, 100000, 150000, 250000, 400000]
            print("--------\nThresholds\n")
            for threshold in thresholds:
                qualifying_rounds = len([x for x in Round_results if x >= threshold])
                if qualifying_rounds > 0:
                    print(f"Rounds >= {threshold}: {qualifying_rounds} (1 in {num_rounds / qualifying_rounds:.2f})")
                else:
                    print(f"Rounds >= {threshold}: {qualifying_rounds} (1 in *undefined*)")
            print("--------\nAverage and Median\n")
            print(f"Average result: {sum(Round_results) / len(Round_results):.2f}")
            print(f"Median result: ", sorted(Round_results)[len(Round_results) // 2])
            print("Current Time: " + str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ", Mission complete. You're welcome.")

        profiler = cProfile.Profile()
        profiler.runcall(profiled_code)
        profiler.dump_stats('profile_results.prof')

        p = pstats.Stats('profile_results.prof')
        p.sort_stats('cumulative').print_stats(10)

        self.finish_time = time.time()
        time_spent_in_seconds = self.finish_time - self.start_time
        print(f"總耗時 (單位: 秒): {time_spent_in_seconds:,}")
        rounds_per_second = self.round_count / time_spent_in_seconds
        print(f"速度 (回合數 / 每秒): {rounds_per_second:.2f}")

    def update_all_blocks(self, new_board_state):
        # print("update method called")
        self.board_state = new_board_state
        for i in range(25):
            self.update_single_block(i, True)
        self.window.update()  # Update the GUI
        # print("updating all blocks")

    def update_single_block(self, i, flag_update_all=False):

        file_name, display_string = self.Round.get_latest_board().blocks[i].get_display_string()

        image = Image.open(file_name)
        photo = ImageTk.PhotoImage(image)
        font_color = 'white' if 'coin_1.png' in file_name else 'black'
        font_size = 16
        if "[C]" == display_string:
            font_size = 24
        elif "multiplier.png" in file_name:
            font_size = 20
        self.block_display_images[i].config(image=photo, text=display_string, font=("Helvetica", font_size),
                                            fg=font_color)
        self.block_display_images[i].image = photo  # keep a reference to the image
        if not flag_update_all:
            self.window.update()
            # print("updating block index", i)

    def next_step(self):
        latest_board = self.Round.get_latest_board()  # Cache the result of get_latest_board
        if not latest_board.is_finished_state():
            self.Round.next_step()

            # removed window update code during action spin debug to make it faster (maybe)
            # if not self.action_spin:
                # self.window.update()
            # return 0
        else:
            # print("Game finished")
            # print("Total value:", latest_board.get_total_value())
            # print(self.Round.board_history)
            return 1

    def next_block(self):
        # pop the 1st one in the list, not the last one
        if len(self.empty_block_index) < 1:
            return -1
        block_index = self.empty_block_index.pop(0)
        self.update_single_block(block_index)

    def init_regular_spin(self):
        # create a new round
        if self.ONGOING_ROUND:
            # msg box alert: tell user must wait until current round over
            messagebox.showinfo("警告", "禁止同時進行多個獎勵購買.")
            return -1
        self.round_result_label.config(text=f"Round result:\n\n")
        self.PlayerProfile.rounds_played += 1
        self.PlayerProfile.total_wagered += CONST_BASE_BET * CONST_BONUS_BUY_COST
        # update profile label
        self.profile_info_label.config(text=self.PlayerProfile.get_info(True))
        self.ONGOING_ROUND = True
        self.Round = round_class.Round()
        self.update_all_blocks(self.Round.get_latest_board())
        self.Round.spin(seed=self.seed)
        for i in range(25):
            self.empty_block_index.append(i)
        # then display the result one by one accordingly
        self.coin_reveal_loop()

    def coin_reveal_loop(self):
        # Check if the board is in a finished state

        interval = self.PlayerProfile.get_interval_between_coins()
        # If the board is not in a finished state, continue the loop
        if len(self.empty_block_index) > 0:
            # self.window.after(interval, self.next_block)
            self.next_block()
        elif not self.Round.get_latest_board().is_finished_state():
            interval = self.PlayerProfile.get_interval_between_steps()
            self.window.after(interval, self.next_step)
            self.update_all_blocks(self.Round.get_latest_board())
            blocks = self.Round.get_latest_board().blocks

            if not self.Round.get_latest_board().get_total_value() >= round_class.CONST_MAX_WIN:
                for i in range(25):
                    if blocks[i].isEmpty():
                        self.empty_block_index.append(i)
        # Call coin_reveal_loop again to continue the loop
        if self.Round.get_latest_board().is_finished_state() and len(self.empty_block_index) <= 0:
            if self.Round.get_latest_board().get_total_value() >= round_class.CONST_MAX_WIN:
                self.window.after(interval, self.next_step)
            self.update_all_blocks(self.Round.get_latest_board())
            # print("完整獎金:")
            # print out board history but ignore the first element
            # print(self.Round.board_history[1:])
            self.ONGOING_ROUND = False
            Board_Total_Value = self.Round.get_latest_board().get_total_value()
            self.PlayerProfile.add_round(Board_Total_Value)
            self.profile_info_label.config(text=self.PlayerProfile.get_info())
            self.round_result_label.config(text=f"Round result:\n{Board_Total_Value:,}x\n{Board_Total_Value*CONST_BASE_BET:,.6f} {CONST_CURRENCY_UNIT}")
            return 1
        self.window.after(int(interval * 1.5), self.coin_reveal_loop)

math_class.init_seed_configs()
test_round = round_class.Round()
# test_round.spin()

# latest_board = test_round.get_latest_board()
interface = visualized_window(test_round)
