import tkinter as tk


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.geometry('%dx%d+%d+%d' % (width, height, x, y))


def create_window():
    window = tk.Tk()
    window.title("Spieler")
    window.geometry("800x480")
    window.configure(bg="red")

    text_label = tk.Label(window, text="Spieler 2", bg="red", fg="white", font=("Helvetica", 24))
    text_label.pack(pady=50, padx=50)

    # Beenden-Button zentriert unten
    quit_button = tk.Button(window, text="Beenden", command=window.destroy, bg="red", fg="white")
    quit_button.pack(side=tk.BOTTOM, pady=20)

    # Musik-Button zentriert unten
    music_button = tk.Button(window, text="Musik", bg="green", fg="white")
    music_button.pack(side=tk.BOTTOM, pady=20)

    window.mainloop()


if __name__ == "__main__":
    create_window()
