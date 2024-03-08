import time
import tkinter
from tkinter import *
from tkinter import messagebox
import pygame
import threading
import Constants
# from GLDummy import GLDummy  ##todo entfernen, wenn debug beendet
from GameLogic import GameLogic


# from GameLogic import GameLogic ##todo einkommentieren, für real stuff


class GUI(object):

    def __init__(self):
        self.game_instance = GameLogic() #todo einkommentieren, für real stuff
        # self.game_instance = GLDummy()  ##todo entfernen, wenn debug beendet
        self.active_game_thread = None

        self.fenster = Tk()
        self.fenster.title(Constants.WINDOW_TITLE)
        self.fenster.geometry("%dx%d+0+0" % (Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        pygame.init()
        # pygame.mixer.music.load('sounds/FallenderStein.mp3') #todo SOUND STUFF

        self.current_round_number = 0
        self.spieler1_eingabefeld = None
        self.spieler2_eingabefeld = None
        self.game_mode_container = IntVar() # todo 0 = 1v1 1=PvE
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

        def ctrl_sound_state_change() -> None:
            """
            Change the value of the sound state data container "sound_state_container".
            :return: None
            """
            if self.sound_state_container.get() == 0:
                print("Es sollte Musik laufen!")  # todo rm debug msg
                # pygame.mixer.music.play(-1) #todo SOUND STUFF
                # pygame.mixer.music.set_volume(.5) #todo SOUND STUFF
            else:
                print("Jetzt läuft keine Musik!")  # todo rm debug msg
                pygame.mixer.music.stop()

        def ctrl_game_mode_change() -> None:
            """
            Change the value of the game mode data container "game_mode_container".
            :return: None
            """
            if self.game_mode_container.get() == 0:
                spieler1_label.grid(row=3, column=0)
                self.spieler1_eingabefeld.grid(row=3, column=1)
                spieler2_label.grid(row=4, column=0)
                self.spieler2_eingabefeld.grid(row=4, column=1)

                cpuLevel_Label.grid_forget()
                radio_leicht.grid_forget()
                radio_schwer.grid_forget()
            else:
                spieler1_label.grid(row=3, column=0)
                self.spieler1_eingabefeld.grid(row=3, column=1)
                spieler2_label.grid_forget()
                self.spieler2_eingabefeld.grid_forget()

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
                                   value=2)

        start_button = Button(self.fenster, text=Constants.GAME_START_BUTTON, command=self.__start_game_instance)
        start_button.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)

        sound_Label = Label(self.fenster, text=Constants.GAME_SOUND_LABEL)
        radio_sound_on = Radiobutton(self.fenster, text=Constants.GAME_SOUND_LABEL_ON, padx=20,
                                     variable=self.sound_state_container,
                                     value=0, command=ctrl_sound_state_change)
        radio_sound_off = Radiobutton(self.fenster, text=Constants.GAME_SOUND_LABEL_OFF, padx=20,
                                      variable=self.sound_state_container,
                                      value=1, command=ctrl_sound_state_change)

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
        ctrl_sound_state_change()
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
            self.game_instance.stop()
            spiele_fenster.quit()

        def change_active_player(current_player: int) -> None:
            """
            Change the display (window content) for current player.
            :param current_player: player for the next turn.
            :return: None
            """
            if not current_player:
                spieler_name_anzeigen_label['text'] = Constants.GAME_CURRENT_PLAYER_LABEL.format(
                    cplayer=self.spieler1_eingabefeld.get())
                spieler_name_anzeigen_label.configure(bg=Constants.GAME_COLOR_BACKGROUND_PLAYER_1)
                spiele_fenster.configure(bg=Constants.GAME_COLOR_BACKGROUND_PLAYER_1)
            else:
                spieler_name_anzeigen_label['text'] = Constants.GAME_CURRENT_PLAYER_LABEL.format(
                    cplayer=self.spieler2_eingabefeld.get())
                spieler_name_anzeigen_label.configure(bg=Constants.GAME_COLOR_BACKGROUND_PLAYER_2)
                spiele_fenster.configure(bg=Constants.GAME_COLOR_BACKGROUND_PLAYER_2)

        def close_top_window() -> None:
            """
            Close the running game window and show the main menu window.
            :return: None
            """
            spiele_fenster.destroy()

        def build_grid() -> None:
            """
            Set position of gui elements inside the grid.
            :return: None
            """
            spiele_fenster.grid_rowconfigure(0, weight=1)
            spiele_fenster.grid_rowconfigure(1, weight=1)
            spiele_fenster.grid_columnconfigure(0, weight=1)
            spieler_name_anzeigen_label.grid(row=0, column=0)
            beenden_button1.grid(row=1, column=0)

        spiele_fenster = tkinter.Toplevel(self.fenster)
        spiele_fenster.title(Constants.WINDOW_TITLE_RUNNING_GAME)
        spiele_fenster.geometry("%dx%d+0+0" % (Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        beenden_button1 = Button(spiele_fenster, text=Constants.GAME_END_BUTTON, command=action_end_game)
        beenden_button1.config(width=Constants.GAME_BTN_SIZE_WIDTH, height=Constants.GAME_BTN_SIZE_HEIGHT)
        spieler_name_anzeigen_label = Label(spiele_fenster, font=("Arial", 25))
        spiele_fenster.wm_overrideredirect(True)
        build_grid()
        change_active_player(0)

        self.active_game_thread = threading.Thread(target=self.game_instance.run_game)
        self.game_instance.set_mode_and_difficulty(self.game_mode_container.get(), self.game_difficulty_container.get())
        self.game_instance.set_gui_update_method(change_active_player)
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
        print("Shutting down OS")  # todo implement os shutdown function


## todo [done] GUI Schick machen... Schrift größer, Hintergrundfarbe f. Spieler setzen
## todo [done] In GUI und GameLogic alle Methoden, die nicht von außen gebraucht werden mit __ verstecken
## todo [done] Konstanten auslagern
## todo [done] Methoden Doku und Kommentare weg
## todo [done] Spielregeln und Info Buttons aktivieren und weitere Ansichten hierfür implementieren (mit "Back" Button)
## todo [done] InfoPage formatieren
## todo [done] RadioButton für Schwierigkeitsstufe MITTEL kann gelöscht werden
## todo [done] Spielregeln einbinden
## todo die drei Sounds implementieren
## todo Add Computer Player Actions... in zwei Schwierigkeitsgraden
## todo Fix Durchlauftext bei Start des Spiels (oder schauen, wie er mit Musik wirkt)
## todo (optional) Check how to show Bildschirmtastatur
## todo (optional) Check how to fullscreen (ohne Titelleiste und ohne Icons)
## todo (optional) Check how to hide mouse
## todo Add EasterEgg...
if __name__ == "__main__":
    gui = GUI()
