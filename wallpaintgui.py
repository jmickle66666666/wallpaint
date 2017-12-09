from tkinter import *


class LoadDialogue(Tk):
    def __init__(self, parent=None):
        Tk.__init__(self, parent)
        self.title("Load")


if __name__ == "__main__":
    app = LoadDialogue()
    app.mainloop()