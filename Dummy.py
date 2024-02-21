import time


class Dummy:
    def __init__(self):
        self.player_nr: int = 1

    def play(self):
        while 1:
            time.sleep(2)
            self.player_nr = 1 if self.player_nr == 0 else 0
            print(self.player_nr)