from ultralytics import YOLO

# Load a model
#model = YOLO('yolov8l.pt')
#model = YOLO('../runs/detect/bar_batch_1280_imgsz5/weights/best.pt')  # build a new model from scratch
#model = YOLO('../runs/detect/asuka_with_no_mana/weights/best.pt')  # load a pretrained model (recommended for training)
model = YOLO('../runs/detect/bar_batch_updated_combo4/weights/best.pt')

# Use the model
if __name__ == '__main__':
    results = model.train(data='data_bars.yaml', imgsz=768, epochs=500, save=True, save_period=20, cache=True, batch=6, device=0, pretrained=True, patience=20, name='bar_batch')  # train the model