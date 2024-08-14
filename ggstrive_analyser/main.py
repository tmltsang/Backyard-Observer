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
from tournament_index_manager import TournamentIndexManager
import sys

def process_video(video, configName):
    predictor : WinPredictor
    Config.load(configName)
    if not Config.get("record"):
        predictor = WinPredictor()
    frame_count = 0
    print(video)
    video_name = Path(video).stem
    capture = cv2.VideoCapture(video)
    frame_rate = capture.get(cv2.CAP_PROP_FPS)
    #All videos are of the formate p1_p2_counter.mkv
    chars = defaultdict(list)
    players = {}
    p1_name = video_name.split('_')[0]
    p2_name = video_name.split('_')[1]

    tournament_round: str
    p1_player_name: str
    p2_player_name: str
    tournament_index_manager: TournamentIndexManager = None
    if Config.get('tournament_mode'):
        p1_player_name = video_name.split('_')[3]
        p2_player_name = video_name.split('_')[4]
        tournament_round= video_name.split('_')[5].split('.')[0]
        tournament = Path(video).parent.name
        tournament_index_manager = TournamentIndexManager(p1_player_name, p2_player_name, tournament_round, tournament)

    chars[p1_name].append(Config.P1)
    players[Config.P1] = p1_name
    chars[p2_name].append(Config.P2)
    players[Config.P2] = p2_name

    print("%s vs %s" % (p1_name, p2_name))
    bar_collector = BarCollector(frame_rate, players)
    asuka_manager: AsukaManager
    asuka_manager = None
    if (chars["asuka"] != None or len(chars["asuka"]) > 0) and Config.get('asuka_model_path') != None:
        asuka_manager = AsukaManager(players, chars["asuka"])
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
                if current_state:
                    if Config.get("record"):
                        if Config.get("tournament_mode"):
                            tournament_index_manager.update_set_time(current_state)
                            csv_data_recorder.write(current_state.flatten(), current_state.round_win_state, current_state.set_win_state, tournament_index_manager)
                            if asuka_manager:
                                asuka_manager.write(current_state, asuka_spells, tournament_index_manager)
                            tournament_index_manager.update(current_state)
                        else:
                            csv_data_recorder.write(current_state.flatten(), current_state.round_win_state, current_state.set_win_state)
                            if asuka_manager:
                                asuka_manager.write(current_state, asuka_spells)
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


def main(args):
    configName = args[1]
    Config.load(configName)
    video_paths = Config.get("video_path")
    training_vid_list = []
    for video_path in video_paths:
        if exists(video_path):
            if isfile(video_path):
                training_vid_list.append(video_path)
            else:
                training_vid_list.extend([video_path.rstrip('/') + "/" + f for f in listdir(video_path) if isfile(join(video_path, f))])
        else:
            raise Exception(f"The file {video_path} does not exist")

    print(training_vid_list)
    if Config.get("record") and not Config.get("debug"):
        try:
            pool = Pool(4)
            pool.starmap(process_video, [(vid, configName) for vid in training_vid_list])
        except Exception as e:
            print(e)
        finally:
            pool.close()
            pool.join()
    else:
        for video in training_vid_list:
            process_video(video, configName)
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)

