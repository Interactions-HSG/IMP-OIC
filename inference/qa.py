from tflite_support.task import text
import os


class Bert:

    def __init__(self, model_path):
        self.bert = text.BertQuestionAnswerer.create_from_file(model_path)

    def answer(self, context, question):
        results = self.bert.answer(context, question)
        if len(results.answers) > 0:
            return results.answers[0].text
        else: return ""


class Inference:

    def __init__(self, context_path):
        if not os.path.isfile(context_path):
            print(f"Could not find directory {context_path}")
            self.context = ""
        else:
            with open(context_path, "r") as file:
                self.context = file.read()
                file.close()
        self.langmodel = Bert("ckpt/albert_metadata.tflite")

    def infer(self, question):
        if 5 < len(question) < 60:
            return self.langmodel.answer(self.context, question)
        else:
            return "Search query too short or too large"
