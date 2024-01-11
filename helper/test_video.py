from ultralytics import YOLO
import cv2

model = YOLO('runs/detect/bar_batch_36/weights/best.pt')
capture = cv2.VideoCapture('training/videos/testament_anji_1.mp4')
if (capture.isOpened() == False):
    print("Error opening file")

while(capture.isOpened()):
    ret, frame = capture.read()
    if ret:
        results = model.predict(frame, conf=0.5, agnostic_nms=True)
        annotated_frame = results[0].plot()
        cv2.imshow("main", annotated_frame)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break
    else:
        break
    # When everything done, release the video capture object
capture.release()
cv2.destroyAllWindows()