from ultralytics import YOLO
from abc import ABC, abstractmethod
from config import Config

class VisionModel():
   model: YOLO
   def __init__(self, model_path):
      self.model = YOLO(model_path)
