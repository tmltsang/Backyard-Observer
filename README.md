# Backyard Observer
![demo](img/docs/backyard-observer.gif)

*Metrics Gathering*

![pred_demo](img/docs/prediction.gif)

*Real-time Predictions*

A visual analyser for *Guilty Gear -Strive-*, vision model and metrics collector for [backyard-insight.info](https://backyard-insight.info/)

## About this project
Attempting to predict match wins in *Guilty Gear -Strive-*. It has two reponsibilities:
1. Creation of a [YOLOv8](https://docs.ultralytics.com/) vision model to read the UI of GuiltyGear strive
    * Some of the config can be found under [training](training/). This project mainly used [data_bars.yaml](training/data_bars.yaml) and [data_asuka.yaml](training/data_asuka.yaml)
2. Using the visual moddels to gather metrics
    * This occurs under the [observer](observer/) directory

## Getting Started
### Create venv and install dependencies
```bash
### pip and venv
python -m venv venv
source venv/bin/activate
python -r requirements.txt

### Conda
conda create --name backyard-observer --file environment.yml
conda activate backyard-observer
```


### Training a Vision Model
There were a few vision models trained

1. Bar model ([data_bars.yaml](training/data_bars.yaml))
    * Vision model that reads the UI
2. Asuka model ([data_asuka.yaml](training/data_asuka.yaml))
    * Vision model that can read Asuka's spells
3. Testament model ([data.yaml](training/data.yaml) deprecated)
    * Deprecated model, attempted to distinguish different testament moves


The dataset to train the models aren't included here however you can attempt to create your own using [labelimg](https://github.com/HumanSignal/labelImg) to annotate. There are a few helpful script under [helper](helper/), mainly  [frame_splitter.py](helper/frame_splitter.py) to create frames. For the Asuka model, the [asuka_synthetic_frames.py](helper/asuka_synthetic_frames.py) script can be used to add spell icons to any frame and create a corresponding annotation file.

#### Directory Structure
```
.
└── training/
    ├── train/
    │   ├── images
    │   └── labels
    └── valid/
        ├── images
        └── labels
```

To train a YOLOv8, make sure your directory looks like ^
The names of `train` and `valid` can be changed, just make sure you change the fields in the appropriate `data.yaml`.

### Metrics Gathering
#### Running
```
python observer/main.py <config>
```

There are several modes that the metrics gathering defined by the .yml files in [observer/conf](observer/conf/) all
#### Configs
* `record_config`
    * Shown in *Metrics Gathering* above
    * Used to perform mass stats gathering to train the prediction model
    * Default video location is `training/videos/gg_matches`
    * Videos need to be of the format `<p1_char_name>_<p2_char_name>_<id>`
        * e.g. `testament_chaos_1`
    * Default output location is `csv/`
        * For more explanation of the output see [ggstrive.ipynb](https://colab.research.google.com/drive/1ybJt9Y1jr8Qtdvq8T515--zxLptH8D7v?usp=sharing)
    * Multi-proccessed by default
        * Set `debug: true ` to see the video with annotations as it is processed
* `pred_config`
    * Shown in *Real-time Predictions* above
    * This is not fully featured and a demo
    * Default video location is `videos/gg_matches`
        * Videos need to be of the format `<p1_char_name>_<p2_char_name>_<id>`
        * e.g. `testament_chaos_1`
* `asuka_config`
    * An extension of `record_config.yml` that will also track stats about Asuka's spells.
    * Should be able to work for non-asuka games as well however it is more resource intensive as it has to run two vision models
    * Default video location is `training/videos/asuka/`
    * Videos need to be of the format `<p1_char_name>_<p2_char_name>_<id>`
        * e.g. `testament_chaos_1`
    * Default output location is `csv/asuka`
        * For more explanation of the output see [ggstrive_asuka.ipynb](https://colab.research.google.com/drive/1HPtgk7gfxv6YQVEiv5CYf8RlGwLRczoV?usp=sharing)
* `tournament_config` and `tournament_asuka_config`
    * Extension of `record_config` and `asuka_config` used for collecting the metrics used in [Backyard-Insight](https://github.com/tmltsang/Backyard-Insight)
    *  Output is cleaned via [ggstrive-Tournament.ipynb](https://colab.research.google.com/drive/1_gkzzw3t4O7hxUaud6jyS6_gkZBsgGU-?usp=sharing)


## License
Distributed under the MIT License. See [LICENSE.txt](LICENSE.txt) for more information
