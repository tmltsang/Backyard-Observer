from abc import ABC, abstractmethod
from vision_model import VisionModel
from collections import defaultdict

class Collector(ABC):
    vision_model: VisionModel 
    bar_cls_dict: dict

    def convert_class_to_name(self, boxes_cls, xywhn, bar_cls_dict):
        found_cls = defaultdict(list)
        for i, cls in enumerate(boxes_cls):
            found_cls[bar_cls_dict[cls]].append(xywhn[i])
        return found_cls

    def is_p1_side(self, xywhn):
        return xywhn[0] < 0.5

    @abstractmethod
    def read_frame(self, frame):
        pass