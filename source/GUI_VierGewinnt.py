import tkinter
from tkinter import *
from tkinter import messagebox
import pygame

fenster = Tk()
fenster.title("4 Gewinnt")


def minimize_test():
    fenster.update_idletasks()
    fenster.wm_overrideredirect(False)
    fenster.state('iconic')


def maximize_test():
    fenster.update_idletasks()
    fenster.wm_overrideredirect(True)
    fenster.state('normal')


count = 1


def minimize():
    global count
    # make window minimize
    # weil boolscher Wert, true =1 false =0
    if count % 2:
        # blendet die Fensterleiste aus
        fenster.wm_overrideredirect(True)
        count = count + 1
        print(count)
    else:
        # blendet die Fensterleiste ein
        fenster.wm_overrideredirect(False)
        count = count + 1
        print(count)


def action_Spieler_wechseln(spielerNameAnzeigen_Label1, spielerNameAnzeigen_Label2):
    if count % 2:
        spielerNameAnzeigen_Label2.grid_forget()
        spielerNameAnzeigen_Label1.grid(row=3, column=1)


    else:
        spielerNameAnzeigen_Label1.grid_forget()
        spielerNameAnzeigen_Label2.grid(row=3, column=1)


def spielstarten():
    print("Spiel wird gestartet!")
    spielerName1 = get_SpielerName1()
    spielerName2 = get_SpielerName2()
    print(spielerName1)
    print(spielerName2)

    if var1.get() == 0:

        if (len(spielerName1) > 0) & (len(spielerName2) > 0):
            action_oeffne_spieleFenster()

        else:
            messagebox.showwarning(message="Du Spasst, Fehler 1")
    else:

        if len(spielerName1) > 0:
            action_oeffne_spieleFenster()
        else:
            messagebox.showwarning(message="Du Spasst")


def onRadioButtonChange():
    if var1.get() == 0:

        spieler1_label.grid(row=3, column=0)
        spieler1_eingabefeld.grid(row=3, column=1)
        spieler2_label.grid(row=4, column=0)
        spieler2_eingabefeld.grid(row=4, column=1)

        cpuLevel_Label.grid_forget()
        radio_leicht.grid_forget()
        radio_mittel.grid_forget()
        radio_schwer.grid_forget()
    else:
        spieler1_label.grid(row=3, column=0)
        spieler1_eingabefeld.grid(row=3, column=1)
        spieler2_label.grid_forget()
        spieler2_eingabefeld.grid_forget()

        cpuLevel_Label.grid(row=5, column=1)
        radio_leicht.grid(row=6, column=0)
        radio_mittel.grid(row=6, column=1)
        radio_schwer.grid(row=6, column=2)


pygame.init()
pygame.mixer.music.load('sounds/FallenderStein.mp3')


def onRadioButtonSound():
    if var3.get() == 0:
        print("Es sollte Musik laufen!")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(.5)

    else:
        print("Jetzt läuft keine Musik!")
        pygame.mixer.music.stop()


def get_SpielerName1():
    return spieler1_eingabefeld.get()


def get_SpielerName2():
    return spieler2_eingabefeld.get()


def action_get_info_dialog():
    m_text = "\
    ************************\n\
    Autoren: OFR Sonnberger und OFRzS Blank\n\
    Date: Schuljahr 2023/2024\n\
    Version: 2.0\n\
    ************************"
    messagebox.showinfo(message=m_text, title="Infos")


# Fenster nach vorneholen mit z-index
# bildschirm größe anpassen, info fesnter position anpassen mit x,y

def action_get_spielregeln_dialog():
    m_text = "\
    ************************\n\
    Spielregeln für 4 Gewinnt\n\
    Text Text Text\n\
    Viel Erfolg und Spaß!\n\
    ************************"
    messagebox.showinfo(message=m_text, title="Spielregeln")


spielmodus_label = Label(fenster, text="Spielmodus wählen:")

var1 = IntVar()
var2 = IntVar()
var3 = IntVar()


def action_Variablen_setzen():
    var1.set(0)
    var2.set(0)
    var3.set(0)


willkommen_label = Label(fenster, text="Willkommen bei 4 Gewinnt. Bitte wählen sie ihr Spiel.")

spieler1_label = Label(fenster, text="Spieler 1: ")
spieler2_label = Label(fenster, text="Spieler 2: ")

