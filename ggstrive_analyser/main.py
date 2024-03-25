import cv2
from bar_collection import BarCollector
from data_recorder import CSVDataRecorder
from os import listdir
from os.path import isfile, join
from pathlib import Path
from win_predictor import WinPredictor
import yaml


def main():
    with open("ggstrive_analyser/conf/config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    video_path = cfg["video_path"]
    training_vid_list = [f for f in listdir(video_path) if isfile(join(video_path, f))]
    print(training_vid_list)
    predictor = None
    if not cfg["record"]:
        predictor = WinPredictor(cfg)
    for video in training_vid_list:
        frame_count = 0
        capture = cv2.VideoCapture(video_path + "/" + video)
        bar_collector = BarCollector(cfg) 
        csv_data_recorder = None
        if cfg["record"]:
            csv_data_recorder = CSVDataRecorder(cfg, Path(video).stem)
        while(capture.isOpened()):
            #print(frame_count)
            ret, frame = capture.read()
            if frame_count % cfg["num_frames"] == 0:
                #print ("in here")
                if ret:
                    #cv2.imshow("main", frame)
                    current_state = bar_collector.read_frame(frame)
                    if current_state:
                        if cfg["record"]:
                            csv_data_recorder.write(current_state)
                        else:
                            print(f'Round Win: %f' % (predictor.predict_win_round(current_state)))
                            print(f'Set Win: %f' % (predictor.predict_win_set(current_state)))
                else: 
                    break
                if cv2.waitKey(1) == ord('q'):
                    cv2.destroyAllWindows()
                    break
            frame_count += 1
        csv_data_recorder.final_write()
        capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

