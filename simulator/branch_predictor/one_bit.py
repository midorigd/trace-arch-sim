class OneBitPredictor:

    def __init__(self):
        self._prediction = False
        self.mispredictions = 0
        self.total = 0

    def step(self, actual: bool) -> bool:
        correct = self._prediction == actual
        if not correct:
            self.mispredictions += 1
            self._prediction = actual  # update: flip to match outcome
        self.total += 1
        return correct
