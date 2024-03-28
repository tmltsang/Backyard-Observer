import cv2
import matplotlib.pyplot as plt
from bar_collection import BarCollector
from data_recorder import CSVDataRecorder
from os import listdir
from os.path import isfile, join, exists
from pathlib import Path
from win_predictor import WinPredictor
from graph import RTGraph
import yaml


def main():
    with open("ggstrive_analyser/conf/pred_config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    video_path = cfg["video_path"]
    training_vid_list = []
    if exists(video_path):
        if isfile(video_path):
            training_vid_list = [video_path]
        else:
            training_vid_list = [video_path + "/" + f for f in listdir(video_path) if isfile(join(video_path, f))]
    else:
        raise Exception("The file does not exist")

    print(training_vid_list)
    predictor : WinPredictor
    quit = False
    if not cfg["record"]:
        predictor = WinPredictor(cfg)
    for video in training_vid_list:
        frame_count = 0
        capture = cv2.VideoCapture(video)
        frame_rate = capture.get(cv2.CAP_PROP_FPS)

        bar_collector = BarCollector(cfg, frame_rate)
        csv_data_recorder: CSVDataRecorder
        round_graph: RTGraph
        set_graph: RTGraph
        if cfg["record"]:
             csv_data_recorder = CSVDataRecorder(cfg, Path(video).stem)
        else:
            fig, axs = plt.subplots(2)
            fig.suptitle("Win %")
            round_graph = RTGraph(axs[0])
            set_graph = RTGraph(axs[1])
            plt.ion()
        while(capture.isOpened()):
            #print(frame_count)
            ret, frame = capture.read()
            if frame_count % cfg["num_frames"] == 0:
                #print ("in here")
                if ret:
                    #cv2.imshow("main", frame)
                    current_state = bar_collector.read_frame(frame)
                    # if current_state:
                    #     print(current_state.flatten())
                    if current_state:
                        if cfg["record"]:
                            csv_data_recorder.write(current_state)
                        else:
                            round_graph.update(predictor.predict_win_round(current_state)[0][1])
                            set_graph.update(predictor.predict_win_set(current_state)[0][1], add_vline=current_state.round_end)
                            print(current_state.round_end)
                            # print(f'Round Win: %f' % (predictor.predict_win_round(current_state)[0][0]))
                            # print(f'Set Win: %f' % (predictor.predict_win_set(current_state)[0][0]))
                            plt.show()
                else:
                    break
                if cv2.waitKey(1) == ord('q'):
                    quit = True
                    cv2.destroyAllWindows()
                    break
            frame_count += 1
        if cfg["record"]:
            csv_data_recorder.final_write()
        capture.release()
        cv2.destroyAllWindows()
        if quit:
            break

if __name__ == '__main__':
    main()

