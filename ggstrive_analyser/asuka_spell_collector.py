from config import Config
from vision_model import VisionModel
from collector import Collector
import cv2

import numpy as np

class AsukaSpellCollector(Collector):
    asukas: dict
    opponent: str
    previous_spells: list

    def __init__(self, players:dict, asukas: dict):
        self.vision_model = VisionModel(Config.get('asuka_model_path'))
        self.asukas = asukas
        if Config.P1 in asukas:
            self.opponent = players[Config.P2]
        else:
            self.opponent = players[Config.P1]
        self.bar_cls_dict = None
        self.previous_spells = None

    def read_frame(self, frame):
        results = self.vision_model.model.predict(frame, conf=0.5, verbose=False)
        resultsCpu = results[0].cpu()

        #results.pandas().xyxy[0].sort_values('xmin')
        #annotated_frame = results[0].plot()
        #cv2.imshow("main", annotated_frame)
        if self.bar_cls_dict == None:
            self.bar_cls_dict = results[0].names
        spell_cls = resultsCpu.boxes.cls.numpy()
        spell_xywhn = resultsCpu.boxes.xywhn.numpy()
        #Get the indexes of the sorted list
        if len(spell_cls) == Config.ASUKA_SPELL_COUNT * len(self.asukas):
            sorted_spells = np.argsort(spell_xywhn[:,0])
            named_spells = []
            bar_cls_dict = results[0].names
            for sorted_index in sorted_spells:
                named_spells.append(bar_cls_dict[spell_cls[sorted_index]])
            spell_state = {}
            #Assuming that asukas will always be in the order ["p1", "p2"]
            for player in self.asukas:
                spell_state[player] = {"opponent": self.opponent}
                for i, spell in list(enumerate(named_spells[:4])):
                    spell_state[player][f"asuka_spell_{i+1}"] = spell
                del named_spells[:4]
            self.previous_spells = spell_state
            return spell_state
        else:
            return self.previous_spells
        #found_cls = self.convert_class_to_name(resultsCpu.boxes.cls.numpy(), resultsCpu.boxes.xywhn.numpy(), self.bar_cls_dict)

