import time


class Dummy:
    def __init__(self):
        self.gui_update_method = None
        self.player_nr: int = 1
        self.is_running = 1

    def stop(self):
        self.is_running = not self.is_running

    def set_gui_update_method(self, gui_update_method):
        self.gui_update_method = gui_update_method

    def play(self):
        while self.is_running:
            time.sleep(2)
            self.player_nr = 1 if self.player_nr == 0 else 0
            self.gui_update_method()
            print(self.player_nr)
