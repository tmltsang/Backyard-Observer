import cv2
import torch
from vision import Vision
from time import time
from ultralytics import YOLO


def main():
    model = YOLO('runs/detect/train/weights/best.pt')
    capture = cv2.VideoCapture('testament_vs_hc.mp4')

    if (capture.isOpened() == False):
        print("Error opening file")

    while(capture.isOpened()):
        ret, frame = capture.read()
        if ret:
            results = model(frame)
            results[0] = results[0].cuda()
            annotated_frame = results[0].plot()

            cv2.imshow("YOLOv8 Inference", annotated_frame)
            #cv.imshow('Matches', output_img)
            #print('FPS {}'.format(1 / (time() - loop_time)))
            loop_time = time()
            #if (len(rects) > 0):
            #    cv.imwrite('debug/result' + str(time()) + '.jpg', output_img)

            # press 'q' with the output window focused to exit.
            # waits 1 ms every loop to process key presses
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break
        else:
            break
    # When everything done, release the video capture object
    capture.release()

    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
