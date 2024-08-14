from asuka_spell_collector import AsukaSpellCollector
from data_recorder import CSVDataRecorder, JSONDataRecorder
from typing import List, Dict, Set
from game_state import GameState
from config import Config
from win_state import WinState
from collections import defaultdict
from tournament_index_manager import TournamentIndexManager

class AsukaManager:
    asuka_spell_collector: AsukaSpellCollector
    asuka_csv_data_recorders: Dict[str, CSVDataRecorder]
    spell_data_recorder: JSONDataRecorder
    players: Dict[str, str]
    asukas: List[str]
    round_spells: Dict[str, Set[str]]
    total_spells: Dict[str, Dict[str, int]]

    def __init__(self, players: Dict[str, str], asukas: List[str]):
        self.asuka_spell_collector = AsukaSpellCollector(players, asukas)
        self.players = players
        self.asukas = asukas
        self.total_spells = defaultdict(lambda: defaultdict(int))
        self.round_spells = defaultdict(set)

    def create_data_recorders(self, video_name: str):
        self.asuka_csv_data_recorders = {}
        for player in self.asukas:
            self.asuka_csv_data_recorders[player] = CSVDataRecorder(filename=f'{Config.get("csv_path")}/spell/{video_name}_{player}.csv',
                                                    fields=Config.get("asuka_csv_fields"),
                                                    round_win_field=Config.get('asuka_win_field'))

        self.spell_data_recorder = JSONDataRecorder(filename=f'{Config.get("csv_path")}/spell/{video_name}.json')
    #For all intents and purposes P1.WIN == Asuka win so if Asuka wins in P2, the state has to be P1.Win
    def determine_asuka_winner(self, asuka_player: str, curr_win_state: WinState):
        if curr_win_state != WinState.NO_WIN:
            if asuka_player == Config.P2:
                return WinState.P1_WIN if curr_win_state == WinState.P2_WIN else WinState.P2_WIN
            else:
                return curr_win_state
        else:
            return curr_win_state

    def write(self, current_state: GameState, asuka_spells: dict, tournament_index_manager: TournamentIndexManager = None):
        for player in asuka_spells:
            round_win_state = self.determine_asuka_winner(player, current_state.round_win_state)
            asuka_spells[player]['time'] = current_state.time
            asuka_spells[player]['player_side'] = player
            self.asuka_csv_data_recorders[player].write(asuka_spells[player], round_win_state, tournament_index_manager=tournament_index_manager)

            self.round_spells[player].update([value for (key, value) in asuka_spells[player].items() if 'asuka_spell' in key.lower()])
            #End of round, report what spells were seen
            if round_win_state != WinState.NO_WIN:
                for spell in self.round_spells[player]:
                    self.total_spells[spell]['seen'] += 1
                    if round_win_state == WinState.P1_WIN:
                        self.total_spells[spell]['win'] += 1
                self.write_spells()

    def final_write(self, win_state: WinState):
        for player in self.asukas:
            if len(self.asuka_csv_data_recorders[player].current_round_history) > 0:
                self.asuka_csv_data_recorders[player].final_write(self.determine_asuka_winner(player, win_state))

    def write_spells(self):
        self.spell_data_recorder.write(self.total_spells)
