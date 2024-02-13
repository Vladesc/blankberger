### Vier Gewinnt Spiel
### Ansteuerung einer 6x7 LED-Matrix

# ------------------------------------------------------------------------#
#                                 HEAD                                   #
# ------------------------------------------------------------------------#
### Bibliotheken
import RPi.GPIO as GPIO  # Raspberry Pi Standart GPIO Bibliothek
import time  # Bibliothek fuer time-Funktionen
import sys  # This module provides a number of functions and variables that can

# be used to manipulate different parts of the Python runtime environment (z.B. sys.exit())

### Initialisierung
GPIO.setmode(GPIO.BCM)  # Verwendung der , wie sie auf dem Board heissen
GPIO.setwarnings(False)  # Deaktiviere GPIO-Warnungen
GPIO.cleanup()  # Zuruecksetzen aller GPIO-Pins

G_NOT = 14  # Output Enable   Pinnamen      OUTPUT
RCK = 15  # Storage Register Clock        OUTPUT
SCK = 18  # Shift RegisterClock           OUTPUT
SCLR_NOT = 23  # Shift Register Clear          OUTPUT
SI = 24  # Serial Data                   OUTPUT
BUTTON_0 = 2  # Button 1 von Links                 INPUT
BUTTON_1 = 3  # Button 2 von Links                 INPUT
BUTTON_2 = 4  # Button 3 von Links                 INPUT
BUTTON_3 = 17  # Button 4 von Links                 INPUT
BUTTON_4 = 27  # Button 5 von Links                 INPUT
BUTTON_5 = 22  # Button 6 von Links                 INPUT
BUTTON_6 = 10  # Button 7 von Links                 INPUT

### Setup GPIOs (Declare GPIOs as INPUT or OUTPUT)
# WICHTIG: Da mit PULL-UP-Widerstand gearbeitet wird, muss der Button den PIN auf LOW ziehen
#          -> Durch Buttondruck wird Pin auf GND gelegt! -> HIGH-Signal in Python
GPIO.setup(G_NOT, GPIO.OUT)  # OUTPUT
GPIO.setup(RCK, GPIO.OUT)  # OUTPUT
GPIO.setup(SCK, GPIO.OUT)  # OUTPUT
GPIO.setup(SCLR_NOT, GPIO.OUT)  # OUTPUT
GPIO.setup(SI, GPIO.OUT)  # OUTPUT
GPIO.setup(BUTTON_0, GPIO.IN, GPIO.PUD_UP)  # BUTTON_1 -> IN (mit Pull-Up Wiederstand, standartmaessig auf HIGH)
GPIO.setup(BUTTON_1, GPIO.IN, GPIO.PUD_UP)  # BUTTON_2 -> IN (mit Pull-Up Wiederstand, standartmaessig auf HIGH)
GPIO.setup(BUTTON_2, GPIO.IN, GPIO.PUD_UP)  # BUTTON_3 -> IN (mit Pull-Up Wiederstand, standartmaessig auf HIGH)
GPIO.setup(BUTTON_3, GPIO.IN, GPIO.PUD_UP)  # BUTTON_4 -> IN (mit Pull-Up Wiederstand, standartmaessig auf HIGH)
GPIO.setup(BUTTON_4, GPIO.IN, GPIO.PUD_UP)  # BUTTON_5 -> IN (mit Pull-Up Wiederstand, standartmaessig auf HIGH)
GPIO.setup(BUTTON_5, GPIO.IN, GPIO.PUD_UP)  # BUTTON_6 -> IN (mit Pull-Up Wiederstand, standartmaessig auf HIGH)
GPIO.setup(BUTTON_6, GPIO.IN, GPIO.PUD_UP)  # BUTTON_7 -> IN (mit Pull-Up Wiederstand, standartmaessig auf HIGH)

### Globale Variablen
# Innerhalb einer Funktion koennen globale Variablen lesend aufgerufen werden
# Will man eine globale Variable innerhalb einer Funktion veraendern,
# muss man diese mit "global ..." in der Funktion definieren!
# Eine innerhalb einer Funktion definierte Variable ist immer lokal
reset = 0
button_state = 0  # Variable fuer Button-Funktion (siehe 'def Button(button_nr)')
button_old = 0  # Variable fuer Button-Funktion (siehe 'def Button(button_nr)')
columns = 14  # 7 Spalten mit jeweils zwei Farben -> 14 (eigentlich 16, da Scheiberegister 16 Bits braucht, letzten 2 Bits sind beliebig und werden in der Funktion send_data() seperat mitgesendet)
columns_unused = [0,
                  0]  # Anzahl der unbenutzten Spalten (=Anzahl der im Schieberegisterbaustein NICHT benutzten Ausgaenge, HIGH-SIDE)
