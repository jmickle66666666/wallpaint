import omg, sys, math, omg.txdef, json, os.path, random, string
from PIL import Image, ImageDraw

class Wallpaint():
    def __init__(self, wadpath = None, mapid = None):
        self.cache = {}
        self.tex_packs = []
        self.wad_path = wadpath
        self.map_id = mapid
        if self.wad_path is not None:
            self.wad = omg.WAD(self.wad_path)
        if self.map_id is not None:
            self.wmap = omg.mapedit.MapEditor(self.wad.maps[self.map_id])
        self.wtex = None
        self.loaded_textures = False

    def load_texturepacks(self):
        self.loaded_textures = True
        tpaths = [line.rstrip('\n') for line in open("texture_packs.txt")]
        tpaths.insert(len(tpaths), self.wad_path)
        for p in tpaths:
            try:
                self.tex_packs.append(omg.WAD(p))
            except:
                pass

    def tile_image(self, img_from, img_to, offset=None):
        # tiles img_from onto img_to with optional offset
        if offset is None:
            offset = (0, 0)

        for i in range(img_to.size[0]):
            for j in range(img_to.size[1]):
                px = img_from.getpixel(((i + offset[0]) % img_from.size[0], (j + offset[1]) % img_from.size[1]))
                img_to.putpixel((i, j), px)

        return img_to

    def make_texture(self, t):
        # return an Image of a texture (build from patches)

        if not self.loaded_textures:
            self.load_texturepacks()

        if t in self.cache.keys():
            return self.cache[t]

        texture_wad = None
        texture_def = None
        texture_ch = None

        master_list = []

        for tx_ch in self.tex_packs:
            txd = omg.txdef.Textures(tx_ch.txdefs)
            txw = tx_ch
            master_list.append(txw)
            if t in txd:
                texture_wad = txw
                texture_def = txd
                texture_ch = tx_ch

        if texture_def is None:
            print("!!CANNOT FIND {} IN TEXTURE PACKS!!".format(t))
            print("")
            print("try editing texture_packs.txt and adding your texture wad path to it")
            return

        output = Image.new("RGB", (texture_def[t].width, texture_def[t].height))
        for p in texture_def[t].patches:
            for tx in master_list:
                if p.name.upper() in tx.patches:
                    pimg = tx.patches[p.name.upper()].to_Image()
                    output.paste(pimg, (p.x, p.y))
                    break

        self.cache[t] = output

        return output

    def line_length(self, line):
        i = self.wmap.vertexes[line.vx_a]
        j = self.wmap.vertexes[line.vx_b]
        return int(math.sqrt((i.x - j.x)**2 + (i.y - j.y)**2))

    def build_line(self, line):
        if not self.loaded_textures:
            self.load_texturepacks()

        linedef = self.wmap.linedefs[line]
        sidedef = self.wmap.sidedefs[linedef.front]
        sector = self.wmap.sectors[sidedef.sector]

        length = self.line_length(linedef)
        f_height = sector.z_ceil - sector.z_floor
        b_height = 0

        z1 = sector.z_ceil
        z2 = z1
        z4 = sector.z_floor
        z3 = z4

        if linedef.back > -1:
            bsid = self.wmap.sidedefs[linedef.back]
            bsec = self.wmap.sectors[bsid.sector]
            b_height = bsec.z_ceil - bsec.z_floor
            if bsec.z_ceil < z1: z2 = bsec.z_ceil
            if bsec.z_floor > z4: z3 = bsec.z_floor

        tx_u = None
        tx_m = None
        tx_d = None

        line_img = Image.new("RGB", (length, f_height), "black")

        offs = (sidedef.off_x, sidedef.off_y)

        secs = [0,0,0]

        if sidedef.tx_up != "-" and z1 != z2:
            secs[0] = 1
            tx_u = self.make_texture(sidedef.tx_up)
            if linedef.upper_unpeg:
                uoffs = (offs[0], offs[1])
            else:
                uoffs = (offs[0], offs[1]-(z1-z2))
            sec_up = Image.new("RGB", (length,z1-z2), "black")
            sec_up = self.tile_image(tx_u, sec_up, uoffs)
            line_img.paste(sec_up, (0, z1-z1))
        if sidedef.tx_mid != "-":
            secs[1] = 1
            if linedef.lower_unpeg:
                moffs = (offs[0],offs[1]-(z2-z3))
            else:
                moffs = (offs[0],offs[1])
            tx_m = self.make_texture(sidedef.tx_mid)
            sec_mid = Image.new("RGB", (length, z2-z3), "black")
            sec_mid = self.tile_image(tx_m, sec_mid, moffs)
            line_img.paste(sec_mid, (0, z1-z2))
        if sidedef.tx_low != "-" and z3 != z4:
            secs[2] = 1
            if linedef.lower_unpeg:
                loffs = (offs[0],offs[1]-(z3-z4))
            else:
                loffs = (offs[0],offs[1])
            tx_d = self.make_texture(sidedef.tx_low)
            sec_low = Image.new("RGB", (length, z3-z4), "black")
            sec_low = self.tile_image(tx_d, sec_low, loffs)
            line_img.paste(sec_low, (0, z1-z3))

        return line_img, z1, z4, line, secs

    def build_all(self, lines):
        if not self.loaded_textures:
            self.load_texturepacks()

        built_lines = []
        for l in lines:
            built_lines.append(self.build_line(l))

        length = 0
        top = -32767
        bottom = 32767
        for l in built_lines:
            length += l[0].size[0]
            if l[1] > top: top = l[1]
            if l[2] < bottom: bottom = l[2]

        output = Image.new("RGB", (length, top - bottom), "black")

        ldat = []

        o = 0
        for l in built_lines:
            dline = {}
            dline['id'] = l[3]
            dline['offsetx'] = o
            dline['offsety'] = top-l[1]
            dline['length'] = l[0].size[0]
            dline['height'] = l[1] - l[2]
            dline['secs'] = l[4]
            output.paste(l[0],(o,top-l[1]))
            o += l[0].size[0]
            ldat.append(dline)

        wdat = {}
        wdat['linedata'] = ldat
        wdat['wad_path'] = self.wad_path
        wdat['map_id'] = self.map_id

        # with open('walldat.json', 'w') as outfile:
            # json.dump(wdat, outfile)

        # output.save('output.png')

        return output, wdat

    def preview(self, linelist):
        if not self.loaded_textures:
            self.load_texturepacks()
        self.build_all(linelist)[0].show("Preview")

    def save(self, linelist, filename):
        if not self.loaded_textures:
            self.load_texturepacks()
        image, data = self.build_all(linelist)
        data["image_path"] = filename

        with open('walldat.json', 'w') as outfile:
            json.dump(data, outfile)

        image.save(filename)


    def rebuild(self, output_path):
        if os.path.exists('walldat.json') != True:
            print("no data found: walldat.json")
            return

        with open('walldat.json') as openfile:
            wjson = json.load(openfile)
        self.wad_path = wjson['wad_path']
        self.map_id = wjson['map_id']
        line_data = wjson['linedata']
        tex_img = Image.open(wjson['image_path'],'r')
        self.wad = omg.WAD(str(self.wad_path))
        self.wmap = omg.MapEditor(self.wad.maps[str(self.map_id)])
        self.txd = omg.txdef.Textures()
        for l in line_data:
            limg = tex_img.crop((l['offsetx'],l['offsety'],l['offsetx']+l['length'],l['offsety']+l['height'])).copy()
            limg = limg.convert('RGB')
            # add image to textures
            tname = self.getname()
            patch = omg.Graphic()
            patch.from_Image(limg)
            self.wad.patches[tname] = patch
            self.txd[tname] = omg.txdef.TextureDef()
            self.txd[tname].name = tname
            self.txd[tname].patches.append(omg.txdef.PatchDef())
            self.txd[tname].patches[0].name = tname
            self.txd[tname].width, self.txd[tname].height = patch.dimensions

            # set line's sidedef textures to this
            linedef = self.wmap.linedefs[l['id']]
            sidedef = self.wmap.sidedefs[linedef.front]
            sidedef.off_x = 0
            sidedef.off_y = 0
            linedef.upper_unpeg = True
            linedef.lower_unpeg = False
            if l['secs'][0] == 1: sidedef.tx_up = tname
            if l['secs'][1] == 1: sidedef.tx_mid = tname
            if l['secs'][2] == 1:
                sidedef.tx_low = tname
                linedef.lower_unpeg = True

        self.wad.txdefs = self.txd.to_lumps()
        self.wad.maps[str(self.map_id)] = self.wmap.to_lumps()
        self.wad.to_file(output_path)
        os.remove('walldat.json')
        os.remove(wjson['image_path'])

    def getname(self):
        ltrs = string.digits + string.ascii_uppercase

        def n_2_l(n):
            sid = ""
            while n > len(ltrs):
                sid += ltrs[n % len(ltrs)]
                n = int(n/len(ltrs))
            sid += ltrs[n]
            return sid[::-1]

        n = 0
        while "WPT"+n_2_l(n) in self.wad.patches:
            n += 1

        return "WPT"+n_2_l(n)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        if "rebuild" in sys.argv:
            wp = Wallpaint()
            wp.rebuild("output.wad")
        else:
            print("usage:")
            print("    wallpaint.py wad map [line numbers]")
    else:

        lines = []
        for i in range(3, len(sys.argv)):
            lines.append(int(sys.argv[i]))
        wp = Wallpaint(sys.argv[1], sys.argv[2].upper())

        wp.save(lines,"output.png")
