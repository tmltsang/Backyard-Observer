import sys
sys.path.insert(0, '.')

import cv2
from vision import Vision
import argparse

#Assuming we run this in the root of the directory
parser = argparse.ArgumentParser(description='Split a video into frames')
parser.add_argument('path', metavar='path', type=str, nargs='+',
                    help='list of video paths')

parser.add_argument('--output_path', default='training/images', nargs='?', help='path to store frames after split')
args = parser.parse_args()

#Look for frames with testament's portrait as that will be part of the game
testament_portrait = Vision("helper/Chara_TST.png")
for path in args.path:
    capture = cv2.VideoCapture(path)
    frameNr = 0
    while (True):
        success, frame = capture.read()
        if success:
            rects = testament_portrait.find(frame)
            output_img = testament_portrait.draw_rectangles(frame, rects)
            cv2.imshow("test", output_img)
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break
            #cv2.imwrite(f'{args.output_path.rstrip("/")}/frame_{frameNr}.jpg', frame)
        else:
            break
        frameNr = frameNr+1
    capture.release()