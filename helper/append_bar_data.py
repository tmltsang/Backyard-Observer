import cv2
from ultralytics import YOLO
import argparse
import os

parser = argparse.ArgumentParser(description='Apply model to existing images')
parser.add_argument('path', default='training/train/images', nargs='?', help='path with existing images')
#Argument that allows an alternate mode, to verify the images with a currently trained model
parser.add_argument('--output_path_labels', default='training/train_bar/labels', nargs='?', help='path to store labels after split (only works with --use_model)')

args = parser.parse_args()

model = YOLO("runs/detect/bar_batch_14/weights/best.pt")
all_image_names = sorted(os.listdir(f"{args.path}"))
for image_name in all_image_names:
    results = model(f"{args.path}/{image_name}")
    results[0] = results[0].cuda()
    annotated_frame = results[0].plot()
    print(results[0].boxes)
    cv2.imshow("annonatated_frame", annotated_frame)
    file_name = image_name.split('.jpg')[0]
    label_path = f"{args.output_path_labels}/{file_name}.txt"
    f = open(label_path, 'w')
    for i, cls in enumerate(results[0].boxes.cls):
        current_box_coords = ' '.join(str(x) for x in results[0].boxes.xywhn[i].tolist())
        print(current_box_coords)
        f.write(f'{int(cls)} {current_box_coords}\n')
    f.close()