from tkinter import *
from tkinter.filedialog import askopenfilename
import omg
import drawmap
from PIL import Image
from PIL import ImageTk
import threading


class LoadDialogue(Tk):
    def __init__(self, parent=None):
        Tk.__init__(self, parent)
        self.title("wallpaint")
        self.frame = Frame(self, width=320, height=240)
        self.frame.grid(sticky="NSWE")
        self.frame.rowconfigure(2, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.load_button = None
        self.title_label = None
        self.load_path = None
        self.path = ""
        self.map_select = None
        self.wad = None
        # self.resizable(False, False)
        self.minsize(640, 480)
        self.configure(pady=8, padx=8)
        self.select_map_button = None
        self.map_preview = None

        self.test_frame = None

        self.init_gui()

    def init_gui(self):
        self.title_label = Label(self.frame, text="pick you're poison,,")
        self.title_label.grid(columnspan=3, sticky="NEW")
        self.load_path = Entry(self.frame, state=DISABLED)
        self.load_path.grid(row=1, column=0, columnspan=3, sticky="EW")
        self.load_button = Button(self.frame, text="...", command=self.load_wad)
        self.load_button.grid(row=1, column=2, sticky="E")
        self.select_map_button = Button(self.frame, text="Open", command=self.open_map)
        self.select_map_button.grid(row=3, column=0, sticky="wS")
        self.map_select = Listbox(self.frame, width=6, selectmode=SINGLE)
        self.map_select.grid(row=2, column=0, sticky="NSWE")
        self.map_select.bind("<<ListboxSelect>>", self.on_map_select)
        img = self.blank_image()
        self.map_preview = Label(self.frame, image=img, bg="#000")
        self.map_preview.image = img
        self.map_preview.grid(row=2, column=1, rowspan=2, columnspan=2, sticky="NEWS")

    def on_map_select(self, e):
        index = self.map_select.curselection()[0]
        name = self.map_select.get(index)

        def async_update_image():
            img = drawmap.drawmap(self.wad,
                                  name,
                                  self.map_preview.winfo_width() - 10,
                                  self.map_preview.winfo_height() - 10)
            pimg = ImageTk.PhotoImage(img)
            self.map_preview.configure(image=pimg)
            self.map_preview.image = pimg

        t = threading.Thread(target=async_update_image)
        t.start()

    def blank_image(self):
        image = Image.new("RGB", (100, 100), color="black")
        return ImageTk.PhotoImage(image)

    def load_wad(self):
        self.path = askopenfilename()

        self.load_path.config(state=NORMAL)
        self.load_path.delete(0, END)
        self.load_path.insert(0, self.path)
        self.load_path.config(state=DISABLED)

        self.map_select.delete(0, END)

        self.wad = omg.WAD(self.path)
        for m in self.wad.maps:
            self.map_select.insert(END, m)

    def open_map(self):
        index = self.map_select.curselection()[0]
        print(self.map_select.get(index))


if __name__ == "__main__":
    app = LoadDialogue()
    app.mainloop()