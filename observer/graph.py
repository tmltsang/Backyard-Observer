import pandas as pd
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from win_state import WinState
from game_state import GameState

class RTGraph:
    y_history: list
    vlines: list
    sub_plot: Axes
    graph = None
    window_size: int

    def __init__(self, sub_plot, window_size = 10):
        self.y_history = []
        self.vlines = []
        self.sub_plot = sub_plot
        self.window_size = window_size

    def update(self, new_y_value, add_vline_color = ""):
        self.y_history.append(new_y_value)
        if len(self.y_history) > self.window_size:
            if add_vline_color:
                vline_x = len(self.y_history) - self.window_size
                #add_vline[1] = color of line
                self.vlines.append((vline_x, add_vline_color))
                #print(self.vlines)
            if self.graph != None:
                self.graph.remove()
            self.plot()

    def plot(self):

        moving_average_list = pd.Series(self.y_history).rolling(self.window_size).mean().tolist()
        #Remove null values
        moving_average_list = moving_average_list[self.window_size - 1:]
        self.sub_plot.set_xlim(0, len(moving_average_list))
        self.graph = self.sub_plot.plot(range(len(moving_average_list)), moving_average_list, color = 'g')[0]
        for vline in self.vlines:
            self.sub_plot.axvline(vline[0], color=vline[1])

class RoundGraphManager:
    round_graphs: list
    set_graph: RTGraph
    def __init__(self):
        self.reset()
        plt.ion()

    def reset(self):
        self.fig = plt.figure(figsize = (9, 6))
        self.fig.suptitle("P1 Win %")
        self.round_graphs = [RTGraph(self.__new_sub_plot(2, 1, 1, "Round 1"))]
        self.set_graph = RTGraph(self.__new_sub_plot(2, 1, 2, "Set"))

    def __new_sub_plot(self, ncols, nrows, index, title):
        sub_plot = self.fig.add_subplot(ncols, nrows, index)
        sub_plot.set_title(title)
        sub_plot.set_ylim(0,1)
        sub_plot.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off
        return sub_plot



    def update(self, current_state: GameState, p1_round_predict, p1_set_predict):
        vline_color = ""
        p1_round_count = current_state.p1.round_count
        p2_round_count = current_state.p2.round_count
        if current_state.round_win_state == WinState.P1_WIN:
            vline_color = "r"
            p1_round_count += 1
        elif current_state.round_win_state == WinState.P2_WIN:
            vline_color = "b"
            p2_round_count += 1

        # if len(self.round_graphs ) > 1:
        #     for graph in self.round_graphs[:-1]:
                # self.round_graphs[i].sub_plot
        self.round_graphs[-1].update(p1_round_predict)
        self.set_graph.update(p1_set_predict, add_vline_color=vline_color)

        if current_state.set_win_state != WinState.NO_WIN:
                self.reset()
        elif current_state.round_win_state != WinState.NO_WIN:
            curr_round_count = p1_round_count + p2_round_count + 1
            self.round_graphs.append(RTGraph(self.__new_sub_plot(2, curr_round_count, curr_round_count, "Round "+ str(curr_round_count))))
            for i in range(curr_round_count - 1):
                self.round_graphs[i].sub_plot.remove()
                self.round_graphs[i].sub_plot = self.__new_sub_plot(2, curr_round_count, i+1, "Round "+ str(i+1))
                self.round_graphs[i].plot()
        plt.show()


