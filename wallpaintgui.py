from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
import omg
import drawmap
import wallpaint
from PIL import Image
from PIL import ImageTk
import threading
import os
import webbrowser


class LoadDialogue(Tk):
    def __init__(self, parent=None):
        Tk.__init__(self, parent)
        self.title("wallpaint")
        self.frame = Frame(self, width=320, height=240, bg="#222222")
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
        self.minsize(640, 640)
        self.configure(pady=8, padx=8)
        self.select_map_button = None
        self.map_preview = None
        self.test_frame = None
        img = Image.open("header.png")

        self.header_image = ImageTk.PhotoImage(img)
        self.init_gui()

    def init_gui(self):
        self.configure(bg="#222222")
        self.title_label = Label(self.frame, text="title", bg="#222222")
        self.title_label.configure(image=self.header_image)
        self.title_label.grid(columnspan=3, sticky="NEW")
        self.load_path = Entry(self.frame, state=DISABLED)
        self.load_path.grid(row=1, column=0, columnspan=3, sticky="EW")
        self.load_button = Button(self.frame, text="...", command=self.load_wad)
        self.load_button.grid(row=1, column=2, sticky="E")
        self.focus()
        self.select_map_button = Button(self.frame, text="Open", command=self.open_map)
        self.select_map_button.grid(row=3, column=0, sticky="wS")
        self.map_select = Listbox(self.frame, width=6, selectmode=SINGLE)
        self.map_select.grid(row=2, column=0, sticky="NSWE")
        self.map_select.bind("<<ListboxSelect>>", self.on_map_select)
        self.map_preview = Label(self.frame, bg="#000")
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
        MapView(None, self.path, self.map_select.get(index))


