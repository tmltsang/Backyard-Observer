import cv2
from collections import defaultdict
from vision import Vision
from time import time
from ultralytics import YOLO
from bar import *
import plotly.offline as py
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np

def make_edge(x, y, text, width):
    return go.Scatter(x = x,
                      y = y,
                      line = dict(width = width, color = 'cornflowerblue'),
                      hoverinfo = 'text',
                      text = ([text]),
                      mode = 'lines')

def convert_class_to_name(boxes_cls, bar_cls_dict):
    found_cls = []
    for cls in boxes_cls:
        found_cls.append(bar_cls_dict[cls])
    return found_cls

def main():
    testament_last_move = None
    testament_move_count = defaultdict(int)
    testament_move_matrix = defaultdict(lambda: defaultdict(int))
    testament_cls = None
    bar_cls_dict = None
    model = YOLO('runs/detect/batch_32/weights/best.pt')
    capture = cv2.VideoCapture('training/videos/testament_anji_1.mp4')
    # reader = easyocr.Reader(['en'], gpu='cuda:0')
    if (capture.isOpened() == False):
        print("Error opening file")
    counter = 0
    new_round = False
    health1_history = []
    health2_history = []
    while(capture.isOpened()):
        ret, frame = capture.read()
        if ret:
            results = model.predict(frame, conf=0.8, agnostic_nms=True)
            resultsCpu = results[0].cpu()
            annotated_frame = results[0].plot()
            if bar_cls_dict == None:
                bar_cls_dict = results[0].names
            found_cls = convert_class_to_name(resultsCpu.boxes.cls.numpy(), bar_cls_dict)
            # p1_health_bar = Bar(100, 75, 480, 20, [0,35,210], [179,255,255])
            # health1_percent, health1 = p1_health_bar.read_bar_percent(frame)
            # p2_health_bar = Bar(700, 75, 480, 20, [0,35,210], [179,255,255], True)
            # health2_percent, health2 = p2_health_bar.read_bar_percent(frame)
            if "round_start" in found_cls:
                new_round = True
            else:
                if new_round:
                    #Round start image has just disappeared, initialise for new round
                    if found_cls :

                new_round = False

            if health1_percent > 0.99 and health2_percent > 0.99:
                if not new_round:
                    new_round = True
                    if health1_history[-1] > health2_history[-1]:
                        print("Winner P1")
                    else:
                        print("WInner P2")
            else:
                new_round = False
            # If neither healthbar is present then most likely in a cinematic super
            if health1_percent > 0.01 or health2_percent > 0.01:
                health1_history.append(health1_percent)
                health2_history.append(health2_percent)

            cv2.imshow("main", annotated_frame)
           # cv2.imshow("p2health", health2)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            #cv2.imshow("YOLOv8 Inference", annotated_frame)
            #cv.imshow('Matches', output_img)
            #print('FPS {}'.format(1 / (time() - loop_time)))
            loop_time = time()
            #if (len(rects) > 0):
            #    cv.imwrite('debug/result' + str(time()) + '.jpg', output_img)

            # press 'q' with the output window focused to exit.
            # waits 1 ms every loop to process key presses
            # counter += 1
            # counter %= 60
                # layout = go.Layout(
                #     paper_bgcolor='rgba(0,0,0,0)', # transparent background
                #     plot_bgcolor='rgba(0,0,0,0)', # transparent 2nd background
                #     xaxis =  {'showgrid': False, 'zeroline': False}, # no gridlines
                #     yaxis = {'showgrid': False, 'zeroline': False}, # no gridlines
                # )
                # # Create figure
                # fig = go.Figure(layout = layout)
                # # Add all edge traces
                # for trace in edge_trace:
                #     fig.add_trace(trace)
                # # Add node trace
                # fig.add_trace(node_trace)
                # # Remove legend
                # fig.update_layout(showlegend = False)
                # # Remove tick labels
                # fig.update_xaxes(showticklabels = False)
                # fig.update_yaxes(showticklabels = False)
                # # Show figure
                # fig.show()
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break
        else:
            break
    # When everything done, release the video capture object
    capture.release()
  
    health1_history = np.array(health1_history)
    health2_history = np.array(health2_history)
    fig2 = go.Figure(data = [go.Scatter(x = np.arange(health1_history.size), y = health1_history,  name = "p1"),
                                go.Scatter(x = np.arange(health2_history.size), y = health2_history,  name = "p2")],
                                layout = {"xaxis": {"title" : "Frame Count"},  "yaxis": {"title": "Health %"}, "title": "Health bar"})
    fig2.show()
    # Closes all the frames
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()

