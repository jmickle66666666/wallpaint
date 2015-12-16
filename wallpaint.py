import omg, sys, math, omg.txdef
from PIL import Image, ImageDraw

cache = {}
tex_packs = []
wad = None
wmap = None
wtex = None

def load_texturepacks():
    tpaths = [line.rstrip('\n') for line in open('texture_packs.txt')]
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
            px = img_from.getpixel(( (i + offset[0]) % img_from.size[0], (j + offset[1]) % img_from.size[1] ))
            img_to.putpixel((i,j),px)
            
    return img_to

# def texture_to_image(

def make_texture(t):
    # return an Image of a texture (build from patches)
    
    if t in cache.keys():
        return cache[t]
    
    for tx_ch in tex_packs:
        txd = omg.txdef.Textures(tx_ch.txdefs)
        txw = tx_ch
        if t in txd: break
        
    if t not in txd: 
        print ("!!CANNOT FIND {} IN TEXTURE PACKS!!".format(t))
        print ("")
        print ("try editing texture_packs.txt and adding your texture wad path to it")
        return
    
    
    output = Image.new("RGB",(txd[t].width,txd[t].height))
    for p in txd[t].patches:
        pimg = txw.patches[p.name.upper()].to_Image()
        output.paste(pimg,(p.x,p.y))
        
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
    
    # print "zs {} {} {} {}".format(z1,z2,z3,z4)
    # print "length {}".format(length)
    # print "f_height {}".format(f_height)
    # print "b_height {}".format(b_height)
    # print sidedef.tx_up
    # print sidedef.tx_mid
    # print sidedef.tx_low
    
    tx_u = None
    tx_m = None
    tx_d = None
    
    line_img = Image.new("RGB",(length,f_height),"black")
    
    offs = (sidedef.off_x,sidedef.off_y)
    
    if sidedef.tx_up != "-" and z1 != z2: 
        tx_u = make_texture(sidedef.tx_up)
        if linedef.upper_unpeg:
            uoffs = (offs[0],offs[1])
        else:
            uoffs = (offs[0],offs[1]-(z1-z2))
        sec_up = Image.new("RGB",(length,z1-z2),"black")
        sec_up = tile_image(tx_u,sec_up,uoffs)
        line_img.paste(sec_up,(0,z1-z1))
    if sidedef.tx_mid != "-": 
        if linedef.lower_unpeg:
            moffs = (offs[0],offs[1]-(z2-z3))
        else:
            moffs = (offs[0],offs[1])
        tx_m = make_texture(sidedef.tx_mid)
        sec_mid = Image.new("RGB",(length,z2-z3),"black")
        sec_mid = tile_image(tx_m,sec_mid,moffs)
        line_img.paste(sec_mid,(0,z1-z2))
    if sidedef.tx_low != "-" and z3 != z4: 
        if linedef.lower_unpeg:
            loffs = (offs[0],offs[1]-(z3-z4))
        else:
            loffs = (offs[0],offs[1])
        tx_d = make_texture(sidedef.tx_low)
        sec_low = Image.new("RGB",(length,z3-z4),"black")
        sec_low = tile_image(tx_d,sec_low,loffs)
        line_img.paste(sec_low,(0,z1-z3))
    
    return (line_img,z1,z4)

def build_all(lines):
    built_lines = []
    for l in lines:
        built_lines.append(build_line(l))
        
    length = 0
    top = -32767
    bottom = 32767
    for l in built_lines:
        length += l[0].size[0]
        # print l[1]
        if l[1] > top: top = l[1]
        if l[2] < bottom: bottom = l[2]
        
    # print top 
    # print bottom
        
    output = Image.new("RGB",(length,top - bottom),"black")
    
    o = 0
    for l in built_lines:
        output.paste(l[0],(o,top-l[1]))
        o += l[0].size[0]
    
    output.show()

    
if __name__=="__main__":
    if len(sys.argv) < 3:
        print "usage:"
        print "    wallpaint.py wad map [line numbers]"
    else :
        wad_path = sys.argv[1]
        map_id = sys.argv[2].upper()
        lines = []
        for i in range(3,len(sys.argv)):
            lines.append(int(sys.argv[i]))
            
        load_texturepacks()
        wad = omg.WAD(wad_path)
        wmap = omg.mapedit.MapEditor(wad.maps[map_id])
        #build_line(lines[0])[0].show()
        build_all(lines)