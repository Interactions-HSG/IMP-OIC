from flask import Flask, render_template, request
from qa import Inference
import os
import shutil
import sys

app = Flask(__name__)
app.config.update(SERVER_NAME='127.0.0.1:5000')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/results/', methods=['POST'])
def search_request():
    query = request.form["input"]
    if len(query.split(" ")) == 0:
        return index()

    answer = inference.infer(query)
    response = {"question": query, "answer": answer}
    return render_template('results.html', res=response)


if __name__ == "__main__":
    graph2text = sys.argv[1]
    tg_plot = sys.argv[2]
    inference = Inference(graph2text)
    if os.path.isfile(tg_plot):
        shutil.copy(tg_plot, "static/tg.png")
    app.run(debug=False)
