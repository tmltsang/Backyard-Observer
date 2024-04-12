from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO('runs/detect/asuka_with_no_mana2/weights/best.pt')
capture = cv2.VideoCapture('training/videos/gg_matches/completed/asuka_chaos_1.mkv')
if (capture.isOpened() == False):
    print("Error opening file")
framecount = 0
while(capture.isOpened()):
    ret, frame = capture.read()
    if framecount % 5 == 0:
        if ret:
            results = model.predict(frame, conf=0.5, verbose=False)
            resultsCpu = results[0].cpu()
            annotated_frame = results[0].plot()
            spell_cls = resultsCpu.boxes.cls.numpy()
            spell_xywhn = resultsCpu.boxes.xywhn.numpy()
            #Get the indexes of the sorted list
            sorted_spells = np.argsort(spell_xywhn[:,0])
            named_spell = []
            bar_cls_dict = results[0].names
            for sorted_index in sorted_spells:
                named_spell.append(bar_cls_dict[spell_cls[sorted_index]])
            print(named_spell)
            cv2.imshow("main", annotated_frame)
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break
        else:
            break
    # When everything done, release the video capture object
    framecount += 1
capture.release()
cv2.destroyAllWindows()