rows = 6  # 6 Zeilen (eigentlich 8, da Schieberegister 8 Bit braucht, letzten 2 Bits sind beliebig und werden in der Funktion send_data() seperat mitgesendet)
rows_unused = [0,
               0]  # Anzahl der unbenutzten Zeilen (=Anzahl der im Schieberegisterbaustein nicht benutzten Ausgaenge, LOW-SIDE)
clk_delay = 0.00000001  # Delay zur sicheren Erkennung der Signalflanken (siehe Datenblatt Schieberegister 74HC595), mind. 6ns
data = [0]  # Datenvektor mit den aktuellen Daten des Spielfeldes, Initialwert
row = [1, 0, 0, 0, 0, 0,  # Zeile1
       0, 1, 0, 0, 0, 0,  # Zeile2
       0, 0, 1, 0, 0, 0,  # Zeile3
       0, 0, 0, 1, 0, 0,  # Zeile4
       0, 0, 0, 0, 1, 0,  # Zeile5
       0, 0, 0, 0, 0, 1]  # Zeile6
pos = 0  # aktuelle Position in der Matrix (im Datenverktor -> pos = Index des Datenvektors data)
pos_max = 12  # maximale Position in einer Zeile (fuer gruen, rot gilt pos_max+1)
player_nr: int = 0  # Player Number (0...Player 1, 1...Player 2)
win_row = [0, 0, 0,
           0]  # Initialwert des Gewinnvekors -> Vektor, der die Positionen der zum Sieg fuehrenden Daten speichert, also Positionen der '4 in einer Reihe'


# ------------------------------------------------------------------------#
#                                 Functions                              #
# ------------------------------------------------------------------------#
def button(button_nr):
    # Funktion gibt ein Signal button_state aus, wenn der geforderte Taster gedrueckt wird"
    # Dieses Signal kann nur ausgegeben werden, wenn button_state zuvor 0 war"
    # -> dadurch werden wiederholte Aufrufe der Funktion bei laenger betaetigtem Taster vermieden"
    global button_state
    global button_old

    # Setze button_state auf 1, wenn BUTTON gedrueckt (GPIO.input == 0 wegen Pull-Up) und button_state == 0
    if GPIO.input(button_nr) == 0 and button_state == 0:
        button_old = button_nr  # Merke aktuelle button_nr
        button_state = 1  # Setze button_state auf 1
        time.sleep(0.01)  # Zeitverzoegerung, um Tasterprellen zu umgehen
        return button_state  # Gib den Wert button_state zurueck

    # Setze button_state auf 0, sobald zuvor betaetigte BUTTON (button_old) losgelassen wird
    elif GPIO.input(button_nr) == 1 and button_state == 1 and button_old == button_nr:
        button_state = 0  # Diese elif-Anweisung verhindert, dass der Taster bei durchgehendem Druecken neu ausgeloest wird
        time.sleep(0.01)  # Zeitverzoegerung, um Tasterprellen zu umgehen
        # Erfolgt kein Return-Befehlt, liefert die Funktion den Wert 'none'


def send_data(data):
    # Funktion sendet 'data' an Shift-Register und aktiviert Ausgabe an das Storage-Register
    # ->Ausgabe der Daten im Storgage-Register auf die LED-Matrix
    # Dabei wird jede Zeile seperat angesteuert
    # -> Immer nur eine Zeile der LED-Matrix wird beschrieben, danach wird diese geloescht und die naechste Zeile beschrieben
    r = 0  # Zaehlvariable zum Auswaehlen der einzelnen Zeilen im Vektor 'data' und 'row'

    # Schleife sendet (6+2)-Bit-Vektor 'row' mit Information, welche Zeile angesteuert werden soll
    # und (14+2)-Bit-Vektor 'data' mit Information, was in der entsprechenden Zeile angezeigt werden soll
    # (welche LEDs in der entsprechenden Zeile leuchten sollen)
    while r < rows:
        clear_shift_register()  # Funktionsaufruf, loesche alle Werte im Shift-Register
        set_shift_register(row[
                           0 + r * rows:rows + r * rows])  # Funktionsaufruf, sende 6-Bit-Vektor 'row' mit Information, welche Zeile angesteuert werden soll
        set_shift_register(rows_unused)  # Vektor [0,0] fuer die NICHT benutzten Ausgaenge der Schieberegister HIGH-Side
        set_shift_register(data[
                           0 + r * columns:columns + r * columns])  # Funktionsaufruf, sende 14-Bit-Vektor 'data' mit Information, was in der entsprechenden Zeile angezeigt werden soll
        set_shift_register(
            columns_unused)  # Vektor [0,0] fuer die NICHT benutzten Ausgaenge der Schieberegister LOW-Side
        set_storage_register()  # Funktionsaufruf, Ausgabe der Daten im Shift-Register an LED-Matrix
        r = r + 1


