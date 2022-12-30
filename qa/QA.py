from tflite_support.task import text


class QA:

    def __init__(self, model_path):
        self.bert = text.BertQuestionAnswerer.create_from_file(model_path)

    def answer(self, context, question):
        results = answerer.answer(context, question)
        