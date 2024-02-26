import time


class GLDummy(object):
    def __init__(self):
        self.close_game_gui_method = None
        self.gui_update_method = None
        self.thread_is_running = 1
        self.current_player = 0

    def stop(self) -> None:
        """
        Stop running game -> stop game instance
        :return: None
        """
        self.thread_is_running = not self.thread_is_running

    def set_destroy_game_gui(self, close_game_gui_method) -> None:
        """
        Set the Method to close the running game window and show the main menu window.
        :param close_game_gui_method: Method to close the running game window and show the main menu window
        :return: None
        """
        self.close_game_gui_method = close_game_gui_method

    def set_gui_update_method(self, gui_update_method) -> None:
        """
        Set the Method to update the game window with active player number.
        :param gui_update_method: Method to update the game window with current player information
        :return: None
        """
        self.gui_update_method = gui_update_method

    def run_game(self) -> None:
        while self.thread_is_running:
            self.set_gui_update_method(self.current_player)
            self.current_player = 0 if self.current_player == 1 else 1
            time.sleep(2)