def output_enable():
    # Funktion aktiviert Ausgaenge der Scheiberegisterbausteine
    GPIO.output(G_NOT, GPIO.LOW)  # Qa bis Qh aktivieren
    time.sleep(clk_delay)  # Delay zur sicheren Erkennung der Signalpegel


def output_disable():
    # Funktion deaktiviert Ausgaenge der Scheiberegisterbausteine
    GPIO.output(G_NOT, GPIO.HIGH)  # Qa bis Qh deaktivieren
    time.sleep(clk_delay)  # Delay zur sicheren Erkennung der Signalpegel


def clear_shift_register():
    # Funktion loescht Daten im Shift-Register
    GPIO.output(SCLR_NOT, GPIO.LOW)  # Shift-Register loeschen (solange SCLR_NOT LOW ist)
    time.sleep(clk_delay)
    GPIO.output(SCLR_NOT, GPIO.HIGH)  # Shift-Register wird nichtmehr geloescht
    time.sleep(clk_delay)


def set_shift_register(data):
    # Funktion senden 'data' an Shift-Register
    i = 0  # Zaehlvariable, Index -> data[i]
    data_length = len(data)  # Laenge des Datenvektors bestimmen

    while i < data_length:
        # Hier wird geschaut ob das aktuell zu uebergebende Bit 1 oder 0 ist
        if data[i] == 1:
            GPIO.output(SI, GPIO.HIGH)  # Wenn data[i] == 1 -> SERIAL DATA OUTPUT 'SI'auf HIGH
            time.sleep(clk_delay)
        elif data[i] == 0:
            GPIO.output(SI, GPIO.LOW)  # Wenn data[i] == 0 -> SERIAL DATA OUTPUT 'SI' auf LOW
            time.sleep(clk_delay)

        GPIO.output(SCK, GPIO.HIGH)  # Uebergabe des Serial Data Wertes in erste Stufe des Shift-Registers
        time.sleep(clk_delay)  # und Weitergabe der aktuellen Werte des Shiftregisters einer Stufe
        GPIO.output(SCK, GPIO.LOW)  # auf die Naechste bei LOW-HIGH-Flanke
        time.sleep(clk_delay)

        i = i + 1


def set_storage_register():
    # Funktion gibt aktuellen Daten im Shift-Register an Storage-Register weiter bei LOW-HIGH-Flanke an RCK
    # (Das Storage-Register (=Ausgang) gibt Daten direkt auf die LED-Matrix bzw. die Treiberstufen vor der Matrix,
    # sofern die Ausgaenge Qa bis Qh der Schieberegisterbausteine aktiviert wurden (siehe 'def Output_Enable()')
    GPIO.output(RCK, GPIO.HIGH)
    time.sleep(clk_delay)
    GPIO.output(RCK, GPIO.LOW)
    time.sleep(clk_delay)


def sample(sample_nr):
    # Funktion enthaelt verschiedene Samples, welche mithilfe der Funktion Send_Data() auf der LED-Matrix
    # angezeigt werden koennen, z.B.: Send_Data(Sample(2))
    # WICHTIG: Die LED-Matrix besitzt nur 7 LED-Spalten mit je 2 Farben (gruen(g), rot(r)) -> 14 Spalten
    #          Da die Schieberegisterbausteine zur Ansteuerung der Spalten aber 2*8=16 Ausgaenge besitzen,
    #          muessen die 2 ungenutzten Ausgaenge (Spalte 15 und 16) mitgesendet werden
    #          Diese werden in der Funktion send_data() seperat mitgesendet und muessen hier nit extra eingetragen werden

    if sample_nr == 0:  # Startbildschirm
        #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
        #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        data = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile1
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile2
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile3
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile4
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile5
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Zeile6

    if sample_nr == 1:  # "HI"
        #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
        #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        data = [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0,  # Zeile1
                0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0,  # Zeile2
                0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0,  # Zeile3
                0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0,  # Zeile4
                0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0,  # Zeile5
                0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0]  # Zeile6

    if sample_nr == 2:  # "DU"
        #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
        #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        data = [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1,  # Zeile1
                1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1,  # Zeile2
                1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1,  # Zeile3
                1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1,  # Zeile4
                1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1,  # Zeile5
                1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1]  # Zeile6

    if sample_nr == 3:  # Spieler 1 gewinnt
        #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
        #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        data = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,  # Zeile1
                1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0,  # Zeile2
                1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0,  # Zeile3
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,  # Zeile4
                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,  # Zeile5
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Zeile6

    if sample_nr == 4:  # Spieler 2 gewinnt
        #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
        #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        data = [0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,  # Zeile1
                0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1,  # Zeile2
                0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,  # Zeile3
                0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,  # Zeile4
                0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,  # Zeile5
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Zeile6

    if sample_nr == 5:  # Unentschieden
        #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
        #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        data = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,  # Zeile1
                1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0,  # Zeile2
                1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0,  # Zeile3
                1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0,  # Zeile4
                1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0,  # Zeile5
                1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # Zeile6

    if sample_nr == 6:  # Lauftext, Player 2 Win
        #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|  -->                                                                              |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
        #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|  -->                                                                              |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0,
                0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile1
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0,
                0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile2
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0,
                0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile3
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile4
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0,
                1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile5
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0]  # Zeile6

    if sample_nr == 7:  # Lauftext, Start-Screen '4 GEWINNT'
        #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|  -->     																                                          								   |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
        #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|  -->                                                                                                                         	                   |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
                0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile1
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
                0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile2
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0,
                0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0,
                0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile3
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0,
                0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0,
                0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile4
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
                0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Zeile5
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0]  # Zeile6

    return (data)  # Funktion gibt bei Aufruf als Wert den Vektor 'data' zuruek


