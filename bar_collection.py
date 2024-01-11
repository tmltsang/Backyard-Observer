import cv2
import csv
from collections import defaultdict
from time import time
from ultralytics import YOLO
import numpy as np
from player_state import PlayerState

def convert_class_to_name(boxes_cls, xywhn, bar_cls_dict):
    found_cls = defaultdict(list)
    for i, cls in enumerate(boxes_cls):
        found_cls[bar_cls_dict[cls]].append(xywhn[i])
    return found_cls

def is_p1_side(xywhn):
    return xywhn[0] < 0.5

def get_last_p1_health(current_round_history):
    return current_round_history[-1]['p1_health']

def get_last_p2_health(current_round_history):
    return current_round_history[-1]['p2_health']
    
def set_round_win(current_round_history, p1_round_win):
    for row in current_round_history:
        row['p1_round_win'] = p1_round_win
    return current_round_history

def set_set_win(current_set_history, p1_set_win):
    for row in current_set_history:
        row['p1_set_win'] = p1_set_win
    return current_set_history


bar_cls_dict = None
model = YOLO('runs/detect/bar_batch_x_768_imgsz/weights/best.pt')
capture = cv2.VideoCapture('training/videos/testament_anji_1.mp4')
fields = ['p1_health', 'p2_health', 'p1_round_win', 'p1_set_win']

#Initialise csv file
filename = 'gg.csv'
with open(filename, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fields)

# reader = easyocr.Reader(['en'], gpu='cuda:0')
if (capture.isOpened() == False):
    print("Error opening file")
counter = 0
new_round = False
round_end = False

p1_round_win = 0
p1_curr_round_win = 0
p1_set_win = 0
p2_round_win = 0
p2_curr_round_win = 0
p2_set_win = 0

p1_health_bar_total = 0.0
p2_health_bar_total = 0.0

#p1_health_bar_history = []
#p2_health_bar_history = []
frameCount = 0
current_round_history = []
current_set_history = []
while(capture.isOpened()):
    ret, frame = capture.read()
    if ret:
        if frameCount % 2 == 0:
            results = model.predict(frame, conf=0.5, imgsz=(640, 768), verbose=False)
            resultsCpu = results[0].cpu()
            annotated_frame = results[0].plot()
            if bar_cls_dict == None:
                bar_cls_dict = results[0].names
            
            found_cls = convert_class_to_name(resultsCpu.boxes.cls.numpy(), resultsCpu.boxes.xywhn.numpy(), bar_cls_dict)
            cv2.imshow("main", annotated_frame) 
            if "round_start" in found_cls.keys():
                new_round = True
                round_end = False
            elif "slash" in found_cls.keys():
                round_end = True
            else:
                if new_round and len(found_cls["heart_lost"]) + len(found_cls["heart"]) == 4 and len(found_cls["healthbar"]) == 2:
                    #Round start image has just disappeared, initialise for new round
                    #Determine if new set
                    for health_bar in found_cls["healthbar"]:
                        if is_p1_side(health_bar):
                            p1_health_bar_total = health_bar[2]
                            print(f'p1healthtotal: %f' % p1_health_bar_total)
                        else:
                            p2_health_bar_total = health_bar[2]
                            print(f'p2healthtotal: %f' % p2_health_bar_total)
                    if len(found_cls["heart"]) == 4:
                        #If there are no round wins and its a new set, then it's the first round
                        p1_set_win = False
                        if p1_curr_round_win + p2_curr_round_win != 0:
                            #determine who won last round and assign set win
                            if get_last_p1_health(current_round_history) < get_last_p2_health(current_round_history):
                                p2_set_win += 1
                                p2_curr_round_win += 1
                                p1_set_win = False
                            else: 
                                p1_set_win += 1
                                p1_curr_round_win += 1
                                p1_set_win = True
                            p1_round_win += p1_curr_round_win
                            p2_round_win += p2_curr_round_win
                            current_set_history += set_round_win(current_round_history, p1_set_win)
                            current_round_history = set_set_win(current_set_history, p1_set_win)

                            print("P1 Round Wins: %d, Set Wins: %d, P2 Round Wins: %d, Set Wins %d" % (p1_round_win, p1_set_win, p2_round_win, p2_set_win))

                            with open(filename, 'a') as csvfile:
                                writer = csv.DictWriter(csvfile, fieldnames=fields)
                                writer.writerows(current_set_history)

                            current_round_history = []
                            current_set_history = []
                    else:
                        p2_curr_round_win = 0
                        p1_curr_round_win = 0
                        p1_round_win = False
                        for heart_lost in found_cls["heart_lost"]:
                            if is_p1_side(heart_lost):
                                p2_curr_round_win += 1
                                p1_round_win = False
                            else:
                                p1_curr_round_win += 1
                                p1_round_win = True
                        current_set_history += set_round_win(current_round_history, p1_round_win)
                        current_round_history = []
                        print("P1 Round Wins: %d, P2 Round Wins: %d" % (p1_curr_round_win, p2_curr_round_win))
                    new_round = False
                elif not new_round and not round_end and 0 < len(found_cls["healthbar"]) <= 2:
                    #Should see both health bars during a game, but default to previous value if can't be seen
                    p1_health = get_last_p1_health(current_round_history) if len(current_round_history) > 0 else 1
                    p2_health = get_last_p2_health(current_round_history) if len(current_round_history) > 0 else 1
                    for health_bar in found_cls["healthbar"]:
                        if is_p1_side(health_bar):
                            p1_health = float(health_bar[2]/p1_health_bar_total)
                        else:
                            p2_health = float(health_bar[2]/p2_health_bar_total)
                    current_round_history.append({'p1_health': p1_health, 'p2_health':p2_health})
            if round_end and len(found_cls["healthbar"]) == 1:
                #Should only be a single healthbar left
                if get_last_p1_health(current_round_history) != 0 and get_last_p2_health(current_round_history) != 0:
                    if is_p1_side(found_cls["healthbar"][0]):
                        current_round_history.append({'p1_health': get_last_p1_health(current_round_history), 'p2_health': 0})
                        print(f'P1 Wins Round with final Health: %f' % get_last_p1_health(current_round_history))
                    else:
                        current_round_history.append({'p1_health': 0, 'p2_health': get_last_p2_health(current_round_history)})
                        print(f'P2 Wins Round with final Health: %f' % get_last_p2_health(current_round_history))
                round_end = False
        frameCount += 1
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break
    else:
        break

#Determine winner of final set
if  get_last_p1_health(current_round_history) <  get_last_p2_health(current_round_history):
    p2_set_win += 1
    p2_curr_round_win += 1
else: 
    p1_set_win += 1
    p1_curr_round_win += 1
p1_round_win += p1_curr_round_win
p2_round_win += p2_curr_round_win
current_set_history += set_round_win(current_round_history, p1_set_win)
current_round_history = set_set_win(current_set_history, p1_set_win)

print("P1 Round Wins: %d, Set Wins: %d, P2 Round Wins: %d, Set Wins %d" % (p1_round_win, p1_set_win, p2_round_win, p2_set_win))

with open(filename, 'a') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writerows(current_set_history)

current_round_history = []
current_set_history = []

capture.release()