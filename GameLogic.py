from __future__ import annotations
from random import randrange
import RPi.GPIO as GPIO
import time


class GameLogic(object):
    def __init__(self):
        ### Init Thread handling variables
        self.close_game_gui_method = None
        self.gui_update_method = None
        self.gui_play_sound_method = None
        self.thread_is_running = 1

        ### Initialisierung GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.cleanup()

        self.output_enable_pin = 14
        self.output_rck_storage_register_clock = 15
        self.output_sck_shift_register_clock = 18
        self.output_sclr_not_shift_register_clear = 23
        self.output_si_serial_data = 24
        self.input_button_from_left = [2, 3, 4, 17, 27, 22, 10]

        self.__gpio_setup()

        self.reset_game = 0
        self.button_is_pressed = 0
        self.last_button_pressed = 0
        # 7 Spalten mit jeweils zwei Farben -> 14 (eigentlich 16, da Scheiberegister 16 Bits braucht, letzten 2 Bits sind beliebig und werden in der Funktion send_data() seperat mitgesendet)
        self.columns_total = 14
        # Anzahl der unbenutzten Spalten (=Anzahl der im Schieberegisterbaustein NICHT benutzten Ausgaenge, HIGH-SIDE)
        self.columns_unused = [0, 0]
        # 6 Zeilen (eigentlich 8, da Schieberegister 8 Bit braucht, letzten 2 Bits sind beliebig und werden in der Funktion send_data() seperat mitgesendet)
        self.rows = 6
        # Anzahl der unbenutzten Zeilen (=Anzahl der im Schieberegisterbaustein nicht benutzten Ausgaenge, LOW-SIDE)
        self.rows_unused = [0, 0]
        self.clk_delay = 0.00000001  # Delay zur sicheren Erkennung der Signalflanken (siehe Datenblatt Schieberegister 74HC595), mind. 6ns
        self.data_vector = [0]
        self.row = [1, 0, 0, 0, 0, 0,  # Zeile1
                    0, 1, 0, 0, 0, 0,  # Zeile2
                    0, 0, 1, 0, 0, 0,  # Zeile3
                    0, 0, 0, 1, 0, 0,  # Zeile4
                    0, 0, 0, 0, 1, 0,  # Zeile5
                    0, 0, 0, 0, 0, 1]  # Zeile6
        self.current_index_in_data = 0
        self.max_index_in_data_row = 12
        self.game_mode = 0
        self.pve_difficulty = 0
        self.current_player_number: int = 0
        self.win_check_container = [0, 0, 0, 0]
        self.vladesc_ref = '0612'
        self.vladesc_p0 = ""
        self.vladesc_p1 = ""

    def __gpio_setup(self) -> None:
        """
        Setup GPIOs (Declare GPIOs as INPUT or OUTPUT)
        WICHTIG: Da mit PULL-UP-Widerstand gearbeitet wird, muss der Button, den PIN auf LOW ziehen
                 → Durch Buttondruck wird Pin auf GND gelegt! → HIGH-Signal in Python
        BUTTON_n → IN (mit Pull-Up Wiederstand, standartmaessig auf HIGH)
        :return:
        """
        GPIO.setup(self.output_enable_pin, GPIO.OUT)  # OUTPUT
        GPIO.setup(self.output_rck_storage_register_clock, GPIO.OUT)  # OUTPUT
        GPIO.setup(self.output_sck_shift_register_clock, GPIO.OUT)  # OUTPUT
        GPIO.setup(self.output_sclr_not_shift_register_clear, GPIO.OUT)  # OUTPUT
        GPIO.setup(self.output_si_serial_data, GPIO.OUT)  # OUTPUT
        for x in range(len(self.input_button_from_left)):
            GPIO.setup(self.input_button_from_left[x], GPIO.IN, GPIO.PUD_UP)

    # ------------------------------------------------------------------------#
    #                                 Functions                              #
    # ------------------------------------------------------------------------#
    def __button(self, button_nr) -> int | None:
        """
        Funktion gibt das Signal button_is_pressed aus, wenn der geforderte Taster gedrueckt wird.
        Dieses Signal kann nur ausgegeben werden, wenn button_state zuvor 0 war.
        Dadurch werden wiederholte Aufrufe der Funktion bei laenger betaetigtem Taster vermieden.
        → Setze button_state auf 1, wenn BUTTON gedrueckt (GPIO.input == 0 wegen Pull-Up) und button_state == 0
        → Setze button_state auf 0, sobald zuvor betaetigte BUTTON (button_old) losgelassen wird
        :param button_nr:
        :return: button_is_pressed or None
        """
        if not GPIO.input(button_nr) and not self.button_is_pressed:
            self.last_button_pressed = button_nr
            self.button_is_pressed = 1
            time.sleep(0.01)
            return self.button_is_pressed
        elif GPIO.input(button_nr) and self.button_is_pressed and self.last_button_pressed == button_nr:
            self.button_is_pressed = 0
            time.sleep(0.01)
            return None

    def __send_data(self, data) -> None:
        """
        Funktion sendet 'data' an Shift-Register und aktiviert Ausgabe an das Storage-Register
        → Ausgabe der Daten im Storgage-Register auf die LED-Matrix
        Dabei wird jede Zeile seperat angesteuert
        → Immer nur eine Zeile der LED-Matrix wird beschrieben, danach wird diese gelöscht
        und die naechste Zeile beschrieben.

        Die Schleife sendet (6+2)-Bit-Vektor 'row' mit Information, welche Zeile angesteuert werden soll
        und (14+2)-Bit-Vektor 'data' mit Information, was in der entsprechenden Zeile angezeigt werden soll
        (welche LEDs in der entsprechenden Zeile leuchten sollen).

        Funktionsaufruf "set_shift_register" with data, sende 14-Bit-Vektor 'data' mit Information,
        was in der entsprechenden Zeile angezeigt werden soll
        :param data: Data Vector
        :return: None
        """

        row_in_vector_data = 0
        while row_in_vector_data < self.rows:
            self.__clear_shift_register()
            self.__set_shift_register(self.row[
                                      0 + row_in_vector_data * self.rows:self.rows + row_in_vector_data * self.rows])
            self.__set_shift_register(self.rows_unused)
            self.__set_shift_register(data[
                                      0 + row_in_vector_data * self.columns_total: self.columns_total + row_in_vector_data * self.columns_total])
            self.__set_shift_register(self.columns_unused)
            self.__set_storage_register()
            row_in_vector_data = row_in_vector_data + 1

    def __output_enable(self) -> None:
        """
        Activate output of shift register blocks.
        Activate Qa to Qh and set delay for secure registration of signal level.
        :return: None
        """
        GPIO.output(self.output_enable_pin, GPIO.LOW)
        time.sleep(self.clk_delay)

    def __output_disable(self) -> None:
        """
        Deactivate output of shift register blocks.
        Deactivate Qa to Qh and set delay for secure registration of signal level.
        :return: None
        """
        GPIO.output(self.output_enable_pin, GPIO.HIGH)
        time.sleep(self.clk_delay)

    def __clear_shift_register(self) -> None:
        """
        Clear data in shift register until SCLR_NOT_LOW.
        :return: None
        """
        GPIO.output(self.output_sclr_not_shift_register_clear, GPIO.LOW)
        time.sleep(self.clk_delay)
        GPIO.output(self.output_sclr_not_shift_register_clear, GPIO.HIGH)
        time.sleep(self.clk_delay)

    def __set_shift_register(self, data) -> None:
        """
        Send data vector to shift register.
        → If data is 1 set SERIAL DATA OUTPUT (SI) to high.
        → If data is 0 set SERIAL DATA OUTPUT (SI) to low.

        Send serial data value in first stage of shift register and send actual data in next stage when Low-High-Flank.
        Set delay for secure registration of signal level.
        :param data:
        :return: None
        """
        data_index = 0
        data_length = len(data)

        while data_index < data_length:
            if data[data_index] == 1:
                GPIO.output(self.output_si_serial_data, GPIO.HIGH)
                time.sleep(self.clk_delay)
            elif data[data_index] == 0:
                GPIO.output(self.output_si_serial_data, GPIO.LOW)
                time.sleep(self.clk_delay)

            GPIO.output(self.output_sck_shift_register_clock, GPIO.HIGH)
            time.sleep(self.clk_delay)
            GPIO.output(self.output_sck_shift_register_clock, GPIO.LOW)
            time.sleep(self.clk_delay)
            data_index = data_index + 1

    def __set_storage_register(self) -> None:
        """
        Funktion gibt aktuellen Daten im Shift-Register an Storage-Register weiter bei LOW-HIGH-Flanke an RCK
        (Das Storage-Register (=Ausgang) gibt Daten direkt auf die LED-Matrix bzw. die Treiberstufen vor der Matrix,
        sofern die Ausgaenge Qa bis Qh der Schieberegisterbausteine aktiviert wurden (siehe 'def Output_Enable()')
        :return: None
        """
        GPIO.output(self.output_rck_storage_register_clock, GPIO.HIGH)
        time.sleep(self.clk_delay)
        GPIO.output(self.output_rck_storage_register_clock, GPIO.LOW)
        time.sleep(self.clk_delay)

    @staticmethod
    def __sample(sample_nr) -> list[int]:
        """
        Funktion enthaelt verschiedene Samples, welche mithilfe der Funktion Send_Data() auf der LED-Matrix
        angezeigt werden koennen, z.B.: Send_Data(Sample(2)).
        Struktur:
                 #  |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
                 #  |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        WICHTIG: Die LED-Matrix besitzt nur 7 LED-Spalten mit je 2 Farben (gruen(g), rot(r)) -> 14 Spalten
                 Da die Schieberegisterbausteine zur Ansteuerung der Spalten aber 2*8=16 Ausgaenge besitzen,
                 muessen die 2 ungenutzten Ausgaenge (Spalte 15 und 16) mitgesendet werden.
                 Diese werden in der Funktion send_data() seperat mitgesendet und muessen hier nit extra eingetragen werden
        Sample 0: Startbildschirm
        Sample 1: HI
        Sample 2: DU
        Sample 3: Spieler 1 gewinnt
        Sample 4: Spieler 2 gewinnt
        Sample 5: Unentschieden
        Sample 6: Lauftext Player 2 win
        Sample 7: 4 Gewinnt
        :param sample_nr:
        :return:
        """
        sample_vector = None
        if sample_nr == 0:
            sample_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif sample_nr == 1:
            sample_vector = [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0,
                             0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0,
                             0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0,
                             0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0,
                             0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0,
                             0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0]
        elif sample_nr == 2:
            sample_vector = [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1,
                             1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1,
                             1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1,
                             1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1,
                             1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1,
                             1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1]
        elif sample_nr == 3:
            sample_vector = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                             1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0,
                             1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0,
                             1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                             1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif sample_nr == 4:
            sample_vector = [0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,
                             0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1,
                             0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,
                             0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif sample_nr == 5:
            sample_vector = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                             1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0,
                             1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0,
                             1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0,
                             1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0,
                             1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        elif sample_nr == 6:
            sample_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,
                             0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile1
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1,
                             0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile2
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,
                             0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile3
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile4
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,
                             0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile5
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Zeile6
        elif sample_nr == 7:
            sample_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1,
                             0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,
                             0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile1
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,
                             0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile2
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
                             0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,
                             0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile3
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
                             0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,
                             0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile4
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1,
                             0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
                             0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Zeile5
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Zeile6
        return sample_vector

    def __position_check(self, level: int) -> int:
        """
        Funktion zur Ueberpruefung, ob auf der aktuellen Position in der Matrix eine 1 oder eine 0 ist.
        Je nach player_nr wird auch geprueft, ob die rechte oder linke Position der aktuellen 1 oder 0 ist.
        Dies ist wichtig, da sonst in einer LED beide Farben leuchten koennen
        |LD1|
        |g,r|
        |1,1|
        :param level:
        :return: Funktion gibt bei Aufruf 'state' (1 oder 0) zuruek
        """
        self.state = (self.data_vector[self.current_index_in_data] == level
                      or (self.current_player_number == 0 and self.data_vector[self.current_index_in_data + 1] == level)
                      or (self.current_player_number == 1 and self.data_vector[self.current_index_in_data - 1] == level)
                      )
        return self.state

    def __win_check(self, current_row: int) -> int:
        """
        Funktion ueberprueft, ob sich horizontal, vertikal oder diagonal "4 in einer Reihe" befinden.
        Dazu wird ausgehend von der aktuellen Position in allen Richtungen gesucht und die Variable 'led_in_a_row' hochgezaehlt.
        Sobald diese den Wert 4 erreicht, endet die Funktion und gibt den Wert '1' zurueck.
        Sollten keine 4 in einer Reihe gefunden werden, endet die Funktion ohne Rueckgabewert "4 in einer Reihe"
        entspricht 4 LEDs der gleichen Farbe in einer Reihe (horizontal, vertikal oder diagonal) auf der LED-Anzeige
        :param current_row:
        :return:
        """
        i = 1
        led_in_a_row = 1
        current_row = self.rows - current_row - 1
        matrix_right_border = current_row * self.columns_total + self.max_index_in_data_row + self.current_player_number
        matrix_left_border = current_row * self.columns_total + self.current_player_number
        self.win_check_container = [self.current_index_in_data, 0, 0, 0]

        # Horizontal nach rechts |0 0 0 0 0 0|
        while self.current_index_in_data + i * 2 <= matrix_right_border:  # |0 0 0 0 0 0|
            if self.data_vector[self.current_index_in_data + i * 2] == 1:  # |0 0 0 0 0 0|
                self.win_check_container[led_in_a_row] = self.current_index_in_data + i * 2  # |0 x x x x 0|
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        # Horizontal nach links
        while self.current_index_in_data - i * 2 >= matrix_left_border:
            if self.data_vector[self.current_index_in_data - i * 2] == 1:
                self.win_check_container[led_in_a_row] = self.current_index_in_data - i * 2
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        led_in_a_row = 1
        # Vertikal nach unten |0 x 0 0 0 0|
        while self.current_index_in_data + i * self.columns_total < self.rows * self.columns_total:  # |0 x 0 0 0 0|
            if self.data_vector[self.current_index_in_data + i * self.columns_total] == 1:  # |0 x 0 0 0 0|
                self.win_check_container[
                    led_in_a_row] = self.current_index_in_data + i * self.columns_total  # |0 x 0 0 0 0|
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        led_in_a_row = 1
        # Diagonal nach rechts steigend |0 0 0 0 x 0|
        while self.current_index_in_data - i * self.columns_total > 0 and self.current_index_in_data + i * 2 <= matrix_right_border:  # |0 0 0 x 0 0|
            if self.data_vector[self.current_index_in_data + i * 2 - i * self.columns_total] == 1:  # |0 0 x 0 0 0|
                self.win_check_container[
                    led_in_a_row] = self.current_index_in_data + i * 2 - i * self.columns_total  # |0 x 0 0 0 0|
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        # Diagonal nach links fallend
        while self.current_index_in_data + i * self.columns_total < self.rows * self.columns_total and self.current_index_in_data - i * 2 >= matrix_left_border:
            if self.data_vector[self.current_index_in_data - i * 2 + i * self.columns_total] == 1:
                self.win_check_container[led_in_a_row] = self.current_index_in_data - i * 2 + i * self.columns_total
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break

        i = 1
        led_in_a_row = 1
        # Diagonal nach rechts fallend |0 x 0 0 0 0|
        while self.current_index_in_data + i * self.columns_total < self.rows * self.columns_total and self.current_index_in_data + i * 2 <= matrix_right_border:  # |0 0 x 0 0 0|
            if self.data_vector[self.current_index_in_data + i * 2 + i * self.columns_total] == 1:  # |0 0 0 x 0 0|
                self.win_check_container[
                    led_in_a_row] = self.current_index_in_data + i * 2 + i * self.columns_total  # |0 0 0 0 x 0|
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        # Diagonal nach links steigend
        while self.current_index_in_data - i * self.columns_total > 0 and self.current_index_in_data - i * 2 >= matrix_left_border:
            if self.data_vector[self.current_index_in_data - i * 2 - i * self.columns_total] == 1:
                self.win_check_container[led_in_a_row] = self.current_index_in_data - i * 2 - i * self.columns_total
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break

    def __win_screen(self) -> None:
        """
        Funktion zeigt die "4 in einer Reihe" des Gewinners 10s im Blinkinterval von 0.25s an und ruft danach für
        4s eine blinkende Gewinnanzeige (Sample(3+player_nr)) mit der Spielernummer des Gewinner
        im 0.5s Blinkintervall auf

        For-Schleife zur blinkenden Hervorhebung der Gewinnreihe
        Dabei wird fuer 10*0.25s = 2,5s das Spielfeld angezeigt
        und alle 0.25s die Gewinnreihe ein- und ausgeschaltet

        Ebenfalls trigger der Anzeige, um den gewinner anzuzeigen.
        :return:
        """
        self.gui_update_method(3 if self.current_player_number == 0 else 4)
        for x in range(0, 9):
            self.__blink_screen(0.25, 0, self.data_vector)
            for i in range(0, 4):
                self.data_vector[self.win_check_container[i]] = not self.data_vector[self.win_check_container[i]]

        self.__blink_screen(4, 0.5, self.__sample(3 + self.current_player_number))

    def __draw_screen(self) -> None:
        """
        Funktion ruft fuer 4sec eine blinkende Unentschiedenanzeige (Sample(5)) mit 0.5sec Blinkintervall auf
        :return: None
        """
        self.gui_update_method(7)
        self.__blink_screen(4, 0.5, self.__sample(5))

    def __blink_screen(self, time_length: float | int, interval: float | int, data: list[int]) -> None:
        """
        Funktion schreibt "data" auf die Matrix und lässt diese für die angegebene Dauer 'time_length'
        im entsprechenden Intervall 'interval' blinken.
        Dabei werden die Ausgänge der Schieberegister im entsprechenden Takt aktiviert und deaktiviert.
        Angaben der Zeitwerte in sec.
        time.time(): Return the time in seconds since the epoch as a floating point number from the system clock.
        :param time_length: The length of the full blink interval in seconds
        :param interval: interval in seconds between two consecutive blinks
        :param data: Array with data to blink (generated from self.sample(int) method or self.data)
        :return: None
        """
        time_start = time.time()
        time_start_blink = time.time()
        while time.time() < time_start + time_length:
            self.__send_data(data)
            if time.time() > time_start_blink + interval:
                self.__output_disable()
                time.sleep(interval)
                self.__output_enable()
                time_start_blink = time.time()

    def __send_running_text(self, text: list[int]) -> None:
        """
        Funktion sendet eine Lauftext (Textsample, welches länger als die Breite des Displays ist) auf das Display.
        Dabei wird der Text von rechts nach links über die Anzeige geschoben, sodass ein bewegtes Bild entsteht.
        Um den Lauftext zu erzeugen, wird nur ein Ausschnitt des gesamten Datenvektors 'text' genommen.
        Dieser wird an den Vektor 'data' übergeben und für 0.15s durch die Funktion Blink_Screen() dargestellt.
        Danach wird der aktuelle Ausschnitt des Datenvektors 'text' um eine Spalte nach rechts verschoben.
        Nun wird auch dieser an den Vektor 'data' übergeben und für 0.15s durch die Funktion Blink_Screen() dargestellt.
        → solange, bis der Ausschnitt des Datenvektors 'text' die letzte Spalte erreicht

        |LD1|LD2|LD3|LD4|LD5|LD6|LD7|     -->       |LD1|LD2|LD3|LD4|LD5|LD6|LD7|
        |g,r|g,r|g,r|g,r|g,r|g,r|g,r|     -->       |g,r|g,r|g,r|g,r|g,r|g,r|g,r|
        -----------------------------               ----------------------------
        |0,1,0,0,0,1,0,0,0,0,0,1,0,1|0,1,...     0,1|0,0,0,1,0,0,0,0,0,1,0,1,0,0|...  # Zeile1
        |0,1,0,0,0,1,0,0,0,0,0,1,0,0|0,0,...     0,1|0,0,0,1,0,0,0,0,0,1,0,0,0,0|...  # Zeile2
        |0,1,0,1,0,1,0,0,0,0,0,1,0,0|0,1,...     0,1|0,1,0,1,0,0,0,0,0,1,0,0,0,1|...  # Zeile3
        |0,0,0,0,0,1,0,0,0,0,0,1,0,0|0,0,...     0,0|0,0,0,1,0,0,0,0,0,1,0,0,0,0|...  # Zeile4
        |0,0,0,0,0,1,0,0,0,0,0,1,0,1|0,1,...     0,0|0,0,0,1,0,0,0,0,0,1,0,1,0,1|...  # Zeile5
        |0,0,0,0,0,0,0,0,0,0,0,0,0,0|0,0,...     0,0|0,0,0,0,0,0,0,0,0,0,0,0,0,0|...  # Zeile6
        -----------------------------               -----------------------------
        :param text:
        :return:
        """
        text_move_column = 0
        current_row = 0
        total_row_length = int(len(text) / self.rows)
        while text_move_column <= total_row_length - self.columns_total:
            while current_row < self.rows:
                dv_from = current_row * self.columns_total
                dv_to = dv_from + self.columns_total
                txt_from = text_move_column + current_row * total_row_length
                txt_to = txt_from + self.columns_total
                self.data_vector[dv_from:dv_to] = text[txt_from:txt_to]
                current_row = current_row + 1
            current_row = 0
            self.__blink_screen(0.15, 0, self.data_vector)
            text_move_column = text_move_column + 2

    def __fall_animation(self, current_row) -> None:
        """
        Funktion zur Animation einer Fallenden LED auf der LED-Matrix bei betaetigen des Enter-Buttons.
        Dazu wird eine 1 (LED AN) innerhalb der aktuellen Spalte einmal durch alle Zeilen geschoben und fuer jeweils 0,05s pro Zeile ausgegeben.
        Dabei ist die aktuelle Position 'pos' bereits an der Zielposition, also an der Position, wo die LED "hinfaellt".
        Diese Zielposition ist abhaengig davon, wieweit die ausgewaehlte Spalte bereits beim Spielen "aufgefuellt" wurde.
        :param current_row:
        :return:
        """
        row_start = self.rows - current_row - 1
        fall_pos_old = self.current_index_in_data - row_start * self.columns_total
        current_row = 1

        while current_row * self.columns_total < self.current_index_in_data:
            fall_pos = self.current_index_in_data - row_start * self.columns_total + current_row * self.columns_total
            self.data_vector[fall_pos] = 1
            self.data_vector[fall_pos_old] = 0
            self.__blink_screen(0.05, 0, self.data_vector)
            fall_pos_old = fall_pos
            current_row = current_row + 1
        self.data_vector[fall_pos_old] = 0

    # ------------------------------------------------------------------------#
    #                          EasterEgg                                      #
    # ------------------------------------------------------------------------#
    def __vladesc_win_screen(self) -> None:
        self.gui_update_method(5 if self.current_player_number == 0 else 6)
        for x in range(0, 9):
            self.__blink_screen(0.25, 0, self.data_vector)
            for i in range(0, 4):
                self.data_vector[self.win_check_container[i]] = not self.data_vector[self.win_check_container[i]]
        self.__blink_screen(4, 0.5, self.__sample(3 + self.current_player_number))

    def __vladesc_add(self, btn_nr: int) -> None:
        if self.game_mode == 1:
            return
        if self.current_player_number == 0:
            self.vladesc_p0 = self.vladesc_p0 + str(int(btn_nr / 2)) if len(self.vladesc_p0) != len(self.vladesc_ref) else ""
        else:
            self.vladesc_p1 = self.vladesc_p1 + str(int(btn_nr / 2)) if len(self.vladesc_p1) != len(self.vladesc_ref) else ""

    def __vladesc_check(self) -> bool:
        if self.game_mode == 1:
            return False
        if self.current_player_number == 0:
            return self.vladesc_p0 == self.vladesc_ref
        else:
            return self.vladesc_p1 == self.vladesc_ref

    # ------------------------------------------------------------------------#
    #                          BtnHandling (new)                              #
    # ------------------------------------------------------------------------#
    def __handle_button_input(self, btn_nr: int, pos_old: int) -> int:
        """
        Verarbeiten der Eingabe eines Buttons. Dabei wird kombiniert die Position der aktiven LED auf die Position des Buttons gesetzt
        sowie die Anzeige der Fallanimation gestartet.
        Hinweis: Zwei Sleeps mit 0.05, damit der Sound besser abgespielt wird/passt.
        :param btn_nr: Nummer des gedrückten Buttons
        :param pos_old: Alte, aktive Position, die resettet werden muss.
        :return: 1 if game over; 0 if game not over
        """
        pos_new = btn_nr + self.current_player_number
        if (type(pos_new) is not int
                or type(pos_old) is not int
                or type(self.current_player_number) is not int
                or pos_new != pos_old and (self.data_vector[btn_nr] == 1 or self.data_vector[btn_nr + 1] == 1)):
            return 1
        self.gui_play_sound_method()
        self.__vladesc_add(btn_nr)
        time.sleep(0.05)
        self.__change_active_position(pos_new, pos_old)
        time.sleep(0.05)
        return self.__check_game_over(self.__stone_set_and_fall(pos_new, pos_old))

    def __change_active_position(self, pos_new: int, pos_old: int):
        """
        Setzen der aktiven Position auf den Wert des Buttons+Playernummer sowie reset der alten Position
        :param pos_new: Nummer des gedrückten Buttons
        :param pos_old: Alte, aktive Position, die resettet werden muss.
        :return: None
        """
        self.data_vector[pos_new] = 1
        if pos_new != pos_old:
            self.data_vector[pos_old] = 0
        self.__send_data(self.data_vector)

    def __stone_set_and_fall(self, pos_new: int, pos_old: int) -> int:
        """
        Senden der Informationen des Buttons, ausführen der FallAnimation (leeres Feld = 0).
        Fallanimation wird nur ausgeführt, wenn die Spalte noch nicht gefüllt ist.
        Ansonsten kann der Spieler noch einmal setzen, bis das einsetzen eines Steins möglich ist.
        :param pos_new: Neue Position des Steins
        :param pos_old: Alte Position des Steins
        :return: unterstes, leeres Feld
        """
        last_empty_field = 0
        self.data_vector[pos_new] = 0
        self.current_index_in_data = pos_new + (self.rows - 1) * self.columns_total

        while last_empty_field < self.rows:
            if self.__position_check(1):
                last_empty_field = last_empty_field + 1
                self.current_index_in_data = self.current_index_in_data - self.columns_total
            else:
                if self.current_index_in_data != pos_old:
                    self.data_vector[pos_old] = 0
                    self.__fall_animation(last_empty_field)
                self.data_vector[self.current_index_in_data] = 1
                break
        return last_empty_field

    def __check_game_over(self, last_empty_field: int) -> int:
        """
        Prüfen ob der Spieler gewonnen hat.
        Switch des aktiven Spielers.
        Reset der LED (für die nächste Runde)
        Prüfen auf Unendschieden.
        :param last_empty_field:
        :return: 1 = true 0 = false
        """
        if not self.__is_win(last_empty_field):
            return 0
        self.__switch_player_set_start()
        if not self.__is_patt():
            return 0
        return 1

    def __is_win(self, last_empty_field: int) -> int:
        """
        Ueberpruefe, ob 4 in einer Reihe (horizontal, vertikal, diagonal)
        Funktionsaufruf, Starte Gewinner-Bildschirm
        Setze reset als Return Value und Starte das Spiel neu
        :param last_empty_field:
        :return: 1 = true 0 = false
        """
        if self.__vladesc_check():
            self.__vladesc_win_screen()
            time.sleep(5)
            self.__end_game()
            return 0
        if self.__win_check(last_empty_field) == 1:
            self.__win_screen()
            self.__end_game()
            return 0
        return 1

    def __is_patt(self) -> int:
        """
        Pruefe, ob die Matrix bereits komplett ausgefuellt wurde (ohne dass bereits ein Sieg errungen wurde).
        Sollte die Position beim 'Ueberpruefen der aktuellen Position auf eine 1' den rechten Rand der Matrix
        ueberschritten haben, starte den Unentschieden-Bildschirm.
        Setze reset als Return Value und Starte das Spiel neu.
        :return: 1 = true 0 = false
        """
        if self.current_index_in_data > self.max_index_in_data_row + self.current_player_number:
            self.__draw_screen()
            self.__end_game()
            return 0
        return 1

    def __end_game(self) -> None:
        """
        Stop the game instance and close the game gui window
        :return: None
        """
        self.stop()
        self.close_game_gui_method()

    def __switch_player_set_start(self) -> None:
        """
        Toogle Player Number ( 0...Player 1, 1...Player 2) and reset aktuelle Position zurueck auf Startposition (oben links).
        Beachten des Sonderfalls, dass das obere linke Feld bereits belegt ist.
        → In diesem Fall verschieben des Steins nach rechts, bis Feld frei.
        Ebenfalls setzen der Spielernummer in der GUI
        :return: 1 = true 0 = false
        """
        self.current_player_number = (0 if self.current_player_number == 1 else 1)
        self.gui_update_method(self.current_player_number)
        self.current_index_in_data = 0 + self.current_player_number

        while self.current_index_in_data <= self.max_index_in_data_row + self.current_player_number:
            if self.__position_check(1):
                self.current_index_in_data = self.current_index_in_data + 2
                pass
            else:
                self.data_vector[self.current_index_in_data] = 0
                break

    # ------------------------------------------------------------------------#
    #                      PvE Environment Actions                            #
    # ------------------------------------------------------------------------#
    def __environment_action(self) -> int:
        """
        Run environment actions if game mode is PvE
        :return: 0 = end round; 1 = run further
        """
        actual_player = [self.current_player_number].copy()
        while self.current_player_number == actual_player[0]:
            if self.pve_difficulty == 0:
                return self.__handle_button_input(
                    self.__environment_select_button(self.data_vector.copy(), 40) * 2,
                    self.current_index_in_data)
            else:
                return self.__handle_button_input(
                    self.__environment_select_button(self.data_vector.copy(), 0) * 2,
                    self.current_index_in_data)

    def __environment_select_button(self, check_vector: list[int], easy_percentage: int) -> int:
        """
        1. Prüfen, ob der Spieler in der nächsten Runde gewinnen könnte
            → Ja: Nummer des Buttons zurückgeben und abbruch der Prüfung
        2. Prüfen, ob der Spieler in den nächsten zwei Runden gewinnen könnte
            → Ja: Nummer des Buttons zurückgeben und abbruch der Prüfung
        3. Prüfen, ob der Computer in der nächsten Runde gewinnen könnte
            → Ja: Nummer des Buttons zurückgeben und abbruch der Prüfung
        4. Prüfen, ob der Computer in den nächsten zwei Runden gewinnen könnte
            → Ja: Nummer des Buttons zurückgeben und abbruch der Prüfung
        5. Rückgabe des ermittelten Wertes oder Random Wert. Hier kommt der Prozentwert zum Einsatz.
        :param check_vector: Aktueller DataVektor, der geprüft werden soll.
        :param easy_percentage: Prozentwert (0-100), um wie viel Wahrscheinlichkeit ein Zufallswert zurückgegeben wird.
        :return: Nummer des Buttons, der ausgelöst werden soll
        """

        def win_check_for_player(check_player_number: int):
            """
            1. Prüfen, ob der übergebene Player in der nächsten Runde gewinnen könnte
            2. Prüfen, ob der übergebene Player in der übernächsten Runde gewinnen könnte
            :param check_player_number:
            :return:
            """
            for check_column in range(int(self.columns_total / 2)):
                if self.environment_win_check(check_vector.copy(), check_column, check_player_number) == 1:
                    return check_column
            for manipulate_row in range(int(self.columns_total / 2)):
                manipulated_vector = self.environment_manipulate_vector(check_vector.copy(), manipulate_row,
                                                                        check_player_number)
                if manipulated_vector is None:
                    continue
                for check_column in range(int(self.columns_total / 2)):
                    if self.environment_win_check(manipulated_vector.copy(), check_column, check_player_number) == 1:
                        return manipulate_row
            return -1

        if randrange(1, 100) > easy_percentage:
            press_btn = win_check_for_player(not self.current_player_number)
            press_btn = win_check_for_player(self.current_player_number) if press_btn == -1 else press_btn
            return randrange(int(self.columns_total / 2)) if press_btn == -1 else press_btn
        else:
            return randrange(int(self.columns_total / 2))

    def environment_manipulate_vector(self, check_vector: list[int], set_x: int, player_check: int) -> None | list[int]:
        """
        Manipulieren des Vektors, um eine zweischichtprüfung zuzulassen.
        Einfügen eines Steins in der Spalte "set_x" für den Spieler "player_check".
        :param check_vector:
        :param set_x: X-Position, von der aus überprüft werden soll
        :param player_check: 0=Player1, 1=Environment → Für wen soll Gewinn geprüft werden.
        :return: "None" wenn einfügen nicht möglich, andernfalls Rückgabe des manipulierten Vektors.
        """
        position_set = 0
        check_position = set_x * 2
        check_row = self.rows - 1
        while not position_set:
            if check_row == -1:
                return None
            if (check_vector[check_row * self.columns_total + check_position] == 1
                    or check_vector[check_row * self.columns_total + check_position + 1] == 1):
                check_row = check_row - 1
            else:
                check_vector[check_row * self.columns_total + check_position + player_check] = 1
                position_set = 1
        return check_vector

    def environment_win_check(self, check_vector: list[int], set_x: int, player_check: int):
        """
        1. Vektor Manipulieren und Einfügen eines Steins in der Spalte "set_x" für den Spieler "player_check".
        2. Prüfen, ob mit Einfügen dieses Steins der Spieler "player_check" gewinnt.
        :param check_vector:
        :param set_x: X-Position, von der aus überprüft werden soll
        :param player_check: 0=Player1, 1=Environment → Für wen soll Gewinn geprüft werden.
        :return: 1 = gewinnt; 0 = gewinnt nicht; -1 = geht nicht
        """
        position_set = 0
        current_index_in_vector = 0
        check_position = set_x * 2
        check_row = self.rows - 1
        while not position_set:
            if check_row == -1:
                return -1
            if (check_vector[check_row * self.columns_total + check_position] == 1
                    or check_vector[check_row * self.columns_total + check_position + 1] == 1):
                check_row = check_row - 1
            else:
                current_index_in_vector = check_row * self.columns_total + check_position + player_check
                check_vector[current_index_in_vector] = 1
                position_set = 1

        # --------------------- von Position aus prüfen
        i = 1
        led_in_a_row = 1
        matrix_right_border = check_row * self.columns_total + self.max_index_in_data_row + player_check
        matrix_left_border = check_row * self.columns_total + player_check
        env_win_check_container = [current_index_in_vector, 0, 0, 0]
        # Horizontal nach rechts |0 0 0 0 0 0|
        while current_index_in_vector + i * 2 <= matrix_right_border:  # |0 0 0 0 0 0|
            if check_vector[current_index_in_vector + i * 2] == 1:  # |0 0 0 0 0 0|
                env_win_check_container[led_in_a_row] = current_index_in_vector + i * 2  # |0 x x x x 0|
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        # Horizontal nach links
        while current_index_in_vector - i * 2 >= matrix_left_border:
            if check_vector[current_index_in_vector - i * 2] == 1:
                env_win_check_container[led_in_a_row] = current_index_in_vector - i * 2
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        led_in_a_row = 1
        # Vertikal nach unten |0 x 0 0 0 0|
        while current_index_in_vector + i * self.columns_total < self.rows * self.columns_total:  # |0 x 0 0 0 0|
            if check_vector[current_index_in_vector + i * self.columns_total] == 1:  # |0 x 0 0 0 0|
                env_win_check_container[
                    led_in_a_row] = current_index_in_vector + i * self.columns_total  # |0 x 0 0 0 0|
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        led_in_a_row = 1
        # Diagonal nach rechts steigend |0 0 0 0 x 0|
        while current_index_in_vector - i * self.columns_total > 0 and current_index_in_vector + i * 2 <= matrix_right_border:  # |0 0 0 x 0 0|
            if check_vector[current_index_in_vector + i * 2 - i * self.columns_total] == 1:  # |0 0 x 0 0 0|
                env_win_check_container[
                    led_in_a_row] = current_index_in_vector + i * 2 - i * self.columns_total  # |0 x 0 0 0 0|
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        # Diagonal nach links fallend
        while current_index_in_vector + i * self.columns_total < self.rows * self.columns_total and current_index_in_vector - i * 2 >= matrix_left_border:
            if check_vector[current_index_in_vector - i * 2 + i * self.columns_total] == 1:
                env_win_check_container[led_in_a_row] = current_index_in_vector - i * 2 + i * self.columns_total
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break

        i = 1
        led_in_a_row = 1
        # Diagonal nach rechts fallend |0 x 0 0 0 0|
        while current_index_in_vector + i * self.columns_total < self.rows * self.columns_total and current_index_in_vector + i * 2 <= matrix_right_border:  # |0 0 x 0 0 0|
            if check_vector[current_index_in_vector + i * 2 + i * self.columns_total] == 1:  # |0 0 0 x 0 0|
                env_win_check_container[
                    led_in_a_row] = current_index_in_vector + i * 2 + i * self.columns_total  # |0 0 0 0 x 0|
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        i = 1
        # Diagonal nach links steigend
        while current_index_in_vector - i * self.columns_total > 0 and current_index_in_vector - i * 2 >= matrix_left_border:
            if check_vector[current_index_in_vector - i * 2 - i * self.columns_total] == 1:
                env_win_check_container[led_in_a_row] = current_index_in_vector - i * 2 - i * self.columns_total
                led_in_a_row = led_in_a_row + 1
                if led_in_a_row == 4:
                    return 1
                i = i + 1
            else:
                break
        return 0

    # ------------------------------------------------------------------------#
    #                                 Main                                    #
    # ------------------------------------------------------------------------#

    def stop(self) -> None:
        """
        Stop running game -> stop game instance
        :return: None
        """
        self.__reset_game_instance()
        self.thread_is_running = 0

    def set_mode_and_difficulty(self, mode: int, difficulty: int = None) -> None:
        """
        Set game mode
        :param mode: GameMode 0=PvP 1=PvE
        :param difficulty: Schwierigkeit des Computergegners 0=easy 1=hard
        :return: None
        """
        self.game_mode = [mode].copy()[0]
        self.pve_difficulty = [difficulty].copy()[0]

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

    def set_gui_play_sound_method(self, gui_play_sound_method) -> None:
        """
        Set the Method to play game sound
        :param gui_play_sound_method: Method to play game sound
        :return: None
        """
        self.gui_play_sound_method = gui_play_sound_method

    def __reset_game_instance(self) -> None:
        """
        nachdem Reset ausgeloest wurde:
        → reset zuruecksetzen
        → position zuruecksetzen
        → player_nr zuruecksetzen
        → Funktionsaufruf, schreibe Startbildschirm (Sample(0)) auf 'data'
        :return: None
        """
        self.reset_game = 1
        self.current_index_in_data = 0
        self.current_player_number = 0
        self.gui_update_method(self.current_player_number)
        self.data_vector = self.__sample(0)

    def __init_game(self) -> None:
        """
        Activate output of shift register blocks, clear actual content of shift register,
        clean output of shift register and send sample(7) to output.
        :return: None
        """
        self.vladesc_p1 = ""
        self.vladesc_p0 = ""
        self.thread_is_running = 1
        self.__output_enable()
        self.__clear_shift_register()
        self.__set_storage_register()
        self.__send_running_text(self.__sample(7))

    def run_game(self) -> None:
        """
        Run the game from outside.
        :return: None
        """
        self.__init_game()
        while self.thread_is_running:
            self.__reset_game_instance()
            while self.reset_game and self.thread_is_running:
                self.__send_data(self.data_vector)
                for btn_index in range(len(self.input_button_from_left)):
                    if ((self.game_mode == 1 and self.current_player_number == 1)
                            or (self.game_mode == 2 and self.thread_is_running)):
                        self.reset_game = self.__environment_action()
                    else:
                        if self.__button(self.input_button_from_left[btn_index]):
                            self.reset_game = self.__handle_button_input(btn_index * 2, self.current_index_in_data)