def position_check(level):
    # Funktion zur Ueberpruefung, ob auf der aktuellen Position in der Matrix eine 1 oder eine 0 ist
    # Je nach player_nr wird auch geprueft, ob die rechte oder linke Position der aktuellen 1 oder 0 ist
    # Dies ist wichtig, da sonst in einer LED beide Farben leuchten koennen
    # ->|LD1|
    #   |g,r|
    #   |1,1|
    state = (data[pos] == level
             or (player_nr == 0 and data[pos + 1] == level)
             or (player_nr == 1 and data[pos - 1] == level))
    return (state)  # Funktion gibt bei Aufruf 'state' (1 oder 0) zuruek


def win_check(r):
    # Funktion ueberprueft, ob sich horizontal, vertikal oder diagonal "4 in einer Reihe" befinden
    # Dazu wird ausgehend von der aktuellen Position in allen Richtungen gesucht
    # und die Variable 'coins_in_a_row' hochgezaehlt
    # Sobald diese den Wert 4 erreicht, endet die Funktion und gibt den Wert '1' zurueck
    # Sollten keine 4 in einer Reihe gefunden werden, endet die Funktion ohne Rueckgabewert
    # "4 in einer Reihe" entspricht 4 LEDs der gleichen Farbe in einer Reihe (horizontal, vertikal oder diagonal) auf der LED-Anzeige
    global win_row

    i = 1  # Zaehlvariable zum aendern der Position horizontal, vertikal oder diagonal
    coins_in_a_row = 1  # Zaehler fuer Anzahl der LEDs in einer Reihe (horizontal, vertikal oder diagonal)
    r = rows - r - 1  # r ...in welcher Zeile befinde ich mich aktuell
    x_max = r * columns + pos_max + player_nr  # Abfragegrenze (rechter Rand der Matrix) in x-Richtung
    x_min = r * columns + player_nr  # Abfragegrenze (linkter Rand der Matrix) in x-Richtung
    win_row = [pos, 0, 0,
               0]  # Speichert die Positionen der LEDs in der Gewinn-Reihe (fuer Blinkende Hervorhebung der Gewinnreihe aud Anzeige)

    # Horizontal nach rechts					  			# |0 0 0 0 0 0|
    while pos + i * 2 <= x_max:  # |0 0 0 0 0 0|
        if data[pos + i * 2] == 1:  # |0 0 0 0 0 0|
            win_row[coins_in_a_row] = pos + i * 2  # |0 x x x x 0|
            coins_in_a_row = coins_in_a_row + 1
            if coins_in_a_row == 4:
                return (1)
            i = i + 1
        else:
            break
    i = 1
    # Horizontal nach links
    while pos - i * 2 >= x_min:
        if data[pos - i * 2] == 1:
            win_row[coins_in_a_row] = pos - i * 2
            coins_in_a_row = coins_in_a_row + 1
            if coins_in_a_row == 4:
                return (1)
            i = i + 1
        else:
            break

    i = 1
    coins_in_a_row = 1
    # Vertikal nach unten								# |0 x 0 0 0 0|
    while pos + i * columns < rows * columns:  # |0 x 0 0 0 0|
        if data[pos + i * columns] == 1:  # |0 x 0 0 0 0|
            win_row[coins_in_a_row] = pos + i * columns  # |0 x 0 0 0 0|
            coins_in_a_row = coins_in_a_row + 1
            if coins_in_a_row == 4:
                return (1)
            i = i + 1
        else:
            break

    i = 1
    coins_in_a_row = 1
    # Diagonal nach rechts steigend   			      	# |0 0 0 0 x 0|
    while pos - i * columns > 0 and pos + i * 2 <= x_max:  # |0 0 0 x 0 0|
        if data[pos + i * 2 - i * columns] == 1:  # |0 0 x 0 0 0|
            win_row[coins_in_a_row] = pos + i * 2 - i * columns  # |0 x 0 0 0 0|
            coins_in_a_row = coins_in_a_row + 1
            if coins_in_a_row == 4:
                return (1)
            i = i + 1
        else:
            break
    i = 1
    # Diagonal nach links fallend
    while pos + i * columns < rows * columns and pos - i * 2 >= x_min:
        if data[pos - i * 2 + i * columns] == 1:
            win_row[coins_in_a_row] = pos - i * 2 + i * columns
            coins_in_a_row = coins_in_a_row + 1
            if coins_in_a_row == 4:
                return (1)
            i = i + 1
        else:
            break

    i = 1
    coins_in_a_row = 1
    # Diagonal nach rechts fallend 										# |0 x 0 0 0 0|
    while pos + i * columns < rows * columns and pos + i * 2 <= x_max:  # |0 0 x 0 0 0|
        if data[pos + i * 2 + i * columns] == 1:  # |0 0 0 x 0 0|
            win_row[coins_in_a_row] = pos + i * 2 + i * columns  # |0 0 0 0 x 0|
            coins_in_a_row = coins_in_a_row + 1
            if coins_in_a_row == 4:
                return (1)
            i = i + 1
        else:
            break
    i = 1
    # Diagonal nach links steigend
    while pos - i * columns > 0 and pos - i * 2 >= x_min:
        if data[pos - i * 2 - i * columns] == 1:
            win_row[coins_in_a_row] = pos - i * 2 - i * columns
            coins_in_a_row = coins_in_a_row + 1
            if coins_in_a_row == 4:
                return (1)
            i = i + 1
        else:
            break


