import cv2
import csv
from os import listdir
from os.path import isfile, join
from pathlib import Path
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

def tension_gear_check(tension_amount, tension_gear):
    if tension_gear == 2:
        # Return max tension if there are 2 gears
        return 1
    max_tension = 0
    if tension_gear < 2:
        max_tension = ((1 + tension_gear) * 0.5) - 0.01
    return min(max_tension, tension_amount)

def bar_clamp(bar_amount):
    return max(min(bar_amount, 1),0)
    

def set_round_win(current_round_history, p1_round_win):
    for row in current_round_history:
        row['p1_round_win'] = p1_round_win
    return current_round_history

def set_set_win(current_set_history, p1_set_win):
    for row in current_set_history:
        row['p1_set_win'] = p1_set_win
    return current_set_history

video_path = 'training/videos'
training_vid_list = [f for f in listdir(video_path) if isfile(join(video_path, f))]
print(training_vid_list)
model = YOLO('runs/detect/bar_batch_x_768_imgsz/weights/best.pt')
for video in training_vid_list:
    capture = cv2.VideoCapture(video_path + "/" + video)
    bar_cls_dict = None
    fields = ['frame', 'p1_health', 'p2_health', 'p1_tension', 'p2_tension', 'p1_burst', 'p2_burst', 'p1_risc', 'p2_risc', 'p1_round_count', 'p2_round_count','p1_round_win', 'p1_set_win']

    #Initialise csv file
    filename = "csv/" + Path(video).stem + ".csv"
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)

    # reader = easyocr.Reader(['en'], gpu='cuda:0')
    if (capture.isOpened() == False):
        print("Error opening file")
    counter = 0
    new_round = False
    round_end = False
    between_round = True

    p1_round_win = 0
    p1_curr_round_win = 0
    p1_set_win = 0
    p2_round_win = 0
    p2_curr_round_win = 0
    p2_set_win = 0

    # p1_health_bar_total = 0.0
    # p2_health_bar_total = 0.0

    # p1_tension_bar_total = 0.0
    # p2_tension_bar_total = 0.0

    # p1_burst_bar_total = 0.0
    # p2_burst_bar_total = 0.0

    # p1_risc_bar_total = 0.0
    # p2_risc_bar_total = 0.0

    init_bars = {}
    init_bars["healthbar"] = {}
    init_bars["empty_tension"] = {}
    init_bars["empty_risc"] = {}
    init_bars["full_burst"] = {}

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
                    between_round = False
                elif "slash" in found_cls.keys():
                    round_end = True
                else:
                    if new_round and len(found_cls["heart_lost"]) + len(found_cls["heart"]) == 4 and\
                    len(found_cls["healthbar"]) == 2 and \
                    len(found_cls["empty_risc"]) == 2 and \
                    len(found_cls["empty_tension"]) == 2:
                        #Round start image has just disappeared, initialise for new round
                        #Determine if new set
                        for bar_name in init_bars.keys():
                            for bar in found_cls[bar_name]:
                                if is_p1_side(bar):
                                    init_bars[bar_name]["p1"] = bar[2]
                                    print(f'P1 %s bar init to value %f' % (bar_name, init_bars[bar_name]["p1"]))
                                else:
                                    init_bars[bar_name]["p2"] = bar[2]
                                    print(f'P2 %s bar init to value %f' % (bar_name, init_bars[bar_name]["p2"]))

                        # for health_bar in found_cls["healthbar"]:
                        #     if is_p1_side(health_bar):
                        #         p1_health_bar_total = health_bar[2]
                        #         print(f'p1healthtotal: %f' % p1_health_bar_total)
                        #     else:
                        #         p2_health_bar_total = health_bar[2]
                        #         print(f'p2healthtotal: %f' % p2_health_bar_total)
                        if len(found_cls["heart"]) == 4:
                            #If there are no round wins and its a new set, then it's the first round
                            p1_won_set = False
                            if p1_curr_round_win + p2_curr_round_win != 0:
                                #determine who won last round and assign set win
                                if get_last_p1_health(current_round_history) < get_last_p2_health(current_round_history):
                                    p2_set_win += 1
                                    p2_curr_round_win += 1
                                    p1_won_set = False
                                else: 
                                    p1_set_win += 1
                                    p1_curr_round_win += 1
                                    p1_won_set = True
                                p1_round_win += p1_curr_round_win
                                p2_round_win += p2_curr_round_win
                                current_set_history += set_round_win(current_round_history, p1_won_set)
                                current_round_history = set_set_win(current_set_history, p1_won_set)

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
                    elif not new_round and not round_end and not between_round and 0 < len(found_cls["healthbar"]) <= 2:
                        #Should see both health bars during a game, but default to previous value if can't be seen
                        p1_health = get_last_p1_health(current_round_history) if len(current_round_history) > 0 else 1
                        p2_health = get_last_p2_health(current_round_history) if len(current_round_history) > 0 else 1
                        for health_bar in found_cls["healthbar"]:
                            if is_p1_side(health_bar):
                                p1_health = bar_clamp(float(health_bar[2]/init_bars["healthbar"]["p1"]))
                            else:
                                p2_health = bar_clamp(float(health_bar[2]/init_bars["healthbar"]["p2"]))

                        #Get Tension
                        p1_tension = current_round_history[-1]['p1_tension'] if len(current_round_history) > 0 else 0
                        p2_tension = current_round_history[-1]['p2_tension'] if len(current_round_history) > 0 else 0
                        p1_tension_gear = 0
                        p2_tension_gear = 0

                        for tension_gear in found_cls["tension_gears"]:
                            if is_p1_side(tension_gear):
                                p1_tension_gear += 1
                            else:
                                p2_tension_gear += 1
                        #print(f'p1 tension gear: %d, p2 tension gear: %d' % (p1_tension_gear, p2_tension_gear))
                        for empty_tension in found_cls["empty_tension"]:
                            if is_p1_side(empty_tension):
                                p1_tension = bar_clamp(tension_gear_check(1 - float(empty_tension[2]/init_bars["empty_tension"]["p1"]), p1_tension_gear))
                            else:
                                p2_tension = bar_clamp(tension_gear_check(1 - float(empty_tension[2]/init_bars["empty_tension"]["p2"]), p2_tension_gear))
                        #Get Risc
                        p1_risc = current_round_history[-1]['p1_risc'] if len(current_round_history) > 0 else 0
                        p2_risc = current_round_history[-1]['p2_risc'] if len(current_round_history) > 0 else 0
                        for empty_risc in found_cls["empty_risc"]:
                            if is_p1_side(empty_risc):
                                p1_risc = bar_clamp(1 - float(empty_risc[2]/init_bars["empty_risc"]["p1"]))
                            else:
                                p2_risc = bar_clamp(1 - float(empty_risc[2]/init_bars["empty_risc"]["p2"]))
                        #Get Burst
                        p1_burst = current_round_history[-1]['p1_burst'] if len(current_round_history) > 0 else 0
                        p2_burst = current_round_history[-1]['p2_burst'] if len(current_round_history) > 0 else 0
                        for burst in found_cls["burst"]:
                            if is_p1_side(burst):
                                p1_burst = bar_clamp(float(burst[2]/init_bars["full_burst"]["p1"]))
                            else:
                                p2_burst = bar_clamp(float(burst[2]/init_bars["full_burst"]["p2"]))
                        for full_burst in found_cls["full_burst"]:
                            if is_p1_side(full_burst):
                                p1_burst = 1.0
                            else:
                                p2_burst = 1.0
                        current_round_history.append({'frame': frameCount, 'p1_health': p1_health, 'p2_health':p2_health, 
                                                      'p1_tension': p1_tension, 'p2_tension': p2_tension, 
                                                      'p1_risc': p1_risc, 'p2_risc': p2_risc, 
                                                      'p1_burst': p1_burst, 'p2_burst': p2_burst,
                                                      'p1_round_count': p1_curr_round_win, 'p2_round_count': p2_curr_round_win})
                if round_end and len(found_cls["healthbar"]) == 1:
                    #Should only be a single healthbar left
                    if get_last_p1_health(current_round_history) != 0 and get_last_p2_health(current_round_history) != 0:
                        last_of_round = current_round_history[-1]
                        if is_p1_side(found_cls["healthbar"][0]):
                            last_of_round['p2_health'] = 0
                            current_round_history.append(last_of_round)
                            print(f'P1 Wins Round with final Health: %f' % get_last_p1_health(current_round_history))
                        else:
                            last_of_round['p1_health'] = 0
                            current_round_history.append(last_of_round)
                            print(f'P2 Wins Round with final Health: %f' % get_last_p2_health(current_round_history))
                    round_end = False
                    between_rounds = True
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