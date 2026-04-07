class OneBitPredictor:

    def __init__(self):
        self.prediction = False
        self.mispredicts = 0
        self.total = 0

    def predict(self, actual):
        if self.prediction != actual:
            self.mispredicts += 1
            self.prediction = actual

        self.total += 1