def win_screen():
    # Funktion zeigt die "4 in einer Reihe" des Gewinners 10s im Blinkinterval von 0.25s an
    # und ruft danach fuer 4s eine blinkende Gewinnanzeige (Sample(3+player_nr)) mit der Spielernummer des Gewinner
    # im 0.5s Blinkintervall auf

    # For-Schleife zur blinkenden Hervorhebung der Gewinnreihe
    # Dabei wird fuer 10*0.25s = 2,5s das Spielfeld angezeigt
    # und alle 0.25s die Gewinnreihe ein- und ausgeschaltet
    for x in range(0, 9):  # Von x=0 bis 9
        blink_screen(0.25, 0, data)  # Gib aktuelles Spielfeld aus
        for i in range(0, 4):  # Von i=0 bis 4
            data[win_row[i]] = not data[win_row[i]]  # Toogle Data der Gewinnreihe => Gewinnreihe auf 1 bzw. 0 setzen

    blink_screen(4, 0.5,
                 sample(3 + player_nr))  # Ausgabe der Spielernummer des Gewinners fuer 4s im 0.5s Blinkintervall


def draw_screen():
    # Funktion ruft fuer 4sec eine blinkende Unentschiedenanzeige (Sample(5))
    # mit 0.5sec Blinkintervall auf
    blink_screen(4, 0.5, sample(5))


def blink_screen(time_length, interval, data):
    # Funktion schreibt "data" auf die Matrix und laesst diese fuer die angegebene Dauer 'time_length'
    # im entsprechenden Intervall 'interval' blinken
    # Dabei werden die Ausgaenge der Schieberegister im entsprechenden Takt aktiviert und deaktiviert
    # Angaben der Zeitwerte in sec
    # time.time(): Return the time in seconds since the epoch as a floating point number from the system clock.

    time_start = time.time()  # Schreibe die aktuelle Systemzeit auf die Variable 'time_start'
    time_start_blink = time.time()  # Schreibe die aktuelle Systemzeit auf die Variable 'time_start_blink'

    while time.time() < time_start + time_length:  # Solange aktuelle Systemzeit die Startsystemzeit + die geforderte Zeit, die die Matrix blinken soll, nicht ueberschritten hat:
        send_data(data)  # Sende Daten
        # Durch die If-Schleife wird der Ausgang der Schieberegister in geforderten Intervall Ein- und Ausgeschaltet
        if time.time() > time_start_blink + interval:  # Sobald aktuelle Systemzeit die Start-Blink-Zeit + die Blink-Intervall-Zeit ueberschritten hat:
            output_disable()  # Deaktiviere Ausgang der Schieberegister
            time.sleep(interval)  # Schlafe fuer die Dauer des Blink-Intervalls
            output_enable()  # Aktiviere Ausgang der Schieberegister
            time_start_blink = time.time()  # Setze time_start_blink erneut auf die aktuelle Systemzeit


