from abc import ABC, abstractmethod
import os
import csv
import json
from win_state import WinState
from game_state import GameState
from config import Config

class DataRecorder(ABC):
    @abstractmethod
    def write(self, data: dict, round_win_state: WinState, set_win_state: WinState):
        pass

class CSVDataRecorder(DataRecorder):
    filename: str
    fields: list
    current_round_history: list
    current_set_history: list
    round_win_field: str
    set_win_field: str
    round_mode: bool

    def __init__(self, filename: str, fields: list, round_win_field: str, set_win_field: str = ""):
        super().__init__()
        self.filename = filename
        self.fields = fields
        self.current_round_history = []
        self.current_set_history = []
        self.round_win_field = round_win_field
        self.round_mode = True
        if set_win_field:
            self.round_mode = False
            self.set_win_field = set_win_field

        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fields)

    def __record_round_win(self, p1_round_win: bool):
        for row in self.current_round_history:
            row[self.round_win_field] = p1_round_win

    def __record_set_win(self, p1_set_win: bool):
        for row in self.current_set_history:
            row[self.set_win_field] = p1_set_win

    def write_round_win(self, round_win_state: WinState):
        self.__record_round_win(round_win_state == WinState.P1_WIN)
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fields)
            writer.writerows(self.current_round_history)
        self.current_round_history = []

    def write_set_win(self, set_win_state: WinState):
        self.__record_round_win(set_win_state == WinState.P1_WIN)
        self.current_set_history += self.current_round_history
        self.__record_set_win(set_win_state == WinState.P1_WIN)
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fields)
            writer.writerows(self.current_set_history)
        self.current_round_history = []
        self.current_set_history = []

    def write(self, data: dict, round_win_state: WinState, set_win_state: WinState = WinState.NO_WIN):
        self.current_round_history.append(data)
        if round_win_state != WinState.NO_WIN:
            if self.round_mode:
                self.write_round_win(round_win_state)
            else:
                self.__record_round_win(round_win_state == WinState.P1_WIN)
                self.current_set_history += self.current_round_history
            self.current_round_history = []
            #print("P1 wins round %r" % (current_state.win_state))

        if not self.round_mode:
            if set_win_state != WinState.NO_WIN:
                self.write_set_win(set_win_state)

    #Flushes the set_history in case it was never written
    def final_write(self, win_state: WinState):
        print("writing last set")
        print("winner is: %r" % (win_state))
        if self.round_mode:
            self.write_round_win(win_state)
        else:
            self.write_set_win(win_state)

class JSONDataRecorder(DataRecorder):
    filename: str

    def __init__(self, filename):
        self.filename = filename
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

    def write(self, data: dict, round_win_state: WinState = WinState.NO_WIN, set_win_state: WinState = WinState.NO_WIN):
        with open(self.filename, 'w') as file:
            json.dump(data, file)