class TwoBitPredictor:

    def __init__(self):
        self._state = 1  # weakly not-taken
        self.mispredictions = 0
        self.total = 0

    def step(self, actual: bool) -> bool:
        prediction = self._state >= 2
        correct = prediction == actual
        if not correct:
            self.mispredictions += 1
        self.total += 1
        self._state = min(self._state + 1, 3) if actual else max(self._state - 1, 0)
        return correct
