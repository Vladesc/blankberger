from __future__ import annotations

from random import randrange


class MockEnvWinCheck:

    def __init__(self):
        self.rows = 6
        self.columns_total = 14
        self.max_index_in_data_row = 12

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
        current_row = check_row  # todo das geht auch schöner
        matrix_right_border = current_row * self.columns_total + self.max_index_in_data_row + player_check
        matrix_left_border = current_row * self.columns_total + player_check
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

    def env_check(self, check_vector: list[int]):
        """
        1. Prüfen, ob der Spieler in den nächsten zwei Runden gewinnen könnte
            → Ja: Stein setzen und abbruch der Prüfung
        2. Prüfen, ob der Computer in der nächsten Runde gewinnen könnte
            → Ja: Stein setzen und abbruch der Prüfung
        3. Prüfen, ob der Computer in den nächsten zwei Runden gewinnen könnte
            → Ja: Stein setzen und abbruch der Prüfung
        4. Stein random setzen.
        :param check_vector:
        :return: Nummer des Buttons, der ausgelöst werden soll
        """

        # check_player_number = 0
        def win_check_for_player(check_player_number: int):
            print("checking player", check_player_number)
            # check Player win in two turns
            for check_column in range(int(self.columns_total / 2)):
                if self.environment_win_check(check_vector.copy(), check_column, check_player_number) == 1:
                    print("1 turn ", check_player_number, " win ", check_column)
                    return check_column
            for manipulate_row in range(int(self.columns_total / 2)):
                manipulated_vector = self.environment_manipulate_vector(check_vector.copy(), manipulate_row,
                                                                        check_player_number)
                if manipulated_vector is None:
                    continue
                for check_column in range(int(self.columns_total / 2)):
                    if self.environment_win_check(manipulated_vector.copy(), check_column, check_player_number) == 1:
                        print("2 turn ", check_player_number, " win ", manipulate_row)
                        return manipulate_row
            return -1
        """
        # check Computer win in one turn
        check_player_number = 1
        for check_column in range(int(self.columns_total / 2)):
            if self.environment_win_check(check_vector.copy(), check_column, check_player_number) == 1:
                print("1 turn e win ", check_column)
                return check_column
        # check Computer win in two turns
        for manipulate_row in range(int(self.columns_total / 2)):
            manipulated_vector = self.environment_manipulate_vector(check_vector.copy(), manipulate_row,
                                                                    check_player_number)
            if manipulated_vector is None:
                continue
            for check_column in range(int(self.columns_total / 2)):
                if self.environment_win_check(manipulated_vector.copy(), check_column, check_player_number) == 1:
                    print("2 turn e win ", manipulate_row)
                    return manipulate_row
        # Random set stone
        return randrange(int(self.columns_total / 2))
        """
        # Random set stone
        press_btn = win_check_for_player(0)
        press_btn = win_check_for_player(1) if press_btn == -1 else press_btn
        return randrange(int(self.columns_total / 2)) if press_btn == -1 else press_btn


if __name__ == '__main__':
    """
    data_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    """
    data_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1,
                   0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
                   0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]
    mock = MockEnvWinCheck()

    print("press button: ", mock.env_check(data_vector))
