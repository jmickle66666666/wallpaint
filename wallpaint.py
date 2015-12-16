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
	#tiles img_from onto img_to with optional offset
	if offset is None: offset = (0,0)
	
	for i in range()

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
    
    print "zs {} {} {} {}".format(z1,z2,z3,z4)
    print "length {}".format(length)
    print "f_height {}".format(f_height)
    print "b_height {}".format(b_height)
    print sidedef.tx_up
    print sidedef.tx_mid
    print sidedef.tx_low
    
    tx_u = None
    tx_m = None
    tx_d = None
    
    if sidedef.tx_up != "-": tx_u = make_texture(sidedef.tx_up)
    if sidedef.tx_mid != "-": tx_m = make_texture(sidedef.tx_mid)
    if sidedef.tx_low != "-": tx_d = make_texture(sidedef.tx_low)
    
    sec_mid = Image.new("RGB",(length,z3-z2),"black")
    for i in range(0,int(length/tx_m.size[0])):
        for j in range(0,int((z3-z2)/tx_m.size[0])):
            sec_mid.paste(tx_m,(i*tx_m.size[0],j*tx_m.size[1]))
            
    sec_mid.show()
    
    line_img = Image.new("RGB",(length,f_height),"black")
    draw = ImageDraw.Draw(line_img)
    draw.rectangle((0,z1-z1,length,z1-z2),fill="#ff0000")
    draw.rectangle((0,z1-z2,length,z1-z3),fill="#ffff00")
    draw.rectangle((0,z1-z3,length,z1-z4),fill="#00ffff")
    
    
    #line_img.show()


    
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
        for l in lines:
            build_line(l)