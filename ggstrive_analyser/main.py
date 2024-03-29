import cv2
from bar_collection import BarCollector
from data_recorder import CSVDataRecorder
from os import listdir, cpu_count
from os.path import isfile, join, exists
from pathlib import Path
from win_predictor import WinPredictor
from graph import RoundGraphManager
from config import Config
from multiprocessing import Pool
import yaml

def process_video(video):
    predictor : WinPredictor
    cfg = Config("config")
    if not cfg.get("pred_record"):
        predictor = WinPredictor(cfg)
    frame_count = 0
    video_name = Path(video).stem
    capture = cv2.VideoCapture(video)
    frame_rate = capture.get(cv2.CAP_PROP_FPS)
    #All videos are of the formate p1_p2_counter.mkv
    p1_name = video_name.split('_')[0]
    p2_name = video_name.split('_')[1]
    print("%s vs %s" % (p1_name, p2_name))
    #print(frame_rate)
    bar_collector = BarCollector(cfg, frame_rate, p1_name, p2_name)
    csv_data_recorder: CSVDataRecorder
    if cfg.get("record"):
        csv_data_recorder = CSVDataRecorder(cfg, video_name)
    else:
        rgm = RoundGraphManager()

    while(capture.isOpened()):
        #print(frame_count)
        ret, frame = capture.read()
        if frame_count % cfg.get("num_frames") == 0:
            #print ("in here")
            if ret:
                #cv2.imshow("main", frame)
                current_state = bar_collector.read_frame(frame)
                # if current_state:
                #     print(current_state.flatten())
                if current_state:
                    #print(current_state.win_state)
                    if cfg.get("record"):
                        csv_data_recorder.write(current_state)
                    else:
                        rgm.update(current_state, predictor.predict_win_round(current_state)[0][1], predictor.predict_win_set(current_state)[0][1])
            else:
                break
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break
        frame_count += 1
    if cfg.get("record"):
        if len(csv_data_recorder.current_round_history) > 0 or len(csv_data_recorder.current_set_history) > 0:
            csv_data_recorder.final_write()
    capture.release()
    #cv2.destroyAllWindows()


def main():
    # with open("ggstrive_analyser/conf/config.yml", "r") as ymlfile:
    #     cfg = yaml.safe_load(ymlfile)
    cfg = Config("config")
    video_path = cfg.get("video_path")
    training_vid_list = []
    if exists(video_path):
        if isfile(video_path):
            training_vid_list = [video_path]
        else:
            training_vid_list = [video_path + "/" + f for f in listdir(video_path) if isfile(join(video_path, f))]
    else:
        raise Exception("The file does not exist")

    print(training_vid_list)
    try:
        pool = Pool(4)
        pool.imap_unordered(process_video, training_vid_list)
    finally:
        pool.close()
        pool.join()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

