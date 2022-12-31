from flask import Flask, render_template, request
from qa import Inference

app = Flask(__name__)
app.config.update(SERVER_NAME='127.0.0.1:5000')
inference = Inference(" ")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results/', methods=['POST'])
def search_request():
    query = request.form["input"]
    if len(query.split(" ")) == 0:
        return index()
    
    answer = inference.infer(query)
    response = {"answer": answer}
    return render_template('results.html', res=response)


if __name__ == "__main__":
    app.run(debug=False)
