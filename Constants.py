from typing import Final

WINDOW_HEIGHT: Final = 480
WINDOW_WIDTH: Final = 800
WINDOW_TITLE: Final = "4 Gewinnt"
WINDOW_TITLE_RUNNING_GAME: Final = "Sie spielen gerade 4 Gewinnt"

GAME_MODE_LABEL: Final = "Spielmodus wählen"
GAME_WELCOME_LABEL: Final = "Willkommen bei 4 Gewinnt. Bitte wählen sie ihr Spiel."
GAME_PLAYER_1_LABEL: Final = "Spieler 1: "
GAME_PLAYER_2_LABEL: Final = "Spieler 2: "

GAME_PLAYER_1_PLACEHOLDER: Final = "Spieler 1"
GAME_PLAYER_2_PLACEHOLDER: Final = "Spieler 2"
GAME_ENVIRONMENT_PLACEHOLDER: Final = "Deep Blue 1996"

GAME_MODE_PVE_LABEL: Final = "Spieler gegen Computer"
GAME_MODE_PVP_LABEL: Final = "Spieler gegen Spieler"
GAME_MODE_PVP_DIFFICULTY_CHOOSE: Final = "Wählen sie die Schwierigkeit aus:"
GAME_MODE_PVP_DIFFICULTY_EASY: Final = "Leicht"
GAME_MODE_PVP_DIFFICULTY_MEDIUM: Final = "Mittel"
GAME_MODE_PVP_DIFFICULTY_HARD: Final = "Schwer"

GAME_SOUND_LABEL: Final = "Sound: "
GAME_SOUND_LABEL_ON: Final = "On"
GAME_SOUND_LABEL_OFF: Final = "Off"

GAME_INFO_BUTTON: Final = "Info"
GAME_RULES_BUTTON: Final = "Spielregeln"
GAME_START_BUTTON: Final = "Spiel Starten"
GAME_SHUTDOWN_BUTTON: Final = "Shutdown System"
GAME_MAIN_MENU_BUTTON: Final = "Hauptmenü"
GAME_END_BUTTON: Final = "Beenden"
GAME_BTN_SIZE_HEIGHT: Final = 2
GAME_BTN_SIZE_WIDTH: Final = 15

GAME_PVE_MSG_MISSING_NAME: Final = "Spieler 1 hat keinen Namen."
GAME_PVP_MSG_MISSING_NAME: Final = "Es sind nicht für alle Spieler Namen eingetragen."
GAME_CURRENT_PLAYER_LABEL: Final = "Spieler {cplayer} ist dran"
GAME_CURRENT_PLAYER_LABEL_END: Final = "Spieler {cplayer} hat gewonnen"
GAME_CURRENT_PLAYER_LABEL_VLADESC: Final = ("So preiset den Herrn in Neulatein: "
                                            "\nOh Herrum, schenkenum unsum deinum Segenum. "
                                            "\nAaameeenum. "
                                            "\n\nDir, {cplayer}, sei die Kraft des Gottimperators gewährt."
                                            "\nSpieler {cplayer} hat gewonnen."
                                            "\n- Vladesc")
GAME_CURRENT_PLAYER_LABEL_START: Final = [
    "Möge die Macht mit Dir sein. \n- Christopher Robin",
    "Wenns regnet wird man nass. \n- Albert Einstein",
    "Ich denke, also bin ich. \n- Ein amerikanischer Präsident",
    "Flieht, ihr Narren. \n- OTL Holger Müller",
    "How much is the fish. \n- Karl Marx",
    "Segnen wir den Wald, bis wir meschugge sind. \n- Der Papst",
    "Du bist nicht du, wenn du hungrig bist. \n- Der weiße Hai",
    "Da hält der Geschmack, was der Duft verspricht. \n- Dixi-Klo",
    "Sein oder Nicht Sein - Das ist hier die Frage \n- Schrödingers Katze",
    "Halt mal kurz. \n- Zeus zu Atlas",
    "Bei uns wird Gleichberechtigung groß geschrieben. \n- Der Duden",
    "Und er sprach: Es werde Licht! Und es ward Licht. \n- Thomas Alva Edison",
    "Orange is the new Black. \n- Donald Trump",
    "Designed to make a difference. \n- Das Minuszeichen",
    "Guten Freunden gibt man ein Küsschen. \n- Judas",
    "Hurra, hurra die Hexe brennt! \n- Petunia Dursley",
    "Der Bass muss ficken. \n- Richard Wagner",
    "Deine Mudda! \n- Siegmund Freud",
    "Die Krone: eine Kopfbedeckung, \ndie den Kopf überflüssig macht. \n- Ludwig XVI",
    "Ihr Ziel befindet sich rechts. \n- Gandalf der Graue",
    "Teile meiner Antwort \nkönnten die Bevölkerung verunsichern. \n- Herodes",
    "HALT STOP, JETZT REDE ICH! \n- Kim Jong-un",
    "Zwei geh\'n rein, einer kommt raus. \n- Jack the Ripper"]
GAME_COLOR_BACKGROUND_START: Final = "lightblue"
GAME_COLOR_BACKGROUND_END: Final = "lightblue"
GAME_COLOR_BACKGROUND_PLAYER_1: Final = "red"
GAME_COLOR_BACKGROUND_PLAYER_2: Final = "green"
GAME_COLOR_BACKGROUND_VLADESC: Final = "spring green"

GAME_INFO_CONTENT = ("************************\n"
                     "Autoren: OFR Sonnberger und OFRzS Blank\n"
                     "Code wizard: Vladesc\n"
                     "Date: Schuljahr 2023/2024\n"
                     "Version: 0.8.15\n"
                     "************************")

GAME_RULES_CONTENT = ("> Ziel des Spiels <\n"
                      "Das Ziel von 4-Gewinnt ist es, als erster Spieler vier seiner Spielsteine in eine waagerechte,\n"
                      "senkrechte oder diagonale Reihe zu platzieren.\n"
                      "> Spielbrett <\n"
                      "Das Spielbrett besteht aus 7 Spalten und 6 Reihen, was insgesamt 42 Feldern entspricht.\n"
                      "> Spielvorbereitung:\n"
                      "Das Spiel beginnt mit einem leeren Spielbrett.\n"
                      "Es gibt zwei Spieler:\n"
                      "Spieler 1 verwendet rote Spielsteine,\n"
                      "Spieler 2 verwendet grüne Spielsteine.\n"
                      "> Spielablauf <\n"
                      "Die Spieler setzen abwechselnd einen Spielstein in eine der leeren Spalten des Spielbretts.\n"
                      "Die Spielsteine fallen immer bis zum untersten freien Feld in der ausgewählten Spalte.\n"
                      "Das Ziel ist es, vier Spielsteine in einer Reihe zu platzieren, entweder horizontal, vertikal oder diagonal.\n"
                      "Ein Spieler gewinnt, wenn er als Erster vier seiner Spielsteine in einer Reihe platziert hat.\n"
                      "Das Spiel endet unentschieden, wenn das Spielbrett voll ist und keiner der Spieler vier\n"
                      "Spielsteine in einer Reihe hat.\n"
                      "> Spielmodi <\n"
                      "Spieler gegen Spieler: Zwei Spieler treten gegeneinander an.\n"
                      "Spieler gegen KI: Ein Spieler tritt gegen die künstliche Intelligenz an.\n"
                      "> Gewinnerklärung <\n"
                      "Der Spieler, der zuerst vier seiner Spielsteine in einer Reihe platziert, gewinnt das Spiel.\n"
                      "Wir wünschen Ihnen nun viel Spaß und spannende Partien bei unserem 4-Gewinnt.")