spieler1_eingabefeld = Entry(fenster, bd=5, width=40)
spieler2_eingabefeld = Entry(fenster, bd=5, width=40)

radio_oneOnOne = Radiobutton(fenster,
                             text="Spieler gegen Spieler",
                             padx=20,
                             variable=var1,
                             command=onRadioButtonChange,
                             value=0)
radio_oneOnCpu = Radiobutton(fenster,
                             text="Spieler gegen Computer",
                             padx=20,
                             variable=var1,
                             command=onRadioButtonChange,
                             value=1)

cpuLevel_Label = Label(fenster, text="Wählen sie die Schwierigkeit aus:")

radio_leicht = Radiobutton(fenster,
                           text="Leicht",
                           padx=20,
                           variable=var2,
                           value=0)
radio_mittel = Radiobutton(fenster,
                           text="Mittel",
                           padx=20,
                           variable=var2,
                           value=1)
radio_schwer = Radiobutton(fenster,
                           text="Schwer",
                           variable=var2,
                           padx=20,
                           value=2)

start_button = Button(fenster, text="Spiel starten", command=spielstarten)

sound_Label = Label(fenster, text="Sound: ")
radio_sound_on = Radiobutton(fenster, text="On", padx=20, variable=var3, value=0, command=onRadioButtonSound)
radio_sound_off = Radiobutton(fenster, text="Off", padx=20, variable=var3, value=1, command=onRadioButtonSound)

spielregeln_button = Button(fenster, text="Spielregeln", command=action_get_spielregeln_dialog)
info_button = Button(fenster, text="Info", command=action_get_info_dialog)
beenden_button = Button(fenster, text="Beenden", command=fenster.quit)
admin_button = Button(fenster, text="Adminkram", command=minimize_test)

willkommen_label.grid(row=0, column=1)

spielmodus_label.grid(row=1, column=1)
radio_oneOnOne.grid(row=2, column=0)
radio_oneOnCpu.grid(row=2, column=2)

spieler1_label.grid(row=3, column=0)
spieler1_eingabefeld.grid(row=3, column=1)
spieler2_label.grid(row=4, column=0)
spieler2_eingabefeld.grid(row=4, column=1)

start_button.grid(row=10, column=1)

sound_Label.grid(row=11, column=0)
radio_sound_on.grid(row=12, column=0)
radio_sound_off.grid(row=13, column=0)

spielregeln_button.grid(row=13, column=1)
info_button.grid(row=13, column=2)
beenden_button.grid(row=14, column=1)
admin_button.grid(row=14, column=2)

# Vollbildmodus bei Start
w, h = fenster.winfo_screenwidth(), fenster.winfo_screenheight()
fenster.geometry("%dx%d+0+0" % (w, h))

# Fenster während des Spiels
counter = 0


def action_oeffne_spieleFenster():
    def spieler_wechseln():
        global counter

        counter = counter + 1
        if counter % 2:
            spielerNameAnzeigen_Label2.grid_forget()
            spielerNameAnzeigen_Label1.grid(row=0, column=0)

        else:
            spielerNameAnzeigen_Label1.grid_forget()
            spielerNameAnzeigen_Label2.grid(row=0, column=0)

    spieleFenster = tkinter.Toplevel(fenster)
    spieleFenster.title("Sie spielen gerade 4 Gewinnt")

    w, h = spieleFenster.winfo_screenwidth(), spieleFenster.winfo_screenheight()
    spieleFenster.geometry("%dx%d+0+0" % (w, h))

    erneutSpielenButton = Button(spieleFenster, text="Spiel erneut Starten", command=spieler_wechseln)
    beenden_button1 = Button(spieleFenster, text="Beenden", command=spieleFenster.quit)
    spielerNameAnzeigen_Label1 = Label(spieleFenster, text="Spieler " + spieler1_eingabefeld.get() + " ist dran")
    spielerNameAnzeigen_Label2 = Label(spieleFenster, text="Spieler " + spieler2_eingabefeld.get() + " ist dran")
    spieleFenster.wm_overrideredirect(True)

    erneutSpielenButton.grid(row=1, column=1)
    beenden_button1.grid(row=1, column=2)


maximize_test()
minimize()
onRadioButtonSound()
action_Variablen_setzen()

# in der Eingabeschleife auf die Eingabe durch den Benutzer warten.
fenster.mainloop()

# def main():
#    tuedinge()


if __name__ == "__main__":
    fenster.mainloop()