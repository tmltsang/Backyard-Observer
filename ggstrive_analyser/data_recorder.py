from abc import ABC, abstractmethod
import os
import csv
from win_state import WinState
from game_state import GameState

class DataRecorder(ABC):
    previous_state: GameState
    cfg: dict

    @abstractmethod
    def __init__(self, cfg: dict):
        self.previous_state = GameState()
        self.cfg = cfg

    @abstractmethod
    def write(self, current_state: GameState):
        pass

    # @abc.abstractproperty
    # def previous_state(self):
    #     return self._previous_state

    def prev_round_winner(self, current_state: GameState):
        if self.previous_state:
            if current_state.p1.round_count > self.previous_state.p1.round_count:
                return WinState.P1_WIN
            elif current_state.p2.round_count > self.previous_state.p2.round_count:
                return WinState.P2_WIN
        return WinState.NO_WIN
    
    def prev_set_winner(self, current_state: GameState):
        if self.previous_state:
            if (current_state.p1.round_count + current_state.p2.round_count == 0) and\
                not (self.previous_state.p1.round_count + self.previous_state.p2.round_count == 0):
                # print("current p1 round count %d" % (current_state["p1"].round_count))
                # print("current p2 round count %d" % (current_state["p2"].round_count))

                # print("previous p1 round count %d" % (self.previous_state["p1"].round_count))
                # print("previous p2 round count %d" % (self.previous_stat e["p2"].round_count))

                if self.previous_state.p1.health < self.previous_state.p2.health:
                    return WinState.P2_WIN
                else:
                    return WinState.P1_WIN
        return WinState.NO_WIN

class CSVDataRecorder(DataRecorder):
    filename: str
    fields: list
    current_round_history: list
    current_set_history: list

    def __init__(self, cfg: dict, filename: str):
        super().__init__(cfg)
        self.filename = cfg["csv_path"] + "/" +  filename + ".csv"
        self.fields = cfg["csv_fields"]
        self.current_round_history = []
        self.current_set_history = []

        # #backup current
        # if  os.path.isdir(cfg["csv_path"]):
        #     os.rename(cfg["csv_path"], cfg["csv_path"] + "_backup")

        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fields)
    
    def __record_round_win(self, p1_round_win: bool):
        for row in self.current_round_history:
            row['p1_round_win'] = p1_round_win
    
    def __record_set_win(self, p1_set_win: bool):
        for row in self.current_set_history:
            row['p1_set_win'] = p1_set_win

    def write_set_win(self, set_win_state: WinState):
        self.__record_round_win(set_win_state == WinState.P1_WIN)
        self.current_set_history += self.current_round_history
        self.__record_set_win(set_win_state == WinState.P1_WIN)
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fields)
            writer.writerows(self.current_set_history)
        self.current_round_history = []
        self.current_set_history = []
            
    def write(self, current_state: GameState):
        # print (current_state)
        # print (self.previous_state)
        self.current_round_history.append(current_state.flatten())

        round_win_state = self.prev_round_winner(current_state)

        if round_win_state != WinState.NO_WIN:
            self.__record_round_win(round_win_state == WinState.P1_WIN)
            self.current_set_history += self.current_round_history
            self.current_round_history = []
            print("P1 wins round %r" % (round_win_state))


        set_win_state = self.prev_set_winner(current_state)
        
        if set_win_state != WinState.NO_WIN:
            self.write_set_win(set_win_state)
            print("P1 wins set %r" % (set_win_state))

        self.previous_state = current_state
    
    #Due to implementation, sets are only recorded once the next one starts. So we'll need to manually record the last set
    def final_write(self):
        print("writing last set")
        set_win_state = WinState.P1_WIN
        if self.previous_state.p1.health < self.previous_state.p2.health:
            set_win_state = WinState.P2_WIN
        print("winner is: %r" % (set_win_state))
        self.write_set_win(set_win_state)