def send_running_text(text):
    # Funktion sendet eine Lauftext (Textsample, welches laenger als die breite des Displays ist) auf das Display
    # Dabei wird der Text von rechts nach links ueber die Anzeige geschoben, sodass ein bewegtes Bild entsteht
    # Um den Lauftext zu erzeugen, wird nur ein Ausschnitt des gesammten Datenvektors 'text' genommen
    # Dieser wird an den Vektor 'data' uebergeben und fuer 0.15s durch die Funktion Blink_Screen() dargestellt
    # Danach wird der aktuelle Ausschnitt des Datenvektors 'text' um eine Spalte nach rechts verschoben
    # Nun wird auch dieser an den Vektor 'data' uebergeben und fuer 0.15s durch die Funktion Blink_Screen() dargestellt
    # -> solange, bis der Ausschnitt des Datenvektors 'text' die letze Spalte erreicht

    #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|     -->       |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
    #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|     -->       |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
    #  -----------------------------               ----------------------------
    #  |0,1,0,0,0,1,0,0,0,0,0,1,0,1|0,1,...     0,1|0,0,0,1,0,0,0,0,0,1,0,1,0,0|...  # Zeile1
    #  |0,1,0,0,0,1,0,0,0,0,0,1,0,0|0,0,...     0,1|0,0,0,1,0,0,0,0,0,1,0,0,0,0|...  # Zeile2
    #  |0,1,0,1,0,1,0,0,0,0,0,1,0,0|0,1,...     0,1|0,1,0,1,0,0,0,0,0,1,0,0,0,1|...  # Zeile3
    #  |0,0,0,0,0,1,0,0,0,0,0,1,0,0|0,0,...     0,0|0,0,0,1,0,0,0,0,0,1,0,0,0,0|...  # Zeile4
    #  |0,0,0,0,0,1,0,0,0,0,0,1,0,1|0,1,...     0,0|0,0,0,1,0,0,0,0,0,1,0,1,0,1|...  # Zeile5
    #  |0,0,0,0,0,0,0,0,0,0,0,0,0,0|0,0,...     0,0|0,0,0,0,0,0,0,0,0,0,0,0,0,0|...  # Zeile6
    #  -----------------------------               -----------------------------

    i = 0  # Zaehlvariable zum Verschieben des Ausschnittes im Vektor 'text' um eine Spalte nach rechts
    r = 0  # Zaehlvariable fuer die aktuelle Zeile im Datenvektor
    columns_length = int(len(text) / rows)  # Anzahl der Spalten des gesammten Lauftextes
    # int(), weil bei Bruchrechnung x,0 rauskommt ...muss aber ohne Kommastelle sein, da dieser Wert Spaeter als Index genutzt wird

    while i <= columns_length - columns:  # Solange rechter Rand des Lauftextes noch nicht erreicht wurde und:
        while r < rows:  # solange die letzte Zeile nicht ueberschritten wurde
            data[r * columns:columns + r * columns] = text[
                                                      i + r * columns_length:i + columns_length + r * columns_length]  # Schreibe den mit i ausgewaehlten Ausschnitt des Lauftextes auf auf die entsprechende Zeile r in'data'
            r = r + 1  # erhoehe Zeile um 1

        r = 0  # Zuruecksetzen der Zaehlvariable fuer die aktuelle Zeile
        blink_screen(0.15, 0, data)  # Ausgabe des aktuellen Ausschnittes
        i = i + 2  # Verschiebe den Ausschnitt im Vektor 'text' um eine LED-Spalte (=2 Spalten im Lauftext) nach rechts


def fall_animation(r):
    # Funktion zur Animation einer Fallenden LED auf der LED-Matrix bei betaetigen des Enter-Buttons
    # Dazu wird eine 1 (LED AN) innerhalb der aktuellen Spalte einmal durch alle Zeilen geschoben und fuer jeweils 0,05s pro Zeile ausgegeben
    # Dabei ist die aktuelle Position 'pos' bereits an der Zielposition, also an der Position, wo die LED "hinfaellt"
    # Diese Zielposition ist abhaengig davon, wieweit die ausgewaehlte Spalte bereits beim Spielen "aufgefuellt" wurde

    global data  # Aufruf der globalen Variable 'data' (da diese innerhalb der Funktion veraendert wird)

    r_start = rows - r - 1  # Berechnung der Startreihe aus der akteullen Zeile
    fall_pos_old = pos - r_start * columns  # Initialwert der zuletzt akteullen Position in der Spalte
    r = 1  # Variable fuer aktuelle Zeile

    while r * columns < pos:  # Solange die Zielposition beim "Fallen" noch nicht erreicht wurde:
        fall_pos = pos - r_start * columns + r * columns  # erhoehe die Fallposition um eine Zeile
        data[fall_pos] = 1  # Setze data der aktuellen Fallposition auf 1
        data[fall_pos_old] = 0  # Setze data der alten Fallposition (Position, von der man beim "Fallen" kommt)
        blink_screen(0.05, 0, data)  # Ausgabe

        fall_pos_old = fall_pos  # Setze die alte Fallposition auf die aktuelle
        r = r + 1  # Erhoehe die Zeile um 1
    data[
        fall_pos_old] = 0  # Zueletzt muss data der letzten Fallposition wieder auf 0 gesetzt werden, danach wird die Animation beendet


