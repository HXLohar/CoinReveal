import tkinter as tk
from time import sleep
import threading
from tkinter import messagebox
from tkinter import simpledialog
import cProfile
import pstats
import time

import round_class

CONST_SLEEP_TIME = 50
DATABASE_UPDATE_INTERVAL = 1000




class visualized_window:
    def __init__(self, round_class=None):
        self.Round = round_class
        self.Round_list = []
        if round_class is None:
            self.Round = round_class.Round()
        self.board_state = self.Round.current_board
        # window size 800x600 with disabled minimize and maximize buttons and not allowing size change
        self.window = tk.Tk()
        self.window.title("CoinFLip")
        self.window.geometry("800x600")
        self.window.resizable(False, False)
        self.action_spin = False
        self.labels = []
        block_size = 50  # size of each block in pixels
        for i in range(5):
            for j in range(5):
                x = 30 + j * block_size
                y = 40 + i * block_size
                label = tk.Label(self.window, text=self.board_state.board[i * 5 + j].get_string(), borderwidth=2,
                                 relief="groove")
                label.place(x=x, y=y, width=block_size, height=block_size)
                self.labels.append(label)
        self.spin_button = tk.Button(self.window, text="Spin", command=self.next_step)
        self.spin_button.place(x=350, y=300, width=100, height=50)
        self.rounds_entry = tk.Entry(self.window)
        DEFAULT_ACTION_SPINS_AMOUNT = '100000'
        self.rounds_entry.insert(0, DEFAULT_ACTION_SPINS_AMOUNT)  # Default value
        self.rounds_entry.place(x=350, y=360, width=100, height=20)

        # Add a button to perform the rounds
        self.rounds_button = tk.Button(self.window, text="Action Spins", command=self.action_spins)
        self.rounds_button.place(x=350, y=390, width=100, height=50)

        # display the interface
        self.window.mainloop()

    def ask_string(self, title, prompt, default_value):
        result = simpledialog.askstring(title, prompt, initialvalue=default_value, parent=self.window)
        while result is None:
            self.window.after(100)  # Wait for 100 ms
            result = simpledialog.askstring(title, prompt, initialvalue=default_value, parent=self.window)
        return result

    def action_spins(self):
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
                db_table_name = self.ask_string("Input", "Please input the table name\nOr leave blank for default_table: ",
                                           "default_table")

                # print("called action spins")
                for i in range(num_rounds):
                    self.Round = round_class.Round()
                    self.action_spin = True
                    self.Round.spin()
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
            thresholds = [500, 600, 1000, 2500, 5000, 10000, 20000, 50000, 100000, 150000, 200000, 250000]
            print("--------\nThresholds\n")
            for threshold in thresholds:
                qualifying_rounds = len([x for x in Round_results if x >= threshold])
                if qualifying_rounds > 0:
                    print(f"Rounds >= {threshold}: {qualifying_rounds} (1 in {num_rounds / qualifying_rounds:.2f})")
                else:
                    print(f"Rounds >= {threshold}: {qualifying_rounds} (1 in *undefined*)")
            print("--------\nAverage and Median\b")
            print(f"Average result: {sum(Round_results) / len(Round_results):.2f}")
            print(f"Median result: ", sorted(Round_results)[len(Round_results) // 2])
            print("Current Time: " + str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ", Mission complete. You're welcome.")

        profiler = cProfile.Profile()
        profiler.runcall(profiled_code)
        profiler.dump_stats('profile_results.prof')

        p = pstats.Stats('profile_results.prof')
        p.sort_stats('cumulative').print_stats(10)

    def update(self, new_board_state):
        print("update method called")
        self.board_state = new_board_state
        for i in range(25):
            self.labels[i].config(text=self.board_state.board[i].get_string())

    def next_step(self):
        if not self.Round.get_latest_board().is_finished_state():
            self.Round.next_step()
            if not self.action_spin:
                self.update(self.Round.current_board)
                self.window.update()
        else:
            print("Game finished")
            print("Total value:", self.Round.get_latest_board().get_total_value())
            return


test_round = round_class.Round()
test_round.spin()

# latest_board = test_round.get_latest_board()
interface = visualized_window(test_round)
