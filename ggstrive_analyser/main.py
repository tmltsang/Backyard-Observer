import cv2
from asuka_manager import AsukaManager
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
    Config.load("config")
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
    asuka_manager: AsukaManager
    asuka_manager = None
    if (chars["asuka"] != None or len(chars["asuka"]) > 0) and Config.get('asuka_model_path') != None:
        asuka_manager = AsukaManager(players, chars["asuka"])
        #asuka_spell_collector = AsukaSpellCollector(players, chars["asuka"])
    csv_data_recorder: CSVDataRecorder
    if Config.get("record"):
        csv_data_recorder = CSVDataRecorder(filename=f'{Config.get("csv_path")}/{video_name}.csv',
                                            fields=Config.get("csv_fields"),
                                            round_win_field=Config.get('round_win_field'),
                                            set_win_field=Config.get('set_win_field'))
        if asuka_manager:
            asuka_manager.create_data_recorders(video_name)

    else:
        rgm = RoundGraphManager()

    while(capture.isOpened()):
        ret, frame = capture.read()
        if frame_count % Config.get("num_frames") == 0:
            if ret:
                current_state = bar_collector.read_frame(frame)
                if asuka_manager:
                    asuka_spells = asuka_manager.asuka_spell_collector.read_frame(frame)
                #print(asuka_spells)
                if current_state:
                    if Config.get("record"):
                        csv_data_recorder.write(current_state.flatten(), current_state.round_win_state, current_state.set_win_state)
                        if asuka_manager:
                            asuka_manager.write(current_state, asuka_spells)
                        #print(asuka_spells[Config.P2])
                    else:
                        current_round_pred = predictor.predict_win_round(current_state)[0][1]
                        current_set_pred = predictor.predict_win_set(current_round_pred, current_state)[0][1]
                        rgm.update(current_state, current_round_pred, current_set_pred)
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
        if asuka_manager:
            asuka_manager.final_write(bar_collector.determine_round_winner())
            asuka_manager.write_spells()
    capture.release()
    #cv2.destroyAllWindows()


def main():
    Config.load("config")
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
    if Config.get("record"):
        try:
            pool = Pool(4)
            pool.imap_unordered(process_video, training_vid_list)
        except Exception as e:
            print(e)
        finally:
            pool.close()
            pool.join()
    else:
        for video in training_vid_list:
            process_video(video)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

