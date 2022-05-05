from paddlenlp import Taskflow

class NLP:
    def __init__(self):
        schema = ["时间", "出发地", "目的地", "费用"]
        self.ie_model = Taskflow("information_extraction", schema=schema)
        self.dialogue_model = Taskflow("dialogue")
    
    def chat(self, text):
        result = self.dialogue_model([text])
        return result[0]
    
    def ie(self, text):
        result = self.ie_model(text)
        return result
    