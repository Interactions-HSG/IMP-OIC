# OIC️

## Installation and usage

### Submodules

Add the RelTR with the following commands: 

```
git submodule init
git submodule update
```

### Scene Graph

Follow the instructions in the `RelTR` submodule for installation.
`RelTR` requires Python 3.6.

### Symbolic Link (graphene)

_Note_: graphene can be used within the same environment as the Scene Graph.

- Run `pip3 install -r requirements.txt`

- For example, to run graphene on raw images, use
```
python3 graphene.py --img_path eval/img/airport
```

- To have a data2text export of the temporal graph
```
python3 graphene.py --img_path eval/img/airport --text graph2text.txt --visual tg.png
```

- Or if you already have created graphs, use
```
python3 graphene.py --graph_path eval/reltr/airport --text graph2text.txt --visual tg.png
```

Run `python3 graphene.py --help` for synopsis on graphene 


### QA interface

*Note*: `tflight-support` requires a Python version newer than `RelTR` and can therefore not be used with graphene.

- `cd inference`
- Optional: create conda environment or virtual environment with a Python version higher than 3.6
- Run `pip3 install -r requirements.txt`
- Download [Albert](https://tfhub.dev/tensorflow/lite-model/albert_lite_base/squadv1/metadata/1?lite-format=tflite) weights, rename them to `albert_metadata.tflite` and place them into `qa/ckpt`
- If the data2text export (done with `--text` in graphene) is `scene.txt` and the temporal graph plot (done with `--visual`) is `scene.png`, start the server with `python3 server.py ../out/scene.txt ../out/scene.png` and open _http://127.0.0.1:5000_ in your browser

## Data handling

### Frame extraction

To extract frames from a video, you can use
```
python3 utils/extractframes.py path_to_video frames_per_second
```

### Demo data

We provide demo images and preprocessed frame graphs (to be used with `--graph_path` option) in `eval/img` and `eval/reltr`, respectively.

## Directory structure

```
IMP-OIC
| 
└───dataset (Helper files to train RelTR)
└───eval
|  └───img (Images for evaluation)
|  └───reltr (Completed scene graph from RelTR, can be used with --graph-path)
|  └───vid (Original videos, can be converted to frames with extractframes.py)
|  └───yolo (YOLO classification results)
└───inference (Language model QA)
└───out (Generated for results)
└───RelTR (Submodule)
└───structures (Datastructures for the symbolic link)
└───utils (Helper files)
... 
```

## Common errors

### Directory not empty: `temp`

**Solution**: Delete the `temp` directory located in the root directory.

The `temp` directory is created for storing the scene graph descriptions obtained from RelTR in JSON format. For tests, they can be directly used with the `--graph_path` option and are not deleted automatically.

### RelTR is not running

Note that RelTR requires Python 3.6 and Tensorflow libraries that are specific for CPU or CUDA-compatible GPUs. Follow the installation instructions of the `RelTR` submodule.
Note that weights have to be downloaded for RelTR (see installation instructions).

### The QA system does not work

The ALBERT language model is dependent on the `tflite-support` library that requires a Python version newer than ~3.8 and is furthermore not available for Windows.
Furthermore, it requires a metadata file (see installation instructions).