### ISR Interrupt-Funktion
# Diese sogenannten Call-Back-Functions (Funktionen, die durch GPIO.add_event_detect aufgerufen werden)
# laufen PARALLEL zum Hauptprogramm
# Es koennen mehrere Callback-Funktionen durch einen GPIO.add_event_detect aufgerufen werden, diese werden jedoch sequenziell
# abgearbeitet (aber parallel zum Hauptprogramm, siehe https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/)

def reset_button(button_nr):
    # Funktion fuer Reset des Hauptprogramms
    # Wird Enter-Button 2s betaetigt, wird 'reset' auf 1 gesetzt
    # dadurch wird das Hauptprogramm unterbrochen und neu initialisiert
    global reset
    time_start = time.time()  # Funktionsaufruf, Return the time in seconds since the epoch as a floating point number from the system clock.
    time_reset = 2  # [t] = seconds, Zeit die gewartet werden soll (Die der Enterbutton betaetigt werden soll)

    # Schleife ueberprueft, ob die aktuelle Systemzeit die Startsystemzeit + den zu wartenden Wert in sec bereits erreicht hat
    # Dabei wird alle 200ms ueberprueft, ob der Enter-Butten bereits wieder losgelassen wurde
    while time.time() < time_start + time_reset:  # Wenn die Wartezeit von 2s noch nicht erreicht wurde:
        time.sleep(0.2)  # -> schalfe 200ms
        if GPIO.input(BUTTON_1) == 1:  # Ueberpruefe, ob Enter-Butten losgelassen wurde, wenn ja:
            return  # Beende Funktion, ohne reset auszuloesen
    reset = 1  # Falls Wartezeit erreicht wurde und Enter-Button noch immer betaetigt
    # -> Setze 'reset'


### Interrupt Events
# GPIO.add_event_detect(BUTTON_ENTER, GPIO.FALLING, callback = Reset, bouncetime = 200)

# ------------------------------------------------------------------------#
#                          BtnHandling (new)                              #
# ------------------------------------------------------------------------#
def handle_button_input(btn_nr: int, pos_old: int) -> int:
    """
    Verarbeiten der Eingabe eines Buttons. Dabei wird kombiniert die Position der aktiven LED auf die Position des Buttons gesetzt
    sowie die Anzeige der Fallanimation gestartet.
    :param btn_nr: Nummer des gedrückten Buttons
    :param pos_old: Alte, aktive Position, die resettet werden muss.
    :return: None
    """
    global data
    pos_new = btn_nr + player_nr
    if (type(pos_new) is not int
            or type(pos_old) is not int
            or type(player_nr) is not int
            or pos_new != pos_old and (data[btn_nr] == 1 or data[btn_nr + 1] == 1)):
        print("error_something_went_wrong")
        return 1
    print("SetStone")
    change_active_position(pos_new, pos_old)
    return check_game_over(stone_set_and_fall(pos_new, pos_old))

def change_active_position(pos_new: int, pos_old: int):
    """
    Setzen der aktiven Position auf den Wert des Buttons+Playernummer sowie reset der alten Position
    :param pos_new: Nummer des gedrückten Buttons
    :param pos_old: Alte, aktive Position, die resettet werden muss.
    :return: None
    """
    global data
    data[pos_new] = 1
    data[pos_old] = 0


def stone_set_and_fall(pos_new: int, pos_old: int) -> int:
    """
    Senden der Informationen des Buttons, ausführen der FallAnimation (leeres Feld = 0).
    :param pos_new: Neue Position des Steins
    :param pos_old: Alte Position des Steins
    :return: unterstes, leeres Feld
    """
    global data
    global pos
    last_empty_field = 0  # Zaehlvariable zum Durchsuchen der Zeilen einer Spalte nach dem untersten leeren Feld
    data[pos_new] = 0
    pos = pos_new + (rows - 1) * columns  # Position wird auf die letzte Zeile der aktuellen Spalte geschoben

    while last_empty_field < rows:  # Solange die obere Zeile nicht ueberschritten wird:
        if position_check(1):  # Wenn 'data' an der aktuellen Position 1 ist:
            last_empty_field = last_empty_field + 1  # -> Erhoehe Zaehlvariable um 1
            pos = pos - columns  # → Erhoehe die aktuelle Position um eine Zeile nach oben
        else:  # Sonst:
            # Diese If-Anweisung prueft, ob die aktuell erreichte Position der urspruenglichen Position (oberste Zeile) entspricht
            # Diese Abfage ist wichtig, da sonst die Matrix an der aktuellen Position auf 1 und danach gleich wieder auf 0 gesetzt wird
            # dadurch koennte man niemals die obere Zeile beschreiben
            if pos != pos_old:  # Wenn die aktuelle Position nicht der urspruenglichen Position entspricht (heisst: aktuelle Position hat noch nicht wieder die obere Zeile erreicht):
                data[
                    pos_old] = 0  # -> Setze 'data' der alten Position auf 0 (LED in der oberen Zeile ausschalten, ausser diese ist das letzte freie Feld in der Spalte)
                fall_animation(last_empty_field)  # -> Funktionsaufruf, Fallanimation
            data[pos] = 1  # -> Setze 'data' der aktuellen Position auf 1
            break  # -> Beende Schleife
    return last_empty_field


