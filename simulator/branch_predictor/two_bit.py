class TwoBitPredictor:

    def __init__(self):
        self.state = 1
        self.mispredictions = 0
        self.total = 0

    def predict(self):
        return self.state >= 2

    def update(self, actual):
        prediction = self.state >= 2

        if prediction != actual:
            self.mispredictions += 1

        self.total += 1

        if actual:
            state = min(state + 1, 3)
        else:
            state = max(state - 1, 0)
