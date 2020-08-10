from b import b
from pprint import pprint

screen_width, screen_height = 3000, 1000
platform_width, platform_height = b*4, b*4
map = ['-'*(screen_width//platform_width)]
map += [' '*(screen_width//platform_width-2) + '-' for i in range(screen_height//platform_height-2)]
map += ['-' * (screen_width // platform_width)]

pprint(map)

