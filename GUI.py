import time
import tkinter
from tkinter import *
from tkinter import messagebox
import pygame
import threading
import Constants
from Dummy import Dummy


class GUI(object):

    def __init__(self):
        self.game_instance = Dummy()
        self.active_game_thread = threading.Thread(target=self.game_instance.play)

        self.fenster = Tk()
        self.fenster.title(Constants.WINDOW_TITLE)
        self.fenster.geometry("%dx%d+0+0" % (Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        pygame.init()
        # pygame.mixer.music.load('sounds/FallenderStein.mp3') #todo SOUND STUFF

        self.current_round_number = 0
        self.spieler1_eingabefeld = None
        self.spieler2_eingabefeld = None
        self.game_mode_container = IntVar()
        self.game_difficulty_container = IntVar()
        self.sound_state_container = IntVar()

        self.main_window()

        # in der Eingabeschleife auf die Eingabe durch den Benutzer warten.
        self.fenster.mainloop()

    def main_window(self):
        @staticmethod
        def action_get_info_dialog():
            m_text = "\
                ************************\n\
                Autoren: OFR Sonnberger und OFRzS Blank\n\
                Date: Schuljahr 2023/2024\n\
                Version: 2.0\n\
                ************************"
            messagebox.showinfo(message=m_text, title="Infos")

        @staticmethod
        def action_get_rules_dialog():
            m_text = "\
                ************************\n\
                Spielregeln für 4 Gewinnt\n\
                Text Text Text\n\
                Viel Erfolg und Spaß!\n\
                ************************"
            messagebox.showinfo(message=m_text, title="Spielregeln")

        def build_grid():
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

        def reset_game_container_values():
            self.game_mode_container.set(0)
            self.game_difficulty_container.set(0)
            self.sound_state_container.set(0)

        def ctrl_sound_state_change():
            if self.sound_state_container.get() == 0:
                print("Es sollte Musik laufen!")
                # pygame.mixer.music.play(-1) #todo SOUND STUFF
                # pygame.mixer.music.set_volume(.5) #todo SOUND STUFF
            else:
                print("Jetzt läuft keine Musik!")
                pygame.mixer.music.stop()

        def ctrl_game_mode_change():
            if self.game_mode_container.get() == 0:
                spieler1_label.grid(row=3, column=0)
                self.spieler1_eingabefeld.grid(row=3, column=1)
                spieler2_label.grid(row=4, column=0)
                self.spieler2_eingabefeld.grid(row=4, column=1)

                cpuLevel_Label.grid_forget()
                radio_leicht.grid_forget()
                radio_mittel.grid_forget()
                radio_schwer.grid_forget()
            else:
                spieler1_label.grid(row=3, column=0)
                self.spieler1_eingabefeld.grid(row=3, column=1)
                spieler2_label.grid_forget()
                self.spieler2_eingabefeld.grid_forget()

                cpuLevel_Label.grid(row=5, column=1)
                radio_leicht.grid(row=6, column=0)
                radio_mittel.grid(row=6, column=1)
                radio_schwer.grid(row=6, column=2)

        spielmodus_label = Label(self.fenster, text=Constants.GAME_MODE_LABEL)
        willkommen_label = Label(self.fenster, text=Constants.GAME_WELCOME_LABEL)

        spieler1_label = Label(self.fenster, text=Constants.GAME_PLAYER_1_LABEL)
        spieler2_label = Label(self.fenster, text=Constants.GAME_PLAYER_2_LABEL)

        self.spieler1_eingabefeld = Entry(self.fenster, bd=5, width=40)
        self.spieler2_eingabefeld = Entry(self.fenster, bd=5, width=40)

        # todo JUST FOR DEBUG
        self.spieler1_eingabefeld.insert(0, "TEST_1")
        self.spieler2_eingabefeld.insert(0, "TEST_2")
        # todo /JUST FOR DEBUG

        radio_oneOnOne = Radiobutton(self.fenster,
                                     text="Spieler gegen Spieler",
                                     padx=20,
                                     variable=self.game_mode_container,
                                     command=ctrl_game_mode_change,
                                     value=0)
        radio_oneOnCpu = Radiobutton(self.fenster,
                                     text="Spieler gegen Computer",
                                     padx=20,
                                     variable=self.game_mode_container,
                                     command=ctrl_game_mode_change,
                                     value=1)

        cpuLevel_Label = Label(self.fenster, text="Wählen sie die Schwierigkeit aus:")

        radio_leicht = Radiobutton(self.fenster,
                                   text="Leicht",
                                   padx=20,
                                   variable=self.game_difficulty_container,
                                   value=0)
        radio_mittel = Radiobutton(self.fenster,
                                   text="Mittel",
                                   padx=20,
                                   variable=self.game_difficulty_container,
                                   value=1)
        radio_schwer = Radiobutton(self.fenster,
                                   text="Schwer",
                                   variable=self.game_difficulty_container,
                                   padx=20,
                                   value=2)

        start_button = Button(self.fenster, text="Spiel starten", command=self.start_game_instance)

        sound_Label = Label(self.fenster, text="Sound: ")
        radio_sound_on = Radiobutton(self.fenster, text="On", padx=20, variable=self.sound_state_container,
                                     value=0, command=ctrl_sound_state_change)
        radio_sound_off = Radiobutton(self.fenster, text="Off", padx=20, variable=self.sound_state_container,
                                      value=1, command=ctrl_sound_state_change)

        spielregeln_button = Button(self.fenster, text="Spielregeln", command=action_get_rules_dialog)
        info_button = Button(self.fenster, text="Info", command=action_get_info_dialog)
        end_application_button = Button(self.fenster, text=Constants.GAME_END_BUTTON, command=self.fenster.quit)
        shutdown_system_button = Button(self.fenster, text=Constants.GAME_SHUTDOWN_BUTTON,
                                        command=self.action_shutdown_system)

        # Set Element Position
        build_grid()

        # Fenster während des Spiels
        ctrl_sound_state_change()
        reset_game_container_values()

    def game_window(self):
        def action_end_game():
            self.game_instance.stop()
            spiele_fenster.quit()

        def change_active_player(current_player: int):
            if current_player:
                spieler_name_anzeigen_label2.grid_forget()
                spieler_name_anzeigen_label1.grid(row=0, column=0)
            else:
                spieler_name_anzeigen_label1.grid_forget()
                spieler_name_anzeigen_label2.grid(row=0, column=0)

        spiele_fenster = tkinter.Toplevel(self.fenster)
        spiele_fenster.title("Sie spielen gerade 4 Gewinnt")
        spiele_fenster.geometry("%dx%d+0+0" % (Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))

        erneut_spielen_button = Button(spiele_fenster, text="Spiel erneut Starten", command=change_active_player) ## todo warum hier changePlayer
        beenden_button1 = Button(spiele_fenster, text="Beenden", command=action_end_game)
        spieler_name_anzeigen_label1 = Label(spiele_fenster,
                                             text="Spieler " + self.spieler1_eingabefeld.get() + " ist dran")
        spieler_name_anzeigen_label2 = Label(spiele_fenster,
                                             text="Spieler " + self.spieler2_eingabefeld.get() + " ist dran")
        spiele_fenster.wm_overrideredirect(True)

        erneut_spielen_button.grid(row=1, column=1)
        beenden_button1.grid(row=1, column=2)

        self.game_instance.set_gui_update_method(change_active_player)
        self.active_game_thread.start()

    def start_game_instance(self):
        print("Spiel wird gestartet!")
        spieler_namen = (self.spieler1_eingabefeld.get(), self.spieler2_eingabefeld.get())
        print("Spieler1: ", spieler_namen[0])
        print("Spieler2: ", spieler_namen[1])
        if self.game_mode_container.get() == 0:
            if (len(spieler_namen[0]) > 0) & (len(spieler_namen[1]) > 0):
                self.game_window()
            else:
                messagebox.showwarning(message="Es sind nicht für alle Spieler Namen eingetragen")
        else:
            if len(spieler_namen[0]) > 0:
                self.game_window()
            else:
                messagebox.showwarning(message="Der Spieler 1 hat keinen Namen")

    @staticmethod
    def action_shutdown_system():
        print("Shutting down OS")  # todo implement os shutdown function


if __name__ == "__main__":
    gui = GUI()
