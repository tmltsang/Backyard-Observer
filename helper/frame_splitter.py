import sys
sys.path.insert(0, '.')

import cv2
import argparse
import random
from pathlib import Path
from ultralytics import YOLO

#Assuming we run this in the root of the directory
parser = argparse.ArgumentParser(description='Split a video into frames')
parser.add_argument('path', metavar='path', type=str, nargs='+',
                    help='list of video paths')

parser.add_argument('--output_path', default='training/images', nargs='?', help='path to store frames after split')
#Argument that allows an alternate mode, to verify the images with a currently trained model
parser.add_argument('--use_model', nargs='?', help='Path to model to be used')
parser.add_argument('--output_path_labels', default='training/images', nargs='?', help='path to store labels after split (only works with --use_model)')
parser.add_argument('--full_split', action=argparse.BooleanOptionalAction)

args = parser.parse_args()

#Look for frames with testament's portrait as that will be part of a match
#testament_portrait = Vision("helper/Chara_TST.png", threshold=0.9, scale_percent=33)

random.seed(42)
use_model = args.use_model is not None
model = None
if use_model:
    model = YOLO(args.use_model)

for path in args.path:
    print(path)
    capture = cv2.VideoCapture(path)
    total_frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    random_frames = random.sample(range(0, int(total_frames)), 3)
    if args.full_split:
        random_frames = range(0, int(total_frames))
    for frame_num in random_frames:
        capture.set(cv2.CAP_PROP_POS_FRAMES,frame_num)
        success, frame = capture.read()
        if success:
            #rects = testament_portrait.find(frame)
            if use_model:
                results = model(frame)
                results[0] = results[0].cuda()
                annotated_frame = results[0].plot()
                print(results[0].boxes)
                cv2.imshow("annonatated_frame", annotated_frame)
                label_path = f'{args.output_path_labels.rstrip("/")}/{Path(path).stem}_frame_{frame_num}.txt'
                print(label_path)
                f = open(label_path, 'w')
                for i, cls in enumerate(results[0].boxes.cls):
                    current_box_coords = ' '.join(str(x) for x in results[0].boxes.xywhn[i].tolist())
                    print(current_box_coords)
                    f.write(f'{int(cls)} {current_box_coords}\n')
                f.close()
            print(f'{args.output_path.rstrip("/")}/{Path(path).stem}_frame_{frame_num}.jpg')
            cv2.imwrite(f'{args.output_path.rstrip("/")}/{Path(path).stem}_frame_{frame_num}.jpg', frame)
            #cv2.imshow("test", frame)
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break
        else:
            break
        #frameNr = frameNr+1
    capture.release()