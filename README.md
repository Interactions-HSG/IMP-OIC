# OIC️

## Installation

### Submodules

Add the RelTR with the following commands: 

```
git submodule init
git submodule update
```

### Scene Graph

Follow the instructions in the `RelTR` submodule for installation.
`RelTR` requires Python 3.6 and must in most environments be run separately.

### Symbolic Link (graphene)

_Note_: graphene can be used within the same environment as the Scene Graph.

- Run `pip3 install -r requirements.txt`

For example, to run graphene on raw images, use
```
python3 graphene.py --img_path eval/img/airport --text graph2text.txt --visual tg.png
```
or if you already have created graphs, use
```
python3 graphene.py --graph_path eval/reltr/airport --text graph2text.txt --visual tg.png
```

Run 'python3 graphene.py --help' for synopsis on graphene 


### QA interface

- Optional: 
- Run `pip3 install -r requirements.txt`
- Download [Albert](https://tfhub.dev/tensorflow/lite-model/albert_lite_base/squadv1/metadata/1?lite-format=tflite) weights and place them into `qa/ckpt`
- `cd inference` and run `python3 server.py`
- Open `http://127.0.0.1:5000` in your browser