class MapView(Tk):
    def __init__(self, parent, wadpath, mapname):
        Tk.__init__(self, parent)
        self.title(mapname)
        self.frame = Frame(self)
        self.frame.grid(sticky="NEWS")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.frame.rowconfigure(4, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.map_canvas = None
        self.preview_button = None
        self.export_button = None
        self.clear_button = None
        self.line_list_box = None
        self.textures_button = None

        self.bg_color = "#221c23"
        self.line_color = "#ac3232"
        self.selected_color = "#4d6c30"
        self.highlight_color = "#fcf337"
        self.selected_highlight_color = "#9be753"

        self.wp = wallpaint.Wallpaint(wadpath, mapname)

        self.line_list = []

        self.wadpath = wadpath
        self.wad = omg.WAD(wadpath)
        self.mapname = mapname

        self.scale = 0.1

        self.max_scale = 1.0
        self.min_scale = 0.01
        self.mouse_x = 0
        self.mouse_y = 0

        self.init_gui()
        self.build_map()

        # Event binding
        self.map_canvas.bind(sequence="<ButtonPress-1>", func=self.on_mouse_down)
        self.map_canvas.bind(sequence="<Motion>", func=self.on_mouse_move)
        self.map_canvas.bind(sequence="<ButtonRelease-1>", func=self.on_mouse_up)
        self.map_canvas.bind_all(sequence="<KeyPress>", func=self.on_key_down)
        self.map_canvas.bind_all(sequence="<KeyRelease>", func=self.on_key_up)
        # self.map_canvas.bind(sequence="<MouseWheel>", func=self.on_mouse_wheel)

        self.dragging = False
        self.mouse_down = False
        self.last_pos = (0, 0)

        if not os.path.isfile("texture_packs.txt"):
            if messagebox.askyesno("hey", "looks like you have no texture wads set up (like iwads) , wanna fix that?"):
                TexturePackSelector()

    def init_gui(self):
        self.map_canvas = Canvas(self.frame, width=640, height=480, bg=self.bg_color)
        self.map_canvas.grid(row=0, column=0, rowspan=5, sticky="NEWS")

        self.preview_button = Button(self.frame, text="preview", command=self.create_preview)
        self.preview_button.grid(row=0, column=1, sticky="NEW")

        self.clear_button = Button(self.frame, text="clear", command=self.clear_lines)
        self.clear_button.grid(row=1, column=1, sticky="NEW")

        self.textures_button = Button(self.frame, text="textures", command=TexturePackSelector)
        self.textures_button.grid(row=3, column=1, sticky="NEW")

        self.line_list_box = Listbox(self.frame, width=6)
        self.line_list_box.grid(row=4, column=1, sticky="NEWS")

        self.export_button = Button(self.frame, text="export", command=self.export)
        self.export_button.grid(row=2, column=1, sticky="NEW")

    def create_preview(self):
        # print("wallpaint {} {}".format(self.mapname, self.line_list))
        lines = []
        for l in self.line_list:
            lines.append(int(l)-1)
        self.wp.preview(lines)

    def clear_lines(self):
        self.line_list = []
        self.line_list_box.delete(0, END)
        self.update_line_colors()

    def build_map(self):
        minx = 10000
        miny = 10000
        maxx = -10000
        maxy = -10000
        mapeditor = omg.MapEditor(self.wad.maps[self.mapname])

        for l in mapeditor.linedefs:
            vx_a = mapeditor.vertexes[l.vx_a]
            vx_b = mapeditor.vertexes[l.vx_b]

            minx = min(minx, vx_a.x)
            miny = min(miny, vx_a.y)
            maxx = max(maxx, vx_a.x)
            maxy = max(maxy, vx_a.y)
            minx = min(minx, vx_b.x)
            miny = min(miny, vx_b.y)
            maxx = max(maxx, vx_b.x)
            maxy = max(maxy, vx_b.y)

            self.map_canvas.create_line(vx_a.x * self.scale,
                                        -vx_a.y * self.scale,
                                        vx_b.x * self.scale,
                                        -vx_b.y * self.scale,
                                        fill=self.line_color,
                                        tags=mapeditor.linedefs.index(l) + 1)

        self.map_canvas.move("all", self.map_canvas.winfo_reqwidth() / 2, self.map_canvas.winfo_reqheight() / 2)

    def export(self):
        lines = []
        for l in self.line_list:
            lines.append(int(l) - 1)
        self.wp.save(lines, asksaveasfilename(title="Save unwrapped image!", initialfile="output.png"))
        webbrowser.open("file://" + os.path.dirname(os.path.realpath(__file__)))

        self.close()
        RebuildDialogue().mainloop()

    def close(self):
        self.destroy()

    # Event handlers
    def on_key_down(self, event):
        if event.char == " ":
            self.dragging = True

        if event.char == "]":
            self.scale_map(1)

        if event.char == "[":
            self.scale_map(-1)

        if event.char == "c":
            self.clear_lines()

    def scale_map(self, delta):
        last_scale = self.scale
        if self.max_scale > (self.scale + (delta * 0.1)) > self.min_scale:
            self.scale += (delta * 0.1)
            delta = self.scale / last_scale
            self.map_canvas.scale("all", self.mouse_x, self.mouse_y, delta, delta)

    def on_key_up(self, event):
        if event.char == " ":
            self.dragging = False

    def on_mouse_down(self, event):

        closest = self.map_canvas.find_closest(self.mouse_x, self.mouse_y)
        line_id = self.map_canvas.gettags(closest)[0]

        if line_id not in self.line_list:
            self.line_list.append(line_id)
            self.line_list_box.insert(END, line_id)
        else:
            index = self.line_list.index(line_id)
            del self.line_list[index]
            self.line_list_box.delete(index)

        self.update_line_colors()

        self.mouse_down = True

    def on_mouse_up(self, event):
        # self.update_cursor(event)
        self.mouse_down = False

    def on_mouse_wheel(self, event):
        print("is this happening")
        last_scale = self.scale
        if self.max_scale > (self.scale + (event.delta * 0.1)) > self.min_scale:
            self.scale += (event.delta * 0.1)
            delta = self.scale / last_scale
            self.map_canvas.scale("all", event.x, event.y, delta, delta)

    def on_mouse_move(self, event):
        move = (event.x - self.last_pos[0], event.y - self.last_pos[1])
        self.last_pos = (event.x, event.y)
        self.mouse_x = event.x
        self.mouse_y = event.y

        # Canvas dragging
        if self.dragging:
            self.map_canvas.move("all", move[0], move[1])

        self.update_line_colors()

    def update_line_colors(self):
        # Highlight nearest line
        self.map_canvas.itemconfig("all", fill=self.line_color, width=1.0)

        for l in self.line_list:
            self.map_canvas.itemconfig(self.map_canvas.find_withtag(l)[0], fill=self.selected_color, width=1.0)

        closest = self.map_canvas.find_closest(self.mouse_x, self.mouse_y)
        if self.map_canvas.gettags(closest)[0] in self.line_list:
            self.map_canvas.itemconfig(closest, fill=self.selected_highlight_color, width=2.0)
        else:
            self.map_canvas.itemconfig(closest, fill=self.highlight_color, width=2.0)


class RebuildDialogue(Tk):
    def __init__(self, parent = None):
        Tk.__init__(self, parent)
        self.wp = wallpaint.Wallpaint()
        self.title("Rebuild")
        self.label = Label(self, text="When you're done editing, hit ok!!!")
        self.ok_button = Button(self, text="ok!!!", command=self.ok)
        self.label.grid()
        self.ok_button.grid(row=1)
        self.configure(padx=16, pady=16)

    def ok(self):
        self.wp.rebuild(asksaveasfilename(title="Save your new wad!!", initialfile="output.wad"))
        webbrowser.open("file://" + os.path.dirname(os.path.realpath(__file__)))
        self.destroy()


class TexturePackSelector(Tk):
    def __init__(self, parent=None):
        Tk.__init__(self, parent)
        self.title("Texture Packs")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.pack_list = Listbox(self, width=40, selectmode=SINGLE)
        self.pack_list.grid(rowspan=2, sticky="NEWS")
        self.add_button = Button(self, text="+", command=self.add)
        self.add_button.grid(row=0, column=1, sticky="EN")
        self.remove_button = Button(self, text="-", command=self.remove)
        self.remove_button.grid(row=1, column=1, sticky="EN")
        self.done_button = Button(self, text="ok", command=self.done)
        self.done_button.grid(row=1, column=1, sticky="ES")

        self.packs = []

        if os.path.isfile("texture_packs.txt"):
            with open("texture_packs.txt", "r") as f:
                self.packs = f.readlines()

        for t in self.packs:
            self.pack_list.insert(END, t)

    def add(self):
        path = askopenfilename()
        self.pack_list.insert(END, path)

    def remove(self):
        if len(self.pack_list.curselection()) > 0:
            index = int(self.pack_list.curselection()[0])
            self.pack_list.delete(index)

    def done(self):
        self.packs = []
        for i in self.pack_list.get(0, END):
            self.packs.append(i)
        with open("texture_packs.txt", "w") as f:
            f.writelines(self.packs)
        self.destroy()


if __name__ == "__main__":
    if os.path.exists('walldat.json'):
        app = RebuildDialogue()

    app = LoadDialogue()
    app.mainloop()
