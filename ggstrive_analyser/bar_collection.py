import cv2
from collections import defaultdict
from time import time
from player_state import PlayerState
from copy import deepcopy
from vision_model import BarVisionModel
from game_state import GameState
from win_state import WinState
from config import Config

class BarCollector:
    new_round: bool
    round_end: bool
    between_round: bool
    init_bars: dict
    frameCount: int
    previous: GameState
    bar_cls_dict: dict
    ui_on_screen: dict
    frame_rate: int
    p1_name: str
    p2_name: str
    cfg: Config
    bar_vision_model: BarVisionModel

    def __init__(self, cfg: Config, frame_rate: int, p1_name: str, p2_name: str):
        self.new_round = False
        self.round_end = False
        self.between_round = True
        self.init_bars = {}
        self.init_bars["healthbar"] = {}
        self.init_bars["empty_tension"] = {}
        self.init_bars["empty_risc"] = {}
        self.init_bars["full_burst"] = {}
        self.frame_count = 0
        self.p1_name = p1_name
        self.p2_name = p2_name
        self.previous = GameState(0, PlayerState(name=p1_name), PlayerState(name=p2_name))
        self.bar_cls_dict = None
        self.ui_on_screen = {"p1": {"just": False, "punish": False, "counter": False, "reversal": False}, "p2":{"just": False, "punish": False, "counter": False, "reversal": False}}
        self.frame_rate = frame_rate

        self.bar_vision_model = BarVisionModel()
        self.cfg = cfg

    def __convert_class_to_name(self, boxes_cls, xywhn, bar_cls_dict):
        found_cls = defaultdict(list)
        for i, cls in enumerate(boxes_cls):
            found_cls[bar_cls_dict[cls]].append(xywhn[i])
        return found_cls

    def __is_p1_side(self, xywhn):
        return xywhn[0] < 0.5

    #Special case for the counter text as that can appear in the middle
    #It is assumed that only one character will be 'damaged' at the current time and the other player will be given the counter
    #However there is a rare case that the characters trade damage, in that case it is attributed to p1
    def __is_p1_side_counter(self, xywhn, p1_curr_damaged):
        if xywhn[2] > 0.5:
            return not p1_curr_damaged
        else:
            return self.__is_p1_side(xywhn)

    def __bar_clamp(self, bar_amount):
        return max(min(bar_amount, 1),0)

    def __get_last_p1_health(self):
        return self.previous.p1.health

    def __get_last_p2_health(self):
        return self.previous.p2.health

    def __tension_gear_check(self, tension_amount, tension_gear):
        if tension_gear == 2:
            # Return max tension if there are 2 gears
            return 1
        max_tension = 0
        if tension_gear < 2:
            max_tension = ((1 + tension_gear) * 0.5) - 0.01
        return min(max_tension, tension_amount)
    
    def __create_last_round_state(self, win_state: WinState):
        last_of_round = deepcopy(self.previous)
        last_of_round.win_state = win_state
        if win_state == WinState.P1_WIN:
            last_of_round.p2.health = 0
        else:
            last_of_round.p1.health = 0
        print(f'{self.p1_name}_{self.p2_name}: Round_finished: {win_state}')
        return last_of_round

    def __record_bar_values(self, found_cls):
    #Should see both health bars during a game, but default to previous value if can't be seen
        p1_health = self.__get_last_p1_health()
        p2_health = self.__get_last_p2_health()
        for health_bar in found_cls["healthbar"]:
            if self.__is_p1_side(health_bar):
                p1_health = self.__bar_clamp(float(health_bar[2]/self.init_bars["healthbar"]["p1"]))
            else:
                p2_health = self.__bar_clamp(float(health_bar[2]/self.init_bars["healthbar"]["p2"]))

        #Get Tension
        p1_tension = self.previous.p1.tension
        p2_tension = self.previous.p2.tension
        p1_tension_gear = 0
        p2_tension_gear = 0

        for tension_gear in found_cls["tension_gears"]:
            if self.__is_p1_side(tension_gear):
                p1_tension_gear += 1
            else:
                p2_tension_gear += 1

        for empty_tension in found_cls["empty_tension"]:
            if self.__is_p1_side(empty_tension):
                p1_tension = self.__bar_clamp(self.__tension_gear_check(1 - float(empty_tension[2]/self.init_bars["empty_tension"]["p1"]), p1_tension_gear))
            else:
                p2_tension = self.__bar_clamp(self.__tension_gear_check(1 - float(empty_tension[2]/self.init_bars["empty_tension"]["p2"]), p2_tension_gear))
        #Get Risc
        p1_risc = self.previous.p1.risc
        p2_risc = self.previous.p2.risc
        for empty_risc in found_cls["empty_risc"]:
            if self.__is_p1_side(empty_risc):
                p1_risc = self.__bar_clamp(1 - float(empty_risc[2]/self.init_bars["empty_risc"]["p1"]))
            else:
                p2_risc = self.__bar_clamp(1 - float(empty_risc[2]/self.init_bars["empty_risc"]["p2"]))
        #Get Burst
        p1_burst = self.previous.p1.burst
        p2_burst = self.previous.p2.burst
        for burst in found_cls["burst"]:
            if self.__is_p1_side(burst):
                p1_burst = self.__bar_clamp(float(burst[2]/self.init_bars["full_burst"]["p1"]))
            else:
                p2_burst = self.__bar_clamp(float(burst[2]/self.init_bars["full_burst"]["p2"]))
        for full_burst in found_cls["full_burst"]:
            if self.__is_p1_side(full_burst):
                p1_burst = 1.0
            else:
                p2_burst = 1.0

        p1_curr_damaged = False
        p2_curr_damaged = False
        for curr_damaged in found_cls["health_lost"]:
            if self.__is_p1_side(curr_damaged):
                p1_curr_damaged = True
            else:
                p2_curr_damaged = True

        p1_ui_counts = {}
        p2_ui_counts = {}
        for ui_text in self.ui_on_screen["p1"]:
            p1_ui_counts[ui_text] = getattr(self.previous.p1, ui_text)
            p2_ui_counts[ui_text] = getattr(self.previous.p2, ui_text)
            p1_ui_seen = False
            p2_ui_seen = False
            for ui in found_cls[ui_text]:
                is_p1_side: bool
                #The counter text has the special case where it can be in the middle of the screen
                if ui_text == "counter":
                    is_p1_side = self.__is_p1_side_counter(ui, p1_curr_damaged)
                else:
                    is_p1_side = self.__is_p1_side(ui)
                if is_p1_side:
                    if not self.ui_on_screen["p1"][ui_text]:
                        p1_ui_counts[ui_text] += 1
                    p1_ui_seen = True
                else:
                    if not self.ui_on_screen["p2"][ui_text]:
                        p2_ui_counts[ui_text] += 1
                    p2_ui_seen = True
            self.ui_on_screen["p1"][ui_text] = p1_ui_seen
            self.ui_on_screen["p2"][ui_text] = p2_ui_seen

        p1 = PlayerState(name = self.p1_name, health = p1_health, tension = p1_tension, burst = p1_burst, risc = p1_risc, curr_damaged = p1_curr_damaged,
                            counter = p1_ui_counts["counter"], reversal = p1_ui_counts["reversal"], punish = p1_ui_counts["punish"],
                            just = p1_ui_counts["just"])

        p2 = PlayerState(name = self.p2_name, health = p2_health, tension = p2_tension, burst = p2_burst, risc = p2_risc, curr_damaged = p2_curr_damaged,
                         counter = p2_ui_counts["counter"], reversal = p2_ui_counts["reversal"], punish = p2_ui_counts["punish"],
                         just = p2_ui_counts["just"])
        # for ui_text, is_on_screen in self.ui_on_screen.keys():
        #     for ui in found_cls[ui_text]:
        #         if self.__is_p1_side(ui):
        current_state = GameState((self.cfg.get("num_frames") * self.frame_count)/self.frame_rate, WinState.NO_WIN, p1, p2)
        #self.previous = current_state
        return current_state

    def read_frame(self, frame) -> GameState:
        self.frame_count += 1
        results = self.bar_vision_model.model.predict(frame, conf=0.6, imgsz=(640, 768), verbose=False)
        resultsCpu = results[0].cpu()
        annotated_frame = results[0].plot()
        cv2.imshow("main", annotated_frame)
        if self.bar_cls_dict == None:
            self.bar_cls_dict = results[0].names

        found_cls = self.__convert_class_to_name(resultsCpu.boxes.cls.numpy(), resultsCpu.boxes.xywhn.numpy(), self.bar_cls_dict)
        #cv2.imshow("main", annotated_frame)
        if "round_start" in found_cls.keys():
            #Only possible if it never determined a winner, at the start of next round, base it off of last known health values
            self.new_round = True
            self.between_round = False
            if self.round_end:
                if self.__get_last_p1_health() > self.__get_last_p2_health():
                    win_state = WinState.P1_WIN
                else:
                    win_state = WinState.P2_WIN
                self.round_end = False
                return self.__create_last_round_state(win_state)

        elif ("slash" in found_cls.keys() or "perfect" in found_cls.keys()) and not self.between_round:
            self.round_end = True
            win_state = WinState.NO_WIN
            if "perfect" in found_cls.keys():
                #Should only be a single healthbar left
                if self.__get_last_p1_health() > self.__get_last_p2_health():
                    win_state = WinState.P1_WIN
                    print(f'{self.p1_name}_{self.p2_name}: P1 Wins Round with perfect')
                else:
                    win_state = WinState.P2_WIN
                    print(f'{self.p1_name}_{self.p2_name}: P2 Wins Round with perfect')
            else:
                if "slash_p1" in found_cls.keys():
                    win_state = WinState.P1_WIN
                elif "slash_p2" in found_cls.keys():
                    win_state = WinState.P2_WIN
            if win_state != win_state.NO_WIN:
                self.round_end = False
                self.between_round = True
                return self.__create_last_round_state(win_state)

        else:
            p1_curr_round_count = self.previous.p1.round_count
            p2_curr_round_count = self.previous.p2.round_count

            if self.new_round and len(found_cls["heart_lost"]) + len(found_cls["heart"]) == 4 and\
                len(found_cls["healthbar"]) == 2 and \
                len(found_cls["empty_risc"]) == 2 and \
                len(found_cls["empty_tension"]) == 2:
                #Round start image has just disappeared, initialise for new round
                #Determine if new set
                for bar_name in self.init_bars.keys():
                    for bar in found_cls[bar_name]:
                        if self.__is_p1_side(bar):
                            self.init_bars[bar_name]["p1"] = bar[2]
                            #print(f'P1 %s bar init to value %f' % (bar_name, self.init_bars[bar_name]["p1"]))
                        else:
                            self.init_bars[bar_name]["p2"] = bar[2]
                            #print(f'P2 %s bar init to value %f' % (bar_name, self.init_bars[bar_name]["p2"]))
                p1_curr_round_count = 0
                p2_curr_round_count = 0

                #Hacky solution to reset the ui_text counters
                self.previous.p1.counter = 0
                self.previous.p2.counter = 0

                self.previous.p1.just = 0
                self.previous.p2.just = 0

                self.previous.p1.punish = 0
                self.previous.p2.punish = 0

                self.previous.p1.reversal = 0
                self.previous.p2.reversal = 0

                for heart_lost in found_cls["heart_lost"]:
                    if self.__is_p1_side(heart_lost):
                        p2_curr_round_count += 1
                    else:
                        p1_curr_round_count += 1

                self.new_round = False
                self.frame_count = 0
            if not self.new_round and not self.round_end and not self.between_round and 0 < len(found_cls["healthbar"]) <= 2:
                current_state = self.__record_bar_values(found_cls)
                current_state.p1.round_count = p1_curr_round_count
                current_state.p2.round_count = p2_curr_round_count
                #print("%d %d" % (p1_curr_round_count, p2_curr_round_count))
                self.previous = current_state
                return current_state
        # if self.round_end and len(found_cls["p1_slash"]) > 0 or len(found_cls["p2_slash"]) > 0:
        #     self.round_end = False
        #     self.between_round = True
        #     #Should only be a single healthbar left
        #     if self.__get_last_p1_health() != 0 and self.__get_last_p2_health() != 0:
        #         last_of_round = self.previous
        #         last_of_round.round_end = True
        #         if self.__is_p1_side(found_cls["healthbar"][0]):
        #             last_of_round.p2.health = 0
        #             last_of_round.win_state = WinState.P1_WIN
        #             print(f'P1 Wins Round with final Health: %f' % self.__get_last_p1_health())
        #             return last_of_round
        #         else:
        #             last_of_round.p1.health = 0
        #             last_of_round.win_state = WinState.P2_WIN
        #             print(f'P2 Wins Round with final Health: %f' % self.__get_last_p2_health())
        #             return last_of_round

        return None