def check_game_over(last_empty_field: int) -> int:
    """
    Prüfen ob der Spieler gewonnen hat.
    Switch des aktiven Spielers.
    Reset der LED (für die nächste Runde)
    Prüfen auf Unendschieden.
    :param last_empty_field:
    :return: 1 = true 0 = false
    """
    global player_nr
    if not is_win(last_empty_field):
        return 0
    switch_player_set_start()
    if not is_patt():
        return 0
    return 1


def is_win(last_empty_field: int) -> int:
    """
    Ueberpruefe, ob 4 in einer Reihe (horizontal, vertikal, diagonal)
    Funktionsaufruf, Starte Gewinner-Bildschirm
    Setze reset als Return Value und Starte das Spiel neu
    :param last_empty_field:
    :return: 1 = true 0 = false
    """
    if win_check(last_empty_field) == 1:
        win_screen()
        return 0
    return 1


def is_patt() -> int:
    """
    Pruefe, ob die Matrix bereits komplett ausgefuellt wurde (ohne dass bereits ein Sieg errungen wurde).
    Sollte die Position beim 'Ueberpruefen der aktuellen Position auf eine 1' den rechten Rand der Matrix
    ueberschritten haben, starte den Unentschieden-Bildschirm.
    Setze reset als Return Value und Starte das Spiel neu.
    :param pos_new:
    :return: 1 = true 0 = false
    """
    global pos
    if pos > pos_max + player_nr:
        draw_screen()
        return 0
    return 1


def switch_player_set_start():
    """
    Toogle Player Number ( 0...Player 1, 1...Player 2) and reset aktuelle Position zurueck auf Startposition (oben links).
    Beachten des Sonderfalls, dass das obere linke Feld bereits belegt ist.
    → In diesem Fall verschieben des Steins nach rechts, bis Feld frei
    :return: 1 = true 0 = false
    """
    global player_nr
    global pos
    player_nr = (0 if player_nr == 1 else 1)
    pos = 0 + player_nr

    while pos <= pos_max + player_nr:
        if position_check(1):
            pos = pos + 2
        else:
            data[pos] = 1
            break


# ------------------------------------------------------------------------#
#                                 Main                                   #
# ------------------------------------------------------------------------#

### Initialisierung"

output_enable()  # Funktionsaufruf, aktiviere Ausgaenge der Schieberegisterbausteine
clear_shift_register()  # Funktionsaufruf, loesche aktuellen Inhalt der Shift-Register
set_storage_register()  # Funktionsaufruf, Ausgabe des leeren Shift-Registers
##todo animation einkommentieren
#send_running_text(sample(7))  # Funktionsaufruf, Ausgabe des Startbildschirms ('4 Gewinnt')
while 1:
    reset = 1  # reset zuruecksetzen (nachdem Reset ausgeloest wurde)
    pos = 0  # position zuruecksetzen (nachdem Reset ausgeloest wurde)
    player_nr = 0  # player_nr zuruecksetzen (nachdem Reset ausgeloest wurde)
    data = sample(0)  # Funktionsaufruf, schreibe Startbildschirm (Sample(0)) auf 'data'

    while reset:  # Spiel läuft bis abgeschlossen (reset wird durch Reset-Funktion, Spielgewinn oder Unentschieden ausgeloest)
        send_data(data)  # Funktionsaufruf, Sende 'data' an LED-Matrix
        ## Verarbeiten der Eingabe des Nutzers
        if button(BUTTON_0):
            reset = handle_button_input(0, pos)
        elif button(BUTTON_1):
            reset = handle_button_input(2, pos)
        elif button(BUTTON_2):
            reset = handle_button_input(4, pos)
        elif button(BUTTON_3):
            reset = handle_button_input(6, pos)
        elif button(BUTTON_4):
            reset = handle_button_input(8, pos)
        elif button(BUTTON_5):
            reset = handle_button_input(10, pos)
        elif button(BUTTON_6):
            reset = handle_button_input(12, pos)

##GPIO.cleanup()             # Setzt die GPIOs zurueck
##sys.exit()                 # Apparently sys.exit() allows the program to clean up resources and exit
##                           # gracefully, while os._exit() is rather abrupt.
