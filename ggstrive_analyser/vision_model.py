from ultralytics import YOLO

# class Singleton:
#     def __init__(self, cls):
#         self._cls = cls

#     def Instance(self):
#         try:
#             return self._instance
#         except AttributeError:
#             self._instance = self._cls()
#             return self._instance

#     def __call__(self):
#         raise TypeError('Singletons must be accessed through `Instance()`.')

#     def __instancecheck__(self, inst):
#         return isinstance(inst, self._cls)
# @multiton
# class VisionModel:
#     def __init__(self, model_path):
#         self.id = model_path
#         self.model = YOLO(model_path)

class BarVisionModel:
   def __init__(self):
      self.model = YOLO('runs/detect/bar_batch_updated_combo4/weights/best.pt')
