from tflite_support.task import text


class Bert:

    def __init__(self, model_path):
        self.bert = text.BertQuestionAnswerer.create_from_file(model_path)

    def answer(self, context, question):
        results = self.bert.answer(context, question)
        return results.answers[0].text


class Inference:

    def __init__(self, graph):
        self.graph = graph
        #self.graph_text = graph.to_text()
        self.langmodel = Bert("ckpt/albert_metadata.tflite")

    def infer(self, question):
        if 5 < len(question) < 30:
            return self.langmodel.answer(self.graph_text, question)
        else:
            return "Search query too short or too large"
