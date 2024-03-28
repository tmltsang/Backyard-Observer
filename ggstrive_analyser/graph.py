import pandas as pd
from matplotlib.axes import Axes

class RTGraph:
    y_history: list
    vlines: list
    plot: Axes
    graph = None
    window_size: int

    def __init__(self, plot, window_size = 5):
        self.y_history = []
        self.vlines = []
        self.plot = plot
        self.plot.set_ylim(0,1)
        self.window_size = window_size
    
    def update(self, new_y_value, add_vline = False):
        if self.graph != None:
            self.graph.remove()
        
        self.y_history.append(new_y_value)
        if len(self.y_history) > self.window_size:
            moving_average_list = pd.Series(self.y_history).rolling(self.window_size).mean().tolist()
            #Remove null values
            moving_average_list = moving_average_list[self.window_size - 1:]
            self.plot.set_xlim(0, len(moving_average_list))
            if add_vline:
                self.vlines.append(len(moving_average_list))
                print(self.vlines)
            self.graph = self.plot.plot(range(len(moving_average_list)), moving_average_list, color = 'g')[0]
            for vline in self.vlines:
                self.plot.axvline(vline, color ='r')

    