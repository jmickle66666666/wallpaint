# wallpaint!
easy (well, easier) megatexturing in doom

# why?
Wallpaint is a tool to easily extract patches of textures from walls in a map.

This way, you can paint over and edit sections of walls in your map without having to mess with creating complicated composite textures.

# what?
check out this example: https://imgur.com/a/QKM8T

# how?
usage:
`wallpaint <wad_name> <map_name> [..linedef numbers]`
(eg wallpaint test.wad map01 1 3 50 2 35)

then edit output.png to your liking, then:

`wallpaint rebuild`



wallpaint will build an image of the *front* side of all the linedefs provided, correct with offsets and pegging. You can then paint over the image in whatever image editor you like, and the image will be split back into seperate textures and placed back onto the sidedefs in the map. textures will be converted to doom palette and palletized automatically.

when you rebuild, a wad "output.wad" will be created (and overwritten if already exists!) instead of editing the map in place. 