import cv2
from bar_collector import BarCollector
from asuka_spell_collector import AsukaSpellCollector
from data_recorder import CSVDataRecorder
from collections import defaultdict
from os import listdir, cpu_count
from os.path import isfile, join, exists
from pathlib import Path
from win_predictor import WinPredictor
from graph import RoundGraphManager
from config import Config
from multiprocessing import Pool

def process_video(video):
    predictor : WinPredictor
    if not Config.get("record"):
        predictor = WinPredictor()
    frame_count = 0
    video_name = Path(video).stem
    capture = cv2.VideoCapture(video)
    frame_rate = capture.get(cv2.CAP_PROP_FPS)
    #All videos are of the formate p1_p2_counter.mkv
    chars = defaultdict(list)
    players = {}
    p1_name = video_name.split('_')[0]
    p2_name = video_name.split('_')[1]
    chars[p1_name].append(Config.P1)
    players[Config.P1] = p1_name
    chars[p2_name].append(Config.P2)
    players[Config.P2] = p2_name

    print("%s vs %s" % (p1_name, p2_name))
    #print(frame_rate)
    bar_collector = BarCollector(frame_rate, players)
    if chars["asuka"] != None or len(chars["asuka"]) > 0:
        asuka_spell_collector = AsukaSpellCollector(players, chars["asuka"])
    csv_data_recorder: CSVDataRecorder
    asuka_csv_data_recorders = {}
    if Config.get("record"):
        csv_data_recorder = CSVDataRecorder(filename=f'{Config.get("csv_path")}/{video_name}.csv', 
                                            fields=Config.get("csv_fields"), 
                                            round_win_field=Config.get('round_win_field'), 
                                            set_win_field=Config.get('set_win_field'))
        for player in chars["asuka"]:
            asuka_csv_data_recorders[player] = CSVDataRecorder(filename=f'{Config.get("csv_path")}/spell/{video_name}_{player}.csv', 
                                                    fields=Config.get("asuka_csv_fields"), 
                                                    round_win_field=Config.get('asuka_win_field'))
    else:
        rgm = RoundGraphManager()

    while(capture.isOpened()):
        ret, frame = capture.read()
        if frame_count % Config.get("num_frames") == 0:
            if ret:
                current_state = bar_collector.read_frame(frame)
                asuka_spells = asuka_spell_collector.read_frame(frame)
                #print(asuka_spells)
                if current_state:
                    if Config.get("record"):
                        csv_data_recorder.write(current_state.flatten(), current_state.round_win_state, current_state.set_win_state)
                        for player in asuka_spells:
                            asuka_csv_data_recorders[player].write(asuka_spells[player], current_state.round_win_state, current_state.set_win_state)
                    else:
                        rgm.update(current_state, predictor.predict_win_round(current_state)[0][1], predictor.predict_win_set(current_state)[0][1])
            else:
                break
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break
        frame_count += 1
    if Config.get("record"):
        if len(csv_data_recorder.current_round_history) > 0 or len(csv_data_recorder.current_set_history) > 0:
            bar_collector.determine_round_winner()
            csv_data_recorder.final_write(bar_collector.determine_round_winner())

        for player in chars["asuka"]:
            if len(asuka_csv_data_recorders[player].current_round_history) > 0:
                asuka_csv_data_recorders[player].final_write(bar_collector.determine_round_winner())
    capture.release()
    #cv2.destroyAllWindows()


def main():
    Config.load("asuka_config")
    video_path = Config.get("video_path")
    training_vid_list = []
    if exists(video_path):
        if isfile(video_path):
            training_vid_list = [video_path]
        else:
            training_vid_list = [video_path + "/" + f for f in listdir(video_path) if isfile(join(video_path, f))]
    else:
        raise Exception("The file does not exist")

    print(training_vid_list)
    # if Config.get("record"):
    #     try:
    #         pool = Pool(1)
    #         pool.imap_unordered(process_video, training_vid_list)
    #     except Exception as e:
    #         print(e)
    #     finally:
    #         pool.close()
    #         pool.join()
    # else:
    for video in training_vid_list:
        process_video(video)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

