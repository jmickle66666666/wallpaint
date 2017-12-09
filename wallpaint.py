import omg, sys, math, omg.txdef, json, os.path, random, string
from PIL import Image, ImageDraw

cache = {}
tex_packs = []
wad_path = None
map_id = None
wad = None
wmap = None
wtex = None


def load_texturepacks():
    tpaths = [line.rstrip('\n') for line in open('texture_packs.txt')]
    tpaths.insert(0, wad_path)
    for p in tpaths:
        try:
            tex_packs.append(omg.WAD(p))
        except:
            pass


def tile_image(img_from,img_to,offset=None):
    # tiles img_from onto img_to with optional offset
    if offset is None: 
        offset = (0,0)
    
    for i in range(img_to.size[0]):
        for j in range(img_to.size[1]):
            px = img_from.getpixel(((i + offset[0]) % img_from.size[0], (j + offset[1]) % img_from.size[1]))
            img_to.putpixel((i, j), px)
            
    return img_to


def make_texture(t):
    # return an Image of a texture (build from patches)
    
    if t in cache.keys():
        return cache[t]
    
    for tx_ch in tex_packs:
        txd = omg.txdef.Textures(tx_ch.txdefs)
        txw = tx_ch
        if t in txd:
            break
        
    if t not in txd: 
        print("!!CANNOT FIND {} IN TEXTURE PACKS!!".format(t))
        print("")
        print("try editing texture_packs.txt and adding your texture wad path to it")
        return

    output = Image.new("RGB", (txd[t].width, txd[t].height))
    for p in txd[t].patches:
        pimg = txw.patches[p.name.upper()].to_Image()
        output.paste(pimg, (p.x, p.y))
        
    cache[t] = output
        
    return output
    

def line_length(line):
    i = wmap.vertexes[line.vx_a]
    j = wmap.vertexes[line.vx_b]
    return int(math.sqrt((i.x - j.x)**2 + (i.y - j.y)**2))


def build_line(line):
    linedef = wmap.linedefs[line]
    sidedef = wmap.sidedefs[linedef.front]
    sector = wmap.sectors[sidedef.sector]
    
    length = line_length(linedef)
    f_height = sector.z_ceil - sector.z_floor
    b_height = 0
    
    z1 = sector.z_ceil
    z2 = z1
    z4 = sector.z_floor
    z3 = z4
    
    if linedef.back > -1:
        bsid = wmap.sidedefs[linedef.back]
        bsec = wmap.sectors[bsid.sector]
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
        tx_u = make_texture(sidedef.tx_up)
        if linedef.upper_unpeg:
            uoffs = (offs[0], offs[1])
        else:
            uoffs = (offs[0], offs[1]-(z1-z2))
        sec_up = Image.new("RGB", (length,z1-z2), "black")
        sec_up = tile_image(tx_u, sec_up, uoffs)
        line_img.paste(sec_up, (0, z1-z1))
    if sidedef.tx_mid != "-": 
        secs[1] = 1
        if linedef.lower_unpeg:
            moffs = (offs[0],offs[1]-(z2-z3))
        else:
            moffs = (offs[0],offs[1])
        tx_m = make_texture(sidedef.tx_mid)
        sec_mid = Image.new("RGB", (length, z2-z3), "black")
        sec_mid = tile_image(tx_m, sec_mid, moffs)
        line_img.paste(sec_mid, (0, z1-z2))
    if sidedef.tx_low != "-" and z3 != z4: 
        secs[2] = 1
        if linedef.lower_unpeg:
            loffs = (offs[0],offs[1]-(z3-z4))
        else:
            loffs = (offs[0],offs[1])
        tx_d = make_texture(sidedef.tx_low)
        sec_low = Image.new("RGB", (length, z3-z4), "black")
        sec_low = tile_image(tx_d, sec_low, loffs)
        line_img.paste(sec_low, (0, z1-z3))
    
    return line_img,z1,z4,line,secs


def build_all(lines):
    built_lines = []
    for l in lines:
        built_lines.append(build_line(l))
        
    length = 0
    top = -32767
    bottom = 32767
    for l in built_lines:
        length += l[0].size[0]
        if l[1] > top: top = l[1]
        if l[2] < bottom: bottom = l[2]
        
    output = Image.new("RGB",(length,top - bottom),"black")
    
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
    wdat['wad_path'] = wad_path
    wdat['map_id'] = map_id
    
    with open('walldat.json', 'w') as outfile:
        json.dump(wdat, outfile)

    output.save('output.png')

def rebuild():
    if os.path.exists('walldat.json') != True:
        print("no data found: walldat.json")
        return

    with open('walldat.json') as openfile:
        wjson = json.load(openfile)
    wad_path = wjson['wad_path']
    map_id = wjson['map_id']
    line_data = wjson['linedata']
    tex_img = Image.open('output.png','r')
    global wad
    wad = omg.WAD(str(wad_path))
    wmap = omg.MapEditor(wad.maps[str(map_id)])
    txd = omg.txdef.Textures()
    for l in line_data:
        limg = tex_img.crop((l['offsetx'],l['offsety'],l['offsetx']+l['length'],l['offsety']+l['height'])).copy()
        limg = limg.convert('RGB')
        # add image to textures
        tname = getname()
        patch = omg.Graphic()
        patch.from_Image(limg)
        wad.patches[tname] = patch
        txd[tname] = omg.txdef.TextureDef()
        txd[tname].name = tname
        txd[tname].patches.append(omg.txdef.PatchDef())
        txd[tname].patches[0].name = tname
        txd[tname].width, txd[tname].height = patch.dimensions

        # set line's sidedef textures to this
        linedef = wmap.linedefs[l['id']]
        sidedef = wmap.sidedefs[linedef.front]
        sidedef.off_x = 0
        sidedef.off_y = 0
        linedef.upper_unpeg = True
        linedef.lower_unpeg = False
        if l['secs'][0] == 1: sidedef.tx_up = tname
        if l['secs'][1] == 1: sidedef.tx_mid = tname
        if l['secs'][2] == 1: 
            sidedef.tx_low = tname
            linedef.lower_unpeg = True

    wad.txdefs = txd.to_lumps()
    wad.maps[str(map_id)] = wmap.to_lumps()
    wad.to_file('output.wad')
    os.remove('walldat.json')
    os.remove('output.png')


def getname():
    ltrs = string.digits + string.ascii_uppercase

    def n_2_l(n):
        sid = ""
        while n > len(ltrs):
            sid += ltrs[n % len(ltrs)]
            n = int(n/len(ltrs))
        sid += ltrs[n]
        return sid[::-1]

    n = 0
    while "WPT"+n_2_l(n) in wad.patches:
        n += 1

    return "WPT"+n_2_l(n)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        if "rebuild" in sys.argv:
            rebuild()
        else:
            print("usage:")
            print("    wallpaint.py wad map [line numbers]")
    else :
        wad_path = sys.argv[1]
        map_id = sys.argv[2].upper()
        lines = []
        for i in range(3,len(sys.argv)):
            lines.append(int(sys.argv[i]))
            
        load_texturepacks()
        wad = omg.WAD(wad_path)
        wmap = omg.mapedit.MapEditor(wad.maps[map_id])
        build_all(lines)
