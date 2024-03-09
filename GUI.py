import random
import time
import tkinter
from tkinter import *
from tkinter import messagebox
import pygame
import threading
import Constants
from GameLogic import GameLogic


class GUI(object):

    def __init__(self):
        self.game_instance = GameLogic()
        self.active_game_thread = None

        self.fenster = Tk()
        self.fenster.title(Constants.WINDOW_TITLE)
        self.fenster.geometry("%dx%d+0+0" % (Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        pygame.init()

        self.current_round_number = 0
        self.spieler1_eingabefeld = None
        self.spieler2_eingabefeld = None
        self.game_mode_container = IntVar()
        self.game_difficulty_container = IntVar()
        self.sound_state_container = IntVar()

        self.__main_window()
        self.fenster.mainloop()

    def __main_window(self) -> None:
        """
        Generate initial main window.
        :return: None
        """

        def build_grid() -> None:
            """
            Set position of gui elements inside the grid.
            :return: None
            """
            willkommen_label.grid(row=0, column=1)

            spielmodus_label.grid(row=1, column=1)
            radio_oneOnOne.grid(row=2, column=0)
            radio_oneOnCpu.grid(row=2, column=2)

            spieler1_label.grid(row=3, column=0)
            self.spieler1_eingabefeld.grid(row=3, column=1)
            spieler2_label.grid(row=4, column=0)
            self.spieler2_eingabefeld.grid(row=4, column=1)

            start_button.grid(row=10, column=1)

            sound_Label.grid(row=11, column=0)
            radio_sound_on.grid(row=12, column=0)
            demo_button.grid(row=12, column=1)
            radio_sound_off.grid(row=13, column=0)

            spielregeln_button.grid(row=13, column=1)
            info_button.grid(row=13, column=2)
            end_application_button.grid(row=14, column=1)
            shutdown_system_button.grid(row=14, column=2)

        def reset_game_container_values() -> None:
            """
            Reset data container values for game mode, game difficulty and sound.
            :return: None
            """
            self.game_mode_container.set(0)
            self.game_difficulty_container.set(0)
            self.sound_state_container.set(0)

        def ctrl_game_mode_change() -> None:
            """
            Change the value of the game mode data container "game_mode_container".
            :return: None
            """
            self.spieler2_eingabefeld.delete(0, END)
            if self.game_mode_container.get() == 0:
                spieler1_label.grid(row=3, column=0)
                self.spieler1_eingabefeld.grid(row=3, column=1)
                spieler2_label.grid(row=4, column=0)
                self.spieler2_eingabefeld.grid(row=4, column=1)
                self.spieler2_eingabefeld.insert(0, Constants.GAME_PLAYER_2_PLACEHOLDER)

                cpuLevel_Label.grid_forget()
                radio_leicht.grid_forget()
                radio_schwer.grid_forget()
            else:
                spieler1_label.grid(row=3, column=0)
                self.spieler1_eingabefeld.grid(row=3, column=1)
                spieler2_label.grid_forget()
                self.spieler2_eingabefeld.grid_forget()
                self.spieler2_eingabefeld.insert(0, Constants.GAME_ENVIRONMENT_PLACEHOLDER)

                cpuLevel_Label.grid(row=5, column=1)
                radio_leicht.grid(row=6, column=1)
                radio_schwer.grid(row=7, column=1)

        spielmodus_label = Label(self.fenster, text=Constants.GAME_MODE_LABEL)
        willkommen_label = Label(self.fenster, text=Constants.GAME_WELCOME_LABEL)

        spieler1_label = Label(self.fenster, text=Constants.GAME_PLAYER_1_LABEL)
        spieler2_label = Label(self.fenster, text=Constants.GAME_PLAYER_2_LABEL)

        self.spieler1_eingabefeld = Entry(self.fenster, bd=5, width=40)
        self.spieler2_eingabefeld = Entry(self.fenster, bd=5, width=40)

        self.spieler1_eingabefeld.insert(0, Constants.GAME_PLAYER_1_PLACEHOLDER)
        self.spieler2_eingabefeld.insert(0, Constants.GAME_PLAYER_2_PLACEHOLDER)

        radio_oneOnOne = Radiobutton(self.fenster,
                                     text=Constants.GAME_MODE_PVP_LABEL,
                                     padx=20,
                                     variable=self.game_mode_container,
                                     command=ctrl_game_mode_change,
                                     value=0)
        radio_oneOnCpu = Radiobutton(self.fenster,
                                     text=Constants.GAME_MODE_PVE_LABEL,
                                     padx=20,
                                     variable=self.game_mode_container,
                                     command=ctrl_game_mode_change,
                                     value=1)

        cpuLevel_Label = Label(self.fenster, text=Constants.GAME_MODE_PVP_DIFFICULTY_CHOOSE)

        radio_leicht = Radiobutton(self.fenster,
                                   text=Constants.GAME_MODE_PVP_DIFFICULTY_EASY,
                                   padx=20,
                                   variable=self.game_difficulty_container,
                                   value=0)
        radio_schwer = Radiobutton(self.fenster,
                                   text=Constants.GAME_MODE_PVP_DIFFICULTY_HARD,
                                   variable=self.game_difficulty_container,
                                   padx=20,
                                   value=1)

        start_button = Button(self.fenster, text=Constants.GAME_START_BUTTON, command=self.__start_game_instance)
        start_button.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)

        demo_button = Button(self.fenster, text=Constants.GAME_START_BUTTON, command=self.__start_demo_instance)
        demo_button.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)

        sound_Label = Label(self.fenster, text=Constants.GAME_SOUND_LABEL)
        radio_sound_on = Radiobutton(self.fenster, text=Constants.GAME_SOUND_LABEL_ON, padx=20,
                                     variable=self.sound_state_container,
                                     value=0)
        radio_sound_off = Radiobutton(self.fenster, text=Constants.GAME_SOUND_LABEL_OFF, padx=20,
                                      variable=self.sound_state_container,
                                      value=1, command=pygame.mixer.music.stop)

        spielregeln_button = Button(self.fenster, text=Constants.GAME_RULES_BUTTON, command=self.__rules_window)
        spielregeln_button.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)
        info_button = Button(self.fenster, text=Constants.GAME_INFO_BUTTON, command=self.__info_window)
        info_button.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)
        end_application_button = Button(self.fenster, text=Constants.GAME_END_BUTTON, command=self.fenster.quit)
        end_application_button.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)
        shutdown_system_button = Button(self.fenster, text=Constants.GAME_SHUTDOWN_BUTTON,
                                        command=self.__action_shutdown_system)
        shutdown_system_button.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)

        build_grid()
        reset_game_container_values()

    def __game_window(self) -> None:
        """
        Generate and set the window content of a running game instance.
        Start the game instance thread and react on player actions.
        :return: None
        """

        def action_end_game() -> None:
            """
            Stop the running game instance thread and close the window
            :return: None
            """
            self.spieler1_eingabefeld.delete(0, END)
            self.spieler2_eingabefeld.delete(0, END)
            self.spieler1_eingabefeld.insert(0, Constants.GAME_PLAYER_1_PLACEHOLDER)
            self.spieler2_eingabefeld.insert(0, Constants.GAME_PLAYER_2_PLACEHOLDER)
            self.game_instance.stop()
            close_top_window()

        def window_show_active_p0() -> None:
            """
            Show the active Player 0 in the game window
            :return: None
            """
            spieler_name_anzeigen_label['text'] = Constants.GAME_CURRENT_PLAYER_LABEL.format(
                cplayer=self.spieler1_eingabefeld.get())
            spieler_name_anzeigen_label.configure(bg=Constants.GAME_COLOR_BACKGROUND_PLAYER_1)
            spiele_fenster.configure(bg=Constants.GAME_COLOR_BACKGROUND_PLAYER_1)
            window_show_active()

        def window_show_active_p1() -> None:
            """
            Show the active Player 1 in the game window
            :return: None
            """
            spieler_name_anzeigen_label['text'] = Constants.GAME_CURRENT_PLAYER_LABEL.format(
                cplayer=self.spieler2_eingabefeld.get())
            spieler_name_anzeigen_label.configure(bg=Constants.GAME_COLOR_BACKGROUND_PLAYER_2)
            spiele_fenster.configure(bg=Constants.GAME_COLOR_BACKGROUND_PLAYER_2)
            window_show_active()

        def window_show_active()->None:
            """
            Duplicate content fix for window_show_active p0 and p1
            :return: None
            """
            beenden_button1.grid(row=1, column=0)
            if not self.sound_state_container.get():
                pygame.mixer.music.stop()
                pygame.mixer.music.load('sounds/FallenderStein.mp3')

        def window_show_start() -> None:
            """
            Show start/load screen in the game window and play the start sound.
            :return: None
            """
            spieler_name_anzeigen_label['text'] = random.choice(Constants.GAME_CURRENT_PLAYER_LABEL_START)
            spieler_name_anzeigen_label.configure(bg=Constants.GAME_COLOR_BACKGROUND_START)
            spiele_fenster.configure(bg=Constants.GAME_COLOR_BACKGROUND_START)
            beenden_button1.grid_forget()
            if not self.sound_state_container.get():
                pygame.mixer.music.load('sounds/SpielStart.mp3')
                pygame.mixer.music.play(loops=-1)

        def window_show_end_p0() -> None:
            """
            Show the winner in the game window and play the end sound.
            :return: None
            """
            spieler_name_anzeigen_label['text'] = Constants.GAME_CURRENT_PLAYER_LABEL_END.format(
                cplayer=self.spieler1_eingabefeld.get())
            window_show_end()

        def window_show_end_p1() -> None:
            """
            Show the winner in the game window and play the end sound.
            :return: None
            """
            spieler_name_anzeigen_label['text'] = Constants.GAME_CURRENT_PLAYER_LABEL_END.format(
                cplayer=self.spieler2_eingabefeld.get())
            window_show_end()

        def window_show_end() -> None:
            """
            Duplicate content fix for window_show_end p0 and p1
            :return: None
            """
            spieler_name_anzeigen_label.configure(bg=Constants.GAME_COLOR_BACKGROUND_END)
            spiele_fenster.configure(bg=Constants.GAME_COLOR_BACKGROUND_END)
            beenden_button1.grid_forget()
            if not self.sound_state_container.get():
                pygame.mixer.music.load('sounds/SpielEnde.mp3')
                pygame.mixer.music.play(loops=0)

        def window_show_vladesc_p0() -> None:
            """
            Show the winner in the easteregg game window and play the end sound.
            :return: None
            """
            spieler_name_anzeigen_label['text'] = Constants.GAME_CURRENT_PLAYER_LABEL_VLADESC.format(
                cplayer=self.spieler1_eingabefeld.get())
            window_show_vladesc()

        def window_show_vladesc_p1() -> None:
            """
            Show the winner in the easteregg game window and play the end sound.
            :return: None
            """
            spieler_name_anzeigen_label['text'] = Constants.GAME_CURRENT_PLAYER_LABEL_VLADESC.format(
                cplayer=self.spieler2_eingabefeld.get())
            window_show_vladesc()

        def window_show_vladesc() -> None:
            """
            Duplicate content fix for window_show_vladesc p0 and p1
            :return: None
            """
            spieler_name_anzeigen_label.configure(bg=Constants.GAME_COLOR_BACKGROUND_VLADESC)
            spiele_fenster.configure(bg=Constants.GAME_COLOR_BACKGROUND_VLADESC)
            beenden_button1.grid_forget()
            pygame.mixer.music.load('sounds/Vladesc.mp3')
            pygame.mixer.music.play(loops=0)

        window_show_options = {
            0: window_show_active_p0,
            1: window_show_active_p1,
            2: window_show_start,
            3: window_show_end_p0,
            4: window_show_end_p1,
            5: window_show_vladesc_p0,
            6: window_show_vladesc_p1,
        }

        def show_window_content(show_option: int) -> None:
            """
            Change the display (window content) for current player.
            :param show_option: Method, which will be called from window_show_options
            :return: None
            """
            window_show_options[show_option]()

        def play_sound() -> None:
            """
            Plays the actual loaded soundFile (used by GameLogic Thread)
            :return: None
            """
            if not self.sound_state_container.get():
                pygame.mixer.music.play(loops=0, start=0.2)

        def close_top_window() -> None:
            """
            Close the running game window and show the main menu window.
            :return: None
            """
            pygame.mixer.music.stop()
            spiele_fenster.destroy()

        def build_grid() -> None:
            """
            Set initial position of gui elements inside the grid.
            :return: None
            """
            spiele_fenster.grid_rowconfigure(0, weight=1)
            spiele_fenster.grid_rowconfigure(1, weight=1)
            spiele_fenster.grid_columnconfigure(0, weight=1)
            spieler_name_anzeigen_label.grid(row=0, column=0)
            beenden_button1.grid(row=1, column=0)

        pygame.mixer.music.set_volume(.5)
        spiele_fenster = tkinter.Toplevel(self.fenster)
        spiele_fenster.title(Constants.WINDOW_TITLE_RUNNING_GAME)
        spiele_fenster.geometry("%dx%d+0+0" % (Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        beenden_button1 = Button(spiele_fenster, text=Constants.GAME_MAIN_MENU_BUTTON, command=action_end_game)
        beenden_button1.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)
        spieler_name_anzeigen_label = Label(spiele_fenster, font=("Arial", 25))
        spiele_fenster.wm_overrideredirect(True)
        build_grid()
        show_window_content(2)

        self.active_game_thread = threading.Thread(target=self.game_instance.run_game)
        self.game_instance.set_mode_and_difficulty(self.game_mode_container.get(), self.game_difficulty_container.get())
        self.game_instance.set_gui_update_method(show_window_content)
        self.game_instance.set_gui_play_sound_method(play_sound)
        self.game_instance.set_destroy_game_gui(close_top_window)
        self.active_game_thread.start()

    def __rules_window(self) -> None:
        """
        Generate and set the window content of the rules window.
        :return: None
        """

        def build_grid() -> None:
            """
            Set position of gui elements inside the grid.
            :return: None
            """
            game_rules.grid_rowconfigure(0, weight=1)
            game_rules.grid_rowconfigure(1, weight=1)
            game_rules.grid_columnconfigure(0, weight=1)
            spieler_name_anzeigen_label.grid(row=0, column=0)
            beenden_button1.grid(row=1, column=0)

        game_rules = tkinter.Toplevel(self.fenster)
        game_rules.title(Constants.WINDOW_TITLE_RUNNING_GAME)
        game_rules.geometry("%dx%d+0+0" % (Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        beenden_button1 = Button(game_rules, text=Constants.GAME_MAIN_MENU_BUTTON, command=game_rules.destroy)
        beenden_button1.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)
        spieler_name_anzeigen_label = Label(game_rules, text=Constants.GAME_RULES_CONTENT, font=("Arial", 11),
                                            anchor="w", justify=LEFT)
        game_rules.wm_overrideredirect(True)
        build_grid()

    def __info_window(self) -> None:
        """
        Generate and set the window content of the info window.
        :return: None
        """

        def build_grid() -> None:
            """
            Set position of gui elements inside the grid.
            :return: None
            """
            game_info.grid_rowconfigure(0, weight=1)
            game_info.grid_rowconfigure(1, weight=1)
            game_info.grid_columnconfigure(0, weight=1)
            spieler_name_anzeigen_label.grid(row=0, column=0)
            beenden_button1.grid(row=1, column=0)

        game_info = tkinter.Toplevel(self.fenster)
        game_info.title(Constants.WINDOW_TITLE_RUNNING_GAME)
        game_info.geometry("%dx%d+0+0" % (Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        beenden_button1 = Button(game_info, text=Constants.GAME_MAIN_MENU_BUTTON, command=game_info.destroy)
        beenden_button1.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)
        spieler_name_anzeigen_label = Label(game_info, text=Constants.GAME_INFO_CONTENT, font=("Arial", 20))
        game_info.wm_overrideredirect(True)
        build_grid()

    def __start_demo_instance(self):
        self.spieler1_eingabefeld.delete(0, END)
        self.spieler2_eingabefeld.delete(0, END)
        self.spieler1_eingabefeld.set(Constants.GAME_ENVIRONMENT2_PLACEHOLDER)
        self.spieler2_eingabefeld.set(Constants.GAME_ENVIRONMENT_PLACEHOLDER)
        self.game_mode_container.set(2)
        self.__start_game_instance()

    def __start_game_instance(self):
        spieler_namen = (self.spieler1_eingabefeld.get(), self.spieler2_eingabefeld.get())
        if self.game_mode_container.get() == 0:
            if (len(spieler_namen[0]) > 0) & (len(spieler_namen[1]) > 0):
                self.__game_window()
            else:
                messagebox.showwarning(message=Constants.GAME_PVE_MSG_MISSING_NAME)
        else:
            if len(spieler_namen[0]) > 0:
                self.__game_window()
            else:
                messagebox.showwarning(message=Constants.GAME_PVE_MSG_MISSING_NAME)

    @staticmethod
    def __action_shutdown_system() -> None:
        """
        Shutdown the running operating system.
        :return: None
        """
        print("Shutting down OS")

if __name__ == "__main__":
    gui = GUI()
