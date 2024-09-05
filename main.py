import tkinter as tk
from time import sleep
import threading
from tkinter import messagebox
import time

import round_class
default_alert_threshold = [1, 2, 5]
CONST_SLEEP_TIME = 50
class visualized_window:
    def __init__(self, round_class=None):
        self.Round = round_class
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
                label = tk.Label(self.window, text=self.board_state.board[i*5+j].get_string(), borderwidth=2, relief="groove")
                label.place(x=x, y=y, width=block_size, height=block_size)
                self.labels.append(label)
        self.spin_button = tk.Button(self.window, text="Spin", command=self.next_step)
        self.spin_button.place(x=350, y=300, width=100, height=50)
        self.rounds_entry = tk.Entry(self.window)
        self.rounds_entry.insert(0, '1000')  # Default value
        self.rounds_entry.place(x=350, y=360, width=100, height=20)

        # Add a button to perform the rounds
        self.rounds_button = tk.Button(self.window, text="Action Spins", command=self.action_spins)
        self.rounds_button.place(x=350, y=390, width=100, height=50)

        # display the interface
        self.window.mainloop()
    def action_spins(self):
        alert_threshold = default_alert_threshold
        num_rounds = int(self.rounds_entry.get())
        if messagebox.askokcancel("Action Spins", f"Are you sure you want to perform {num_rounds} rounds?"):
            print("called action spins")
            for i in range(num_rounds):
                self.Round = round_class.Round()
                self.action_spin = True
                self.Round.spin()
                while not self.Round.get_latest_board().is_finished_state():
                    self.next_step()
                self.Round.add_to_database()
                if i in alert_threshold:
                    output_string = "Current Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ", "
                    output_string += f"Progress: Round {i} finished"
                    print(output_string)
                if i > alert_threshold[0] * 9:
                    for j in range(len(alert_threshold)):
                        alert_threshold[j] *= 10
        print("Current Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ", Mission complete. You're welcome.")

    def update(self, new_board_state):
        self.board_state = new_board_state
        for i in range(25):
            self.labels[i].config(text=self.board_state.board[i].get_string())
    def next_step(self):
        if self.Round.get_latest_board().is_finished_state():
            print("Game finished")
            print("Total value:", self.Round.get_latest_board().get_total_value())
            return
        else:

            self.Round.next_step()
            if not self.action_spin:
                self.update(self.Round.current_board)
                self.window.update()


test_round = round_class.Round()
test_round.spin()

# latest_board = test_round.get_latest_board()
interface = visualized_window(test_round)
