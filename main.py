import tkinter as tk
import round_class
class visualized_window:
    def __init__(self, board_state):
        self.board_state = board_state
        # window size 800x600 with disabled minimize and maximize buttons and not allowing size change
        self.window = tk.Tk()
        self.window.title("CoinFLip")
        self.window.geometry("800x600")
        self.window.resizable(False, False)

        self.labels = []
        block_size = 50  # size of each block in pixels
        for i in range(5):
            for j in range(5):
                x = 30 + j * block_size
                y = 40 + i * block_size
                label = tk.Label(self.window, text=self.board_state.board[i*5+j].get_string(), borderwidth=2, relief="groove")
                label.place(x=x, y=y, width=block_size, height=block_size)
                self.labels.append(label)

        # display the interface
        self.window.mainloop()

    def update(self, new_board_state):
        self.board_state = new_board_state
        for i in range(25):
            self.labels[i].config(text=self.board_state.board[i].get_string())

test_round = round_class.round()
test_round.spin()

latest_board = test_round.get_latest_board()
interface = visualized_window(latest_board)
